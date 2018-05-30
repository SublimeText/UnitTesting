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
        git clone --quiet --depth 1 --branch=$UNITTESTING_TAG $UnitTestingRepositoryUrl "$UnitTestingSublimeTextPackagesDirectory" 2>$null
        git -C "$UnitTestingSublimeTextPackagesDirectory" rev-parse HEAD | logVerbose
        logVerbose ""
    }

    # Clone coverage plugin into Packages/coverage.
    if ($IsSublimeTextVersion3 -and (pathExists -Negate $CoverageSublimeTextPackagesDirectory)){
        $COVERAGE_TAG = getLatestCoverageTag $env:COVERAGE_TAG $ConverageRepositoryUrl
        logVerbose "download sublime-coverage tag: $COVERAGE_TAG"
        git clone --quiet --depth 1 --branch=$COVERAGE_TAG $ConverageRepositoryUrl $CoverageSublimeTextPackagesDirectory 2>$null
        git -C $CoverageSublimeTextPackagesDirectory rev-parse HEAD | write-verbose
        logVerbose ""
    }

    & "$UnitTestingSublimeTextPackagesDirectory\sbin\install_sublime_text.ps1" -verbose
}

function InstallPackageControl {
    remove-item $CoverageSublimeTextPackagesDirectory -Force -Recurse
    & "$UnitTestingSublimeTextPackagesDirectory\sbin\install_package_control.ps1" -verbose
}

function InstallColorSchemeUnit {
    if (($SublimeTextVersion -eq 3) -and (pathExists -Negate $ColorSchemeUnitSublimeTextPackagesDirectory)) {
        $COLOR_SCHEME_UNIT_TAG = getLatestColorSchemeUnitTag $env:COLOR_SCHEME_UNIT_TAG $ColorSchemeUnitRepositoryUrl
        logVerbose "download ColorSchemeUnit tag: $COLOR_SCHEME_UNIT_TAG"
        git clone --quiet --depth 1 --branch=$COLOR_SCHEME_UNIT_TAG $ColorSchemeUnitRepositoryUrl $ColorSchemeUnitSublimeTextPackagesDirectory 2>$null
        git -C $ColorSchemeUnitSublimeTextPackagesDirectory rev-parse HEAD | logVerbose
        logVerbose ""
    }
}

function InstallKeypress {
    if (($SublimeTextVersion -eq 3) -and (pathExists -Negate $KeyPressSublimeTextPackagesDirectory)) {
        $KEYPRESS_TAG = getLatestColorSchemeUnitTag $env:KEYPRESS_TAG $KeyPressRepositoryUrl
        logVerbose "download KeyPress tag: $KEYPRESS_TAG"
        git clone --quiet --depth 1 --branch=$KEYPRESS_TAG $KeyPressRepositoryUrl $KeyPressSublimeTextPackagesDirectory 2>$null
        git -C $KeyPressSublimeTextPackagesDirectory rev-parse HEAD | logVerbose
        logVerbose ""
    }
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