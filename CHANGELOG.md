# 1.5.8

  - Update Sublime Text 4 download link

# 1.5.7

  - tearDownClass of TempDirectoryTestCase is now a generator
  - add OverridePreferencesTestCase

# 1.5.6
   - Use deferred runner in default
   - Improve coverage support in ST 4

# 1.5.5
   - default to ST version 4
   - reject sublime text ip
   - Strip whitespace when reading `.python-version`
   - Expose install_package CI command for installing arbitrary packages (Merge d03b414)
   - Fix dummy loading under python 3.8

# 1.5.2
   - support CI testing for Sublime Text 4

# v1.5.0
   - support Sublime Text 4
   - refactor ci script and support github actions
   - use relative import to fix the reloading issue
   - support x32
   - Hide the test syntaxes and the success/failure color schemes

# v1.4.1

   - The default value of `legacy_runner` is now set to `false`.
   - Added `failfast` option

# v1.4.0

   - Introduce a faster test runner, it could be enable by specifying the
     option `legacy_runner` in unittesting.json. The default value of
     `legacy_runner` is set as `true` for the moment. We are deprecating
     the original test runner and will change the default value of `legacy_runner`
     to `false` at some point in the future.
   - Discarded/lost windows fix on unittesting/mixin.py (#139)
   - Optionally generate html report (#141)
   - Allow starting coverage after reload (#140)
   - Optimize output panel by writing less often

  Contributors:
   - thom
   - evandrocoan
   - Randy Lai
   - herr kaste


# v1.3.5

   - refactor ci.ps1 and install_sublime_text.ps1
   - Add command to test for syntax compatibility.
   - various improvements

  Contributors:
   - Guillermo López-Anglada
   - guillermooo
   - herr kaste
   - Randy Lai
   - ehuss


# v1.3.4

   - fix appveyor issue (#121)
   - keep the execuation in the same thread

  Contributors:
   - Randy Lai


# v1.3.3

   - make sure input string when running `UnitTesting`
   - improve docs

  Contributors:
   - Randy Lai
   - Taylor D. Edmiston


# v1.3.2

   - support symlinked package
   - Removed ST2 code. (#97)
   - Refactoring/cleanup of runner. (#98)
   - Removed recent package. (#100)
   - Only print done messages in CI testing (#102)

  Contributors:
   - Thomas Smith
   - thom
   - Randy Lai
   - Gerard Roche
