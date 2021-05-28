UnitTesting
===================

[![Github Action](https://github.com/SublimeText/UnitTesting/workflows/build/badge.svg)](https://github.com/SublimeText/UnitTesting/actions)
[![codecov](https://codecov.io/gh/SublimeText/UnitTesting/branch/master/graph/badge.svg)](https://codecov.io/gh/SublimeText/UnitTesting)
<a href="https://packagecontrol.io/packages/UnitTesting"><img src="https://packagecontrol.herokuapp.com/downloads/UnitTesting.svg"></a>

This is a unittest framework for Sublime Text. It runs unittest testcases on local machines and CI services such as Travis CI, Circle CI and AppVeyor. It also supports testing syntax_test files for the new [sublime-syntax](https://www.sublimetext.com/docs/3/syntax.html) format.

## Deprecation of supports of CircleCI, Travis and Appveyor.

It is too much work to maintain supports for circleci, travis, appveyor and github actions and the same time.
As most users host their projects on github, we are going to only support github actions and deprecate supports for circleci, travis and appveyor.

There is no plan to remove the corresponding scripts from the repo in a near future, but they are not maintained any more and may be removed if they are broken.


## Sublime Text 4

Sublime Text 4 is now supported. However test coverage on Python 3.8 packages is still not working now.


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

These environmental variables are used

- `PACKAGE`: the package name, it is needed if the repo name is different from the package name.
- `SUBLIME_TEXT_VERSION`: 3 or 4
- `SUBLIME_TEXT_ARCH`: `x32` (Sublime Text 3 only) or `x64`
- `UNITTESTING_TAG`: a specific version of UnitTesting to use

To enable GitHub Actions, copy the file [build.yml](https://github.com/randy3k/UnitTesting-example/blob/master/.github/workflows/build.yml) to
your repository.


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
