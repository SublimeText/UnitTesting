[CmdletBinding()]
Param()

$ErrorActionPreference = 'stop'

$STP = "C:\st\Data\Packages"
New-Item -itemtype directory $STP -force >$null

$STIP = "C:\st\Data\Installed Packages"
New-Item -itemtype directory $STIP -force >$null

$STPU = "C:\st\Data\Packages\User"
New-Item -itemtype directory $STPU -force >$null

$PC_PATH = "$STIP\Package Control.sublime-package"
if (-not (Test-Path $PC_PATH)) {
    Write-Verbose "Downloading Package Control.sublime-package"
    $PC_URL = "https://github.com/wbond/package_control/releases/latest/download/Package.Control.sublime-package"
    (New-Object System.Net.WebClient).DownloadFile($PC_URL, $PC_PATH)
}

$PC_SETTINGS = "C:\st\Data\Packages\User\Package Control.sublime-settings"

if (-not (Test-Path $PC_SETTINGS)) {
    Write-Verbose "Creating Package Control.sublime-settings"
    "{`"auto_upgrade`": false, `"ignore_vcs_packages`": true, `"remove_orphaned`": false, `"submit_usage`": false }" | Out-File -filepath $PC_SETTINGS -encoding utf8
}

$PCH_PATH = "$STP\0_install_package_control_helper"
New-Item -itemtype directory $PCH_PATH -force >$null

$BASE = Split-Path -parent $PSCommandPath
Copy-Item "$BASE\install_package_control_helper.py" "$PCH_PATH\install_package_control_helper.py"
Copy-Item "$BASE\.python-version" "$PCH_PATH\.python-version"

Write-Verbose "Starting Sublime Text."

for ($i=1; ($i -le 3) -and -not (Test-Path "$PCH_PATH\failed") -and -not (Test-Path "$PCH_PATH\success"); $i++) {

    & "C:\st\sublime_text.exe"
    $startTime = Get-Date
    while ((-not (Test-Path "$PCH_PATH\failed")) -and  (-not (Test-Path "$PCH_PATH\success")) -and (((Get-Date) - $startTime).totalseconds -le 60)) {
        Write-Host -nonewline "."
        Start-Sleep -seconds 5
    }

    Stop-Process -force -processname sublime_text -ea silentlycontinue
    Start-Sleep -seconds 4
}
Write-Host

Write-Verbose "Terminated Sublime Text."

if (Test-Path "$PCH_PATH\log") {
    Get-Content -Path "$PCH_PATH\log"
}

if (-not (Test-Path "$PCH_PATH\success")) {
    Remove-Item "$PCH_PATH" -Recurse -Force
    throw "Timeout: Fail to install Package Control."
}

Remove-Item "$PCH_PATH" -Recurse -Force

Write-Verbose "Package Control installed."
