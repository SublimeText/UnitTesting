[CmdletBinding()]
param(
    [string]$Command,
    [Parameter(ValueFromRemainingArguments=$true)]
    [Object[]]$RemainingArgs
)

function getDownloadUrl {
    $url = $null
    foreach ( $link in (Invoke-WebRequest "http://www.sublimetext.com/3").Links ) {
        if ( $link.href.endsWith("x64.zip") ) {
           [System.Web.HttpUtility]::UrlDecode($link.href)
           break
        }
    }
}

function Bootstrap {
    if ( ${env:SUBLIME_TEXT_VERSION} -eq "3" ){
        write-verbose "installing sublime text 3"
        $url = getDownloadUrl
        if (-not $url) {
            throw ( "could not download Sublime Text binary")
        }
        $filename = split-path $url -leaf
        start-filedownload $url
        write-verbose "installing $filename"
        # TODO(guillermooo): use ZipFile class in .NET 4.5.
        7z.exe x "$filename" -o"C:\st" > $null
    }elseif ( ${env:SUBLIME_TEXT_VERSION} -eq "2" ){
        write-verbose "installing sublime text 2"
        start-filedownload "http://c758482.r82.cf2.rackcdn.com/Sublime%20Text%202.0.2%20x64.zip"
        write-verbose "installing Sublime%20Text%202.0.2%20x64.zip"
        7z.exe x "Sublime%20Text%202.0.2%20x64.zip" -o"C:\st" > $null
    }

    new-item -itemtype directory "C:\st\Data\Packages\${env:PACKAGE}" -force > $null
    copy * -recurse -force "C:\st\Data\Packages\${env:PACKAGE}"
    if ( ${env:TAG} -eq $null ){
        # the latest tag
        $TAG = git ls-remote --tags https://github.com/randy3k/UnitTesting |  %{$_ -replace ".*/(.*)$", '$1'} | %{[System.Version]$_}|sort | select-object -last 1 | %{ "$_" }
    }else{
        $TAG = ${env:TAG}
    }
    if(!(Test-Path -Path "C:\st\Data\Packages\UnitTesting")){
        git clone -q --branch=$TAG https://github.com/randy3k/UnitTesting.git "C:\st\Data\Packages\UnitTesting" 2>&1 | %{ "$_" }
    }
}

function RunTests {
    & "C:\st\Data\Packages\UnitTesting\sbin\run.ps1" $remainingArgs "${env:PACKAGE}" -verbose
}

switch ($command){
    "bootstrap" { Bootstrap }
    "run_tests" { RunTests }
}
