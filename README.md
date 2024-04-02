UnitTesting
===========

[![test](https://github.com/SublimeText/UnitTesting/actions/workflows/test.yaml/badge.svg)](https://github.com/SublimeText/UnitTesting/actions/workflows/test.yaml)
[![codecov](https://codecov.io/gh/SublimeText/UnitTesting/branch/master/graph/badge.svg)](https://codecov.io/gh/SublimeText/UnitTesting)

This is a unittest framework for Sublime Text.
It runs unittest testcases on local machines and via Github Actions.
It also supports testing syntax_test files for the new [sublime-syntax](https://www.sublimetext.com/docs/3/syntax.html) 
format and sublime-color-scheme files.

## Sublime Text 4

Sublime Text 4 is now supported and testing works for Python 3.8 packages.

## Preparation

1. Install [UnitTesting](https://github.com/SublimeText/UnitTesting) via Package Control.
2. Your package!
3. TestCases should be placed in `test*.py` under the directory `tests` 
   (configurable, see below). The testcases are then loaded by [TestLoader.discover](https://docs.python.org/3.3/library/unittest.html#unittest.TestLoader.discover).

[Here](https://github.com/randy3k/UnitTesting-example) are some small examples

## Running Tests Locally

UnitTesting can be triggered via the command palette command `UnitTesting`.
Enter the package name in the input panel and hit enter, a console should pop
up and the tests should be running. To run only tests in particular files,
enter `<Package name>:<filename>`. `<filename>` should be a unix shell
wildcard to match the file names, `<Package name>:test*.py` is used in
default.


You could run the command `UnitTesting: Test Current Package` to run the
current package. The current package will be first reloaded by UnitTesting
and then the tests will be executed.


It is also possible to generate test
coverage report via [coverage](https://pypi.python.org/pypi/coverage) by using the command
`UnitTesting: Test Current Package with Coverage`.
The file [.coveragerc](.coveragerc) is used to control the coverage configurations. If
it is missing, UnitTesting will ignore the `tests` directory.


## GitHub Actions

Basic: put the following in your workflow.
```yaml
name: test

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
          sublime-text-version: ${{ matrix.st-version }}
      - uses: SublimeText/UnitTesting/actions/run-tests@v1
        with:
          coverage: true
      - uses: codecov/codecov-action@v4
```

Remarks: actions are released in the branch [`v1`](https://github.com/SublimeText/UnitTesting/tree/v1). Minor changes will be pushed to the same branch unless there
are breaking changes.

## Testing syntax_test files

```yaml
name: test-syntax

on: [push, pull_request]

jobs:
  run-syntax-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: SublimeText/UnitTesting/actions/setup@v1
      - uses: SublimeText/UnitTesting/actions/run-syntax-tests@v1
```
Check [this](https://github.com/randy3k/UnitTesting-example) for an example.


## Deferred testing

Tests can be written using the Deferrable testcase, such that you are
able to run sublime commands from your test cases and yield control to sublime
text runtime and continue the execution later. Would be useful to test
asynchronous codes. The idea was inspired by [Plugin UnitTest Harness](https://bitbucket.org/klorenz/sublimepluginunittestharness).


[DeferrableTestCase][1] is used to write the test cases. They are executed by
the [DeferringTextTestRunner][2] and the runner expects not only regular test
functions, but also generators. If the test function is a generator, it does
the following

- if the yielded object is a callable, the runner will evaluate the
  [callable][3] and check its returned value. If the result is not `None`, 
  the runner continues the generator, if not, the runner will wait until the
  condition is met with the default timeout of 4s. The result of the callable
  can be also retrieved from the `yield` statement. The yielded object could 
  be also a dictionary of the form `{"condition": callable, timeout: timeout}` 
  to specify timeout in ms.

- if the yielded object is an integer, say `x`, then it will [continue][4] the
  generator after `x` ms.

- `yield AWAIT_WORKER` would yield to a task in the worker thread.

- otherwise, a single `yield` would yield to a task in the main thread.



An example would be found in [here](https://github.com/randy3k/UnitTesting-example/blob/master/tests/test_defer.py).


## Options

UnitTesting could be configured by providing the following settings in `unittesting.json`

| name                        | description                                                                       | default value |
| --------------------------- | --------------------------------------------------------------------------------- | ------------- |
| tests_dir                   | the name of the directory containing the tests                                    | "tests"       |
| pattern                     | the pattern to discover tests                                                     | "test*.py"    |
| deferred                    | whether to use deferred test runner                                               | true          |
| condition_timeout           | default timeout in ms for callables invoked via `yield`                           | 4000          |
| failfast                    | stop early if a test fails                                                        | false         |
| output                      | name of the test output instead of showing <br> in the panel                      | null          |
| verbosity                   | verbosity level                                                                   | 2             |
| capture_console             | capture stdout and stderr in the test output                                      | false         |
| reload_package_on_testing   | reloading package will increase coverage rate                                     | true          |
| show_reload_progress        | print a detailed list of reloaded modules to console                              | false         |
| coverage                    | track test case coverage                                                          | false         |
| coverage_on_worker_thread   | (experimental)                                                                    | false         |
| start_coverage_after_reload | self explained, irrelevent if `coverage` or `reload_package_on_testing` are false | false         |
| generate_html_report        | generate HTML report for coverage                                                 | false         |
| generate_xml_report         | generate XML report for coverage                                                  | false         |

## Build System

The `unit_testing` command can be used as build system `"target"`. 
All available options can be put into a build system and will be used to override entries from unittesting.json.

### Add `Test Current Package` build

It is recommended to add the following in your `.sublime-project` file so that <kbd>c</kbd>+<kbd>b</kbd> would invoke the testing action.

```json
"build_systems":
[
  {
    "name": "Test Current Package",
    "target": "unit_testing",
    "package": "$package_name",
  }
]
```

### Add `Test Current File` build

It is recommended to add the following in your `.sublime-project` file so that <kbd>c</kbd>+<kbd>b</kbd> would invoke the testing action.

```json
"build_systems":
[
  {
    "name": "Test Current File",
    "target": "unit_testing",
    "package": "$package_name",
    "pattern": "$file_name",
  }
]
```

## Credits

Thanks [guillermooo](https://github.com/guillermooo) and [philippotto](https://github.com/philippotto) for their early efforts in AppVeyor and Travis CI macOS support (though these services are not supported now).


[1]: https://github.com/SublimeText/UnitTesting/blob/60e15d42d6ff96156408aec1999d6a16ddcf8e03/unittesting/core/py33/case.py#L22
[2]: https://github.com/SublimeText/UnitTesting/blob/60e15d42d6ff96156408aec1999d6a16ddcf8e03/unittesting/core/py33/runner.py#L21
[3]: https://github.com/SublimeText/UnitTesting/blob/60e15d42d6ff96156408aec1999d6a16ddcf8e03/unittesting/core/py33/runner.py#L65
[4]: https://github.com/SublimeText/UnitTesting/blob/60e15d42d6ff96156408aec1999d6a16ddcf8e03/unittesting/core/py33/runner.py#L72
