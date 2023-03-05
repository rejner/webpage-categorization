import os
import subprocess
import time

VERBOSE = True

root_dir = os.getcwd()
print(f"Working directory: {root_dir}")
print(f"Starting webcat_ui ({root_dir}/client/webcat_ui)...")

# create logs directory if it doesn't exist
if not os.path.isdir(f"{root_dir}/logs"):
    os.mkdir(f"{root_dir}/logs")

# create logs/webcat_ui.log if it doesn't exist
if not os.path.isfile(f"{root_dir}/logs/webcat_ui.log"):
    open(f"{root_dir}/logs/webcat_ui.log", 'w').close()

# create logs/webcat_ui.pid if it doesn't exist
if not os.path.isfile(f"{root_dir}/logs/webcat_ui.pid"):
    open(f"{root_dir}/logs/webcat_ui.pid", 'w').close()

# create logs/webcat_api.log if it doesn't exist
if not os.path.isfile(f"{root_dir}/logs/webcat_api.log"):
    open(f"{root_dir}/logs/webcat_api.log", 'w').close()

# create logs/webcat_api.pid if it doesn't exist
if not os.path.isfile(f"{root_dir}/logs/webcat_api.pid"):
    open(f"{root_dir}/logs/webcat_api.pid", 'w').close()

# run npm start in client/webcat_ui directory, background process, log to logs/webcat_ui.log
os.chdir(f"{root_dir}/client/webcat_ui")
process = subprocess.Popen(["npm", "start"], stdout=open(f"{root_dir}/logs/webcat_ui.log", "a"), stderr=subprocess.STDOUT)
# save the PID of the last background process
with open(f"{root_dir}/logs/webcat_ui.pid", "w") as f:
    f.write(str(process.pid))

# start flask server in webcat/api
print(f"Starting webcat_api ({root_dir}/webcat/run_api.py)...")
os.chdir(f"{root_dir}/webcat")
process = subprocess.Popen(["python3", "run_api.py"], stdout=open(f"{root_dir}/logs/webcat_api.log", "a"), stderr=subprocess.STDOUT)

# save the PID of the last background process
with open(f"{root_dir}/logs/webcat_api.pid", "w") as f:
    f.write(str(process.pid))


print("Running... (press Ctrl+C to stop)")

# wait until interrupted, then kill all background processes
try:
    while True:
        # sleep for 1 second
        time.sleep(10)
        
except KeyboardInterrupt:
    print("Stopping webcat_ui...")
    with open(f"{root_dir}/logs/webcat_ui.pid", "r") as f:
        pid = int(f.read())
    os.kill(pid, 9)
    print("Stopping webcat_api...")
    with open(f"{root_dir}/logs/webcat_api.pid", "r") as f:
        pid = int(f.read())
    os.kill(pid, 9)
