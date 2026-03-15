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
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_IMAGE = "unittesting-local"
DEFAULT_CACHE_VOLUME = "unittesting-home"
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

    image = args.docker_image
    maybe_build_image(image, args)

    if args.pull:
        run_checked(["docker", "pull", image])

    if args.cache_volume:
        ensure_docker_volume(args.cache_volume)

    command = build_docker_run_command(
        package_root=package_root,
        unit_testing_root=unit_testing_root,
        package_name=package_name,
        image=image,
        cache_volume=args.cache_volume,
        sublime_text_version=args.sublime_text_version,
        scheduler_delay_ms=args.scheduler_delay_ms,
        coverage=args.coverage,
        failfast=args.failfast,
        tests_dir=tests_dir,
        pattern=pattern,
    )

    print(f"Package root: {package_root}")
    print(f"Package name: {package_name}")
    print(f"Docker image: {image}")
    print(f"Scheduler delay: {args.scheduler_delay_ms}ms")
    if args.cache_volume:
        print(f"Cache volume: {args.cache_volume}")
    if tests_dir and pattern:
        print(f"Test target: {tests_dir}/{pattern}")

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
    parser.add_argument("--file", help="Run only tests from this file.")
    parser.add_argument("--pattern", help="Custom unittest discovery pattern.")
    parser.add_argument("--tests-dir", help="Custom tests directory.")
    parser.add_argument("--package-name", help="Override package name.")
    parser.add_argument("--coverage", action="store_true", help="Enable coverage.")
    parser.add_argument("--failfast", action="store_true", help="Stop on first failure.")

    parser.add_argument(
        "--docker-image",
        default=DEFAULT_IMAGE,
        help=f"Docker image to run (default: {DEFAULT_IMAGE}).",
    )
    parser.add_argument(
        "--cache-volume",
        default=DEFAULT_CACHE_VOLUME,
        help=(
            "Docker volume mounted at /root to cache Sublime setup "
            f"(default: {DEFAULT_CACHE_VOLUME})."
        ),
    )
    parser.add_argument(
        "--no-cache-volume",
        dest="cache_volume",
        action="store_const",
        const=None,
        help="Disable persistent cache volume.",
    )
    parser.add_argument(
        "--sublime-text-version",
        type=int,
        default=4,
        help="Sublime Text major version inside container.",
    )
    parser.add_argument(
        "--scheduler-delay-ms",
        type=int,
        default=0,
        help="Delay before running scheduled tests inside Sublime (default: 0).",
    )
    parser.add_argument(
        "--pull",
        action="store_true",
        help="Pull docker image before running.",
    )

    parser.add_argument(
        "--build-image",
        action="store_true",
        help="Force rebuild of local docker image from script directory.",
    )
    parser.add_argument(
        "--build-if-missing",
        dest="build_if_missing",
        action="store_true",
        default=True,
        help="Build image from script directory if missing (default: true).",
    )
    parser.add_argument(
        "--no-build-if-missing",
        dest="build_if_missing",
        action="store_false",
        help="Do not auto-build image if missing.",
    )

    args = parser.parse_args(argv)

    if args.file and args.pattern:
        parser.error("--file and --pattern are mutually exclusive")

    return args


def ensure_docker() -> None:
    if not shutil.which("docker"):
        raise SystemExit("Error: docker executable not found in PATH")


def maybe_build_image(image: str, args: argparse.Namespace) -> None:
    context_dir = Path(__file__).resolve().parent
    if not context_dir.is_dir():
        raise SystemExit(f"Error: missing docker build context: {context_dir}")

    context_hash = docker_context_hash(context_dir)
    image_exists = docker_image_exists(image)
    image_hash = docker_image_context_hash(image) if image_exists else None
    context_changed = image_exists and image_hash != context_hash

    should_build = args.build_image
    should_build = should_build or (args.build_if_missing and not image_exists)
    should_build = should_build or context_changed

    if not should_build:
        return

    if context_changed and not args.build_image:
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
    sublime_text_version: int,
    scheduler_delay_ms: int,
    coverage: bool,
    failfast: bool,
    tests_dir: str | None,
    pattern: str | None,
) -> list[str]:
    command = ["docker", "run", "--rm", "-t"]
    if sys.stdin.isatty():
        command.append("-i")

    command.extend(["-e", f"PACKAGE={package_name}"])
    command.extend(["-e", f"SUBLIME_TEXT_VERSION={sublime_text_version}"])
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

    if tests_dir:
        command.extend(["--tests-dir", tests_dir])

    if pattern:
        command.extend(["--pattern", pattern])

    return command


def run_checked(command: list[str]) -> None:
    result = subprocess.run(command)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
