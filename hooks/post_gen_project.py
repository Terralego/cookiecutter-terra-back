#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from distutils.dir_util import remove_tree
import os
import subprocess

# Workaround cookiecutter no support of symlinks
TEMPLATE = 'cookiecutter-terra-back'
SYMLINKS = {
    ".ansible/scripts/setup_vaults.sh": "cops_wrapper.sh",  #noqa
    ".ansible/scripts/setup_corpusops.sh": "cops_wrapper.sh",  #noqa
    ".ansible/scripts/test.sh": "cops_wrapper.sh",  #noqa
    ".ansible/scripts/setup_core_variables.sh": "cops_wrapper.sh",  #noqa
    ".ansible/scripts/call_roles.sh": "cops_wrapper.sh",  #noqa
    ".ansible/scripts/yamldump.py": "cops_wrapper.sh",  #noqa
    ".ansible/scripts/call_ansible.sh": "cops_wrapper.sh",  #noqa
    ".ansible/scripts/edit_vault.sh": "cops_wrapper.sh",  #noqa
    ".ansible/scripts/print_env.sh": "call_ansible.sh",  #noqa
    ".ansible/scripts/setup_ansible.sh": "cops_wrapper.sh",  #noqa
    ".ansible/playbooks/ping.yml": "../../local/terra-back-deploy/.ansible/playbooks/ping.yml",  #noqa
    ".ansible/playbooks/roles/terralegoback_vars": "../../../local/terra-back-deploy/.ansible/playbooks/roles/terralegoback_vars/",  #noqa
    ".ansible/playbooks/roles/terralegoback": "../../../local/terra-back-deploy/.ansible/playbooks/roles/terralegoback",  #noqa
    ".ansible/playbooks/app.yml": "../../local/terra-back-deploy/.ansible/playbooks/app.yml",  #noqa
    ".ansible/playbooks/deploy_key_setup.yml": "../../local/terra-back-deploy/.ansible/playbooks/deploy_key_setup.yml",  #noqa
    ".ansible/playbooks/deploy_key_teardown.yml": "../../local/terra-back-deploy/.ansible/playbooks/deploy_key_teardown.yml",  #noqa
    ".ansible/playbooks/site.yml": "../../local/terra-back-deploy/.ansible/playbooks/site.yml",  #noqa
    "crontab": "local/terra-back-deploy/crontab",  #noqa
    "requirements.txt": "local/terra-back-deploy/requirements.txt",  #noqa
    "prod/sudoer": "../local/terra-back-deploy/prod/sudoer",  #noqa
    "prod/init.sh": "../local/terra-back-deploy/prod/init.sh",  #noqa
    "prod/start.sh": "../local/terra-back-deploy/prod/start.sh",  #noqa
    "prod/etc/nginx/vhost.conf.template": "../../../local/terra-back-deploy/prod/etc/nginx/vhost.conf.template",  #noqa
    "tox.ini": "local/terra-back-deploy/tox.ini",  #noqa
    "requirements-dev.txt": "local/terra-back-deploy/requirements-dev.txt",  #noqa
    "apt.txt": "local/terra-back-deploy/apt.txt",  #noqa
    "Dockerfile": "local/terra-back-deploy/Dockerfile",  #noqa
}
GITSCRIPT = """
set -ex
git init
git remote add origin {{cookiecutter.git_project_url}}
git add .
rm -rf "{{cookiecutter.deploy_project_dir}}"
git add -f local/.empty
git submodule add -f "{{cookiecutter.deploy_project_url}}" \
             "{{cookiecutter.deploy_project_dir}}"
cp  ~/.cookiecutter_replay/{template}.json .cookiecutter.replay
git commit -am init
"""
MOTD = '''
After having checking in your project, do not remember to add Terralego backend
code as a git submodule with this command:
git submodule add -f {{cookiecutter.egg_project_url}} \
        {{cookiecutter.egg_project_dir}}
'''


def sym(i, target):
    print('* Symlink: {0} -> {1}'.format(i, target))
    d = os.path.dirname(i)
    if os.path.exists('local/terra-back-deploy'):
        remove_tree('local/terra-back-deploy')
    if d and not os.path.exists(d):
        os.makedirs(d)
    if os.path.exists(i):
        if os.path.isdir(i):
            remove_tree(i)
        else:
            os.unlink(i)
    os.symlink(target, i)


def main():
    for i in SYMLINKS:
        sym(i, SYMLINKS[i])

    subprocess.check_call(GITSCRIPT.format(template=TEMPLATE), shell=True)
    print(MOTD)


if __name__ == '__main__':
    main()
# vim:set et sts=4 ts=4 tw=80:
