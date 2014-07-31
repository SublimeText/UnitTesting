param([string]$PackageToTest='UnitTesting')

$script:thisDir = split-path $MyInvocation.MyCommand.Path -parent

version = 3

$SublimePackage = 'path/to/sublime/data'

$package = $PackageToTest

$outDir = "$SublimePackage\User\UnitTesting\tests_output"
$outFile = "$outDir\$package"

remove-item $outFile -force -erroraction silentlycontinue

$jpath = "$SublimePackage\User\UnitTesting\schedule.json"
$jdata = convertfrom-json $jpath

# ===
# if not any([s['package']==package for s in schedule]):
#     schedule.append({'package': package})
# j.save(schedule)
# ===

$IsSTRunning = (get-process "sublime_text") -ne $null

if ($IsSTRunning) {
    start-process "sublime_text" -ArgumentList "--command", "unit_testing_run_scheduler"
}
else {
    start-process "sublime_text"
}

$startTime = Get-date
while (-not (test-path $outFile) -or (get-item $outFile).length -eq 0) {
    "."
    if (((get-date) - $startTime).seconds -ge 60) {
        "Timeout: Sublime Text is not responding."
        exit 1
    }
    start-sleep -seconds 1
}

"start to read output"


$lines = @()
$f = [IO.File]::OpenText($outFile)
while ($true) {
    $line = $f.ReadLine()
    $lines.Add($line)
    $m = $line -match "^(OK|FAILED|ERROR)"
    if (m) { break }
    start-sleep -milliseconds 200
}
$f.Close()

[String]::Join("`n", $lines)

if ($matches[1] -ne "OK") {
    exit 1
}