[CmdletBinding()]
param(
    [ValidateSet('2', '3')]
    [int]$Version = $SublimeTextVersion
)

$ErrorActionPreference = 'stop'

$script:MaxRetries = 20
$script:SublimeTextUrl = "http://www.sublimetext.com/$Version"

. $PSScriptRoot\ps\utils.ps1

# TODO: improve logging overall.
logVerbose "installing sublime text $Version..."

function getDownloadUrl {
    param([string]$Url)
    $html = Invoke-WebRequest $Url -UseBasicParsing
    foreach ($link in $html.Links) {
        if ($link.href.endsWith('x64.zip')) {
           $link.href
           break
        }
    }
}

$downloadUrl = $null

for ($i=1; $i -le $MaxRetries; $i++) {
    try {
        $downloadUrl = getDownloadUrl $SublimeTextUrl
        break
    } catch {
        if ($i -eq $MaxRetries) {
            throw "could not download Sublime Text from '$SublimeTextUrl'"
        }
        start-sleep -seconds 3
    }
}

logVerbose "downloading $downloadUrl..."

$downloadUrl = [Uri]::EscapeUriString($downloadUrl)
$filename = Split-Path $downloadUrl -leaf

for ($i=1; $i -le $MaxRetries; $i++) {
    try {
        downloadFile $downloadUrl (join-path $env:TEMP $filename)
        break
    } catch {
        if ($i -eq $MaxRetries) {
            throw "could not download Sublime Text"
        }
        start-sleep -seconds 3
    }
}

try {
    extractZipToDirectory "${env:Temp}\$filename" "C:\st"
} catch {
    throw "could not extract Sublime Text zip archive"
}

ensureCreateDirectory "C:\st\Data\Packages\User"
