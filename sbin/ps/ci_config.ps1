$ErrorActionPreference = 'stop'

. $PSScriptRoot\utils.ps1

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

    makeGlobalConstant SublimeTextVersion (ensureValue $env:SUBLIME_TEXT_VERSION '^2|3$' -message "the environment variable SUBLIME_TEXT_VERSION must be set to '2' or '3'")
    makeGlobalConstant IsSublimeTextVersion3 ($SublimeTextVersion -eq 3)
    makeGlobalConstant IsSublimeTextVersion2 ($SublimeTextVersion -eq 2)
    makeGlobalConstant SublimeTextDirectory (eitherOr $env:SUBLIME_TEXT_DIRECTORY "$env:SystemDrive\st")
    makeGlobalConstant SublimeTextExecutableHelperPath (join-path $SublimeTextDirectory 'subl.exe')
    makeGlobalConstant SublimeTextExecutablePath (join-path $SublimeTextDirectory 'sublime_text.exe')
    makeGlobalConstant SublimeTextPackagesDirectory (eitherOr $env:SUBLIME_TEXT_PACKAGES_DIRECTORY (join-path $SublimeTextDirectory "Data\Packages"))
    # TODO: For compatibility; remove when not used anymore.
    $global:STP = $SublimeTextPackagesDirectory

    makeGlobalConstant PackageUnderTestName (ensureValue (eitherOr $env:UNITTESTING_PACKAGE_UNDER_TEST_NAME $env:PACKAGE) -message "the environment variable UNITTESTING_PACKAGE_UNDER_TEST_NAME (or alternatively, PACKAGE) is not set")
    # TODO: For compatibility; remove when not used anymore.
    makeGlobalConstant PackageName $PackageUnderTestName
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
