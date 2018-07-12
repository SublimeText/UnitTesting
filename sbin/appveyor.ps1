# //////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////
#
# This script exists for backwards-compatibility. You can instead use ps\ci.ps1 as a drop-in
# replacement.
#
# //////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////

# NOTE: The following parameters must mirror exactly those of ps\ci.ps1.
[CmdletBinding()]
param(
    [Parameter(Position=0, Mandatory=$true)]
    [string]$command,
    [switch] $coverage
)

$ErrorActionPreference = 'stop'

# Scripts other than this bootstrapper are downloaded to and used from this directory.
$global:UnitTestingPowerShellScriptsDirectory = $env:TEMP

if (!$env:UNITTESTING_BOOTSTRAPPED) {
    write-output "[UnitTesting] bootstrapping environment..."

    invoke-webrequest "https://raw.githubusercontent.com/SublimeText/UnitTesting/master/sbin/ps/ci_config.ps1" -outfile "$UnitTestingPowerShellScriptsDirectory\ci_config.ps1"
    invoke-webrequest "https://raw.githubusercontent.com/SublimeText/UnitTesting/master/sbin/ps/utils.ps1" -outfile "$UnitTestingPowerShellScriptsDirectory\utils.ps1"
    invoke-webrequest "https://raw.githubusercontent.com/SublimeText/UnitTesting/master/sbin/ps/ci.ps1" -outfile "$UnitTestingPowerShellScriptsDirectory\ci.ps1"

    $env:UNITTESTING_BOOTSTRAPPED = 1
}

# . $UnitTestingPowerShellScriptsDirectory\ci_config.ps1

# & $UnitTestingPowerShellScriptsDirectory\ci.ps1 @PSBoundParameters
