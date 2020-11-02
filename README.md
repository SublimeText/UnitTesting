UnitTesting
===================

[![Github Action](https://github.com/SublimeText/UnitTesting/workflows/build/badge.svg)](https://github.com/SublimeText/UnitTesting/actions)
[![CircleCI](https://circleci.com/gh/SublimeText/UnitTesting/tree/master.svg?style=shield)](https://circleci.com/gh/SublimeText/UnitTesting/tree/master)
[![Build Status](https://travis-ci.org/SublimeText/UnitTesting.svg?branch=master)](https://travis-ci.org/SublimeText/UnitTesting)
[![Build status](https://ci.appveyor.com/api/projects/status/github/SublimeText/UnitTesting?branch=master&svg=true)](https://ci.appveyor.com/project/randy3k/UnitTesting/branch/master)
[![codecov](https://codecov.io/gh/SublimeText/UnitTesting/branch/master/graph/badge.svg)](https://codecov.io/gh/SublimeText/UnitTesting)
<a href="https://packagecontrol.io/packages/UnitTesting"><img src="https://packagecontrol.herokuapp.com/downloads/UnitTesting.svg"></a>

This is a unittest framework for Sublime Text. It runs unittest testcases on local machines and CI services such as Travis CI, Circle CI and AppVeyor. It also supports testing syntax_test files for the new [sublime-syntax](https://www.sublimetext.com/docs/3/syntax.html) format.

## Sublime Text 4

Sublime Text 4 is now supported (with some caveats)
- Running `coverage` on Python 3.8 packages is not working now.
- Only local testing is supported now (CI services are not working).

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



## Continuous Integration

These environmental variables are used in the CIs.

- `PACKAGE`: the package name, it is needed if the repo name is different from the package name.
- `SUBLIME_TEXT_VERSION`: 2 or 3
- `SUBLIME_TEXT_ARCH`: `x32` or `x64`
- `UNITTESTING_TAG`: a specific version of UnitTesting to use

Following CI's are supported.

|                 | Linux | macOS | Windows |
|-----------------|-------|-------|---------|
| GitHub Actions  | ✅    | ✅    |   ✅   |
| CircleCI        | ✅    | ✅    |   ✅   |
| Travis CI       | ✅    | ✅    |        |
| AppVeyor        |       |       |   ✅   |


### GitHub Actions

To enable GitHub Actions, copy the file [build.yml](https://github.com/randy3k/UnitTesting-example/blob/master/.github/workflows/build.yml) to
your repository.


### Circle CI

To enable Circle CI builds, copy the file
[.circleci/config.yml](https://github.com/randy3k/UnitTesting-example/blob/master/.circleci/config.yml) to your repository. Log in to [Circle CI](https://circleci.com) and add a new project.

Circle CI doesn't offer free macOS plan at the moment, but you could contact them for access if your package is open sourced:

> We also offer the Seed plan for macOS open-source projects. Contact us at billing@circleci.com for access. If you are building a bigger open-source project and need more resources, let us know how we can help you!

### Travis CI

To enable Travis CI Linux and macOS builds, copy the file:
[.travis.yml](https://github.com/randy3k/UnitTesting-example/blob/master/.travis.yml)
(caution: with a beginning dot) to your repository. Log in to [Travis CI](https://travis-ci.com/) to enable CI for your package..

### AppVeyor CI

To enable AppVeyor Windows builds, copy the file [appveyor.yml](https://github.com/randy3k/UnitTesting-example/blob/master/appveyor.yml) to
your repository. Log in to [AppVeyor](http://www.appveyor.com) and add your repository
as a new project.


## Coverage reports

We support Codecov, Coveralls and Codacy. Codecov is recommended as it
supports merging reports from different CIs.


### Codecov

To submit coverage report to [codecov.io](https://codecov.io/):

1. install [codecov](https://pypi.python.org/pypi/codecov)
2. run `codecov` after success

For GitHub Actions, copy the `CODECOV_TOKEN` from codecov.io to GitHub's Secret tab.

### Coveralls

To submit coverage report to [coveralls.io](https://coveralls.io/):

1. install [python-coveralls](https://pypi.python.org/pypi/python-coveralls/)
2. run `coveralls` after success

### Codacy

To submit coverage report to [codacy.com](https://www.codacy.com):

1. install both coverage and codacy-coverage

    ```
    pip install coverage codacy-coverage
    ```

2. generate the xml report: `coverage xml -o coverage.xml`
3. run `python-codacy-coverage`


## Installing Package Control and Dependencies

If your package uses Package Control dependencies, you may want to install
Package Control by uncommenting the line of `install_package_control` in
Travis CI and AppVeyor configuration files.


## Testing syntax_test files

Check [this](https://github.com/randy3k/UnitTesting-example/tree/syntax) for an example.


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
asynchronous codes.

An example would be found in [here](https://github.com/randy3k/UnitTesting-example/tree/deferred).

To activate deferred testing, put the following line in
`unittesting.json`.

```
    "deferred": true,
```

PS: this idea was inspired by [Plugin UnitTest Harness](https://bitbucket.org/klorenz/sublimepluginunittestharness).


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


### Async testing

By default, the tests are running in the main thread and can block the
graphic inference. Asychronized testing could be used if you need the
interface to respond.

Async tests are usually slower than the sync tests because the interface takes
time to respond but it is useful when there are blocking codes in the tests. An
example would be found in
[here](https://github.com/randy3k/UnitTesting-example/tree/async).

However, it is known that async test does not work very well with coverage.
In general, it is **recommended** to use deferred testing over async testing since there is
no need to worry about race condition.


To activate async testing on Travis CI and AppVeyor, put the following line in
`unittesting.json`.

```
    "async": true,
```

Note: if `async` is true, `deferred` is forced to be `false` (relaxation of this is in progress)

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

### Docker container

Check https://github.com/SublimeText/UnitTesting/tree/master/docker


### Credits
Thanks [guillermooo](https://github.com/guillermooo) and [philippotto](https://github.com/philippotto) for their efforts in AppVeyor and Travis CI macOS support.


[1]: https://github.com/randy3k/UnitTesting/blob/dc810ee334bb031710b859478faaf50293880995/unittesting/core/st3/runner.py#L49
[2]: https://github.com/randy3k/UnitTesting/blob/dc810ee334bb031710b859478faaf50293880995/unittesting/core/st3/runner.py#L7
[3]: https://github.com/randy3k/UnitTesting/blob/dc810ee334bb031710b859478faaf50293880995/unittesting/core/st3/runner.py#L49
[4]: https://github.com/randy3k/UnitTesting/blob/dc810ee334bb031710b859478faaf50293880995/unittesting/core/st3/runner.py#L57
