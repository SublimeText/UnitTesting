# Docker image for Sublime Text UnitTesting

## Recommended usage

Use the launcher script:

```sh
# from UnitTesting repo root
./docker/ut-run-tests /path/to/package
./docker/ut-run-tests /path/to/package --file tests/test_example.py
```

Or call it via absolute path from any package directory:

```sh
/path/to/UnitTesting/docker/ut-run-tests .
```

If this directory is on your `PATH`, you can run `ut-run-tests` directly.

The launcher calls `docker/run_tests.py`, builds/uses a local image,
mounts the package at `/project`, runs tests headlessly, and keeps a cache
volume for fast reruns.

By default it:

- builds `unittesting-local` image from `./docker` if missing
- mounts your repo as `/project`
- runs Python unit tests, syntax tests and syntax compatibility checks
- runs UnitTesting through the same CI shell entrypoints
- stores Sublime install/cache in docker volume `unittesting-home`
- synchronizes only changed files into `Packages/<Package>` using `rsync`
- excludes files ignored by Git, including repository-local and global rules

A category with no matching resources is reported and succeeds. Disable
categories that are not needed with:

```sh
ut-run-tests . --no-unit-tests
ut-run-tests . --no-syntax-tests
ut-run-tests . --no-syntax-compatibility-checks
```

`--file` selects its category automatically. Python files run as unit tests,
files whose names start with `syntax_test` run as syntax tests, and
`.sublime-syntax` files run compatibility checks:

```sh
ut-run-tests . --file tests/test_example.py
ut-run-tests . --file syntax_test_example
ut-run-tests . --file Example.sublime-syntax
```

`--pattern` and `--tests-dir` try every enabled category. Use the
`--no-*` options to avoid running unrelated categories when desired.

## Fast reruns

The container entrypoint writes a marker in `/root/.cache/unittesting`.
With `-v unittesting-home:/root`, bootstrap/install runs once and later runs
only refresh your package files and execute tests.

## Concurrent runs and races

The shared cache volume contains the Sublime data directory, including
`Packages`, `Lib`, UnitTesting schedules and test output files. *Concurrent
runs against the same volume are serialized by default* to avoid races while
copying packages, writing schedules and syncing Package Control libraries.
This is a speed-versus-space trade-off: tests are likely to run quickly,
keeping wait times low, and a shared volume uses less disk space than
multiple volumes.

Use `--lock-timeout SECONDS` to control how long a runner waits for the cache
volume lock. Use `--no-lock` only if you know the selected cache volume is not
shared by another runner.

You can increase concurrency by choosing how many cache volumes you use. For
example, a stable volume per package allows different packages to run
concurrently while still keeping warm caches:

```sh
ut-run-tests . --cache-volume unittesting-home-gitsavvy
```

To *maximize* concurrency, use a stable volume per checkout directory. For
example, in a POSIX shell:

```sh
volume="unittesting-home-$(pwd -P | sha256sum | cut -c1-12)"
ut-run-tests . --cache-volume "$volume"
```

Runs that choose different volumes do not wait on each other. Runs that choose
the same volume remain serialized.

## Refresh/update controls (without direct docker commands)

Use launcher flags instead of calling `docker` manually:

- `--refresh-cache`: recreate `unittesting-home` cache volume (forces fresh
  bootstrap, including Sublime Text/Package Control install path)
- `--refresh-image`: rebuild local image (for Dockerfile/entrypoint changes)
- `--refresh`: both `--refresh-cache` and `--refresh-image`

Examples:

```sh
ut-run-tests . --refresh-image
ut-run-tests . --refresh-cache
ut-run-tests . --refresh
```

## Dry run (metadata and schedule only)

Use `--dry-run` to print runner metadata (including detected Sublime
Text and Package Control versions) plus the generated schedule.

```sh
ut-run-tests . --dry-run
```

## Colored output

Use `--color` to control ANSI colors in test output:

- `--color auto` (default): color only when stdout is a TTY
- `--color always`: force color
- `--color never`: disable color

```sh
ut-run-tests . --color always
```

## Manual docker usage

```sh
# build from UnitTesting/docker
docker build -t unittesting-local .

# run from package root
docker run --rm -it \
  -e PACKAGE=$PACKAGE \
  -v $PWD:/project \
  -v unittesting-home:/root \
  unittesting-local run_tests
```

Run a single test file

```sh
docker run --rm -it \
  -e PACKAGE=$PACKAGE \
  -v $PWD:/project \
  -v unittesting-home:/root \
  unittesting-local run_tests --tests-dir tests --pattern test_example.py
```
