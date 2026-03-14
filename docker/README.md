# Docker image for Sublime Text UnitTesting

## Recommended usage

Use the docker wrapper script:

```sh
uv run docker/run_tests.py /path/to/package
uv run docker/run_tests.py /path/to/package --file tests/test_example.py
```

It builds/uses a local image, mounts the package at `/project`, runs tests
headlessly, and keeps a cache volume for fast reruns.

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

## Run a single test file

```sh
docker run --rm -it \
  -e PACKAGE=$PACKAGE \
  -v $PWD:/project \
  -v unittesting-home:/root \
  unittesting-local run_tests --tests-dir tests --pattern test_example.py
```
