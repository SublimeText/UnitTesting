#!/usr/bin/env python3
"""Run Sublime Text UnitTesting in a Docker container.

Usually invoked via the sibling launcher script `ut-run-tests`.
Examples:
    ./docker/ut-run-tests .
    ./docker/ut-run-tests . --file tests/test_main.py
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


DEFAULT_IMAGE = "unittesting-local"
DEFAULT_CACHE_VOLUME = "unittesting-home"
DEFAULT_LOCK_TIMEOUT = 3600
DOCKER_CONTEXT_HASH_LABEL = "org.sublimetext.unittesting.context-hash"
DOCKER_CONTEXT_INPUTS = (
    "Dockerfile",
    "docker.sh",
    "entrypoint.sh",
    "xvfb",
)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    ensure_docker()

    if args.refresh:
        args.refresh_image = True
        args.refresh_cache = True

    image = args.docker_image

    if args.refresh_image or args.refresh_cache:
        if args.refresh_image:
            maybe_build_image(image, refresh=True)

        if args.cache_volume and args.refresh_cache:
            if should_lock_cache(args):
                with CacheVolumeLock(args.cache_volume, args.lock_timeout):
                    wait_for_cache_volume_idle(args.cache_volume, args.lock_timeout)
                    remove_stale_runner_container(args.cache_volume)
                    reset_docker_volume(args.cache_volume)
                    ensure_docker_volume(args.cache_volume)
            else:
                reset_docker_volume(args.cache_volume)
                ensure_docker_volume(args.cache_volume)

        print("Refresh complete.")
        return 0

    package_root = args.package_root.resolve()
    if not package_root.is_dir():
        print(f"Error: package root does not exist: {package_root}", file=sys.stderr)
        return 2

    unit_testing_root = Path(__file__).resolve().parent.parent
    if not unit_testing_root.is_dir():
        print(
            f"Error: UnitTesting root does not exist: {unit_testing_root}",
            file=sys.stderr,
        )
        return 2

    package_name = args.package_name or package_root.name
    tests_dir, pattern = resolve_test_target(
        package_root, args.file, args.tests_dir, args.pattern
    )

    maybe_build_image(image, refresh=False)

    if args.cache_volume:
        ensure_docker_volume(args.cache_volume)

    lock_enabled = should_lock_cache(args)
    runner_name = docker_cache_runner_name(args.cache_volume) if lock_enabled else None
    command = build_docker_run_command(
        package_root=package_root,
        unit_testing_root=unit_testing_root,
        package_name=package_name,
        image=image,
        cache_volume=args.cache_volume,
        container_name=runner_name,
        scheduler_delay_ms=args.scheduler_delay_ms,
        coverage=args.coverage,
        failfast=args.failfast,
        reload_package_on_testing=args.reload_package_on_testing,
        dry_run=args.dry_run,
        color=args.color,
        tests_dir=tests_dir,
        pattern=pattern,
    )

    print(f"Package root: {package_root}")
    print(f"Package name: {package_name}")
    print(f"Docker image: {image}")
    print(f"Scheduler delay: {args.scheduler_delay_ms}ms")
    if args.refresh_image:
        print("Image refresh: enabled")
    if args.cache_volume:
        print(f"Cache volume: {args.cache_volume}")
        if lock_enabled:
            print("Cache lock: enabled")
        if args.refresh_cache:
            print("Cache refresh: enabled")
    if tests_dir and pattern:
        print(f"Test target: {tests_dir}/{pattern}")

    if lock_enabled:
        with CacheVolumeLock(args.cache_volume, args.lock_timeout):
            wait_for_cache_volume_idle(args.cache_volume, args.lock_timeout)
            ensure_runner_container_name_available(args.cache_volume, args.lock_timeout)
            return call_docker_run_with_name_retry(
                command, args.cache_volume, args.lock_timeout
            )

    return subprocess.call(command)


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run UnitTesting headlessly in Docker."
    )

    parser.add_argument(
        "package_root",
        nargs="?",
        default=".",
        type=Path,
        help="Path to the package root (default: current directory).",
    )

    test_group = parser.add_argument_group("test options")
    test_group.add_argument("--file", help="Run only tests from this file.")
    test_group.add_argument("--pattern", help="Custom unittest discovery pattern.")
    test_group.add_argument("--tests-dir", help="Custom tests directory.")
    test_group.add_argument("--package-name", help="Override package name.")
    test_group.add_argument("--coverage", action="store_true", help="Enable coverage.")
    test_group.add_argument("--failfast", action="store_true", help="Stop on first failure.")
    test_group.add_argument(
        "--reload-package-on-testing",
        action="store_true",
        help="Reload package under test before running tests.",
    )
    test_group.add_argument(
        "--scheduler-delay-ms",
        type=int,
        default=0,
        help="Delay before running scheduled tests inside Sublime (default: 0).",
    )
    test_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print runtime metadata and schedule.",
    )
    test_group.add_argument(
        "--color",
        choices=("auto", "always", "never"),
        default="auto",
        help="Colorize test output (default: auto).",
    )

    docker_group = parser.add_argument_group("docker options")
    docker_group.add_argument(
        "--refresh",
        action="store_true",
        help="Rebuild image and recreate cache volume.",
    )
    docker_group.add_argument(
        "--docker-image",
        default=DEFAULT_IMAGE,
        help=f"Docker image to run (default: {DEFAULT_IMAGE}).",
    )
    docker_group.add_argument(
        "--refresh-image",
        action="store_true",
        help="Rebuild the local Docker image.",
    )
    docker_group.add_argument(
        "--cache-volume",
        default=DEFAULT_CACHE_VOLUME,
        help=(
            "Docker volume mounted at /root to cache Sublime setup "
            f"(default: {DEFAULT_CACHE_VOLUME})."
        ),
    )
    docker_group.add_argument(
        "--no-cache-volume",
        dest="cache_volume",
        action="store_const",
        const=None,
        help="Disable persistent cache volume.",
    )
    docker_group.add_argument(
        "--refresh-cache",
        action="store_true",
        help=(
            "Recreate the cache volume so Sublime Text and Package Control "
            "are re-installed."
        ),
    )
    docker_group.add_argument(
        "--lock-timeout",
        type=float,
        default=DEFAULT_LOCK_TIMEOUT,
        help=(
            "Seconds to wait for another runner using the same cache volume "
            f"(default: {DEFAULT_LOCK_TIMEOUT})."
        ),
    )
    docker_group.add_argument(
        "--no-lock",
        action="store_true",
        help="Disable cache-volume serialization (unsafe for concurrent runs).",
    )

    args = parser.parse_args(argv)

    if args.file and args.pattern:
        parser.error("--file and --pattern are mutually exclusive")

    if args.refresh_cache and not args.cache_volume:
        parser.error("--refresh-cache requires a cache volume (omit --no-cache-volume)")

    if args.dry_run and (args.refresh or args.refresh_image or args.refresh_cache):
        parser.error("--dry-run cannot be combined with --refresh* options")

    if args.lock_timeout < 0:
        parser.error("--lock-timeout must be greater than or equal to 0")

    return args


def ensure_docker() -> None:
    if not shutil.which("docker"):
        raise SystemExit("Error: docker executable not found in PATH")


def maybe_build_image(image: str, refresh: bool) -> None:
    context_dir = Path(__file__).resolve().parent
    if not context_dir.is_dir():
        raise SystemExit(f"Error: missing docker build context: {context_dir}")

    context_hash = docker_context_hash(context_dir)
    image_exists = docker_image_exists(image)
    image_hash = docker_image_context_hash(image) if image_exists else None
    context_changed = image_exists and image_hash != context_hash

    should_build = refresh or not image_exists or context_changed
    if not should_build:
        return

    if context_changed and not refresh:
        print("Docker context changed since last image build, rebuilding...")

    print(f"Building docker image '{image}' from {context_dir} ...")
    run_checked([
        "docker",
        "build",
        "--label",
        f"{DOCKER_CONTEXT_HASH_LABEL}={context_hash}",
        "-t",
        image,
        str(context_dir),
    ])


def docker_image_exists(image: str) -> bool:
    result = subprocess.run(
        ["docker", "image", "inspect", image],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def docker_context_hash(context_dir: Path) -> str:
    digest = hashlib.sha256()
    for rel_path in DOCKER_CONTEXT_INPUTS:
        file_path = context_dir / rel_path
        if not file_path.is_file():
            raise SystemExit(f"Error: missing docker context file: {file_path}")

        digest.update(rel_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_path.read_bytes())
        digest.update(b"\0")

    return digest.hexdigest()


def docker_image_context_hash(image: str) -> str | None:
    result = subprocess.run(
        [
            "docker",
            "image",
            "inspect",
            image,
            "--format",
            "{{ index .Config.Labels \"%s\" }}" % DOCKER_CONTEXT_HASH_LABEL,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    if result.returncode != 0:
        return None

    value = result.stdout.strip()
    if not value or value == "<no value>":
        return None

    return value


def ensure_docker_volume(name: str) -> None:
    result = subprocess.run(
        ["docker", "volume", "inspect", name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode == 0:
        return

    run_checked(["docker", "volume", "create", name])


def reset_docker_volume(name: str) -> None:
    result = subprocess.run(
        ["docker", "volume", "inspect", name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        return

    print(f"Resetting cache volume: {name}")
    run_checked(["docker", "volume", "rm", name])


def resolve_test_target(
    package_root: Path,
    test_file: str | None,
    tests_dir: str | None,
    pattern: str | None,
) -> tuple[str | None, str | None]:
    if not test_file:
        return tests_dir, pattern

    file_path = Path(test_file)
    if not file_path.is_absolute():
        file_path = package_root / file_path
    file_path = file_path.resolve()

    if not file_path.is_file():
        raise SystemExit(f"Error: test file does not exist: {file_path}")

    try:
        rel_file_path = file_path.relative_to(package_root)
    except ValueError:
        raise SystemExit(f"Error: file is outside package root: {file_path}")

    rel_parent = rel_file_path.parent.as_posix()
    resolved_tests_dir = rel_parent if rel_parent else "."
    resolved_pattern = rel_file_path.name
    return resolved_tests_dir, resolved_pattern


def build_docker_run_command(
    package_root: Path,
    unit_testing_root: Path,
    package_name: str,
    image: str,
    cache_volume: str | None,
    container_name: str | None,
    scheduler_delay_ms: int,
    coverage: bool,
    failfast: bool,
    reload_package_on_testing: bool,
    dry_run: bool,
    color: str,
    tests_dir: str | None,
    pattern: str | None,
) -> list[str]:
    command = ["docker", "run", "--rm"]
    if container_name:
        command.extend(["--name", container_name])

    if sys.stdin.isatty():
        command.append("-i")
    if sys.stdout.isatty():
        command.append("-t")

    command.extend(["-e", f"PACKAGE={package_name}"])
    command.extend(["-e", f"UNITTESTING_SCHEDULER_DELAY_MS={scheduler_delay_ms}"])
    command.extend(["-e", "UNITTESTING_SOURCE=/unittesting"])
    command.extend(["-e", "PYTHONUNBUFFERED=1"])
    command.extend(["-v", f"{package_root}:/project"])
    command.extend(["-v", f"{unit_testing_root}:/unittesting"])

    if cache_volume:
        command.extend(["-v", f"{cache_volume}:/root"])

    command.append(image)
    command.append("run_tests")

    if coverage:
        command.append("--coverage")

    if failfast:
        command.append("--failfast")

    if reload_package_on_testing:
        command.append("--reload-package-on-testing")

    if dry_run:
        command.append("--dry-run")

    command.extend(["--color", color])

    if tests_dir:
        command.extend(["--tests-dir", tests_dir])

    if pattern:
        command.extend(["--pattern", pattern])

    return command


def should_lock_cache(args: argparse.Namespace) -> bool:
    return bool(args.cache_volume and not args.no_lock)


def call_docker_run_with_name_retry(
    command: list[str], cache_volume: str, timeout: float
) -> int:
    deadline = time.monotonic() + timeout

    while True:
        returncode = subprocess.call(command)
        if returncode != 125:
            return returncode

        # Docker returns 125 for daemon/CLI errors, including the atomic
        # container-name conflict we use as a last line of defense if another
        # launcher did not observe the host-side lock.
        if docker_container_status(docker_cache_runner_name(cache_volume)) is None:
            return returncode

        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return returncode

        ensure_runner_container_name_available(cache_volume, remaining)


def wait_for_cache_volume_idle(cache_volume: str, timeout: float) -> None:
    deadline = time.monotonic() + timeout
    next_notice = 0.0

    while True:
        container_names = docker_running_container_names_using_volume(cache_volume)
        if not container_names:
            return

        now = time.monotonic()
        if now >= deadline:
            names = ", ".join(container_names)
            raise SystemExit(
                f"Timed out waiting for Docker volume '{cache_volume}' "
                f"to become idle. Running containers: {names}"
            )

        if now >= next_notice:
            names = ", ".join(container_names)
            print(
                f"Waiting for Docker volume '{cache_volume}' "
                f"to become idle: {names}"
            )
            next_notice = now + 5

        time.sleep(min(1, max(0, deadline - now)))


def ensure_runner_container_name_available(cache_volume: str, timeout: float) -> None:
    runner_name = docker_cache_runner_name(cache_volume)
    deadline = time.monotonic() + timeout
    next_notice = 0.0

    while True:
        status = docker_container_status(runner_name)
        if status is None:
            return

        if status in ("created", "exited", "dead"):
            remove_docker_container(runner_name)
            return

        now = time.monotonic()
        if now >= deadline:
            raise SystemExit(
                f"Timed out waiting for Docker container '{runner_name}' "
                f"to finish. Current status: {status}"
            )

        if now >= next_notice:
            print(
                f"Waiting for Docker container '{runner_name}' "
                f"to finish. Current status: {status}"
            )
            next_notice = now + 5

        time.sleep(min(1, max(0, deadline - now)))


def remove_stale_runner_container(cache_volume: str) -> None:
    runner_name = docker_cache_runner_name(cache_volume)
    status = docker_container_status(runner_name)
    if status in ("created", "exited", "dead"):
        remove_docker_container(runner_name)


def docker_cache_runner_name(cache_volume: str) -> str:
    digest = hashlib.sha256(cache_volume.encode("utf-8")).hexdigest()[:16]
    return f"unittesting-runner-{digest}"


def docker_running_container_names_using_volume(cache_volume: str) -> list[str]:
    result = subprocess.run(
        [
            "docker",
            "ps",
            "--filter",
            f"volume={cache_volume}",
            "--format",
            "{{.Names}}",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    if result.returncode != 0:
        return []

    return [name for name in result.stdout.splitlines() if name]


def docker_container_status(container_name: str) -> str | None:
    result = subprocess.run(
        [
            "docker",
            "container",
            "inspect",
            container_name,
            "--format",
            "{{.State.Status}}",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    if result.returncode != 0:
        return None

    return result.stdout.strip() or None


def remove_docker_container(container_name: str) -> None:
    run_checked(["docker", "container", "rm", container_name])


class CacheVolumeLock:
    def __init__(self, cache_volume: str, timeout: float) -> None:
        self.cache_volume = cache_volume
        self.timeout = timeout
        self.path = cache_lock_file_path(cache_volume)
        self.file = None

    def __enter__(self) -> "CacheVolumeLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.file = self.path.open("a+", encoding="utf-8")

        deadline = time.monotonic() + self.timeout
        next_notice = 0.0

        while True:
            if try_lock_file(self.file):
                self.write_lock_info()
                return self

            now = time.monotonic()
            if now >= deadline:
                raise SystemExit(
                    f"Timed out waiting for UnitTesting Docker cache lock: {self.path}"
                )

            if now >= next_notice:
                print(
                    f"Waiting for UnitTesting Docker cache lock for "
                    f"volume '{self.cache_volume}'..."
                )
                next_notice = now + 5

            time.sleep(min(1, max(0, deadline - now)))

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self.file is None:
            return

        unlock_file(self.file)
        self.file.close()
        self.file = None

    def write_lock_info(self) -> None:
        assert self.file is not None
        self.file.seek(0)
        self.file.truncate()
        self.file.write(f"volume={self.cache_volume}\n")
        self.file.write(f"pid={os.getpid()}\n")
        self.file.write(f"time={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n")
        self.file.flush()


def cache_lock_file_path(cache_volume: str) -> Path:
    digest = hashlib.sha256(cache_volume.encode("utf-8")).hexdigest()[:16]
    return Path(tempfile.gettempdir()) / "unittesting-docker-locks" / f"{digest}.lock"


def try_lock_file(lock_file) -> bool:
    if os.name == "nt":
        return try_lock_file_windows(lock_file)

    return try_lock_file_posix(lock_file)


def unlock_file(lock_file) -> None:
    if os.name == "nt":
        unlock_file_windows(lock_file)
    else:
        unlock_file_posix(lock_file)


def try_lock_file_windows(lock_file) -> bool:
    import msvcrt

    ensure_lock_byte(lock_file)
    lock_file.seek(0)
    try:
        msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError:
        return False

    return True


def unlock_file_windows(lock_file) -> None:
    import msvcrt

    lock_file.seek(0)
    msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)


def try_lock_file_posix(lock_file) -> bool:
    import fcntl

    try:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        return False

    return True


def unlock_file_posix(lock_file) -> None:
    import fcntl

    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def ensure_lock_byte(lock_file) -> None:
    lock_file.seek(0, os.SEEK_END)
    if lock_file.tell() != 0:
        return

    lock_file.write("\0")
    lock_file.flush()


def run_checked(command: list[str]) -> None:
    result = subprocess.run(command)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
