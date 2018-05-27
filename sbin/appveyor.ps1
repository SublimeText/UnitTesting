[CmdletBinding()]
param(
    [Parameter(Mandatory = $false, Position = 0)]
    [string]$command,
    [Parameter(Mandatory = $false)]
    [switch] $coverage
)

. $PSScriptRoot\utils.ps1
$STP = "C:\st\Data\Packages"
$script:PackageName = $env:PACKAGE

function Bootstrap {
    [CmdletBinding()]
    param(
        [switch] $with_color_scheme_unit
    )
    
    ensureCreateDirectory $STP

    if ($PackageName -eq "__all__"){
        logVerbose "create package directory at $STP\$env:PACKAGE"
        ensureCreateDirectory "$STP\$PackageName"
        logVerbose "copy all subfolders to sublime package directory"
        # TODO: create junctions for all packages.
        ensureCopyDirectoryContents . "$STP"
    } else {
        logVerbose "create directory junction to package at $STP\$PackageName"
        ensureCreateDirectoryJunction "$STP\$env:PACKAGE" .
    }

    git config --global advice.detachedHead false

    $UT_PATH = "$STP\UnitTesting"
    if (!(test-path -path "$UT_PATH")){

        $UT_URL = "https://github.com/randy3k/UnitTesting"
        $UNITTESTING_TAG = getLatestUnitTestingBuildTag $env:UNITTESTING_TAG $env:SUBLIME_TEXT_VERSION $UT_URL

        logVerbose "download UnitTesting tag: $UNITTESTING_TAG"
        git clone --quiet --depth 1 --branch=$UNITTESTING_TAG $UT_URL "$UT_PATH" 2>$null
        git -C "$UT_PATH" rev-parse HEAD | logVerbose
        logVerbose ""
    }

    $COV_PATH = "$STP\coverage"
    if (($env:SUBLIME_TEXT_VERSION -eq 3) -and (!(test-path -path "$COV_PATH"))){

        $COV_URL = "https://github.com/codexns/sublime-coverage"
        $COVERAGE_TAG = getLatestCoverageTag $env:COVERAGE_TAG $COV_URL
        
        logVerbose "download sublime-coverage tag: $COVERAGE_TAG"
        git clone --quiet --depth 1 --branch=$COVERAGE_TAG $COV_URL "$COV_PATH" 2>$null
        git -C "$COV_PATH" rev-parse HEAD | write-verbose
        logVerbose ""
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
    if (($env:SUBLIME_TEXT_VERSION -eq 3) -and (!(test-path -path "$CSU_PATH"))){
        $CSU_URL = "https://github.com/gerardroche/sublime-color-scheme-unit"

        if ( $env:COLOR_SCHEME_UNIT_TAG -eq $null){
            # the latest tag
            $COLOR_SCHEME_UNIT_TAG = git ls-remote --tags $CSU_URL | %{$_ -replace ".*/(.*)$", '$1'} `
                    | where-object {$_ -notmatch "\^"} |%{[System.Version]$_} `
                    | sort | select-object -last 1 | %{ "$_" }
        } else {
            $COLOR_SCHEME_UNIT_TAG = $env:COLOR_SCHEME_UNIT_TAG
        }
        write-verbose "download ColorSchemeUnit tag: $COLOR_SCHEME_UNIT_TAG"
        git clone --quiet --depth 1 --branch=$COLOR_SCHEME_UNIT_TAG $CSU_URL "$CSU_PATH" 2>$null
        git -C "$CSU_PATH" rev-parse HEAD | write-verbose
        write-verbose ""
    }
}

function InstallKeypress {
    $KP_PATH = "$STP\Keypress"
    if (($env:SUBLIME_TEXT_VERSION -eq 3) -and (!(test-path -path "$KP_PATH"))){
        $KP_URL = "https://github.com/randy3k/Keypress"

        if ( $env:KEYPRESS_TAG -eq $null){
            # the latest tag
            $KEYPRESS_TAG = git ls-remote --tags $KP_URL | %{$_ -replace ".*/(.*)$", '$1'} `
                    | where-object {$_ -notmatch "\^"} |%{[System.Version]$_} `
                    | sort | select-object -last 1 | %{ "$_" }
        } else {
            $KEYPRESS_TAG = $env:KEYPRESS_TAG
        }
        write-verbose "download ColorSchemeUnit tag: $KEYPRESS_TAG"
        git clone --quiet --depth 1 --branch=$KEYPRESS_TAG $KP_URL "$KP_PATH" 2>$null
        git -C "$KP_PATH" rev-parse HEAD | write-verbose
        write-verbose ""
    }
}

function RunTests {
    [CmdletBinding()]
    param(
        [switch] $syntax_test,
        [switch] $color_scheme_test
    )

    if ( $syntax_test.IsPresent ){
        & "$STP\UnitTesting\sbin\run_tests.ps1" "$env:PACKAGE" -verbose -syntax_test
    } elseif ( $color_scheme_test.IsPresent ){
        & "$STP\UnitTesting\sbin\run_tests.ps1" "$env:PACKAGE" -verbose -color_scheme_test
    } elseif ( $coverage.IsPresent ) {
        & "$STP\UnitTesting\sbin\run_tests.ps1" "$env:PACKAGE" -verbose -coverage
    } else {
        & "$STP\UnitTesting\sbin\run_tests.ps1" "$env:PACKAGE" -verbose
    }

    stop-process -force -processname sublime_text -ea silentlycontinue
    start-sleep -seconds 2
}

try{
    switch ($command){
        "bootstrap" { Bootstrap }
        "install_package_control" { InstallPackageControl }
        "install_color_scheme_unit" { InstallColorSchemeUnit }
        "install_keypresss" { InstallKeypress }
        "run_tests" { RunTests }
        "run_syntax_tests" { RunTests -syntax_test}
        "run_color_scheme_tests" { RunTests -color_scheme_test}
    }
}catch {
    throw $_
}