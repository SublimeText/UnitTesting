[CmdletBinding()]
param(
    [string]$command
)

$STP = "C:\st\Data\Packages"

function Bootstrap {
    $STI_URL = "https://github.com/randy3k/sublime_text_installer"
    git clone --quiet --depth 1 --branch master "$STI_URL" "C:\sublime_text_installer"

    & "C:\sublime_text_installer\install_sublime_text.ps1" -verbose

    new-item -itemtype directory "$STP\${env:PACKAGE}" -force >$null
    copy * -recurse -force "$STP\${env:PACKAGE}"

    $UT_URL = "https://github.com/randy3k/UnitTesting"

    if ( ${env:TAG} -eq $null ){
        # the latest tag
        write-verbose "download latest UnitTesting tag"
        $TAG = git ls-remote --tags $UT_URL | %{$_ -replace ".*/(.*)$", '$1'} `
                | where-object {$_ -notmatch "\^"} |%{[System.Version]$_} `
                | sort | select-object -last 1 | %{ "$_" }
    }else{
        $TAG = ${env:TAG}
    }

    if(!(test-path -path "$STP\UnitTesting")){
        git clone --quiet --depth 1 --branch=$TAG $UT_URL "$STP\UnitTesting" 2>$null
    }
}

function InstallPackageControl {
    $STI_URL = "https://github.com/randy3k/sublime_text_installer"
    if(!(test-path -path "C:\sublime_text_installer")){
        git clone --quiet --depth 1 --branch master "$STI_URL" "C:\sublime_text_installer"
    }

    & "C:\sublime_text_installer\install_package_control.ps1" -verbose
}

function RunTests {
    [CmdletBinding()]
    param(
        [switch] $syntax_test
    )

    if ( $syntax_test.IsPresent ){
        & "$STP\UnitTesting\sbin\run.ps1" "${env:PACKAGE}" -verbose -syntax_test
    }else{
        & "$STP\UnitTesting\sbin\run.ps1" "${env:PACKAGE}" -verbose
    }
}

try{
    switch ($command){
        "bootstrap" { Bootstrap }
        "install_package_control" { InstallPackageControl }
        "run_tests" { RunTests }
        "run_syntax_tests" { RunTests -syntax_test}
    }
}catch {
    throw $_
}
