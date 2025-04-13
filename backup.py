#!/usr/bin/env python
"""
@author:Hu Yao
@license: Apache Licence
@file: backup.py
@time: 2019/10/22
@contact: hooyao@gmail.com
@site:
@software: PyCharm
"""

import argparse
import logging
import os
import random
import shutil
import string
from logging.handlers import WatchedFileHandler

from coloredlogs import ColoredFormatter
from github import Github
from urllib3 import Retry

from utils import GitHubRepo
from utils import TqdmHandler

ap = argparse.ArgumentParser()
ap.add_argument("-t", "--token", required=True,
                help="Github token, you can generate it on https://github.com/settings/tokens/new?scopes=admin:public_key,repo&description=BackupTool")
ap.add_argument("-d", "--directory", required=True, help="The complete path of target backup directory")
ap.add_argument("-o", "--orgs", nargs='+', required=True, help="List of organizations, separated by space")
args = vars(ap.parse_args())

ACCESS_TOKEN = args['token']
WORKING_DIR = os.path.expanduser(args['directory'])
LOG_FILE_PATH = os.path.join(WORKING_DIR, 'backup.log')
org_list = args['orgs']
if not os.path.exists(WORKING_DIR):
    os.makedirs(WORKING_DIR)

LOG_FORMAT = '%(name)s - %(levelname)s - %(message)s'
formatter = ColoredFormatter(LOG_FORMAT)
stream = TqdmHandler()
stream.setLevel(logging.INFO)
stream.setFormatter(formatter)

file_handler = WatchedFileHandler(filename=LOG_FILE_PATH)
file_handler.setFormatter(formatter)

logging.basicConfig(level=logging.INFO,
                    format=LOG_FORMAT,
                    handlers=[stream, file_handler])


def make_archive(source, destination):
    base = os.path.basename(destination)
    name, ext = os.path.splitext(base)
    archive_type = ext.split('.')[1]
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))
    shutil.make_archive(name, archive_type, archive_from, archive_to)
    shutil.move('%s.%s' % (name, archive_type), destination)


LOGGER = logging.getLogger('BackupTool')

g = Github(ACCESS_TOKEN, retry=Retry(total=5, status_forcelist=[502]))

# create a temp ssh key

user = g.get_user()

key_path = os.path.expanduser('~/.ssh/id_rsa.pub')
# create a temp ssh key
with open(key_path, 'r') as f:
    ssh_pub_key = f.read()
    letters = string.ascii_lowercase
    key_name = 'temp_' + ''.join(random.choice(letters) for i in range(10)) + '_key'

try:
    temp_ssh_key = user.create_key(key_name, ssh_pub_key)
except Exception as e:
    if e.args[1] and 'key is already in use' == e.args[1]['errors'][0]['message']:
        temp_ssh_key = None
    else:
        raise e

github_org_list = [g.get_organization(org) for org in org_list]

candidates = list()
for org in github_org_list:
    org_name = org.login
    if not os.path.exists(os.path.join(WORKING_DIR, org_name)):
        os.makedirs(os.path.join(WORKING_DIR, org_name))
    for repo in org.get_repos():
        if repo.raw_data['disabled']:
            continue
        repo_short_name = repo.name
        repo_ssh_url = repo.ssh_url
        candidates.append((org_name, repo_short_name, repo_ssh_url))

for candidate in list(candidates):
    org_name = candidate[0]
    repo_short_name = candidate[1]
    repo_ssh_url = candidate[2]
    try:
        if not os.path.exists(os.path.join(WORKING_DIR, org_name, repo_short_name + '.zip')):
            local_repo = GitHubRepo(work_dir=os.path.join(WORKING_DIR, org_name),
                                    dir_name=repo_short_name,
                                    org_name=org_name,
                                    repo_name=repo_short_name)

            local_repo.add_remote(remote_url=repo_ssh_url, remote_name='origin')
            local_repo.fetch('origin')
            if len(local_repo.get_branches('origin')) > 0:
                local_repo.checkout_active_branch()
                make_archive(os.path.join(WORKING_DIR, org_name, repo_short_name),
                             os.path.join(WORKING_DIR, org_name, repo_short_name + '.zip'))
                shutil.rmtree(os.path.join(WORKING_DIR, org_name, repo_short_name))
        candidates.remove(candidate)
    except Exception as e:
        LOGGER.error(f'Failed to backup {candidate[0]}/{candidate[1]}')
        LOGGER.error(e)

# clean temp ssh key
if temp_ssh_key:
    temp_ssh_key.delete()
