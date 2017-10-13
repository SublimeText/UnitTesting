import subprocess
import time
import os
import re
import sys
import json
import optparse
import shutil

# todo: allow different sublime versions

# usage
# cd your_package
# python path/to/run_tests.py PACKAGE

parser = optparse.OptionParser()
parser.add_option('--syntax-test', action="store_true", default=False)
parser.add_option('--color-scheme-test', action="store_true", default=False)
parser.add_option('--coverage', action="store_true", default=False)
options, remainder = parser.parse_args()

syntax_test = options.syntax_test
color_scheme_test = options.color_scheme_test
coverage = options.coverage
package = remainder[0] if len(remainder) > 0 else "UnitTesting"

version = int(subprocess.check_output(["subl", "--version"]).decode('utf8').strip()[-4])

# sublime Packages directory
packages_path = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", ".."))

outdir = os.path.join(packages_path, "User", "UnitTesting", package)
if not os.path.isdir(outdir):
    os.makedirs(outdir)
outfile = os.path.join(outdir, "result")
coveragefile = os.path.join(outdir, "coverage")

# remove output
if os.path.exists(outfile):
    os.unlink(outfile)

if os.path.exists(coveragefile):
    os.unlink(coveragefile)

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
    schedule_info = {
        'package': package,
        'output': outfile,
        'syntax_test': syntax_test,
        'color_scheme_test': color_scheme_test,
        'coverage': coverage
    }
    print('Schedule:')
    for k, v in schedule_info.items():
        print('  %s: %s' % (k, v))

    schedule.append(schedule_info)
with open(jpath, 'w') as f:
    f.write(json.dumps(schedule, ensure_ascii=False, indent=True))

# inject scheduler
schedule_source = os.path.join(packages_path, "UnitTesting", "sbin", "run_scheduler.py")
schedule_target = os.path.join(packages_path, "UnitTesting", "zzz_run_scheduler.py")

if not os.path.exists(schedule_target):
    shutil.copyfile(schedule_source, schedule_target)

# launch sublime text
subprocess.Popen(["subl", "-b"])

# wait until the file has something
print("Wait for Sublime Text response")
startt = time.time()
while (not os.path.exists(outfile) or os.stat(outfile).st_size == 0):
    sys.stdout.write('.')
    sys.stdout.flush()
    if time.time() - startt > 60:
        print("Timeout: Sublime Text is not responding")
        if os.path.exists(schedule_target):
            os.unlink(schedule_target)
        sys.exit(1)
    time.sleep(1)
print("")

# todo: use notification instead of polling
print("Start to read output...")
with open(outfile, 'r') as f:
    while True:
        where = f.tell()
        result = f.read()
        sys.stdout.write(result)
        m = re.search("^(OK|FAILED|ERROR)\\b", result, re.MULTILINE)
        if m:
            success = m.group(0) == "OK"
        # break when OK, Failed or error
        if re.search("^UnitTesting: Done\\.$", result, re.MULTILINE):
            break
        elif not result:
            f.seek(where)
        time.sleep(0.2)

# restore .coverage if it exists, needed for coveralls
if os.path.exists(coveragefile):
    with open(coveragefile, "r") as f:
        txt = f.read()
    txt = txt.replace(os.path.realpath(os.path.join(packages_path, package)), os.getcwd())
    with open(os.path.join(os.getcwd(), ".coverage"), "w") as f:
        f.write(txt)

if os.path.exists(schedule_target):
    os.unlink(schedule_target)

if not success:
    sys.exit(1)
