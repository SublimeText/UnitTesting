UnitTesting
===================

[![Github Action](https://github.com/SublimeText/UnitTesting/workflows/build/badge.svg)](https://github.com/SublimeText/UnitTesting/actions)
[![codecov](https://codecov.io/gh/SublimeText/UnitTesting/branch/master/graph/badge.svg)](https://codecov.io/gh/SublimeText/UnitTesting)
<a href="https://packagecontrol.io/packages/UnitTesting"><img src="https://packagecontrol.herokuapp.com/downloads/UnitTesting.svg"></a>

This is a unittest framework for Sublime Text. It runs unittest testcases on local machines and via Github Actions. It also supports testing syntax_test files for the new [sublime-syntax](https://www.sublimetext.com/docs/3/syntax.html) format and sublime-color-scheme files.


## Sublime Text 4

Sublime Text 4 is now supported. Test coverage on Python 3.8 packages is still not working until Package Control supports Python 3.8.

## Preparation

1. Before testing anything, you have to install [UnitTesting](https://github.com/SublimeText/UnitTesting) via Package Control.
2. Your package!
3. TestCases should be placed in `test*.py` under the directory `tests` (configurable, see below). The testcases are then loaded by [TestLoader.discover](https://docs.python.org/3.3/library/unittest.html#unittest.TestLoader.discover).

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
      - uses: actions/checkout@v2
      - uses: SublimeText/UnitTesting/actions/setup@v1
        with:
          sublime-text-version: ${{ matrix.st-version }}
      - uses: SublimeText/UnitTesting/actions/run-tests@v1
        with:
          coverage: true
          codecov-upload: true
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
      - uses: actions/checkout@v2
      - uses: SublimeText/UnitTesting/actions/setup@v1
      - uses: SublimeText/UnitTesting/actions/run-syntax-tests@v1
```
Check [this](https://github.com/randy3k/UnitTesting-example) for an example.

## Options

### Use a different test directory

The default test directory is "tests". To change the test directory, add a
file `unittesting.json` to your repo with the corresponding directory name, eg
`unittest`:

```
    "tests_dir" : "unittest"
```

### Redirect test result to a file

The test result could be redirected to a file by specifying the `output`
variable in `unittesting.json`.

```
    "output" : "foo.txt"
```

### Deferred testing

Tests can be written using the Deferrable testcase, such that you are
able to run sublime commands from your test cases and yield control to sublime
text runtime and continue the execution later. Would be useful to test
asynchronous codes. The idea was inspired by [Plugin UnitTest Harness](https://bitbucket.org/klorenz/sublimepluginunittestharness).


[DeferrableTestCase][1] is used to write the test cases. They are executed by
the [DeferringTextTestRunner][2] and the runner expects not only regular test
functions, but also generators. If the test function is a generator, it does
the following

- if the yielded object is a callable, the runner will evaluate the
  [callable][3] and check its returned value. If the result is `True`, the
  runner continues the generator, if not, the runner will wait until the
  condition is met.

- If the yielded object is an integer, say `x`, then it will [continue][4] the
  generator after `x` ms.

- Otherwise, the `yield` statement would yeild to any queued jobs.

An example would be found in [here](https://github.com/randy3k/UnitTesting-example/blob/master/tests/test_defer.py).

## Others

### Add `Test Current Package` build

It is recommended to add the following in your `.sublime-project` file so that <kbd>c</kbd>+<kbd>b</kbd> would invoke the testing action.

```
"build_systems":
[
  {
    "name": "Test Current Package",
    "target": "unit_testing_current_package",
  }
]
```

### Credits
Thanks [guillermooo](https://github.com/guillermooo) and [philippotto](https://github.com/philippotto) for their efforts in AppVeyor and Travis CI macOS support.


[1]: https://github.com/randy3k/UnitTesting/blob/dc810ee334bb031710b859478faaf50293880995/unittesting/core/st3/runner.py#L49
[2]: https://github.com/randy3k/UnitTesting/blob/dc810ee334bb031710b859478faaf50293880995/unittesting/core/st3/runner.py#L7
[3]: https://github.com/randy3k/UnitTesting/blob/dc810ee334bb031710b859478faaf50293880995/unittesting/core/st3/runner.py#L49
[4]: https://github.com/randy3k/UnitTesting/blob/dc810ee334bb031710b859478faaf50293880995/unittesting/core/st3/runner.py#L57
