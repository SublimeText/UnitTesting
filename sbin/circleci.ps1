# NOTE: These params need to mirror exactly those of ci.ps1
[CmdletBinding()]
param(
    [Parameter(Mandatory = $false, Position = 0)]
    [string]$command,
    [Parameter(Mandatory = $false)]
    [switch] $coverage
)

$ErrorActionPreference = 'stop'

if (!$env:PACKAGE) {
    $env:PACKAGE = $env:CIRCLE_PROJECT_REPONAME
}

if (Test-Path (join-path $PSScriptRoot 'ps')) {
    $global:UnitTestingPowerShellScriptsDirectory = join-path $PSScriptRoot 'ps'
} else {
    # Scripts other than the bootstrapper are downloaded to and used from this directory.
    $global:UnitTestingPowerShellScriptsDirectory = $env:TEMP
}

function downloadScriptIfNotExist {
    param([string]$FileName)
    if (-Not (Test-Path (join-path $UnitTestingPowerShellScriptsDirectory $FileName))) {
        invoke-webrequest "https://raw.githubusercontent.com/SublimeText/UnitTesting/master/sbin/ps/$FileName" -outfile "$UnitTestingPowerShellScriptsDirectory\$FileName"
    }
}

if (!$env:UNITTESTING_BOOTSTRAPPED) {
    write-output "[UnitTesting] bootstrapping environment..."
    downloadScriptIfNotExist "ci_config.ps1"
    downloadScriptIfNotExist "utils.ps1"
    downloadScriptIfNotExist "ci.ps1"
    . $UnitTestingPowerShellScriptsDirectory\ci_config.ps1
    $env:UNITTESTING_BOOTSTRAPPED = 1
}

& $UnitTestingPowerShellScriptsDirectory\ci.ps1 @PSBoundParameters
