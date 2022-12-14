import os
import sys
import asyncio
from datetime import datetime
from pathlib import Path

script_dir = Path("scripts")
log_dir = Path("logs")

ignore = ["tools.py", "solve_failures"]

exec_bin = {
    ".py": "/usr/bin/python3"
}

if len(sys.argv) > 1:
    script_dir = Path(sys.argv[1])

if len(sys.argv) > 2:
    log_dir = Path(sys.argv[2])

print(f'Watching directory {script_dir}/, logs to {log_dir}/')

log_files = {}

async def run(args, log_file):
    print(f'[{args[1]}] Execution at {datetime.now().isoformat()}')
    log_file.write(f'Execution at {datetime.now().isoformat()}\n')
    log_file.flush()

    proc = await asyncio.create_subprocess_exec(*args, stdout=log_file, stderr=log_file)
    retcode = await proc.wait()

    if retcode != 0:
        print(f'[{args[1]}] Done with \u001b[31mnon zero retcode={retcode}\033[0m at {datetime.now().isoformat()}')
    else:
        print(f'[{args[1]}] Done with retcode={retcode} at {datetime.now().isoformat()}')
    log_file.write(f'Done at {datetime.now().isoformat()}\n')
    log_file.flush()

async def main():
    while True:
        files = list(os.listdir(script_dir))
        print(f'Discovered {len(files)} files:')
        tasks = []
        for file in files:
            if file in ignore:
                continue
            script_file_path = script_dir / file
            log_file_path = log_dir / (file + ".txt")
            # print(f'Parsing {script_file_path}')
            suffix = script_file_path.suffix

            if suffix not in exec_bin:
                print(f'\u001b[31mFailed to execute: No runner specified for {script_file_path}\033[0m')
                continue

            # Open log file if not already open
            if file not in log_files:
                log_files[file] = open(log_file_path, "a")

            log_file = log_files[file]

            runner = exec_bin[suffix]
            tasks.append((script_file_path, asyncio.create_task(run([runner, script_file_path], log_file))))
        await asyncio.sleep(5)
        for file, task in tasks:
            if not task.done():
                print(f'\u001b[31m{file} did not finish in specified interval!\033[0m')
                task.cancel()

        print()

if __name__ == "__main__":
    asyncio.run(main())
