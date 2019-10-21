#!/usr/bin/env python
"""
@author:Hu Yao
@license: Apache Licence
@file: mover.py
@time: 2019/06/11
@contact: hooyao@gmail.com
@site:
@software: PyCharm
"""

import logging
import os
import shutil

from github import Github
from urllib3 import Retry

import config
from utils import GitHubRepo


def make_archive(source, destination):
    base = os.path.basename(destination)
    name, ext = os.path.splitext(base)
    format = ext.split('.')[1]
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))
    shutil.make_archive(name, format, archive_from, archive_to)
    shutil.move('%s.%s' % (name, format), destination)


WORKING_DIR = os.path.expanduser('~/GithubBackup/')

LOGGER = logging.getLogger('GitHubRepo')

g = Github(config.ACCESS_TOKEN, retry=Retry(total=5, status_forcelist=[502]))

tscn = g.get_organization('TradeshiftCN')
ts = g.get_organization('Tradeshift')

orgs = [tscn, ts]

candidates = list()
for org in orgs:
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
            local_repo.checkout_active_branch()
            make_archive(os.path.join(WORKING_DIR, org_name, repo_short_name),
                         os.path.join(WORKING_DIR, org_name, repo_short_name + '.zip'))
            shutil.rmtree(os.path.join(WORKING_DIR, org_name, repo_short_name))
        candidates.remove(candidate)
    except Exception as e:
        LOGGER.error(f'Failed migrating {candidate[0]}/{candidate[1]}')
        LOGGER.error(e)
