UnitTesting
===================
Linux & OSX | Windows
------------|------------
 [![Build Status](http://img.shields.io/travis/randy3k/UnitTesting/master.svg)](https://travis-ci.org/randy3k/UnitTesting) | [![Build status](http://img.shields.io/appveyor/ci/randy3k/UnitTesting/branch/master.svg)](https://ci.appveyor.com/project/randy3k/UnitTesting/branch/master)

This is a testing framework for Sublime Text 2 and 3. It helps in testing Sublime Text plugins and works on local machines or via CI services such as [travis-ci](https://travis-ci.org) and [appveyor](http://www.appveyor.com).

If you like it, you could send me some tips via [![](http://img.shields.io/gittip/randy3k.svg)](https://www.gittip.com/randy3k).

### Introduction

There are at least 3 testing frameworks for Sublime Text in town. They are

1. https://github.com/guillermooo/AAAPT
2. https://bitbucket.org/klorenz/sublimepluginunittestharness
3. https://github.com/twolfson/sublime-plugin-tests

`AAAPT` and `pluginunittestharness` work natively in Sublime, but they are ST3 only and do not work with travis-ci. On the other hand, `sublime-plugin-tests` is a great framework, it supports travis-ci. However tests are not natively ran in Sublime Text and it creates a lot of confusion. Given my disappointment with all these frameworks, I decide to write my own framework.

### Getting start example

It is hard to explain the usage without an example, so I have created [UnitTesting-example](https://github.com/randy3k/UnitTesting-example).

Note: The tests in this repo are written to test this plugin and they does not help in regular situations. Go to the getting start example instead.

### Credits
Thanks [guillermooo](https://github.com/guillermooo) and [philippotto](https://github.com/philippotto) for their efforts in AppVeyor and Travis OSX support. 
