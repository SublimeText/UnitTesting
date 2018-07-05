# NOTE: These params need to mirror exactly those of ci.ps1
[CmdletBinding()]
param(
    [Parameter(Mandatory = $false, Position = 0)]
    [string]$command,
    [Parameter(Mandatory = $false)]
    [switch] $coverage
)

$ErrorActionPreference = 'stop'

# Scripts other than the bootstrapper are downloaded to and used from this directory.
$global:UnitTestingPowerShellScriptsDirectory = $env:TEMP

if (!$env:UNITTESTING_BOOTSTRAPPED) {
    write-output "[UnitTesting] bootstrapping environment..."

    $env:SUBLIME_TEXT_VERSION = 3
    $env:UNITTESTING_PACKAGE_UNDER_TEST_NAME = "Foo"

    invoke-webrequest "https://raw.githubusercontent.com/guillermooo/UnitTesting/refactor/appveyorscript2/sbin/ps/ci_config.ps1" -outfile "$UnitTestingPowerShellScriptsDirectory\ci_config.ps1"
    invoke-webrequest "https://raw.githubusercontent.com/guillermooo/UnitTesting/refactor/appveyorscript2/sbin/ps/utils.ps1" -outfile "$UnitTestingPowerShellScriptsDirectory\utils.ps1"
    invoke-webrequest "https://raw.githubusercontent.com/guillermooo/UnitTesting/refactor/appveyorscript2/sbin/ps/ci.ps1" -outfile "$UnitTestingPowerShellScriptsDirectory\ci.ps1"

    . $UnitTestingPowerShellScriptsDirectory\ci_config.ps1

    $env:UNITTESTING_BOOTSTRAPPED = 1
}

# Dependencies are now available to this script.
. $UnitTestingPowerShellScriptsDirectory\utils.ps1

# logWarning "the appveyor.ps1 script is deprecated; use ci.ps1 instead"

# & $UnitTestingPowerShellScriptsDirectory\ci.ps1 @PSBoundParameters

"say: $command"
