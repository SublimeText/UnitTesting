UnitTesting
===================

[![CircleCI](https://circleci.com/gh/SublimeText/UnitTesting/tree/master.svg?style=shield)](https://circleci.com/gh/SublimeText/UnitTesting/tree/master)
[![Build Status](https://travis-ci.org/SublimeText/UnitTesting.svg?branch=master)](https://travis-ci.org/SublimeText/UnitTesting)
[![Build status](https://ci.appveyor.com/api/projects/status/github/SublimeText/UnitTesting?branch=master&svg=true)](https://ci.appveyor.com/project/randy3k/UnitTesting/branch/master)
[![codecov](https://codecov.io/gh/SublimeText/UnitTesting/branch/master/graph/badge.svg)](https://codecov.io/gh/SublimeText/UnitTesting)
<a href="https://packagecontrol.io/packages/UnitTesting"><img src="https://packagecontrol.herokuapp.com/downloads/UnitTesting.svg"></a>

This is a unittest framework for Sublime Text 3. It runs unittest testcases on local machines and CI services such as Travis CI, Circle CI and Appveyor. It also supports testing syntax_test files for the new [sublime-syntax](https://www.sublimetext.com/docs/3/syntax.html) format.


**News**: UnitTesting is now housed by `SublimeText`. You may want to change the urls from
`randy3k/UnitTesting` to `SublimeText/UnitTesting`, e.g.:

- https://raw.githubusercontent.com/SublimeText/UnitTesting/master/sbin/travis.sh


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

### Circle CI

To enable Circle CI Linux and macOS builds, copy the file
[.circleci/config.yml](https://github.com/randy3k/UnitTesting-example/blob/master/.circleci/config.yml) to your repository and change the environmental variable `PACKAGE` to the name of
your package. Login [circleci](https://circleci.com) and add a new project.

Circle CI doesn't offer free macOS plan by default, but you could contact them for access if your package is open sourced:

> We also offer the Seed plan for macOS open-source projects. Contact us at billing@circleci.com for access. If you are building a bigger open-source project and need more resources, let us know how we can help you!

### Travis CI

To enable Travis CI Linux and macOS builds, copy the file:
[.travis.yml](https://github.com/randy3k/UnitTesting-example/blob/master/.travis.yml)
(caution: with a beginning dot) to your repository and
change the environmental variable `PACKAGE` to the name of
your package. Login [travis-ci](https://travis-ci.com/) to enable CI for your package..

### Appveyor CI

To enable Appveyor Windows builds, copy the file `appveyor.yml` to
your repository, change the `PACKAGE` variable in
[appveyor.yml](https://github.com/randy3k/UnitTesting-example/blob/master/appveyor.yml).
Login [appveyor](http://www.appveyor.com) and add your repository
as a new project.


## Coverage reports

We support Codecov, Coveralls and Codacy. Codacov is slightly more favorable as it
supports merging reports from different CIs.


### Codecov

To submit coverage report to [codecov.io](https://codecov.io/):

1. install [codecov](https://pypi.python.org/pypi/codecov)
2. run `codecov` after success


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
travis and appveyor configuration files.


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

To activate deferred testing on travis and appveyor, put the following line in
`unittesting.json`.

```
    "deferred": true,
```

PS: this idea was inspired by [Plugin UnitTest Harness](https://bitbucket.org/klorenz/sublimepluginunittestharness).

### Async testing

By default, the tests are running in the main thread and can block the
graphic inference. Asychronized testing could be used if you need the
interface to respond.

Async tests are usually slower than the sync tests because the interface takes
time to respond but it is useful when there are blocking codes in the tests. An
example would be found in
[here](https://github.com/randy3k/UnitTesting-example/tree/async).

However, it is known that async test does not work very well with coverage.
In general, it is recommended to use deferred testing over async testing since there is
no need to worry about race condition.


To activate async testing on travis and appveyor, put the following line in
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

### Credits
Thanks [guillermooo](https://github.com/guillermooo) and [philippotto](https://github.com/philippotto) for their efforts in AppVeyor and Travis OSX support.
