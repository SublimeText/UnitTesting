[CmdletBinding()]
param(
    [ValidateSet('2', '3')]
    [int]$Version = $SublimeTextVersion
)

$ErrorActionPreference = 'stop'

. $PSScriptRoot\utils.ps1

# TODO: improve logging overall.
write-verbose "installing sublime text $Version..."

$url = $null
for ($i=1; $i -le 20; $i++) {
    try {
        foreach ( $link in (Invoke-WebRequest "http://www.sublimetext.com/$Version" -UseBasicParsing).Links ) {
            if ( $link.href.endsWith("x64.zip") ) {
               $url = $link.href
               break
            }
        }
        break
    } catch {
        if ($i -eq 20) {
            throw "could not download Sublime Text"
        }
        start-sleep -s 3
    }
}

write-verbose "downloading $url..."

$url = [Uri]::EscapeUriString($url)
$filename = Split-Path $url -leaf

for ($i=1; $i -le 20; $i++) {
    try {
        downloadFile $url (join-path $env:TEMP $filename)
        break
    } catch {
        if ($i -eq 20) {
            throw "could not download Sublime Text"
        }
        start-sleep -s 3
    }
}

Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::ExtractToDirectory("${env:Temp}\$filename", "C:\st")

New-Item -itemtype directory "C:\st\Data\Packages\User" -force >$null
