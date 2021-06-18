<#
.SYNOPSIS
The ci.ps1 script controls the execution of Unittesting-related commands in a CI
environment.

.DESCRIPTION
The ci.ps1 script controls the execution of commands related to the Unittesting
package used to write tests for Sublime Text packages and plugins. The ci.ps1
script is meant to be used in a CI server (Windows-only at present). The ci.ps1
script is the entry point for users.

.PARAMETER Command
The name of the command to be executed.

.PARAMETER Coverage
If true, coverage statistics will be calculated.

.NOTES
The ci.ps1 script supersedes the appveyor.ps1 script. If you can choose, use
ci.ps1 from now on. The ci.ps1 script is a drop-in replacement for appveyor.ps1.

On first execution, ci.ps1 bootstraps itself by downloading required files and
copying them to a temp directory from which they are then used. Therefore, this
is the only script you need to download from a CI configuration if you want to
use it.

#>
[CmdletBinding()]
param(
    [Parameter(Position=0, Mandatory=$true)]
    [ValidateSet('bootstrap', 'install_package_control', 'install_color_scheme_unit',
        'install_keypress', 'run_tests', 'run_syntax_tests', 'run_syntax_compatibility', 'run_color_scheme_tests')]
    [string]$command,
    [switch]$coverage
)

# Stop execution on any error. PS default is to continue on non-terminating errors.
$ErrorActionPreference = 'stop'

if (!$UnitTestingPowerShellScriptsDirectory) {
    $global:UnitTestingPowerShellScriptsDirectory = $env:TEMP
}

function downloadScriptIfNotExist {
    param([string]$FileName)
    if (-Not (Test-Path (join-path $UnitTestingPowerShellScriptsDirectory $FileName))) {
        invoke-webrequest "https://raw.githubusercontent.com/SublimeText/UnitTesting/master/sbin/ps/$FileName" -outfile "$UnitTestingPowerShellScriptsDirectory\$FileName"
    }
}

# Do one-time environment initialization if needed.
if (!$env:UNITTESTING_BOOTSTRAPPED) {
    write-output "[UnitTesting] bootstrapping environment..."
    downloadScriptIfNotExist "ci_config.ps1"
    downloadScriptIfNotExist "utils.ps1"
    $env:UNITTESTING_BOOTSTRAPPED = 1
}

. $UnitTestingPowerShellScriptsDirectory\ci_config.ps1
. $UnitTestingPowerShellScriptsDirectory\utils.ps1

function Bootstrap {
    ensureCreateDirectory $SublimeTextPackagesDirectory

    # Copy plugin files to Packages/<Package> folder.
    logVerbose "creating directory junction to package under test at $PackageUnderTestSublimeTextPackagesDirectory..."
    ensureCreateDirectoryJunction $PackageUnderTestSublimeTextPackagesDirectory .

    # Clone UnitTesting into Packages/UnitTesting.
    if (pathExists -Negate $UnitTestingSublimeTextPackagesDirectory) {
        $UNITTESTING_TAG = getLatestUnitTestingBuildTag $env:UNITTESTING_TAG $SublimeTextVersion $UnitTestingRepositoryUrl
        logVerbose "download UnitTesting tag: $UNITTESTING_TAG"
        gitCloneTag $UNITTESTING_TAG $UnitTestingRepositoryUrl $UnitTestingSublimeTextPackagesDirectory
        gitGetHeadRevisionName $UnitTestingSublimeTextPackagesDirectory | logVerbose
        logVerbose ""
    }

    # Clone coverage plugin into Packages/coverage.
    installPackageForSublimeTextIfNotPresent $CoverageSublimeTextPackagesDirectory $env:COVERAGE_TAG $CoverageRepositoryUrl

    & "$UnitTestingSublimeTextPackagesDirectory\sbin\install_sublime_text.ps1" -verbose

    # block update popup
    if (($env:CI -ne $null) -and ($env:SUBLIME_TEXT_VERSION -le 3)) {
        New-NetFirewallRule -DisplayName "Block sublimetext.com IP address" -Direction Outbound -LocalPort Any -Protocol TCP -Action Block -RemoteAddress "45.55.41.223"
    }
}

function InstallPackage {
    param([string]$PackageName, [string]$PackageTag, [string]$PackageUrl)
    installPackageForSublimeTextIfNotPresent $PackageName $PackageTag $PackageUrl
}

function InstallPackageControl {
    remove-item $CoverageSublimeTextPackagesDirectory -Force -Recurse
    & "$UnitTestingSublimeTextPackagesDirectory\sbin\install_package_control.ps1" -verbose
}

function InstallColorSchemeUnit {
    installPackageForSublimeTextIfNotPresent $ColorSchemeUnitSublimeTextPackagesDirectory $env:COLOR_SCHEME_UNIT_TAG $ColorSchemeUnitRepositoryUrl
}

function InstallKeypress {
    installPackageForSublimeTextIfNotPresent $KeyPressSublimeTextPackagesDirectory $env:KEYPRESS_TAG $KeyPressRepositoryUrl
}

function RunTests {
    [CmdletBinding()]
    param([switch]$syntax_test, [switch]$syntax_compatibility, [switch]$color_scheme_test, [switch]$coverage)

    # if (($coverage.IsPresent) -and ($SublimeTextVersion -eq 4)) {
    #     throw "Coverage is not yet supported in Sublime Text 4"
    # }

    # TODO: Change script name to conform to PS conventions.
    # TODO: Do not use verbose by default.
    & "$UnitTestingSublimeTextPackagesDirectory\sbin\run_tests.ps1" $PackageUnderTestName -verbose @PSBoundParameters

    stop-process -force -processname sublime_text -ea silentlycontinue
    start-sleep -seconds 2
}

switch ($command){
    'bootstrap' { Bootstrap }
    'install_package' { InstallPackage }
    'install_package_control' { InstallPackageControl }
    'install_color_scheme_unit' { InstallColorSchemeUnit }
    'install_keypress' { InstallKeypress }
    'run_tests' { RunTests -coverage:$coverage }
    'run_syntax_tests' { RunTests -syntax_test }
    'run_syntax_compatibility' { RunTests -syntax_compatibility }
    'run_color_scheme_tests' { RunTests -color_scheme_test }
}
