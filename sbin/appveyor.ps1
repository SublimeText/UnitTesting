[CmdletBinding()]
param(
    [string]$command
)

function getDownloadUrl($version) {
    $url = $null
    foreach ( $link in (invoke-webrequest "http://www.sublimetext.com/$version").Links ) {
        if ( $link.href.endsWith("x64.zip") ) {
           $url = $link.href
           break
        }
    }
    if (-not $url) {
        throw "could not download Sublime Text binary"
    }
    # Replaces spaces by %20 -- note that other .Net methods in
    # System.Net and System.Web convert spaces to + instead.
    [System.Uri]::EscapeUriString($url)
}

function Bootstrap {
    write-verbose "installing sublime text ${env:SUBLIME_TEXT_VERSION}"
    $url = getDownloadUrl ${env:SUBLIME_TEXT_VERSION}
    $filename = split-path $url -leaf
    start-filedownload $url
    # TODO(guillermooo): use ZipFile class in .NET 4.5.
    7z.exe x "$filename" -o"C:\st" >$null

    new-item -itemtype directory "C:\st\Data\Packages\${env:PACKAGE}" -force >$null
    copy * -recurse -force "C:\st\Data\Packages\${env:PACKAGE}"

    new-item -itemtype directory "C:\st\Data\Packages\User" -force >$null
    "{`"update_check`": false }" | out-file -filepath "C:\st\Data\Packages\User\Preferences.sublime-settings" -encoding ascii

    if ( ${env:TAG} -eq $null ){
        # the latest tag
        write-verbose "download latest UnitTesting tag"
        $TAG = git ls-remote --tags https://github.com/randy3k/UnitTesting | %{$_ -replace ".*/(.*)$", '$1'} | where-object {$_ -notmatch "\^"} |%{[System.Version]$_}|sort | select-object -last 1 | %{ "$_" }
    }else{
        $TAG = ${env:TAG}
    }
    if(!(test-path -path "C:\st\Data\Packages\UnitTesting")){
        git clone --quiet --depth 1 --branch=$TAG https://github.com/randy3k/UnitTesting.git "C:\st\Data\Packages\UnitTesting" 2>$null
    }
}

function RunTests {
    & "C:\st\Data\Packages\UnitTesting\sbin\run.ps1" "${env:PACKAGE}" -verbose
}

switch ($command){
    "bootstrap" { Bootstrap }
    "run_tests" { RunTests }
}
