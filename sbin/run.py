import subprocess
import time
import os
import re
import sys
import json
import optparse

# todo: allow different sublime versions

# usage
# cd ~/.config/sublime-text-3/Packages/UnitTesting
# python sbin/run.py PACKAGE

parser = optparse.OptionParser()
parser.add_option('--syntax-test', action="store_true", default=False)
options, remainder = parser.parse_args()

syntax_test = options.syntax_test
package = remainder[0] if len(remainder) > 0 else "UnitTesting"

version = int(subprocess.check_output(["subl", "--version"]).decode('utf8').strip()[-4])

# sublime package directory
if sys.platform == "darwin":
    packages_path = os.path.expanduser(
        "~/Library/Application Support/Sublime Text %d/Packages" % version)
elif "linux" in sys.platform:
    packages_path = os.path.expanduser("~/.config/sublime-text-%d/Packages" % version)

outdir = os.path.join(packages_path, "User", "UnitTesting", "tests_output")
outfile = os.path.join(outdir, package)

# remove output
if os.path.exists(outfile):
    os.unlink(outfile)

# add schedule
jpath_dir = os.path.join(packages_path, "User", "UnitTesting")
jpath = os.path.join(jpath_dir, "schedule.json")
if not os.path.isdir(jpath_dir):
    os.makedirs(jpath_dir)
try:
    with open(jpath, 'r') as f:
        schedule = json.load(f)
except:
    schedule = []
if not any([s['package'] == package for s in schedule]):
    schedule.append({'package': package, 'syntax_test': syntax_test})
with open(jpath, 'w') as f:
    f.write(json.dumps(schedule, ensure_ascii=False, indent=True))

# launch scheduler
tasks = subprocess.check_output(['ps', 'xw']).decode('utf8')
sublime_is_running = "Sublime" in tasks or "sublime_text" in tasks

if sublime_is_running:
    subprocess.Popen(["subl", "-b", "--command", "unit_testing_run_scheduler"])
else:
    subprocess.Popen(["subl"])

# wait until the file has something
startt = time.time()
while (not os.path.exists(outfile) or os.stat(outfile).st_size == 0):
    sys.stdout.write('.')
    sys.stdout.flush()
    if time.time()-startt > 60:
        print("Timeout: Sublime Text is not responding")
        sys.exit(1)
    time.sleep(1)

print("\nstart to read output")

# todo: use notification instead of polling
with open(outfile, 'r') as f:
    while True:
        where = f.tell()
        result = f.read()
        sys.stdout.write(result)
        m = re.search("^(OK|FAILED|ERROR)", result, re.MULTILINE)
        # break when OK, Failed or error
        if m:
            break
        elif not result:
            f.seek(where)
        time.sleep(0.2)
success = m.group(0) == "OK"

if not success:
    sys.exit(1)
