import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

script_dir = Path("scripts")
log_dir = Path("logs")

exec_bin = {
    ".py": "/usr/bin/python3"
}

if len(sys.argv) > 1:
    script_dir = Path(sys.argv[1])

if len(sys.argv) > 2:
    log_dir = Path(sys.argv[2])

print(f'Watching directory {script_dir}/, logs to {log_dir}/')

log_files = {}

def run():
    files = list(os.listdir(script_dir))
    print(f'Discovered {len(files)} files:')
    for file in files:
        script_file_path = script_dir / file
        log_file_path = log_dir / (file + ".txt")
        print(f'Executing {script_file_path}')
        suffix = script_file_path.suffix

        if suffix not in exec_bin:
            print(f'Failed to execute: No runner specified for {script_file_path}')
            continue

        # Open log file if not already open
        if file not in log_files:
            log_files[file] = open(log_file_path, "a")

        log_file = log_files[file]

        log_file.write(f'Execution at {datetime.now().isoformat()}\n')

        runner = exec_bin[suffix]
        subprocess.Popen([runner, script_file_path], stdout=log_file, stderr=log_file)

run()
