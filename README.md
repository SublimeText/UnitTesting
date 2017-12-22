UnitTesting
===================

[![Build Status](https://travis-ci.org/SublimeText/UnitTesting.svg?branch=master)](https://travis-ci.org/SublimeText/UnitTesting) 
[![Build status](https://ci.appveyor.com/api/projects/status/psbbacfodps9r124/branch/master?svg=true)](https://ci.appveyor.com/project/randy3k/unittesting/branch/master)
[![codecov](https://codecov.io/gh/SublimeText/UnitTesting/branch/master/graph/badge.svg)](https://codecov.io/gh/SublimeText/UnitTesting)
<a href="https://packagecontrol.io/packages/UnitTesting"><img src="https://packagecontrol.herokuapp.com/downloads/UnitTesting.svg"></a>


This is a unittest framework for Sublime Text 3. It runs unittest testcases on local machines and CI services such as [travis-ci](https://travis-ci.org) and [appveyor](http://www.appveyor.com). It also supports testing syntax_test files for the new [sublime-syntax](https://www.sublimetext.com/docs/3/syntax.html) format.


## Sublime Text 2 support is deprecated

UnitTesting for Sublime Text 2 will be no longer supported. Version 0.10.6 is the last version supports Sublime Text 2 and it is available via Package Control on Sublime Text 2.


## Preparation

1. Before testing anything, you have to install [UnitTesting](https://github.com/SublimeText/UnitTesting) via Package Control.
2. Your package!
3. TestCases should be placed in `test*.py` under the directory `tests` (configurable, see below). The testcases are then loaded by [TestLoader.discover](https://docs.python.org/3.3/library/unittest.html#unittest.TestLoader.discover).
4. Some examples are available at https://github.com/randy3k/UnitTesting-example


## Running Tests

UnitTesting can be triggered via the command palette command `UnitTesting`.
Enter the package name in the input panel and hit enter, a console should pop
up and the tests should be running. To run only tests in particular files,
enter `<Package name>:<filename>`. `<filename>` should be a unix shell
wildcard to match the file names, `<Package name>:test*.py` is used in
default.


You could run the command `UnitTesting: Test Current Package` to run the
current package. The current package will be first reloaded by UnitTesting
and then the tests will be executed.


### Test Coverage

It is also possible to generate test
coverage report via [coverage](https://pypi.python.org/pypi/coverage) by using the command
`UnitTesting: Test Current Package with Coverage`.
The file [.coveragerc](.coveragerc) is used to control the coverage configurations. If
it is missing, UnitTesting will ignore the `tests` directory.

## Travis and Appveyor

If the tests can be run locally, let's put them to travis-ci and let travis-ci
takes care of them. First, you have to copy a important file:
[.travis.yml](https://github.com/randy3k/UnitTesting-example/blob/master/.travis.yml) 
(caution: with a beginning dot) to your repo. Then
change the env variable `PACKAGE` to the name of
your package. Don't forget to login [travis-ci](https://travis-ci.org) and
enable travis-ci for your repo. Finally, push to github and wait..

To enable Appveyor for windows platform tests, copy the file `appveyor.yml` to
your repo, change the `PACKAGE` variable in 
[appveyor.yml](https://github.com/randy3k/UnitTesting-example/blob/master/appveyor.yml). The
last but not least, login [appveyor](http://www.appveyor.com) to add your repo
as a project.

### Coverage reports

We support [codecov.io](https://codecov.io/), [coveralls.io](https://coveralls.io/) and
[codacy.com](https://www.codacy.com). codecov.io is sightly preferable as it
supports merging reports from travis and appveyor.


### codecov support

To submit coverage report to [codecov.io](https://codecov.io/):

1. install [codecov](https://pypi.python.org/pypi/codecov)
2. run `codecov` after success


### coveralls.io support

To submit coverage report to [coveralls.io](https://coveralls.io/):

1. install [python-coveralls](https://pypi.python.org/pypi/python-coveralls/)
2. run `coveralls` after success

### codacy support

To submit coverage report to [codacy.com](https://www.codacy.com):

1. install both coverage and codacy-coverage
    
    ```
    pip install coverage codacy-coverage
    ```

2. generate the xml report: `coverage xml -o coverage.xml`
3. run `python-codacy-coverage`


## Installing Package Control and Dependencies

If your package uses Package Control dependencies, you may want to install
Package Control by umcommenting the line of `install_package_control` in
travis and appveyor configuration files.


## Testing syntax_test files

Check [this](https://github.com/randy3k/UnitTesting-example/tree/syntax) for an example.



## Options

### Use a different test directory

The default test directory is "tests". To change the test directory, add a
file `unittesting.json` to your repo with the corresponding directory name, eg
`unittest`:

```
{
    "tests_dir" : "unittest"
}
```

### Redirect test result to a file

The test result could be redirected to a file by specifying the `output`
variable in `unittesting.json`.

```
{
    "output" : "foo.txt"
}
```

### Deferred testing

Tests can be written using the Deferrable testcase, such that you are
able to run sublime commands from your test cases and yield control to sublime
text runtime and continue the execution later. Would be useful to test
asynchronous codes.

A example would be found in [here](https://github.com/randy3k/UnitTesting-example/tree/deferred).

To activate deferred testing on travis and appveyor. Add the file
`unittesting.json` to your repo with the following:

```
{
    "deferred": true,
}
```

PS: this idea was inspired by [Plugin UnitTest Harness](https://bitbucket.org/klorenz/sublimepluginunittestharness).

### Async testing

In default, the tests are running in the main thread and can block the
graphic inference. Asychronized testing could be used if you need the
interface to respond. 

Async tests are usually slower than the sync tests because the interface takes
time to respond but it is useful when there are blocking codes in the tests. A
example would be found in 
[here](https://github.com/randy3k/UnitTesting-example/tree/async). 

However, it is known that async test does not work very well with coverage.
In general, it is recommended to use deferred testing over async testing since there is
no need to worry about race condition.


To activate async testing on travis and appveyor. Add the file
`unittesting.json` to your repo with the following:

```
{
    "async": true,
}
```

Note: if `async` is true, `deferred` is forced to be `false` (relaxation of this is in progress)


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
