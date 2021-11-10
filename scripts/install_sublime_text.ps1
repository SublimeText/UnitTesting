[CmdletBinding()]
param(
    [ValidateSet('2', '3', '4')]
    [int]$Version = $Env:SUBLIME_TEXT_VERSION,
    [Parameter(Mandatory=$false)]
    [ValidateSet('x32', 'x64')]
    [string]$Arch = $Env:SUBLIME_TEXT_ARCH
)

$ErrorActionPreference = 'stop'

$private:MaxRetries = 20
if ($Version -ge 4) {
    $private:SublimeTextUrl = "http://www.sublimetext.com/download"
} else {
    $private:SublimeTextUrl = "http://www.sublimetext.com/$Version"
}

if (($Version -ge 4) -and ($Arch -eq 'x32')) {
    throw "wrong value of $Arch for Sublime Text version $Version."
}

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

$script:webClient = new-object System.Net.WebClient

function downloadFile {
    param([string]$source, [string]$target)
    $webClient.DownloadFile($source, $target)
}

write-verbose "installing sublime text $Version..."

$downloadUrl = $null

write-verbose "fetching download url..."

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

write-verbose "downloading $downloadUrl to $archivePath"

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

$SublimeTextDirectory = "C:\st\"

try {
    expand-archive -LiteralPath $archivePath -DestinationPath $SublimeTextDirectory
} catch {
    throw "could not extract Sublime Text zip from '$archivePath' to '$SublimeTextDirectory'"
}

write-verbose "installed Sublime Text $Version in '$SublimeTextDirectory'"
