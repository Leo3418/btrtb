#  config.py: Read and write configuration files of btrtb.
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

import json
import os

# Configuration file paths

CONFIG_PATH = '/etc/btrtb'
PROGRAM_CONFIG_FILE = 'global.json'
SUBVOL_CONFIG_FILE_NAME = 'config.json'

# Default configurations

DEFAULT_PROGRAM_CONFIG = {
    'snapper-command': 'snapper',
    'btrfs-command-local': 'btrfs'
}
DEFAULT_SUBVOL_CONFIG = {
    'remote-host': 'example.com',
    'remote-backup-path': '/mnt/backups',
    'ssh-command': 'ssh -o "StrictHostKeyChecking accept-new"',
    'btrfs-command-remote': 'sudo btrfs',
    'ls-command-remote': 'ls',
    'mv-command-remote': 'sudo mv'
}

# Create the program configuration file on the first run or after the old
# configuration file has been deleted
__program_config_file_abs_path = f'{CONFIG_PATH}/{PROGRAM_CONFIG_FILE}'
if not os.path.exists(__program_config_file_abs_path):
    if not os.path.isdir(CONFIG_PATH):
        os.mkdir(CONFIG_PATH)
    json.dump(DEFAULT_PROGRAM_CONFIG,
              open(__program_config_file_abs_path, 'w'),
              indent=4)

# Read program configuration
__program_config = json.load(open(__program_config_file_abs_path, 'r'))

# Program configuration values

SNAPPER = __program_config['snapper-command']
BTRFS_LOCAL = __program_config['btrfs-command-local']
SUBVOLS = (subvol for subvol in os.listdir(CONFIG_PATH) if
           os.path.isfile(f'{CONFIG_PATH}/{subvol}/{SUBVOL_CONFIG_FILE_NAME}'))


def create_subvol_config(subvol_config: str) -> None:
    """
    Create a subvolume configuration.

    :param subvol_config: The name of the subvolume configuration.
    :raise ValueError: If the specified subvolume configuration already exists.
    :raise FileExistsError: If the directory that will hold the configuration
        already exists as a file.
    """
    if subvol_config in SUBVOLS:
        raise ValueError(f"config already exists: {subvol_config}")
    subvol_config_dir = f'{CONFIG_PATH}/{subvol_config}'
    if os.path.isfile(subvol_config_dir):
        raise FileExistsError(f"cannot create new directory at "
                              f"{subvol_config_dir} because the path is an "
                              f"existing file; please remove the file and try "
                              f"again")
    if not os.path.isdir(subvol_config_dir):
        os.mkdir(subvol_config_dir)
    json.dump(DEFAULT_SUBVOL_CONFIG,
              open(f'{subvol_config_dir}/{SUBVOL_CONFIG_FILE_NAME}', 'w'),
              indent=4)


def get_subvol_config(subvol_config: str) -> json:
    """
    Return a JSON object for the specified subvolume configuration.

    :param subvol_config: The name of the subvolume configuration.
    :return: The JSON object for the specified subvolume's configuration if the
        subvolume is valid.
    :raise ValueError: If the specified subvolume configuration does not exist.
    """
    if subvol_config not in SUBVOLS:
        raise ValueError(f"unknown config: {subvol_config}")
    subvol_config_file = \
        f'{CONFIG_PATH}/{subvol_config}/{SUBVOL_CONFIG_FILE_NAME}'
    return json.load(open(subvol_config_file, 'r'))


def delete_subvol_config(subvol_config: str) -> None:
    """
    Delete a subvolume configuration.  If the directory holding the
    configuration will be empty after the configuration file is removed, the
    directory will be removed as well; otherwise, the directory will be kept in
    the file system.

    :param subvol_config: The name of the subvolume configuration.
    :raise ValueError: If the specified subvolume configuration does not exist.
    """
    if subvol_config not in SUBVOLS:
        raise ValueError(f"unknown config: {subvol_config}")
    subvol_config_dir = f'{CONFIG_PATH}/{subvol_config}'
    os.remove(f'{subvol_config_dir}/{SUBVOL_CONFIG_FILE_NAME}')
    if len(os.listdir(subvol_config_dir)) == 0:
        os.rmdir(subvol_config_dir)
