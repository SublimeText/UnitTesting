<#
.SYNOPSIS
Installs Sublime Text.

.PARAMETER Version
The major version of Sublime Text to be installed.
#>
[CmdletBinding()]
param(
    [ValidateSet('2', '3')]
    [int]$Version = $SublimeTextVersion,
    [Parameter(Mandatory=$false)]
    [ValidateSet('x32', 'x64')]
    [string]$Arch = $SublimeTextArch
)

$ErrorActionPreference = 'stop'

$private:MaxRetries = 20
$private:SublimeTextUrl = "http://www.sublimetext.com/$Version"

. $PSScriptRoot\ps\utils.ps1

# TODO: improve logging overall.
logVerbose "installing sublime text $Version..."

function getDownloadUrl {
    param([string]$Url)
    $html = Invoke-WebRequest $Url -UseBasicParsing
    foreach ($link in $html.Links) {
        if ($Arch -eq 'x64') {
            if ($link.href.endsWith("$Arch.zip")) {
               $link.href
               break
            }
        } else {
            if ($link.href -match ".*(?<!x64)\.zip") {
               $link.href
               break
            }
        }
    }
}

$downloadUrl = $null

logVerbose "fetching download url..."

for ($i=1; $i -le $MaxRetries; $i++) {
    try {
        $downloadUrl = getDownloadUrl $SublimeTextUrl
        break
    } catch {
        if ($i -eq $MaxRetries) {
            throw "could not download Sublime Text from '$SublimeTextUrl' after $MaxRetries retries"
        }
        start-sleep -seconds 3
    }
}

$downloadUrl = [Uri]::EscapeUriString($downloadUrl)
$filename = split-path $downloadUrl -leaf
$archivePath = join-path $env:TEMP $filename

logVerbose "downloading $downloadUrl..."

for ($i=1; $i -le $MaxRetries; $i++) {
    try {
        downloadFile $downloadUrl $archivePath
        break
    } catch {
        if ($i -eq $MaxRetries) {
            throw "could not download Sublime Text after $MaxRetries retries"
        }
        start-sleep -seconds 3
    }
}

try {
    expand-archive -LiteralPath $archivePath -DestinationPath $SublimeTextDirectory
} catch {
    throw "could not extract Sublime Text zip from '$archivePath' to '$SublimeTextDirectory'"
}

logVerbose "installed Sublime Text $Version in '$SublimeTextDirectory'"
logVerbose "creating $SublimeTextPackagesDirectory\User..."

ensureCreateDirectory "$SublimeTextPackagesDirectory\User"
