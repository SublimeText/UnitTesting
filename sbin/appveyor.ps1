[CmdletBinding()]
param(
    [Parameter(Mandatory = $false, Position = 0)]
    [string]$command,
    [Parameter(Mandatory = $false)]
    [switch] $coverage
)

$STP = "C:\st\Data\Packages"

function Bootstrap {
    [CmdletBinding()]
    param(
        [switch] $with_color_scheme_unit
    )

    new-item -itemtype directory "$STP\${env:PACKAGE}" -force >$null

    if (${env:PACKAGE} -eq "__all__"){
        write-verbose "copy all subfolders to sublime package directory"
        copy * -recurse -force "$STP"
    } else {
        write-verbose "copy the package to sublime text Packages directory"
        copy * -recurse -force "$STP\${env:PACKAGE}"
    }

    git config --global advice.detachedHead false

    $UT_PATH = "$STP\UnitTesting"
    if (!(test-path -path "$UT_PATH")){

        $UT_URL = "https://github.com/randy3k/UnitTesting"

        if ( ${env:UNITTESTING_TAG} -eq $null){
            if (${env:SUBLIME_TEXT_VERSION} -eq 2) {
                $UNITTESTING_TAG = "0.10.6"
            } elseif (${env:SUBLIME_TEXT_VERSION} -eq 3) {
                # the latest tag
                $UNITTESTING_TAG = git ls-remote --tags $UT_URL | %{$_ -replace ".*/(.*)$", '$1'} `
                        | where-object {$_ -notmatch "\^"} |%{[System.Version]$_} `
                        | sort | select-object -last 1 | %{ "$_" }
            }
        } else {
            $UNITTESTING_TAG = ${env:UNITTESTING_TAG}
        }

        write-verbose "download UnitTesting tag: $UNITTESTING_TAG"
        git clone --quiet --depth 1 --branch=$UNITTESTING_TAG $UT_URL "$UT_PATH" 2>$null
        git -C "$UT_PATH" rev-parse HEAD | write-verbose
        write-verbose ""
    }

    $COV_PATH = "$STP\coverage"
    if ((${env:SUBLIME_TEXT_VERSION} -eq 3) -and (!(test-path -path "$COV_PATH"))){

        $COV_URL = "https://github.com/codexns/sublime-coverage"

        if ( ${env:COVERAGE_TAG} -eq $null){
            # the latest tag
            $COVERAGE_TAG = git ls-remote --tags $COV_URL | %{$_ -replace ".*/(.*)$", '$1'} `
                    | where-object {$_ -notmatch "\^"} |%{[System.Version]$_} `
                    | sort | select-object -last 1 | %{ "$_" }
        } else {
            $COVERAGE_TAG = ${env:COVERAGE_TAG}
        }

        write-verbose "download sublime-coverage tag: $COVERAGE_TAG"
        git clone --quiet --depth 1 --branch=$COVERAGE_TAG $COV_URL "$COV_PATH" 2>$null
        git -C "$COV_PATH" rev-parse HEAD | write-verbose
        write-verbose ""
    }


    & "$STP\UnitTesting\sbin\install_sublime_text.ps1" -verbose

}

function InstallPackageControl {
    $COV_PATH = "$STP\coverage"
    remove-item $COV_PATH -Force -Recurse
    & "$STP\UnitTesting\sbin\install_package_control.ps1" -verbose
}

function InstallColorSchemeUnit {
    $CSU_PATH = "$STP\ColorSchemeUnit"
    if ((${env:SUBLIME_TEXT_VERSION} -eq 3) -and (!(test-path -path "$CSU_PATH"))){
        $CSU_URL = "https://github.com/gerardroche/sublime-color-scheme-unit"

        if ( ${env:COLOR_SCHEME_UNIT_TAG} -eq $null){
            # the latest tag
            $COLOR_SCHEME_UNIT_TAG = git ls-remote --tags $CSU_URL | %{$_ -replace ".*/(.*)$", '$1'} `
                    | where-object {$_ -notmatch "\^"} |%{[System.Version]$_} `
                    | sort | select-object -last 1 | %{ "$_" }
        } else {
            $COLOR_SCHEME_UNIT_TAG = ${env:COLOR_SCHEME_UNIT_TAG}
        }
        write-verbose "download ColorSchemeUnit tag: $COLOR_SCHEME_UNIT_TAG"
        git clone --quiet --depth 1 --branch=$COLOR_SCHEME_UNIT_TAG $CSU_URL "$CSU_PATH" 2>$null
        git -C "$CSU_PATH" rev-parse HEAD | write-verbose
        write-verbose ""
    }
}

function RunTests {
    [CmdletBinding()]
    param(
        [switch] $syntax_test
    )

    if ( $syntax_test.IsPresent ){
        & "$STP\UnitTesting\sbin\run_tests.ps1" "${env:PACKAGE}" -verbose -syntax_test
    } elseif ( $coverage.IsPresent ) {
        & "$STP\UnitTesting\sbin\run_tests.ps1" "${env:PACKAGE}" -verbose -coverage
    } else {
        & "$STP\UnitTesting\sbin\run_tests.ps1" "${env:PACKAGE}" -verbose
    }
}

try{
    switch ($command){
        "bootstrap" { Bootstrap }
        "install_package_control" { InstallPackageControl }
        "install_color_scheme_unit" { InstallColorSchemeUnit }
        "run_tests" { RunTests }
        "run_syntax_tests" { RunTests -syntax_test}
    }
}catch {
    throw $_
}
