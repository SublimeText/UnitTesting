
function ensureCreateDirectory {
    param([string]$Path)
    [void](new-item -itemtype d "$Path" -force -erroraction stop)
}

function eitherOr {
    param($Left, $Right)
    if ($Left) { $Left } else { $Right }
}

function nullOr {
    param($Left, $Right)
    if ($Left -eq $null) { $Left } else { $Right }
}

function toLogMessage {
    param([string]$content)
    "[UnitTesting] $content"
}

filter logVerbose {
    param([string]$message)
    write-verbose (toLogMessage (eitherOr $_ $message))
}

filter logWarning {
    param([string]$message)
    write-warning (toLogMessage (eitherOr $_ $message))
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
    # if ([string]::IsNullOrEmpty($Tag)) { "$(getLatestTagFromRemote $UrlToCoverage)".Trim() }
    # else { $Tag }
    if (${env:COVERAGE_TAG} -eq $null){
        # the latest tag
        $COVERAGE_TAG = getLatestTagFromRemote $global:SublimeTextCoverageRepositoryUrl
        # $COVERAGE_TAG = git ls-remote --tags $global:SublimeTextCoverageRepositoryUrl | %{$_ -replace ".*/(.*)$", '$1'} `
        #         | where-object {$_ -notmatch "\^"} |%{[System.Version]$_} `
        #         | sort | select-object -last 1 | %{ "$_" }
        logWarning "found `$COVERAGE_TAG: $COVERAGE_TAG is null: $($COVERAGE_TAG -eq $null)..."
    } else {
        $COVERAGE_TAG = ${env:COVERAGE_TAG}
    }
    $COVERAGE_TAG
}

function ensureCreateDirectoryJunction {
    param([string]$Link, [string]$Target)
    cmd.exe /c mklink /J "$Link" "$Target"
    if ($LASTEXITCODE -ne 0) { throw "could not create directory junction at $Link to $Target" }
}

function ensureValue {
    param($Value, [string]$Pattern='^.*$', [string]$Message=$null)
    if(($Value -eq $null) -or ($Value -notmatch $Pattern)) {
        throw (eitherOr $Message "value is null or unexpected (expected match: $Pattern; got: $Value)")
    }
    $Value
}

function pathExists {
    param([string]$Path, [switch]$Negate=$False)
    if (!$Negate) { test-path $Path } else { !(test-path $Path) }
}