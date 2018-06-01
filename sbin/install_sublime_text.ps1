[CmdletBinding()]
param([int]$st=$global:SublimeTextVersion)

. $PSScriptRoot\utils.ps1

$script:MaxRetriesCount = 20
$script:WaitPeriodSeconds = 3

function scrapDownloadUrl {
    param([string]$DownloadPageUrl)
    $url = $null
    foreach ($link in (Invoke-WebRequest $downloadPageUrl -UseBasicParsing).Links ) {
        if ($link.href.endsWith('x64.zip') ) {
           $url = $link.href
           break
        }
    }
    $url
}

function fetchDownloadUrlWithRetry {
    param([string]$DownloadPageUrl)
    $url = $null
    foreach ($attempt in [System.Linq.Enumerable]::Range(1, $MaxRetriesCount)) {
        try {
            if ($attempt -gt 1) {
                logVerbose "trying to retrieve Sublime Text download url... $attempt/$MaxRetriesCount"
            }
            $url = scrapDownloadUrl $DownloadPageUrl
            break
        } catch {
            logVerbose "could not retrieve Sublime Text download url"
            logVerbose "waiting $WaitPeriodSeconds before trying to retrieve download url again..."
            start-sleep -seconds $WaitPeriodSeconds
            continue
        }
    }
    $url
}

function downloadWithRetry {
    param([string]$Url, [string]$PathToZipFile)
    $wc = new-object system.net.webclient
    foreach ($attempt in [System.Linq.Enumerable]::Range(1, $MaxRetriesCount)) {
        try {
            if ($attempt -gt 1) {
                logVerbose "trying to download Sublime Text... $attempt/$MaxRetriesCount"
            }
            # WebClient was the fastest method among WebClient, Start-WebRequest and Start-BitsTransfer.
            $wc.DownloadFile($Url, $PathToZipFile)
            break
        } catch {
            logVerbose "could not download Sublime Text"
            logVerbose "waiting $WaitPeriodSeconds before trying to download Sublime Text again..."
            start-sleep -seconds $WaitPeriodSeconds
        }
    }
}

# TODO: this should be possible to verify with PS param binding stuff.
ensureValue $st '^2|3$' "wrong Sublime Text version: $st (is `$st null: $($st -eq $null))"

$downloadPageUrl = iif { $global:IsSublimeTextVersion3 } $global:SublimeTextWebsiteUrlForVersion3 $global:SublimeTextWebsiteUrlForVersion2
logVerbose "installing Sublime Text version $st from $downloadPageUrl"
$url = fetchDownloadUrlWithRetry $downloadPageUrl

if (-not $url) {
    throw "could not retrieve Sublime Text download url"
}

$urlEscaped = [Uri]::EscapeUriString($url)
$filename = [Uri]::UnescapeDataString((Split-Path $urlEscaped -leaf))
$pathToZipFile = "$env:Temp\$filename"

logVerbose "downloading Sublime Text binaries from $urlEscaped to $pathToZipFile"
downloadWithRetry $urlEscaped $pathToZipFile
unzip $pathToZipFile $global:SublimeTextDirectory

ensureCreateDirectory "$global:SublimeTextPackagesDirectory\User"
