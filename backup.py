#!/usr/bin/env python3

from datetime import datetime
from subprocess import call
from argparse import ArgumentParser
from shutil import rmtree
from sys import argv
from os import path, makedirs, scandir, remove, rename


parser = ArgumentParser()
required = parser.add_argument_group("required arguments")
required.add_argument("-hn", help="machine hostname", required=True)
required.add_argument("-p", help="path to backup folder", required=True)
optional = parser.add_argument_group("optional arguments")
optional.add_argument("-n", help="number of backups", type=int, default=2)
# optional.add_argument("-s", help="ssh port")

args = parser.parse_args(argv[1:])

hostname = args.hn
if args.p[-1] == "/":
    path_to_backups = args.p + hostname + "/"
else:
    path_to_backups = args.p + "/" + hostname + "/"
if args.n > 0:
    backup_num = args.n
else:
    print("Error - wrong number of backups!")
    exit()
# if args.s is not None:
#     ssh_port = f" -e 'ssh -p {args.s}'"
# else:
#     ssh_port = None

dateFormat = "%H-%M-%S--%d-%m-%Y"


def write_log(header, message):
    with open(path_to_backups + "sync.log", "a") as f:
        f.write(datetime.now().strftime("[%X] ") + header + "\n")
        f.write(message + "\n")


if not path.exists(path_to_backups):
    makedirs(path_to_backups)

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

date_dirs.sort(reverse=True)
safe_list = []
safe_list.append("sync.log")

if len(date_dirs) < backup_num:
    if not date_dirs or date_dirs[-1] != "00-00-00--01-01-0001":
        makedirs(path_to_backups + "00-00-00--01-01-0001")
        safe_list.append("00-00-00--01-01-0001")
    old_backup = "00-00-00--01-01-0001"
else:
    old_backup = date_dirs[backup_num - 1]

safe_list.extend(date_dirs[:backup_num])

for obj in all_objs:
    if obj.name not in safe_list:
        if obj.is_dir():
            rmtree(path_to_backups + obj.name)
        else:
            remove(path_to_backups + obj.name)

new = datetime.now().strftime(dateFormat)

write_log("SUCCESS", f"Sync started at {new}\n")

sync = call(
    f"rsync -avAXHP --delete --delete-excluded --exclude='/dev/*' --exclude=/proc/*' --exclude='/sys/*' --exclude='/tmp/*' --exclude='/run/*' --exclude='/mnt/*' --exclude='/media/*' --exclude='/lost+found' --exclude='/var/lib/pacman/sync/*' --exclude='/var/cache/apt/archives/*' --exclude='/var/cache/*' --exclude='/var/tmp/*' --exclude='/boot/lost+found' --exclude='/home/lost+found' --exclude='/home/*/.thumbnails/*' --exclude='/home/*/.cache/google-chrome/*' --exclude='/home/*/.local/share/Trash/*' --exclude='/home/*/.gvfs/*' --exclude='/home/share/*' /* {path_to_backups}{old_backup}",
    shell=True,
)

if sync == 0:
    header = "SUCCESS"
    message = f"Sync at {new} to {old_backup} successful completed\n"

    rename(path_to_backups + old_backup, path_to_backups + new)

else:
    header = "ERROR"
    message = f"Sync at {new} to {old_backup} crashed\n"

write_log(header, message)
