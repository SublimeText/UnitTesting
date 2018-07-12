<#
.SYNOPSIS
Sets up a number of global constants that can be referred from other scripts.

.DESCRIPTION
Sets up a number of global constants that can be referred from other scripts. The
user must supply some of the values through environmental variables.
#>
$ErrorActionPreference = 'stop'

. $PSScriptRoot\utils.ps1

# Environmental variables that the user must/can set to influence values set here.
#
# SUBLIME_TEXT_VERSION (required)
#   Sets the Sublime Text version to be used for testing.
#
# SUBLIME_TEXT_DIRECTORY
#   Sets the directory where the Sublime Text binaries are found.
#
# SUBLIME_TEXT_PACKAGES_DIRECTORY
#   Sets the Sublime Text Packages directory.
#
# UNITTESTING_PACKAGE_UNDER_TEST_NAME (required)
#   Sets the name of the package being tested.

# We must set constants only once.
if (!$env:UNITTESTING_BOOTSTRAPPED) {
    function local:makeGlobalConstant {
        param([string]$Name, $Value)
        new-variable -name $Name -value $Value -option constant -scope global
    }

    logVerbose "setting global constants and variables..."

    # TODO: If we used directory junctions here too, we wouldn't need this?
    # This constant means that the entire contents of the source directory must be copied to the target directory.
    makeGlobalConstant SymbolCopyAll '__all__'

    # The major version of Sublime Text.
    makeGlobalConstant SublimeTextVersion (ensureValue $env:SUBLIME_TEXT_VERSION '^2|3$' -message "the environment variable SUBLIME_TEXT_VERSION must be set to '2' or '3'")
    # True if SublimeTextVersion is 3.
    makeGlobalConstant IsSublimeTextVersion3 ($SublimeTextVersion -eq 3)
    # True if SublimeTextVersion is 2.
    makeGlobalConstant IsSublimeTextVersion2 ($SublimeTextVersion -eq 2)
    # The path to the Sublime Text binaries directory.
    makeGlobalConstant SublimeTextDirectory (eitherOr $env:SUBLIME_TEXT_DIRECTORY "$env:SystemDrive\st")
    # The path to the Sublime Text executable helper.
    makeGlobalConstant SublimeTextExecutableHelperPath (join-path $SublimeTextDirectory 'subl.exe')
    # The path to the Sublime Text executable.
    makeGlobalConstant SublimeTextExecutablePath (join-path $SublimeTextDirectory 'sublime_text.exe')
    # The path to the Sublime Text Packages directory.
    makeGlobalConstant SublimeTextPackagesDirectory (eitherOr $env:SUBLIME_TEXT_PACKAGES_DIRECTORY (join-path $SublimeTextDirectory "Data\Packages"))
    # TODO: For compatibility; remove when not used anymore.
    $global:STP = $SublimeTextPackagesDirectory

    # The name of the package being tested.
    makeGlobalConstant PackageUnderTestName (ensureValue (eitherOr $env:UNITTESTING_PACKAGE_UNDER_TEST_NAME $env:PACKAGE) -message "the environment variable UNITTESTING_PACKAGE_UNDER_TEST_NAME (or alternatively, PACKAGE) is not set")
    # TODO: For compatibility; remove when not used anymore.
    makeGlobalConstant PackageName $PackageUnderTestName
    # The path to the Sublime Text Packages directory of the package being tested.
    makeGlobalConstant PackageUnderTestSublimeTextPackagesDirectory (join-path $SublimeTextPackagesDirectory $PackageUnderTestName)

    makeGlobalConstant ColorSchemeUnitRepositoryUrl "https://github.com/gerardroche/sublime-color-scheme-unit"
    makeGlobalConstant ColorSchemeUnitSublimeTextPackagesDirectory (join-path $SublimeTextPackagesDirectory 'ColorSchemeUnit')
    makeGlobalConstant CoverageRepositoryUrl "https://github.com/codexns/sublime-coverage"
    makeGlobalConstant CoverageSublimeTextPackagesDirectory (join-path $SublimeTextPackagesDirectory 'coverage')
    makeGlobalConstant KeyPressRepositoryUrl "https://github.com/randy3k/Keypress"
    makeGlobalConstant KeyPressSublimeTextPackagesDirectory (join-path $SublimeTextPackagesDirectory 'Keypress')
    makeGlobalConstant UnitTestingRepositoryUrl "https://github.com/SublimeText/UnitTesting"
    makeGlobalConstant UnitTestingSublimeTextPackagesDirectory (join-path $SublimeTextPackagesDirectory 'UnitTesting')

    # TODO: Is this specific to the CI service?
    # Supress some git warnings
    git config --global advice.detachedHead false
}
