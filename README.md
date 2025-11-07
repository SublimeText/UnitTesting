UnitTesting
===========

[![test](https://github.com/SublimeText/UnitTesting/actions/workflows/test.yaml/badge.svg)](https://github.com/SublimeText/UnitTesting/actions/workflows/test.yaml)
[![codecov](https://codecov.io/gh/SublimeText/UnitTesting/branch/master/graph/badge.svg)](https://codecov.io/gh/SublimeText/UnitTesting)

This is a unittest framework for Sublime Text.
It runs unittest testcases on local machines and via Github Actions.
It also supports testing syntax_test files for the new [sublime-syntax](https://www.sublimetext.com/docs/3/syntax.html) 
format and sublime-color-scheme files.

## Preparation

1. Install [UnitTesting](https://github.com/SublimeText/UnitTesting) via Package Control.
2. Your package!
3. TestCases should be placed in `test*.py` under the directory `tests` 
   (configurable, see below). The testcases are then loaded by [TestLoader.discover](https://docs.python.org/3.3/library/unittest.html#unittest.TestLoader.discover).

[Here](https://github.com/randy3k/UnitTesting-example) are some small examples


## Running Tests Locally

### Command Palette

1. Open `Command Palette` using <kbd>ctrl+shift+P</kbd> or menu item `Tools → Command Palette...`
2. Choose a `Unittesting: ...` command to run and hit <kbd>Enter</kbd>

To test any package...

1. run `UnitTesting: Test Package` 
2. enter the package name in the input panel and hit enter.

An output panel pops up displaying progress and results of running tests. 

To run only tests in particular files, enter `<Package name>:<filename>`.
`<filename>` should be a unix shell wildcard to match the file names.
`<Package name>:test*.py` is used by default.

The command `UnitTesting: Test Current Package` runs all tests 
of the current package the active view's file is part of.
The package is reloaded to pickup any code changes and then tests are executed.

The command `UnitTesting: Test Current Package with Coverage`
runs tests for current package and generates a coverage report via [coverage](https://pypi.python.org/pypi/coverage).
The [.coveragerc](.coveragerc) file is used to control coverage configurations. 
If it is missing, UnitTesting will ignore the `tests` directory.

> [!NOTE]
>
> As of Unittesting 1.8.0 the following commands have been replaced
> to enable more flexible usage and integration in build systems.
>
> unit_testing_current_package
>
>   ```json
>   { "command": "unit_testing", "package": "$package_name" }
>   ```
>
> unit_testing_current_file
>
>   ```json
>   { "command": "unit_testing", "package": "$package_name", "pattern": "$file_name" }
>   ```


### Build System

To run tests via build system specify `unit_testing` build system `"target"`.

```json
{
  "target": "unit_testing"
}
```


### Project specific `Test Current Package` build command

It is recommended to add the following to _.sublime-project_ file 
so that <kbd>ctrl</kbd>+<kbd>b</kbd> would invoke the testing action.

```json
"build_systems":
[
  {
    "name": "Test Current Package",
    "target": "unit_testing",
    "package": "$package_name",
    "failfast": true
  }
]
```


### Project specific `Test Current File` build command

It is recommended to add the following to _.sublime-project_ file 
so that <kbd>ctrl</kbd>+<kbd>b</kbd> would invoke the testing action.

```json
"build_systems":
[
  {
    "name": "Test Current File",
    "target": "unit_testing",
    "package": "$package_name",
    "pattern": "$file_name",
    "failfast": true
  }
]
```


## GitHub Actions

Unittesting provides the following GitHub Actions, which can be combined
in a workflow to design package tests.

1. SublimeText/UnitTesting/actions/setup
   
   _Setup Sublime Text to run tests within._

   > This must always be the first step after checking out the package to test.

2. SublimeText/UnitTesting/actions/run-color-scheme-tests
  
   _Test color schemes using [ColorSchemeUnit](https://packagecontrol.io/packages/ColorSchemeUnit)._

3. SublimeText/UnitTesting/actions/run-syntax-tests

   _Test sublime-syntax definitions using built-in syntax test functions of already running Sublime Text environment._

   > It is an alternative to [SublimeText/syntax-test-action](https://github.com/SublimeText/syntax-test-action) 
   > or sublimehq's online syntax_test_runner

4. SublimeText/UnitTesting/actions/run-tests

   _Runs the `unit_testing` command to perform python unit tests._

> [!NOTE]
> 
> actions are released in the branch [`v1`](https://github.com/SublimeText/UnitTesting/tree/v1). 
> Minor changes will be pushed to the same branch unless there are breaking changes.


### Color Scheme Tests

To integrate color scheme tests via [ColorSchemeUnit](https://packagecontrol.io/packages/ColorSchemeUnit) 
add the following snippet to a workflow file
(e.g. `.github/workflows/color-scheme-tests.yml`).

```yaml
name: ci-color-scheme-tests

on: [push, pull_request]

jobs:
  run-syntax-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: SublimeText/UnitTesting/actions/setup@v1
      - uses: SublimeText/UnitTesting/actions/run-color-scheme-tests@v1
```


### Syntax Tests

To run only syntax tests add the following snippet to a workflow file
(e.g. `.github/workflows/syntax-tests.yml`).

```yaml
name: ci-syntax-tests

on: [push, pull_request]

jobs:
  run-syntax-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: SublimeText/UnitTesting/actions/setup@v1
      - uses: SublimeText/UnitTesting/actions/run-syntax-tests@v1
```

> [!NOTE]
>
> If you are looking for syntax tests only, you may also checkout [SublimeText/syntax-test-action](https://github.com/SublimeText/syntax-test-action).
> Using this test makes most sense to just re-use an already set-up ST test environment.

### Unit Tests

To run only python unit tests on all platforms and versions of Sublime Text
add the following snippet to a workflow file (e.g. `.github/workflows/unit-tests.yml`).

```yaml
name: ci-unit-tests

on: [push, pull_request]

jobs:
  run-tests:
    strategy:
      fail-fast: false
      matrix:
        st-version: [3, 4]
        os: ["ubuntu-latest", "macOS-latest", "windows-latest"]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: SublimeText/UnitTesting/actions/setup@v1
        with:
          package-name: Package Name   # if differs from repo name
          sublime-text-version: ${{ matrix.st-version }}
      - uses: SublimeText/UnitTesting/actions/run-tests@v1
        with:
          coverage: true
          package-name: Package Name   # if differs from repo name
      - uses: codecov/codecov-action@v4
```


### Run All Tests

```yaml
name: ci-tests

on: [push, pull_request]

jobs:
  run-tests:
    strategy:
      fail-fast: false
      matrix:
        st-version: [3, 4]
        os: ["ubuntu-latest", "macOS-latest", "windows-latest"]
    runs-on: ${{ matrix.os }}
    steps:
      # checkout package to test
      - uses: actions/checkout@v4

      # setup test environment
      - uses: SublimeText/UnitTesting/actions/setup@v1
        with:
          sublime-text-version: ${{ matrix.st-version }}

      # run color scheme tests (only on Linux)
      - if: ${{ matrix.os == 'ubuntu-latest' }}
        uses: SublimeText/UnitTesting/actions/run-color-scheme-tests@v1
      
      # run syntax tests and check compatibility with new syntax engine (only on Linux)
      - if: ${{ matrix.os == 'ubuntu-latest' }}
        uses: SublimeText/UnitTesting/actions/run-syntax-tests@v1
        with:
          compatibility: true
      
      # run unit tests with coverage upload
      - uses: SublimeText/UnitTesting/actions/run-tests@v1
        with:
          coverage: true
          extra-packages: |
            A File Icon:SublimeText/AFileIcon
      - uses: codecov/codecov-action@v4
```

Check [this](https://github.com/randy3k/UnitTesting-example) for further examples.


## Options

### Package Configuration

UnitTesting is primarily configured by `unittesting.json` file in package root directory.

```json
{
  "verbosity": 1,
  "coverage": true
}
```

### Build System Configuration

Options provided via build system configuration override `unittesting.json`.

```json
{
  "target": "unit_testing",
  "package": "$package_name",
  "verbosity": 2,
  "coverage": true
}
```

### Command Arguments

Options passed as arguments to `unit_testing` command override `unittesting.json`.

```py
window.run_command("unit_testing", {"package": "$package_name", "coverage": False})
```

### Available Options

| name                        | description                                                  | default value |
| --------------------------- | ------------------------------------------------------------ | ------------- |
| tests_dir                   | the name of the directory containing the tests               | "tests"       |
| pattern                     | the pattern to discover tests                                | "test*.py"    |
| deferred                    | whether to use deferred test runner                          | true          |
| condition_timeout           | default timeout in ms for callables invoked via `yield`      | 4000          |
| failfast                    | stop early if a test fails                                   | false         |
| output                      | name of the test output instead of showing <br> in the panel | null          |
| verbosity                   | verbosity level                                              | 2             |
| warnings                    | The warnings filter controls python warnings treatment.      | "default"     |
| capture_console             | capture stdout and stderr in the test output                 | false         |
| reload_package_on_testing   | reloading package will increase coverage rate                | true          |
| coverage                    | track test case coverage                                     | false         |
| coverage_on_worker_thread   | (experimental)                                               | false         |
| generate_html_report        | generate HTML report for coverage                            | false         |
| generate_xml_report         | generate XML report for coverage                             | false         |

Valid `warnings` values are:

| Value     | Disposition
| --------- | -----------
| "default" | print the first occurrence of matching warnings for each location (module + line number) where the warning is issued
| "error"   | turn matching warnings into exceptions
| "ignore"  | never print matching warnings
| "always"  | always print matching warnings
| "module"  | print the first occurrence of matching warnings for each module where the warning is issued (regardless of line number)
| "once"    | print only the first occurrence of matching warnings, regardless of location

see also: https://docs.python.org/3/library/warnings.html#warning-filter

## Writing Unittests

UnitTesting is based on python's `unittest` library. 
Any valid unittest test case is allowed.

Example:

_tests/test_myunit.py_

```py
from unittesting import TestCase

class MyTestCase(TestCase):

  def test_something(self):
    self.assertTrue(True)
```


### Deferred testing

Tests can be written using deferrable test cases to test results 
of asynchronous or long lasting sublime commands, which require yielding
control to sublime text runtime and resume test execution at a later point.

It is a kind of cooperative multithreading such as provided by `asyncio`,
but with a home grown [DeferringTextTestRunner][2] acting as event loop.

The idea was inspired by [Plugin UnitTest Harness](https://bitbucket.org/klorenz/sublimepluginunittestharness).

[DeferrableTestCase][1] is used to write the test cases. They are executed by
the [DeferringTextTestRunner][2] and the runner expects not only regular test
functions, but also generators. If the test function is a generator, it does
the following

- if the yielded object is a callable, the runner will evaluate the
  [callable][3] and check its returned value. If the result is not `None`, 
  the runner continues the generator, if not, the runner will wait until the
  condition is met with the default timeout of 4s. The result of the callable
  can be also retrieved from the `yield` statement. The yielded object could 
  also be a dictionary of the form 

  ```py
  {
    # required condition callable
    "condition": callable,
    # system timestamp when to start condition checks (default: `time.time()`)
    "start_time": timestamp,
    # optional the interval to invoke `condition()` (default: 17)
    "period": milliseconds,
    # optional timeout to wait for condition to be met (default: value from unittesting.json or 4000)
    "timeout": milliseconds,
    # optional message to print, if condition is not met within timeout
    "timeout_message": "Condition not fulfilled"
  }
  ```

  to specify various overrides such as poll interval or timeout in ms.

- if the yielded object is an integer, say `x`, then it will [continue][4] the
  generator after `x` ms.

- `yield AWAIT_WORKER` would yield to a task in the worker thread.

- otherwise, a single `yield` would yield to a task in the main thread.

Example:

```py
import sublime
from unittesting import DeferrableTestCase


class TestCondition(DeferrableTestCase):

    def test_condition1(self):
        x = []

        def append():
            x.append(1)

        def condition():
            return len(x) == 1

        sublime.set_timeout(append, 100)

        # wait until `condition()` is true
        yield condition

        self.assertEqual(x[0], 1)

    def test_condition2(self):
        x = []

        def append():
            x.append(1)

        def condition():
            return len(x) == 1

        sublime.set_timeout(append, 100)

        # wait until `condition()` is true
        yield {
          "condition": condition,
          "period": 200,
          "timeout": 5000,
          "timeout_message": "Not enough items added to x"
        }

        self.assertEqual(x[0], 1)
```

see also [tests/test_defer.py](https://github.com/randy3k/UnitTesting-example/blob/master/tests/test_defer.py).


### Asyncio testing

Tests for `asyncio` are written using `IsolatedAsyncioTestCase` class.


```py
import asyncio

from unittesting import IsolatedAsyncioTestCase

async def a_coro():
    return 1 + 1

class MyAsyncTestCase(IsolatedAsyncioTestCase):
    async def test_something(self):
        result = await a_coro()
        await asyncio.sleep(1)
        self.assertEqual(result, 2)
```


## Helper TestCases

UnitTesting provides some helper test case classes, 
which perform common tasks such as overriding preferences, setting up views, etc.

- DeferrableViewTestCase
- OverridePreferencesTestCase
- TempDirectoryTestCase
- ViewTestCase

Usage and some examples are available via docstrings, which are displayed as hover popup by [LSP](https://packagecontrol.io/packages/LSP) and e.g. [LSP-pyright](https://packagecontrol.io/packages/LSP-pyright).

## Credits

Thanks [guillermooo](https://github.com/guillermooo) and [philippotto](https://github.com/philippotto) for their early efforts in AppVeyor and Travis CI macOS support (though these services are not supported now).


[1]: https://github.com/SublimeText/UnitTesting/blob/60e15d42d6ff96156408aec1999d6a16ddcf8e03/unittesting/core/py33/case.py#L22
[2]: https://github.com/SublimeText/UnitTesting/blob/60e15d42d6ff96156408aec1999d6a16ddcf8e03/unittesting/core/py33/runner.py#L21
[3]: https://github.com/SublimeText/UnitTesting/blob/60e15d42d6ff96156408aec1999d6a16ddcf8e03/unittesting/core/py33/runner.py#L65
[4]: https://github.com/SublimeText/UnitTesting/blob/60e15d42d6ff96156408aec1999d6a16ddcf8e03/unittesting/core/py33/runner.py#L72
