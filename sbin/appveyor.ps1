[CmdletBinding()]
param([string]$command,
    [Parameter(ValueFromRemainingArguments = $true)] [Object[]]$remainingArgs
)

Function Bootstrap {
    if ( ${env:SUBLIME_TEXT_VERSION} -eq "3" ){
        write-verbose "installing sublime text 3"
        # read the url from sublime website
        $url = ((Invoke-WebRequest "http://www.sublimetext.com/3").Links | where href -match "x64\.zip").href | select-object -first 1
        $filename = $url | %{$_ -replace ".*/(.*)$", '$1'}
        start-filedownload "$url"
        write-verbose "installing $filename"
        7z.exe x "$filename" -o"C:\st" > $null
    }elseif ( ${env:SUBLIME_TEXT_VERSION} -eq "2" ){
        write-verbose "installing sublime text 2"
        start-filedownload "http://c758482.r82.cf2.rackcdn.com/Sublime%20Text%202.0.2%20x64.zip"
        write-verbose "installing Sublime%20Text%202.0.2%20x64.zip"
        7z.exe x "Sublime%20Text%202.0.2%20x64.zip" -o"C:\st" > $null
    }

    mkdir "C:\st\Data\Packages\${env:PACKAGE}" -force > $null
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

Function RunTests {
    invoke-expression "C:\st\Data\Packages\UnitTesting\sbin\run.ps1 $remainingArgs `"${env:PACKAGE}`" -verbose"
}

switch ($command){
    "bootstrap" { Bootstrap }
    "run_tests" { RunTests }
}
