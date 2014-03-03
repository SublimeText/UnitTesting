import subprocess
import tempfile
import time, os
import re
import sys

# cd ~/.config/sublime-text-3/Packages/UnitTesting
# python sbin/run_scheduler.py PACKAGE

# script directory
__dir__ = os.path.dirname(os.path.abspath(__file__))

version = int(subprocess.check_output(["subl","--version"]).decode('utf8').strip()[-4])

# sublime package directory
if sys.platform == "darwin":
    sublime_package = os.path.expanduser("~/Library/Application Support/Sublime Text %d/Packages" % version)
elif "linux" in sys.platform:
    sublime_package = os.path.expanduser("~/.config/sublime-text-%d/Packages" % version)

sys.path.append(os.path.join(sublime_package, "UnitTesting"))
from jsonio import *

package = sys.argv[1] if len(sys.argv)>1 else "UnitTesting"

outdir = os.path.join(sublime_package, "User", "UnitTesting", "tests_output")
outfile = os.path.join(outdir, package)
# remove output
if os.path.exists(outfile): os.unlink(outfile)

# add schedule
jpath = os.path.join(sublime_package, "User", "UnitTesting", "schedule.json")
j = jsonio(jpath)
schedule = j.load()
if not any([s['package']==package for s in schedule]):
    schedule.append({'package': package})
j.save(schedule)

tasks = subprocess.check_output(['ps', 'xw']).decode('utf8')
sublime_is_running = "Sublime" in tasks or "sublime_text" in tasks

if sublime_is_running:
    subprocess.Popen(["subl", "-b", "--command", "unit_testing_run_scheduler"])
else:
    subprocess.Popen(["subl"])

# wait until the file has something
while (not os.path.exists(outfile) or os.stat(outfile).st_size == 0):
    sys.stdout.write('.')
    time.sleep(1)

print("\nstart to read output")

# todo: use notification instead of polling
with open(outfile, 'r') as f:
    while True:
        result = f.read()
        m = re.search("^(OK|FAILED|ERROR)", result, re.MULTILINE)
        # break when OK or Failed
        if m: break
        time.sleep(0.2)
    f.seek(0)
    result = f.read()
print(result)
success = m.group(0)=="OK"

if not success:
    sys.exit(1)
