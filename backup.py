#!/usr/bin/env python3

from datetime import datetime
from subprocess import call
from shutil import rmtree
from os import path, makedirs, scandir, remove, rename

path_to_backups = "/mnt/bank/backups/"

dateFormat = "%H-%M-%S--%d-%m-%Y"

if not path.exists(f"{path_to_backups}"):
    makedirs(f"{path_to_backups}")

all_objs = []
with scandir(path_to_backups) as dir_objs:
    for obj in dir_objs:
        all_objs.append(obj)

date_dirs = []
for obj in all_objs:
    if obj.is_dir():
        try:
            datetime.strptime(obj.name, dateFormat)
            date_dirs.append(obj.name)
        except Exception:
            pass

print()
date_dirs.sort(reverse=True)
safe_list = []
safe_list.append("sync.log")
if len(date_dirs) > 1:
    cur_backup = date_dirs[0]
    old_backup = date_dirs[1]
    safe_list.append(cur_backup)
elif len(date_dirs) == 1:
    if date_dirs[0] != "00-00-00--01-01-0001":
        makedirs(path_to_backups + "00-00-00--01-01-0001")
        cur_backup = date_dirs[0]
        safe_list.append(cur_backup)
    old_backup = "00-00-00--01-01-0001"
else:
    makedirs(path_to_backups + "00-00-00--01-01-0001")
    old_backup = "00-00-00--01-01-0001"

safe_list.append(old_backup)


for obj in all_objs:
    if obj.name not in safe_list:
        if obj.is_dir():
            rmtree(path_to_backups + obj.name)
        else:
            remove(path_to_backups + obj.name)


new = datetime.now().strftime(dateFormat)


sync = call(
    "rsync -aAXv / --exclude={'/dev/*','/proc/*','/sys/*','/tmp/*','/run/*','/mnt/*','/media/*','/lost+found'} --delete "
    + {path_to_backups}
    + {old_backup},
    shell=True,
)

if sync == 0:
    header = "SUCCESS"
    message = f"Sync at {new} to {old_backup} successful completed"

    rename(path_to_backups + old_backup, path_to_backups + new)

else:
    header = "ERROR"
    message = f"Sync at {new} to {old_backup} crashed"


with open(f"{path_to_backups}sync.log", "a") as f:
    f.write(datetime.now().strftime("[%X] ") + header + "\n")
    f.write(message + "\n")
