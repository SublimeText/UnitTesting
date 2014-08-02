UnitTesting
===================
[![Build Status](https://travis-ci.org/randy3k/UnitTesting.png?branch=master)](https://travis-ci.org/randy3k/UnitTesting)

There are at least 3 testing frameworks for Sublime Text in town. They are

1. https://github.com/guillermooo/AAAPT
2. https://bitbucket.org/klorenz/sublimepluginunittestharness
3. https://github.com/twolfson/sublime-plugin-tests

`AAAPT` and `pluginunittestharness` work natively in Sublime, but they are ST3 only and do not work with travis-ci. On the other hard, `sublime-plugin-tests` supports travis-ci, however tests are not natively ran in Sublime and it creates a lot of confusion. After playing with all these frameworks, I decide to write my own framework.

It is hard to explain the usage without an example, so I have created an getting start example, [UnitTesting-example](https://github.com/randy3k/UnitTesting-example).

Note: The tests in this repo are written to test this testing plugin and they are not helping in regular situations. Go to the getting start example instead.
