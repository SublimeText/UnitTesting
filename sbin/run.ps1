param([string]$PackageToTest="UnitTesting")

# todo(guillermooo): Make this configurable.
$packagesPath = 'c:\st\Data\Packages'
$stPath = 'c:\st\sublime_text.exe'

$outDir = "$packagesPath\User\UnitTesting\tests_output"
$outFile = "$outDir\$PackageToTest"
[void] (new-item -itemtype "f" $outFile -force)

remove-item $outFile -force -erroraction silentlycontinue

# Configure packages to be tested.
$jpath = "$packagesPath\User\UnitTesting\schedule.json"
if (test-path $jpath) {
    $schedule = convertfrom-json "$(get-content $jpath)"
}
else {
    [void] (new-item -itemtype "f" -path $jpath -force)
    # todo(guillermooo): use a UTF8 encoding that doesn't add a preamble.
    # Use ascii to avoid UTF8 preamble issues with python's json module.
    "[]" | out-file -encoding "ascii" -FilePath $jpath -force
    $schedule = convertfrom-json "$(get-content $jpath)"
}

$found = (@($schedule | foreach-object { $_.package }) -eq $PackageToTest).length
if ($found -eq 0) {
    $schedule += @{"package" = $PackageToTest}
}
convertto-json $schedule | out-file -filepath $jpath -encoding "ascii"

# XXX(guillermooo): we cannot start the editor minimized?
start-process $stPath -ArgumentList "--command", "unit_testing_run_scheduler"

$startTime = Get-date
while (-not (test-path $outFile) -or (get-item $outFile).length -eq 0) {
    "."
    if (((get-date) - $startTime).seconds -ge 60) {
        "Timeout: Sublime Text is not responding."
        exit 1
    }
    start-sleep -seconds 1
}

write-output "start to read output"

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
    exit 1
}