
function ensureCreateDirectory {
    param([string]$Path)
    [void](new-item -itemtype d "$Path" -force -erroraction stop)
}

filter logVerbose {
    param([string]$message)
    $msg = $message
    if ($_) { $msg = "$_" }
    write-verbose "[UnitTesting] $msg"
}

filter logWarning {
    param([string]$message)
    $msg = $message
    if ($_) { $msg = "$_" }
    write-warning "[UnitTesting] $msg"
}

function ensureCopyDirectoryContents {
    param([string]$Path, [string]$Destination)
    copy-item "$Path\*" -recurse -force $Destination -erroraction stop
}

function ensureRemoveDirectory {
    param([string]$Path)
    if ([System.IO.Path.File].Exists((convert-path $Path))) {
        throw "expected a directory, got a file: $Path"
    }
    remove-item "$Path" -recurse -force -erroraction stop
}

function getLatestTagFromRemote {
    param([string]$UrlToRepository)
    git ls-remote --tags "$UrlToRepository" | %{$_ -replace ".*/(.*)$", '$1'} `
        | where-object {$_ -notmatch "\^"} |%{[System.Version]$_} `
        | sort | select-object -last 1 | %{ "$_" }
}

function getLatestUnitTestingBuildTag {
    param([string]$Tag, [string]$SublimeTextVersion, [string]$UrlToUnitTesting)
    $result = $Tag
    if ([string]::IsNullOrEmpty($Tag)){
        if ($SublimeTextVersion -eq 2) {
            $result = '0.10.6'
        } elseif ($SublimeTextVersion -eq 3) {
            $result = getLatestTagFromRemote $UrlToUnitTesting
        }
    }
    $result
}

function getLatestCoverageTag {
    param([string]$Tag, [string]$UrlToCoverage)
    if ([string]::IsNullOrEmpty($Tag)) { getLatestTagFromRemote $UrlToCoverage }
    else { $Tag }
}

function ensureCreateDirectoryJunction {
    param([string]$Link, [string]$Target)
    cmd.exe /c mklink /J "$Link" "$Target"
    if ($LASTEXITCODE -ne 0) { throw "could not create directory junction at $Link to $Target" }
}