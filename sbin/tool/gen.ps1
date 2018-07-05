# generates base64-encoded verions of files
param([switch]$AsCodeSnippet)

$ErrorActionPreference = 'stop'

$basePath = convert-path $PSScriptRoot

. $basePath\..\ps\utils.ps1

# UTF8 encoding without preamble.
$utf8 = [System.Text.UTF8Encoding]::new($false)

filter convertToBase64String {
    param([string]$Path)
    $thePath = if ($_) { $_ } else { $Path }
    # We need to join the lines returned by get-content.
    $content = (get-content $thePath) -join "`n"
    [System.Convert]::ToBase64String($utf8.GetBytes($content))
}

filter convertFromBase64String {
    param([string]$content)
    $theContent = if ($_) { $_ } else { $content }
    $bytes = [System.Convert]::FromBase64String($theContent)
    "$($utf8.GetString($bytes))"
}

function createTextFile {
    param([string]$Destination, [string]$Content)
    if (!(test-path $Destination)) {
        [System.IO.File]::WriteAllText($Destination, $Content, $utf8)
    } else {
        throw "cannot write file $Destination if it already exists"
    }
}

function packFile {
    param($Path)
    $name = split-path $Path -leaf
    $base64encodedContent = $Path | convertToBase64String
    "$name@@@$base64encodedContent"
}

function unPackFile {
    param($Content)
    $elements = @($Content -split '@@@')
    for ($i = 0; $i -lt $elements.length; $i = $i + 2) {
        createTextFile (join-path (convert-path .) ".\$($elements[$i])") ($elements[$i+1] | convertFromBase64String)
    }
}

if (!$AsCodeSnippet) {
    packFile "$basePath\..\ps\utils.ps1"
    packFile "$basePath\..\ps\ci.ps1"
    packFile "$basePath\..\ps\ci_config.ps1"
} else {
@"
`$local:encodedDependencies = @(
    '$(packFile "$basePath\..\ps\utils.ps1")',
    '$(packFile "$basePath\..\ps\ci.ps1")',
    '$(packFile "$basePath\..\ps\ci_config.ps1")'
    )
"@
}
