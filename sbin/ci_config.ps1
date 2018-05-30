. $PSScriptRoot\utils.ps1

if (!$env:UNITTESTING_BOOTSTRAPPED) {
    function local:makeGlobalConstant {
        param([string]$Name, $Value)
        new-variable -name $Name -value $Value -option constant -scope global
    }

    logVerbose "setting global constants and variables..."

    # TODO: If we used directory junctions here too, we wouldn't need this?
    # This constant means that the entire contents of the source directory must be copied to the target directory.
    makeGlobalConstant SymbolCopyAll '__all__'
    makeGlobalConstant SublimeTextDirectory (eitherOr $env:SUBLIME_TEXT_DIRECTORY "C:\st")
    makeGlobalConstant SublimeTextPackagesDirectory (eitherOr $env:SUBLIME_TEXT_PACKAGES_DIRECTORY "C:\st\Data\Packages")
    makeGlobalConstant SublimeTextExecutablePath (join-path $SublimeTextDirectory 'sublime_text.exe')
    $global:STP = $SublimeTextPackagesDirectory
    makeGlobalConstant PackageUnderTestName (ensureValue $env:PACKAGE -message "the environment variable PACKAGE is not set")
    # TODO: For compatibility; remove when not used anymore.
    makeGlobalConstant PackageName $PackageUnderTestName
    makeGlobalConstant PackageUnderTestSublimeTextPackagesDirectory (join-path $SublimeTextPackagesDirectory $PackageUnderTestName)
    makeGlobalConstant UnitTestingSublimeTextPackagesDirectory (join-path $SublimeTextPackagesDirectory 'UnitTesting')
    makeGlobalConstant CoverageSublimeTextPackagesDirectory (join-path $SublimeTextPackagesDirectory 'coverage')
    makeGlobalConstant ColorSchemeUnitSublimeTextPackagesDirectory (join-path $SublimeTextPackagesDirectory 'ColorSchemeUnit')
    makeGlobalConstant KeyPressSublimeTextPackagesDirectory (join-path $SublimeTextPackagesDirectory 'Keypress')
    makeGlobalConstant SublimeTextVersion (ensureValue $env:SUBLIME_TEXT_VERSION '^2|3$' -message "the environment variable SUBLIME_TEXT_VERSION must be set to '2' or '3'")
    makeGlobalConstant UnitTestingRepositoryUrl "https://github.com/randy3k/UnitTesting"
    makeGlobalConstant CoverageRepositoryUrl "https://github.com/codexns/sublime-coverage"
    makeGlobalConstant ColorSchemeUnitRepositoryUrl "https://github.com/gerardroche/sublime-color-scheme-unit"
    makeGlobalConstant KeyPressRepositoryUrl "https://github.com/randy3k/Keypress"
    makeGlobalConstant IsSublimeText3 ($SublimeTextVersion -eq 3)
    makeGlobalConstant IsSublimeText2 ($SublimeTextVersion -eq 2)

    # TODO: Is this specific to the CI service?
    # Supress some git warnings
    git config --global advice.detachedHead false
}