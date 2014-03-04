UnitTesting
===================
There are at least 3 testing frameworks for Sublime Text in town: 

1. https://github.com/guillermooo/AAAPT
2. https://bitbucket.org/klorenz/sublimepluginunittestharness
3. https://github.com/twolfson/sublime-plugin-tests

They all have their own pros and cons. `AAAPT` and `pluginunittestharness` work natively in Sublime, but they are ST3 only and do not work with travis-ci. On the other hard, `sublime-plugin-tests` is better in this sense and supports travis-ci. I have to admit that it is a very brilliant framework, but it just doesn't sound right to me to run tests outside Sublime when developing. So I decided to write my own testing framework.

It is hard to explain the usage without an example, so I have created an getting start example here: [UnitTesting-example](https://github.com/randy3k/UnitTesting-example).
