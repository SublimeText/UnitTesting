[CmdletBinding()]
param(
    [Parameter(Mandatory=$false, Position=0)]
    [string]$command,
    [Parameter(Mandatory=$false)]
    [switch] $coverage
)

# Stop execution on any error. PS default is to continue on non-terminating errors.
$ErrorActionPreference = 'stop'

$global:UnitTestingPowerShellScriptsDirectory = $env:TEMP

# Do one-time environment initialization if needed.
if (!$env:UNITTESTING_BOOTSTRAPPED) {
    write-output "[UnitTesting] bootstrapping environment..."

    # Download scripts for basic operation.
    invoke-webrequest "https://raw.githubusercontent.com/SublimeText/UnitTesting/master/sbin/ps/ci_config.ps1" -outfile "$UnitTestingPowerShellScriptsDirectory\ci_config.ps1"
    invoke-webrequest "https://raw.githubusercontent.com/SublimeText/UnitTesting/master/sbin/ps/utils.ps1" -outfile "$UnitTestingPowerShellScriptsDirectory\utils.ps1"
    invoke-webrequest "https://raw.githubusercontent.com/SublimeText/UnitTesting/master/sbin/ps/ci.ps1" -outfile "$UnitTestingPowerShellScriptsDirectory\ci.ps1"

    $env:UNITTESTING_BOOTSTRAPPED = 1
}

. $UnitTestingPowerShellScriptsDirectory\ci_config.ps1
. $UnitTestingPowerShellScriptsDirectory\utils.ps1

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
        gitCloneTag $UNITTESTING_TAG $UnitTestingRepositoryUrl $UnitTestingSublimeTextPackagesDirectory
        gitGetHeadRevisionName $UnitTestingSublimeTextPackagesDirectory | logVerbose
        logVerbose ""
    }

    # Clone coverage plugin into Packages/coverage.
    installPackageForSublimeTextVersion3IfNotPresent $CoverageSublimeTextPackagesDirectory $env:COVERAGE_TAG $CoverageRepositoryUrl

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
    param([switch]$TestSyntax, [switch]$TestColorScheme, [switch]$Coverage)

    # TODO: Change script name to conform to PS conventions.
    & "$UnitTestingSublimeTextPackagesDirectory\sbin\run_tests.ps1" $env:PACKAGE -verbose @PSBoundParameters

    stop-process -force -processname sublime_text -ea silentlycontinue
    start-sleep -seconds 2
}

# UnitTesting command names that the ci.ps1 script supports.
enum CiCommand {
    Bootstrap
    InstallPackageControl
    InstallColorSchemeUnit
    InstallKeypress
    RunTests
    RunSyntaxTests
    RunColorSchemeTests
}

# TODO: Remove when no longer needed.
# Map of Legacy command names to current command names. Used to warn users of deprecated command names.
$legacyCommandNames = @{
    'install_package_control' = 'InstallPackageControl',
    'install_color_scheme_unit' = 'InstallColorSchemeUnit',
    'install_keypress' = 'InstallKeypress',
    'run_tests' = 'RunTests',
    'run_syntax_tests' = 'RunSyntaxTests',
    'run_color_scheme_tests' = 'RunColorSchemeTests'
}

# TODO: Remove when no longer needed.
if ($legacyCommandNames.ContainsKey($command)) {
    write-warning "The command name '$command' is deprecated. Consider using '$($legacyCommandNames[$command])' instead."
    $command = $legacyCommandNames[$command]
}

# Stop if we didn't get a valid command name.
if (![enum]::IsDefined([CiCommand], $command)) {
    throw ("The value of the 'Command' parameter must be one of: $([enum]::GetNames([CiCommand]) -join ", ")")
}

try{
    switch ([CiCommand]$command){
        [CiCommand]::Bootstrap { Bootstrap }
        [CiCommand]::InstallPackageControl { InstallPackageControl }
        [CiCommand]::InstallColorSchemeUnit { InstallColorSchemeUnit }
        [CiCommand]::InstallKeypress { InstallKeypress }
        [CiCommand]::RunTests { RunTests -Coverage:$coverage }
        [CiCommand]::RunSyntaxTests { RunTests -TestSyntax }
        [CiCommand]::RunColorSchemeTests { RunTests -TestColorScheme }
    }
}catch {
    throw $_
}
