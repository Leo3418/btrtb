#  upload.py: Upload Btrtb snapshots created by Snapper to an SSH host.
#
#  Copyright (C) 2020 Leo <https://github.com/Leo3418>
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

from btrtb.helpers import *

from subprocess import CalledProcessError
import json
import os


def get_snapper_configs() -> list:
    """
    :return: The list of Snapper configuration names.
    :raise CalledProcessError: If any process for the task gets a non-zero exit
        code.
    """
    proc = subprocess.run(
        f'{SNAPPER} --jsonout list-configs',
        capture_output=True,
        shell=True,
        check=True
    )
    return [snapper_config['config']
            for snapper_config in json.loads(proc.stdout.decode())['configs']]


def upload(snapshot_number: int = 0, snapper_config: str = 'root') -> None:
    """
    Upload a snapshot. If the specified snapshot is already on the remote host,
    nothing will be done.

    :param snapshot_number: The number assigned by Snapper for the snapshot to
        be uploaded. Default value is 0. If the value is 0, then this function
        will upload the latest snapshot.
    :param snapper_config: The name of Snapper configuration whose snapshot is
        being uploaded. Default value is 'root'.
    :raise RuntimeError: If no snapshot has been created yet.
    """
    if snapshot_number == 0:
        snapshot = get_latest_snapshot_obj(snapper_config)
        if snapshot is None:
            raise RuntimeError('No snapshot has been created by Snapper yet')
        else:
            snapshot_number = snapshot['number']
    else:
        snapshot = [snapshot
                    for snapshot in get_local_snapshot_list(snapper_config)
                    if snapshot['number'] == snapshot_number][0]
    snapshot_date = snapshot_obj_to_utc_datetime_fn()(snapshot)
    remote_snapshot_dates = \
        [get_datetime_from_remote_snapshot_path(path)
         for path in get_remote_snapshot_list(snapper_config)]
    if snapshot_date in remote_snapshot_dates:
        print(f'Snapshot {snapshot_number} for Snapper configuration '
              f'{snapper_config} created on {snapshot_date} already exists on '
              f'the remote host; skipping upload')
        return
    parent_number = get_latest_common_snapshot_number(
        snapper_config, snapshot_date)
    send_snapshot(snapshot_number, snapper_config, parent_number)


def send_snapshot(
        snapshot_number: int,
        snapper_config: str = 'root',
        parent_number: int = 0,
) -> None:
    """
    Send a local snapshot to the remote host. If a parent snapshot is
    specified, the snapshot will be sent incrementally.

    :param snapshot_number: The snapshot's number assigned by Snapper.
    :param snapper_config: The name of Snapper configuration whose snapshot is
        being sent. Default value is 'root'.
    :param parent_number: The parent snapshot's number. Default value is 0.
        When the value is greater than 0, the snapshot will be sent
        incrementally.
    :raise CalledProcessError: If any process for the task gets a non-zero exit
        code.
    """
    # Send snapshot
    subvolume = get_subvolume_from_snapper_config(snapper_config)
    if parent_number > 0:
        send_cmd = f'{BTRFS_LOCAL} send ' \
                   f'-p {subvolume}/.snapshots/{parent_number}/snapshot ' \
                   f'{subvolume}/.snapshots/{snapshot_number}/snapshot | ' \
                   f'{SSH} {REMOTE_HOST} {BTRFS_REMOTE} receive ' \
                   f'{REMOTE_BACKUP_PATH}/{snapper_config}'
    else:
        send_cmd = f'{BTRFS_LOCAL} send ' \
                   f'{subvolume}/.snapshots/{snapshot_number}/snapshot | ' \
                   f'{SSH} {REMOTE_HOST} {BTRFS_REMOTE} receive ' \
                   f'{REMOTE_BACKUP_PATH}/{snapper_config}'
    print(f'Running command:\n{send_cmd}')
    send_ret = os.system(send_cmd)
    if send_ret != 0:
        raise CalledProcessError(send_ret, send_cmd)

    # Rename remote snapshot
    remote_snapshot_path = get_remote_snapshot_path_from_datetime(
        snapper_config,
        get_datetime_from_local_snapshot(snapshot_number, snapper_config)
    )
    rename_cmd = f'{SSH} {REMOTE_HOST} {MV_REMOTE} ' \
                 f'{REMOTE_BACKUP_PATH}/{snapper_config}/snapshot ' \
                 f'{remote_snapshot_path}'
    print(f'Running command:\n{rename_cmd}')
    rename_ret = os.system(rename_cmd)
    if rename_ret != 0:
        raise CalledProcessError(rename_ret, rename_cmd)


def get_local_snapshot_list(
        snapper_config: str = 'root'
) -> list:
    """
    Get the list of local snapshots. Each element in the list is an object
    generated from JSON output of Snapper when the '--jsonout' option is used.
    To make timestamps consistent when the local timezone changes, all times in
    the output are UTC times.

    :param snapper_config: The name of Snapper configuration whose snapshots
        are concerned. Default value is 'root'.
    :return: The list of remote snapshots for the specified Snapper
        configuration.
    :raise CalledProcessError: If the process for getting the local snapshot
        list gets a non-zero exit code.
    """
    proc = subprocess.run(
        f'{SNAPPER} -c {snapper_config} --jsonout --utc list',
        capture_output=True,
        shell=True,
        check=True
    )
    return json.loads(proc.stdout.decode())[snapper_config]


def get_latest_snapshot_obj(snapper_config: str = 'root'):
    """
    Get the latest Snapper snapshot object created for the specified Snapper
    configuration, generated from the JSON output of Snapper when the
    '--jsonout' option is used.

    :param snapper_config: The name of Snapper configuration whose snapshots
        are concerned. Default value is 'root'.
    :return: The object for the latest Snapper snapshot of the specified
        configuration, or 'None' if no snapshot has been created yet.
    """
    return max(get_local_snapshot_list(snapper_config),
               key=lambda snapshot: snapshot['number'],
               default=None)


def get_latest_common_snapshot_number(
        snapper_config: str = 'root',
        until: datetime = datetime.now(timezone.utc)
) -> int:
    """
    Get the number of the last snapshot created no later than the specified
    time that exists on both the local machine and the remote host.

    :param snapper_config: The name of Snapper configuration whose snapshots
        are concerned. Default value is 'root'.
    :param until: The date and time for limiting search scope of the last
        snapshot. No snapshot that was created after this time will be
        returned. This argument must be offset-aware in order to facilitate
        time comparison. Default value is the current UTC date and time.
    :return: The number of the latest snapshot for the specified Snapper
        configuration until the specified date and time, or 0 if no such
        snapshot can be found.
    :raise TypeError: If the 'until' datetime is offset-naive.
    """
    # Filter snapshots until the specified date and
    # sort in reverse chronological order
    local_snapshots_raw = \
        [snapshot
         for snapshot in get_local_snapshot_list(snapper_config)
         if snapshot['date'] != '']
    local_snapshots = \
        [snapshot
         for snapshot in local_snapshots_raw
         if snapshot_obj_to_utc_datetime_fn()(snapshot) <= until]
    local_snapshots.sort(key=snapshot_obj_to_utc_datetime_fn(), reverse=True)

    remote_dates_raw = [get_datetime_from_remote_snapshot_path(path)
                        for path in get_remote_snapshot_list(snapper_config)]
    remote_dates = [snapshot
                    for snapshot in remote_dates_raw
                    if snapshot <= until]
    remote_dates.sort(reverse=True)

    # Find the last common snapshot
    i_local = 0
    i_remote = 0
    while i_local < len(local_snapshots) and i_remote < len(remote_dates):
        local_snapshot_obj = local_snapshots[i_local]
        local_datetime = snapshot_obj_to_utc_datetime_fn()(local_snapshot_obj)
        remote_datetime = remote_dates[i_remote]
        if local_datetime == remote_datetime:
            return local_snapshot_obj['number']
        # If one date is earlier than the other, move cursor in the other list
        elif local_datetime < remote_datetime:
            i_remote += 1
        else:
            i_local += 1

    # No common snapshot could be found
    return 0


def snapshot_obj_to_utc_datetime_fn():
    """
    :return: A lambda function that takes a Snapper snapshot object
        generated from Snapper's JSON output when the '--jsonout' option is
        used, and converts it to its creation date and time in the UTC
        timezone.
    """
    return lambda snapshot: datetime.fromisoformat(snapshot['date']) \
        .replace(tzinfo=timezone.utc)


def get_subvolume_from_snapper_config(
        snapper_config: str = 'root'
) -> str:
    """
    Convert a Snapper configuration name to its Btrfs subvolume path.

    :param snapper_config: The name of Snapper configuration. Default value is
        'root'.
    :return: The subvolume path for the Snapper configuration.
    :raise CalledProcessError: If the process for getting the subvolume path
        gets a non-zero exit code.
    """
    proc = subprocess.run(
        f'{SNAPPER} -c {snapper_config} --jsonout get-config',
        capture_output=True,
        shell=True,
        check=True
    )
    config_json = json.loads(proc.stdout.decode())
    return config_json['SUBVOLUME']


def get_datetime_from_local_snapshot(
        snapshot_number: int,
        snapper_config: str = 'root'
) -> datetime:
    """
    Retrieve the creation date and time of a local snapshot. To make timestamps
    consistent when the local timezone changes, the time is a UTC time.

    :param snapshot_number: The snapshot's number assigned by Snapper.
    :param snapper_config: The name of Snapper configuration whose snapshot is
        concerned. Default value is 'root'.
    :return: The date and time when the snapshot was created.
    """
    snapshot_list = get_local_snapshot_list(snapper_config)
    snapshot_object = [snapshot
                       for snapshot in snapshot_list
                       if snapshot['number'] == snapshot_number][0]
    return snapshot_obj_to_utc_datetime_fn()(snapshot_object)
