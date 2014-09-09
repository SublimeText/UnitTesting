[CmdletBinding()]
param([string]$command,
    [Parameter(ValueFromRemainingArguments = $true)] [Object[]]$MyArgs
)

Function Bootstrap {
    if ( ${env:SUBLIME_TEXT_VERSION} -eq "3" ){
        write-verbose "installing sublime text 3"
        start-filedownload "http://c758482.r82.cf2.rackcdn.com/Sublime%20Text%20Build%203065%20x64.zip"
        write-verbose "installing Sublime%20Text%20Build%203065%20x64.zip"
        7z.exe x "Sublime%20Text%20Build%203065%20x64.zip" -o"C:\st" > $null
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
        # $TAG = (invoke-restmethod https://api.github.com/repos/randy3k/UnitTesting/tags) | select -expandproperty "name" -first 1
        # $TAG = "master"
        $TAG = git ls-remote --tags https://github.com/randy3k/UnitTesting |  %{$_ -replace ".*/(.*)$", '$1'} | %{[System.Version]$_}|sort | select-object -last 1 | %{ "$_" }
    }else{
        $TAG = ${env:TAG}
    }
    if(!(Test-Path -Path "C:\st\Data\Packages\UnitTesting")){
        git clone -q --branch=$TAG https://github.com/randy3k/UnitTesting.git "C:\st\Data\Packages\UnitTesting" 2>&1 | %{ "$_" }
    }
}

Function RunTests {
    invoke-expression "C:\st\Data\Packages\UnitTesting\sbin\run.ps1 $MyArgs `"${env:PACKAGE}`" -verbose"
}

switch ($command){
    "bootstrap" { Bootstrap }
    "run_tests" { RunTests}
}
