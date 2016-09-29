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

    & "C:\st\sublime_text.exe"

    $startTime = get-date
    while (-not (test-path "$PCH_PATH\success")) {
        write-host -nonewline "."
        if (((get-date) - $startTime).totalseconds -ge 60) {
            write-host
            stop-process -force -processname sublime_text
            start-sleep -seconds 2
            Remove-Item "$PCH_PATH" -Recurse -Force
            throw "Timeout: Fail to install Package Control."
        }
        start-sleep -seconds 5
    }

    start-sleep -seconds 2
    write-host
    Remove-Item "$PCH_PATH" -Recurse -Force
    write-verbose "Package Control installed."

}catch {
    throw $_
}
