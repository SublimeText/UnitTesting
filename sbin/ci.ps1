[CmdletBinding()]
param(
    [Parameter(Mandatory = $false, Position = 0)]
    [string]$command,
    [Parameter(Mandatory = $false)]
    [switch] $coverage
)

# TODO: Bootstrap the bootstrapper. See appveyor.ps1.

. $PSScriptRoot\ci_config.ps1
. $PSScriptRoot\utils.ps1

function installPackageForSublimeTextVersion3IfNotPresent {
    param([string]$Path, [string]$PreferredTag, [string]RepositoryUrl)
    if ($IsSublimeTextVersion3 -and (pathExists -Negate $Path)) {
        cloneRepositoryTag $PreferredTag $RepositoryUrl $Path
    }
}

function Bootstrap {
    [CmdletBinding()]
    param([switch] $with_color_scheme_unit)
    
    ensureCreateDirectory $SublimeTextPackagesDirectory

    # Copy plugin files to Packages/<Package> folder.
    if ($PackageUnderTestName -eq $SymbolCopyAll){
        logVerbose "creating directory for package under test at $PackageUnderTestSublimeTextPackagesDirectory..."
        ensureCreateDirectory $PackageUnderTestSublimeTextPackagesDirectory
        logVerbose "copying current directory contents to $PackageUnderTestSublimeTextPackagesDirectory..."
        # TODO: create junctions for all packages.
        ensureCopyDirectoryContents . $SublimeTextPackagesDirectory
    } else {
        logVerbose "creating directory junction to package under test at $PackageUnderTestSublimeTextPackagesDirectory..."
        ensureCreateDirectoryJunction $PackageUnderTestSublimeTextPackagesDirectory .
    }

    # Clone UnitTesting into Packages/UnitTesting.
    if (pathExists -Negate $UnitTestingSublimeTextPackagesDirectory) {
        $UNITTESTING_TAG = getLatestUnitTestingBuildTag $env:UNITTESTING_TAG $SublimeTextVersion $UnitTestingRepositoryUrl
        logVerbose "download UnitTesting tag: $UNITTESTING_TAG"
        gitCloneTag $UNITTESTING_TAG UnitTestingRepositoryUrl $UnitTestingSublimeTextPackagesDirectory
        gitGetHeadRevisionName $UnitTestingSublimeTextPackagesDirectory | logVerbose
        logVerbose ""
    }

    # Clone coverage plugin into Packages/coverage.
    installPackageForSublimeTextVersion3IfNotPresent $CoverageSublimeTextPackagesDirectory $env:COVERAGE_TAG $ConverageRepositoryUrl

    & "$UnitTestingSublimeTextPackagesDirectory\sbin\install_sublime_text.ps1" -verbose
}

function InstallPackageControl {
    remove-item $CoverageSublimeTextPackagesDirectory -Force -Recurse
    & "$UnitTestingSublimeTextPackagesDirectory\sbin\install_package_control.ps1" -verbose
}

function InstallColorSchemeUnit {
    installPackageForSublimeTextVersion3IfNotPresent $ColorSchemeUnitSublimeTextPackagesDirectory $env:COLOR_SCHEME_UNIT_TAG $ColorSchemeUnitRepositoryUrl
}

function InstallKeypress {
    installPackageForSublimeTextVersion3IfNotPresent $KeyPressSublimeTextPackagesDirectory $env:KEYPRESS_TAG $KeyPressRepositoryUrl
}

function RunTests {
    [CmdletBinding()]
    param(
        [switch] $syntax_test,
        [switch] $color_scheme_test
    )

    if ( $syntax_test.IsPresent ){
        & "$UnitTestingSublimeTextPackagesDirectory\sbin\run_tests.ps1" "$env:PACKAGE" -verbose -syntax_test
    } elseif ( $color_scheme_test.IsPresent ){
        & "$UnitTestingSublimeTextPackagesDirectory\sbin\run_tests.ps1" "$env:PACKAGE" -verbose -color_scheme_test
    } elseif ( $coverage.IsPresent ) {
        & "$UnitTestingSublimeTextPackagesDirectory\sbin\run_tests.ps1" "$env:PACKAGE" -verbose -coverage
    } else {
        & "$UnitTestingSublimeTextPackagesDirectory\sbin\run_tests.ps1" "$env:PACKAGE" -verbose
    }

    stop-process -force -processname sublime_text -ea silentlycontinue
    start-sleep -seconds 2
}

try{
    switch ($command){
        "bootstrap" { Bootstrap }
        "install_package_control" { InstallPackageControl }
        "install_color_scheme_unit" { InstallColorSchemeUnit }
        "install_keypresss" { InstallKeypress }
        "run_tests" { RunTests }
        "run_syntax_tests" { RunTests -syntax_test}
        "run_color_scheme_tests" { RunTests -color_scheme_test}
    }
}catch {
    throw $_
}