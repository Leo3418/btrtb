#  config.py: Read and write configuration files of btrtb.
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

import json
import os

CONFIG_PATH = '/etc/btrtb'

PROGRAM_CONFIG_FILE = 'config.json'

DEFAULT_PROGRAM_CONFIG = {
    'remote-host': 'example.com',
    'remote-backup-path': '/mnt/backups',
    'ssh-command': 'ssh -o "StrictHostKeyChecking accept-new"',
    'snapper-command': 'snapper',
    'btrfs-command-local': 'btrfs',
    'btrfs-command-remote': 'sudo btrfs',
    'ls-command-remote': 'ls',
    'mv-command-remote': 'sudo mv'
}

__program_config_file_abs_path = \
    '{}/{}'.format(CONFIG_PATH, PROGRAM_CONFIG_FILE)

if not os.path.exists(__program_config_file_abs_path):
    print(f'Configuration file is being created at '
          f'{__program_config_file_abs_path}. Please edit it to set SSH host, '
          f'backup path and other options, then rerun this command.')
    if not os.path.isdir(CONFIG_PATH):
        os.mkdir(CONFIG_PATH)
    json.dump(DEFAULT_PROGRAM_CONFIG,
              open(__program_config_file_abs_path, 'w'),
              indent=4)
    exit(0)

__program_config = json.load(open(__program_config_file_abs_path, 'r'))

REMOTE_HOST = __program_config['remote-host']
REMOTE_BACKUP_PATH = __program_config['remote-backup-path']
SSH = __program_config['ssh-command']
SNAPPER = __program_config['snapper-command']
BTRFS_LOCAL = __program_config['btrfs-command-local']
BTRFS_REMOTE = __program_config['btrfs-command-remote']
LS_REMOTE = __program_config['ls-command-remote']
MV_REMOTE = __program_config['mv-command-remote']
