[CmdletBinding()]
Param()

try{
    $STP = "C:\st\Data\Packages"
    New-Item -itemtype directory $STP -force >$null

    $STIP = "C:\st\Data\Installed Packages"
    New-Item -itemtype directory $STIP -force >$null

    $PC_PATH = "$STIP\Package Control.sublime-package"
    $PC_URL = "https://packagecontrol.io/Package Control.sublime-package"
    (New-Object System.Net.WebClient).DownloadFile($PC_URL, $PC_PATH)

    $PCH_PATH = "$STP\0_install_package_control_helper"
    New-Item -itemtype directory $PCH_PATH -force >$null

    $BASE = Split-Path -parent $PSCommandPath
    Copy-Item "$BASE\pc_helper.py" "$PCH_PATH\pc_helper.py"

    for ($i=1; $i -le 2; $i++) {

        & "C:\st\sublime_text.exe"
        $startTime = get-date
        while ((-not (test-path "$PCH_PATH\success")) -and (((get-date) - $startTime).totalseconds -le 60)){
            write-host -nonewline "."
            start-sleep -seconds 5
        }
        stop-process -force -processname sublime_text -ea silentlycontinue
        start-sleep -seconds 2

        if (test-path "$PCH_PATH\success") {
            break
        }
    }

    if (-not (test-path "$PCH_PATH\success")) {
        if (test-path "$PCH_PATH\log") {
            get-content -Path "$PCH_PATH\log"
        }
        remove-item "$PCH_PATH" -Recurse -Force
        throw "Timeout: Fail to install Package Control."
    }

    remove-item "$PCH_PATH" -Recurse -Force
    write-host

    $PC_SETTINGS = "C:\st\Data\Packages\User\Package Control.sublime-settings"

    if (-not (test-path $PC_SETTINGS)) {
        write-verbose "creating Package Control.sublime-settings"
        "{`"ignore_vcs_packages`": true }" | out-file -filepath $PC_SETTINGS -encoding ascii
    }

    write-verbose "Package Control installed."

} catch {
    throw $_
}
