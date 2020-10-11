# Installation Guide

A better and automated mechanism to install `btrtb` has been planned, but
before it is added, the files for this program must be installed manually.

## Requirements

### File System

Although Snapper can work on non-Btrfs volumes, and `btrtb` is designed to work
with Snapper, `btrtb` can only process snapshots for Btrfs subvolumes.

### Dependencies

You need to have the following programs installed on the machine whose data is
being backed up (*local machine*):

- systemd
- The `btrfs` command, part of the `btrfs-progs` package
- OpenSSH client, which is the `ssh` command
- Python 3
- Snapper

The SSH host where the backups are stored (*remote machine*) needs to have the
following programs:

- `ls` and `mv`
- An SSH server
- The `btrfs` command

## Files Required to Run This Program

- `btrtb/*.py`: Python files for the program itself
- `etc/systemd/*`: systemd unit files which automate runs of this program
- `libexec/btrtb-upload`: The entry point to this program

## Installation Instructions

`btrtb` only needs to be installed on the *local machine*.  No files for this
program need to be installed on the remote machine.  Thus, the following steps
should be performed on the local machine.

1. Find the path to the `site-packages` directory for Python on the backup
   source.  Usually, it is `/usr/lib/python3.x/site-packages`, where `x` is the
   minor release version of Python 3 installed on the backup source.
   Alternatively, you may be able to use
   `/usr/local/lib/python3.x/site-packages` as well.  For more information
   about this directory, please refer to [this page][site-packages].

2. Copy the `btrtb` directory, along with its contents (`-r` flag if using
   `cp`), to the `site-packages` directory.

3. Copy every file under `etc/systemd` to `/usr/lib/systemd/system` *or*
   `/usr/local/lib/systemd/system`.

4. Copy `libexec/btrtb-upload` to `/usr/local/libexec/btrtb/btrtb-upload`.
   Note that for this file, it must be installed under `/usr/local/libexec`.
   If you want to use `/usr/libexec` instead, you have to modify the systemd
   unit files so they point to this path.

5. Make `btrtb-upload` executable:
   ```console
   # chmod +x /usr/local/libexec/btrtb/btrtb-upload
   ```

A correct installation where every file for this program is in the `/usr/local`
hierarchy looks like this:

```
/usr/local
├── lib
│   ├── python3.x
│   │   └── site-packages
│   │       └── btrtb
│   │           ├── config.py
│   │           ├── helpers.py
│   │           └── upload.py
│   └── systemd
│       └── system
│           ├── btrtb-upload.service
│           └── btrtb-upload.timer
└── libexec
    └── btrtb
        └── btrtb-upload
```

[site-packages]: https://docs.python.org/3/library/site.html

---

Copyright (C) 2020 Leo <https://github.com/Leo3418>

Permission is granted to copy, distribute and/or modify this document
under the terms of the GNU Free Documentation License, Version 1.3
or any later version published by the Free Software Foundation;
with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
A copy of the license is included in the file `doc/COPYING.md` and is
available at <https://www.gnu.org/licenses/fdl-1.3.html>.
