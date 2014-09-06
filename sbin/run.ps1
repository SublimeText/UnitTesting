[CmdletBinding()]
param([string]$PackageToTest="UnitTesting")

# UTF8 encoding without preamble (default in .NET is with preamble).
new-variable -name 'UTF8Encoding' -option CONSTANT -scope 'script' `
             -value (new-object System.Text.UTF8Encoding -argumentlist $false)

# todo(guillermooo): Make this configurable.
$packagesPath = 'c:\st\Data\Packages'
$stPath = 'c:\st\sublime_text.exe'

$outDir = "$packagesPath\User\UnitTesting\tests_output"
$outFile = "$outDir\$PackageToTest"
[void] (new-item -itemtype file $outFile -force)

remove-item $outFile -force -erroraction silentlycontinue

# Configure packages to be tested.
$jpath = "$packagesPath\User\UnitTesting\schedule.json"
if (test-path $jpath) {
    $schedule = convertfrom-json "$(get-content $jpath)"
}
else {
    [void] (new-item -itemtype file -path $jpath -force)
    # Only way of using encoding object.
    [System.IO.File]::WriteAllText($jpath, "[]", $UTF8Encoding)
    $schedule = convertfrom-json "$(get-content $jpath)"
}

$found = (@($schedule | foreach-object { $_.package }) -eq $PackageToTest).length
if ($found -eq 0) {
    $schedule += @{"package" = $PackageToTest}
}

[System.IO.File]::WriteAllText(
    $jpath, (convertto-json $schedule), $UTF8Encoding)

# launch sublime
$sublimeIsRunning = get-process 'sublime_text' -erroraction silentlycontinue

# XXX(guillermooo): we cannot start the editor minimized?
if($sublimeIsRunning -eq $null) {
    start-process $stPath
} else {
    start-process $stPath -argumentlist '--command', "unit_testing_run_scheduler"
}

$startTime = get-date
while (-not (test-path $outFile) -or (get-item $outFile).length -eq 0) {
    write-host -nonewline "."
    if (((get-date) - $startTime).totalseconds -ge 60) {
        throw "Timeout: Sublime Text is not responding."
    }
    start-sleep -seconds 1
}
write-host

write-verbose "start to read output"

$copy = "$outfile.copy"
$read = 0
while ($true) {
    # XXX(guillermooo): We can't open a file already opened by another
    # process. By copying the file first, we can work around this. (But if
    # we can copy it we should be able to read it too?).
    # Powershell's `get-content $path -tail 1 -wait` is in fact able to read
    # from an already opened file. Perhaps it uses the same workaround as we
    # do here?
    copy-item $outfile $copy -force

    $lines = (get-content $copy)
    write-output $lines[$read..$lines.length]
    $read += ($lines.length - $read)

    $m = $lines[-1] -match "^(OK|FAILED|ERROR)"
    if ($m) { break }
    start-sleep -milliseconds 200
}

if ($matches[1] -ne "OK") {
    throw "FAILED or ERROR"
}
