# Btrfs Remote Timeline Backup

**Bt**rfs **R**emote **T**imeline **B**ackup (`btrtb`) is a tool which
automates transfers of [Btrfs][btrfs] snapshots created by [Snapper][snapper]
over Secure Shell (SSH).

[btrfs]: https://btrfs.wiki.kernel.org/index.php/Main_Page
[snapper]: http://snapper.io/

## Motivation

Btrfs is a file system available on Linux.  It provides the capability to take
snapshots of the file system, which facilitates backup of system and user data.
Snapper is a tool from openSUSE that automates Btrfs snapshot creations.

The snapshots created by Snapper are saved on the same disk on which the
original data is stored.  If the disk fails, the snapshots will be gone, and
data cannot be recovered.  Thus, a reliable backup plan that uses Snapper
should involve sending the snapshots to another disk, or more preferably,
another host.

Snapper itself does not offer the functionality to send snapshots it creates to
somewhere else, so users need to either export them manually or rely on other
tools and programs.  Manual backup plans work, but they are not scalable and
may become an ordeal.  So, the backup process should be automated as much as
possible.

`btrtb` is a simple program designed for people who want to automate snapshot
exports to an SSH host.  SSH allows you to store your backups anywhere, from a
home backup server to an off-site location for better data protection; using
SSH to store backups to an on-line local disk is possible as well if you are
willing to use `ssh localhost`.  To reduce transfer size, `btrtb` exploits
Btrfs' [incremental snapshot transfer][inc_bak] capability.  When `btrtb` sends
a new snapshot, it searches for the latest parent snapshot that is on both the
local machine and the backup server, to minimize not only the amount of data
transferred, but also backup size on the backup server.

[inc_bak]: https://btrfs.wiki.kernel.org/index.php/Incremental_Backup

## Documentation

More information about `btrtb`, including installation instructions, is
available in files under the `doc` directory.

## Project Status

This program had been originally intended to be some ad hoc backup scripts for
my personal use only.  But after judicious design with portability in mind, I
found that other people could make use of it by changing only a few options of
the program as well, hence I published it.

Initially modeled as merely a simple script, many things need to be done for
`btrtb` to turn it into a generalized backup program.  However, because this
program can be useful, I have decided to publish it early and improve it
gradually.  In the near future, I am going to add a few more features to this
program and improve its usability.

## License

`btrtb` is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

`btrtb` is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the file `COPYING.md` for more details.
