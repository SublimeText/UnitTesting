UnitTesting
===================

[![Build Status](https://travis-ci.org/randy3k/UnitTesting.svg?branch=master)](https://travis-ci.org/randy3k/UnitTesting) 
[![Build status](https://ci.appveyor.com/api/projects/status/9nnjlnj6tetbxuqd/branch/master?svg=true)](https://ci.appveyor.com/project/randy3k/unittesting/branch/master)
[![Coverage Status](https://coveralls.io/repos/github/randy3k/UnitTesting/badge.svg?branch=master)](https://coveralls.io/github/randy3k/UnitTesting?branch=master)
<a href="https://packagecontrol.io/packages/UnitTesting"><img src="https://packagecontrol.herokuapp.com/downloads/UnitTesting.svg"></a>

This is a unittest framework for Sublime Text 2 and 3. It helps in running Sublime Text plugins' tests on local machines or via CI services such as [travis-ci](https://travis-ci.org) and [appveyor](http://www.appveyor.com). It also supports testing syntax_test files for the new [sublime-syntax](https://www.sublimetext.com/docs/3/syntax.html) format.

If you like it, you could send me some tips via [paypal](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=YAPVT8VB6RR9C&lc=US&item_name=tips&currency_code=USD&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted) or [gratipay](https://gratipay.com/~randy3k/).

### Introduction

There are at least 3 testing frameworks for Sublime Text in town. For example,

1. https://github.com/guillermooo/AAAPT
2. https://bitbucket.org/klorenz/sublimepluginunittestharness
3. https://github.com/twolfson/sublime-plugin-tests

While `AAAPT` and `pluginunittestharness` work natively in Sublime, they are only for Sublime Text 3 and do not work with travis-ci. On the other hand, `sublime-plugin-tests` supports travis-ci. But it requires nosetest and creates a lot of confusions. Given my disappointment with all these frameworks, I decide to write my own framework.

### Getting started sample

It is hard to explain the usage without an example, so I have created [UnitTesting-example](https://github.com/randy3k/UnitTesting-example). The tests in this repo are written to test this plugin and they do not help in regular use case. Go to the getting started sample instead.

### Credits
Thanks [guillermooo](https://github.com/guillermooo) and [philippotto](https://github.com/philippotto) for their efforts in AppVeyor and Travis OSX support. 
