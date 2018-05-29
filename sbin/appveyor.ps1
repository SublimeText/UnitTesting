# NOTE: These params need to mirror exactly those of ci.ps1
[CmdletBinding()]
param(
    [Parameter(Mandatory = $false, Position = 0)]
    [string]$command,
    [Parameter(Mandatory = $false)]
    [switch] $coverage
)

. $PSScriptRoot\utils.ps1

logWarning "the appveyor.ps1 script is deprecated; use ci.ps1 instead"

& $PSScriptRoot\ci.ps1 @PSBoundParameters
