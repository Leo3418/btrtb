#  helpers.py: Helper functions that can be reused in many parts of btrtb.
#
#  Copyright (C) 2020-2021 Leo <https://github.com/Leo3418>
#
#  This file is part of btrtb, a tool for automating transfers of Btrfs
#  snapshots via SSH.
#
#  btrtb is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  btrtb is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with btrtb.  If not, see <https://www.gnu.org/licenses/>.

from btrtb.config import *

from datetime import datetime, timezone
import subprocess

"""The format of timestamps added to remote snapshots' paths."""
TIMESTAMP_FORMAT = '%Y-%m-%d_%H:%M:%S'


def get_remote_snapshot_path_from_datetime(
        subvol_config: str,
        dt: datetime = datetime.now(timezone.utc)
) -> str:
    """
    Return a snapshot path that contains a timestamp, which can be used on the
    remote host.

    :param subvol_config: The name of subvolume configuration whose snapshot is
        concerned.
    :param dt: The date and time, used for the snapshot's timestamp. Default
        value is the current UTC date and time, rather than the local time, so
        timestamps will still be consistent when the local timezone changes.
    :return: A string for the absolute path of the remote snapshot, for the
        specified subvolume configuration, at the specified date and time.
    :raise ValueError: If the specified subvolume configuration does not exist.
    """
    config_json = get_subvol_config(subvol_config)
    return '{}/{}/{}'.format(
        config_json['remote-backup-path'],
        subvol,
        dt.strftime(TIMESTAMP_FORMAT)
    )


def get_datetime_from_remote_snapshot_path(path: str) -> datetime:
    """
    Extract the date and time from a snapshot path possibly given by the
    'get_remote_snapshot_path_from_datetime' function.

    :param path: Path of the remote snapshot on the remote host. The path need
        not be absolute; as long as it contains the timestamp in the same
        format that 'get_remote_snapshot_path_from_datetime' uses, this
        function will attempt to extract the date and time.
    :return: The date and time indicated by the specified path.
    :raise ValueError: If the specified path does not have a timestamp in the
        legal format.
    """
    timestamp = path.rpartition('/')[2]
    # If the separator '/' was not found, 'timestamp' will be the original
    # string itself, and we will proceed while assuming it is a legal timestamp
    return datetime.strptime(timestamp, TIMESTAMP_FORMAT)\
        .replace(tzinfo=timezone.utc)


def get_remote_snapshot_list(subvol_config: str) -> list:
    """
    Get the list of snapshots on the remote host.

    :param subvol_config: The name of subvolume configuration whose snapshot is
        concerned.
    :return: The list of remote snapshots for the specified subvolume
        configuration. Each element in the list can be passed in as the
        argument to the 'get_datetime_from_remote_snapshot_path' for getting
        its associated date and time.
    :raise ValueError: If the specified subvolume configuration does not exist.
    :raise CalledProcessError: If the process for getting the remote snapshot
        list gets a non-zero exit code.
    """
    config_json = get_subvol_config(subvol_config)
    ssh = config_json['ssh-command']
    remote_host = config_json['remote-host']
    ls = config_json['ls-command-remote']
    remote_backup_path = config_json['remote-backup-path']
    proc = subprocess.run(
        f'{ssh} {remote_host} {ls} -1 {remote_backup_path}/{subvol_config}',
        capture_output=True,
        shell=True,
        check=True
    )
    # Get file listing from stdout, split into a list, remove empty strings,
    # and convert from byte sequence to string
    return [file_name.decode()
            for file_name in proc.stdout.split(b'\n')
            if len(file_name) != 0]
