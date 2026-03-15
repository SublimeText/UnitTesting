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
- runs UnitTesting through the same CI shell entrypoints
- stores Sublime install/cache in docker volume `unittesting-home`
- synchronizes only changed files into `Packages/<Package>` using `rsync`

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

## Fast reruns

The container entrypoint writes a marker in `/root/.cache/unittesting`.
With `-v unittesting-home:/root`, bootstrap/install runs once and later runs
only refresh your package files and execute tests.

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

## Run a single test file

```sh
docker run --rm -it \
  -e PACKAGE=$PACKAGE \
  -v $PWD:/project \
  -v unittesting-home:/root \
  unittesting-local run_tests --tests-dir tests --pattern test_example.py
```
