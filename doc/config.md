# Configuration Guide

To configure `btrtb` so it automatically sends your local Btrfs snapshots to
the remote backup destination, you need to do the following:

1. [Edit this program's configuration file](#configuration-file)
2. [Configure the remote machine to receive snapshots
   properly](#the-remote-machine)
3. [Enable systemd units for this program](#systemd-units)

## Configuration File

The configuration file for `btrtb` is located at `/etc/btrtb/config.json`.  It
will be generated when the systemd unit `btrtb-upload.service` is being run for
the first time.  You can manually run the service with the following command:

```console
# systemctl start btrtb-upload.service
```

If the configuration file does not exist yet, running this command will only
create the file.  Otherwise, it will upload the latest snapshot to the SSH host
set in the configuration.

The default configuration file uses a dummy SSH host, so you must edit it with
the actual host name of your backup server after `btrtb` creates it.

```json
{
    "remote-host": "example.com",
    "remote-backup-path": "/mnt/backups",
    "ssh-command": "ssh -o \"StrictHostKeyChecking accept-new\"",
    "snapper-command": "snapper",
    "btrfs-command-local": "btrfs",
    "btrfs-command-remote": "sudo btrfs",
    "ls-command-remote": "ls",
    "mv-command-remote": "sudo mv"
}
```

Most users should change the `remote-host`, `remote-backup-path`, and
`ssh-command` options depending on their own situations.  For the remaining
ones, only a few users are expected to find the need to adjust them.

Details for every option are listed below.

### `remote-host`

The host name of the backup server.  The value of this option will be supplied
to the `ssh` command as the `destination` argument, which allows you to specify
the user name and port number for the backup server.  Examples of this option's
value include:

- `example.com`
- `192.0.2.42`
- `2001:db8:beca:57a9::556`
- `user@example.com`
- `user@192.0.2.42`
- `user@2001:db8:beca:57a9::556`
- `ssh://example.com:22`
- `ssh://192.0.2.42:22`

Alternatively, the user name and port number can also be specified in the value
of [`ssh-command` option](#ssh-command).  If you want to connect to a
non-default port (port other than 22) of a host using its IPv6 address, you
might have to specify the port number in that option's value rather than after
the address.

### `remote-backup-path`

The path on the remote machine where you want to store backed-up snapshots at.
The path must be on a Btrfs file system so it can contain Btrfs snapshots.

### `ssh-command`

Alias for the `ssh` command.  You can use this to specify options for the `ssh`
program, like identity file (`-i`), user name (`-l`), port (`-p`), and/or other
OpenSSH options (`-o`).

In the default value for this option, the `StrictHostKeyChecking` option for
OpenSSH is set to `accept-new`, so any new host key will be unconditionally
accepted, but any offending key will be rejected.  This prevents `btrtb` from
being interrupted by OpenSSH's message about a new host key while ensuring
security in the event where verification of existing host key fails.

### `snapper-command`

Alias for the `snapper` command.

### `btrfs-command-local`

Alias for the `btrfs` command on the *local machine*.

### `btrfs-command-remote`

Alias for the `btrfs` command on the *remote machine*.  The command will be
invoked when the remote machine accepts and receives a snapshot.  The default
value prepends `sudo` to `btrfs` to run `btrfs` with superuser privilege,
because it is required for receiving Btrfs snapshots.

### `ls-command-remote`

Alias for the `ls` command on the *remote machine*.  It will be invoked when
`btrtb` retrieves the list of snapshot backups on the remote machine.
Typically, this can be done without superuser privilege.

### `mv-command-remote`

Alias for the `mv` command on the *remote machine*.  It will be invoked after
the remote machine receives a snapshot, for renaming it to a more meaningful
one includes its timestamp.  This may also require superuser privilege, thus
`sudo` is added to the default value as well.

## The Remote Machine

In addition to the software dependencies outlined in the installation guide,
the remote machine must meet the following requirements to receive backup sent
by `btrtb` properly:

- Has a Btrfs file system mounted for storing snapshots
- Does not require interactive authentication for a command that requires
  superuser privilege

A plenitude of guides about creating a Btrfs file system and mounting it are
available on the Internet.

For systems on which `sudo` can be used to acquire superuser privilege, the
typical default behavior of `sudo` when authentication is required is that it
asks you to enter your password from terminal, which is not possible when it is
invoked by `btrtb` over SSH.  One possible workaround is to skip password
authentication, by performing the steps listed [here][sudo-nopasswd].

[sudo-nopasswd]: https://leo3418.github.io/2020/07/24/fedora-raspi-cluster.html#remove-password-prompt-of-sudo

## systemd Units

`btrtb` comes with systemd services for sending snapshots.  Each service has an
associated timer that runs it periodically, which in turns automates the
snapshot transfer operations.

The timers must be started to let `btrtb` run of its own accord.  Use this
command to start the timer for uploading snapshots:
```console
# systemctl start btrtb-upload.timer
```

To start the timer automatically after the system boots, you should enable it:
```console
# systemctl enable btrtb-upload.timer
```

The following commands allow you to view the services' status:
```console
$ systemctl status btrtb-upload.timer
$ systemctl status btrtb-upload.service
```

Viewing a timer's status let you know at what time will it trigger the next run
of its associated service, whereas viewing a service's status allows you to
find information about its last run, including the output of `btrtb`.

You may also edit a timer unit file to customize how its corresponding service
is scheduled to run by following instructions given at [here][edit-timer].

[edit-timer]: https://wiki.archlinux.org/index.php/Systemd/Timers#Examples

---

Copyright (C) 2020 Leo <https://github.com/Leo3418>

Permission is granted to copy, distribute and/or modify this document
under the terms of the GNU Free Documentation License, Version 1.3
or any later version published by the Free Software Foundation;
with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
A copy of the license is included in the file `doc/COPYING.md` and is
available at <https://www.gnu.org/licenses/fdl-1.3.html>.
