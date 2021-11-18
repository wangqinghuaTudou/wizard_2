# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This file is part of Wizard

# MIT License

# Copyright (c) 2021 Leo brunel

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# This wizard module is used to build the user environment
# when launching the application
# It can get the site path and some user
# preferences from $Documents/preferences.yaml

# If a site path is defined this module
# is used to get the current machine user and project
# The user logs are wrapped to the machine ip
# The machine ips are stored in the site database file

# Python modules
import yaml
import json
import os
import importlib
import sys
import shutil

# Wizard modules
from wizard.vars import user_vars
from wizard.vars import ressources
from wizard.core import image
from wizard.core import tools
from wizard.core import environment
from wizard.core import project
from wizard.core import site
from wizard.core import db_core
from wizard.core import db_utils
from wizard.core import team_client

from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

def create_user_folders():
    # Init the user folders
    # ~/Documets/wizard/icons
    # ~/Documets/wizard/scripts
    if not os.path.isdir(user_vars._script_path_):
        os.mkdir(user_vars._script_path_)
    sys.path.append(user_vars._script_path_)
    if not os.path.isdir(user_vars._icons_path_):
        os.mkdir(user_vars._icons_path_)

def init_user_session():
    # Init the session.py file
    # This file permits to execute
    # user scripts in the
    # of the application environment
    with open(user_vars._session_file_, 'w') as f:
        f.write('')

create_user_folders()
init_user_session()

import session

class user:
    def __init__(self):
        self.get_user_prefs_dic()

    def set_psql_dns(self, host, port, user, password):
        DNS = f"host={host} port={port} user={user} password={password}"
        if db_core.try_connection(DNS):
            self.prefs_dic[user_vars._psql_dns_] = DNS
            self.write_prefs_dic()
            environment.set_psql_dns(DNS)
            return 1
        else:
            return None

    def get_psql_dns(self):
        if self.prefs_dic[user_vars._psql_dns_]:
            if db_core.try_connection(self.prefs_dic[user_vars._psql_dns_]):
                environment.set_psql_dns(self.prefs_dic[user_vars._psql_dns_])
                return 1
            else:
                self.prefs_dic[user_vars._psql_dns_] = None
                self.write_prefs_dic()
                return None
        else:
            logger.info("No postgreSQL DNS set")
            return None

    def set_team_dns(self, host, port):
        DNS = (host, port)
        if team_client.try_connection(DNS):
            self.prefs_dic[user_vars._team_dns_] = DNS
            self.write_prefs_dic()
            environment.set_team_dns(DNS)
            logger.info("Team DNS modified")
            return 1
        else:
            logger.warning("Can't reach server with this DNS")
            return None

    def get_team_dns(self):
        if self.prefs_dic[user_vars._team_dns_]:
            if team_client.try_connection(self.prefs_dic[user_vars._team_dns_]):
                environment.set_team_dns(self.prefs_dic[user_vars._team_dns_])
                return 1
            else:
                environment.set_team_dns(self.prefs_dic[user_vars._team_dns_])
                return None
        else:
            logger.info("No team DNS set")
            return None

    def add_context(self, type, context_dic):
        self.prefs_dic[type][environment.get_project_name()] = context_dic
        self.write_prefs_dic()

    def get_context(self, type):
        if environment.get_project_name() in self.prefs_dic[type].keys():
            return self.prefs_dic[type][environment.get_project_name()]
        else:
            return None

    def set_local_path(self, path):
        if path != '' and os.path.isdir(path):
            self.prefs_dic[user_vars._local_path_] = path
            self.write_prefs_dic()
            logger.info("Local path modified")
            return 1
        else:
            logger.warning('Please enter a valid local path')
            return None

    def set_popups_settings(self, enabled=1, sound_enabled=1, duration=3):
        popups_settings_dic = dict()
        popups_settings_dic['enabled'] = enabled
        popups_settings_dic['duration'] = duration
        self.prefs_dic[user_vars._popups_settings_] = popups_settings_dic
        self.write_prefs_dic()

    def get_popups_enabled(self):
        return self.prefs_dic[user_vars._popups_settings_]['enabled']

    def get_popups_duration(self):
        return self.prefs_dic[user_vars._popups_settings_]['duration']

    def get_local_path(self):
        return self.prefs_dic[user_vars._local_path_]

    def get_user_prefs_dic(self):
        # Read ~/Documents/wizard/prefences.yaml
        # or init it if not found
        # return the preferences dictionnary
        self.user_prefs_file = user_vars._user_prefs_file_
        if not os.path.isdir(user_vars._user_path_):
            os.mkdir(user_vars._user_path_)
        if not os.path.isfile(self.user_prefs_file):
            self.prefs_dic = dict()
            self.prefs_dic[user_vars._psql_dns_] = None
            self.prefs_dic[user_vars._team_dns_] = None
            self.prefs_dic[user_vars._tree_context_] = dict()
            self.prefs_dic[user_vars._tabs_context_] = dict()
            self.prefs_dic[user_vars._versions_context_] = dict()
            self.prefs_dic[user_vars._wall_context_] = dict()
            self.prefs_dic[user_vars._asset_tracking_context_] = dict()
            self.prefs_dic[user_vars._console_context_] = dict()
            self.prefs_dic[user_vars._tickets_context_] = dict()
            self.prefs_dic[user_vars._local_path_] = None
            self.prefs_dic[user_vars._popups_settings_] = dict()
            self.prefs_dic[user_vars._popups_settings_]['enabled'] = 1
            self.prefs_dic[user_vars._popups_settings_]['sound_enabled'] = 1
            self.prefs_dic[user_vars._popups_settings_]['duration'] = 3
            self.write_prefs_dic()
        else:
            with open(self.user_prefs_file, 'r') as f:
                self.prefs_dic = yaml.load(f, Loader=yaml.Loader)

    def write_prefs_dic(self):
        with open(self.user_prefs_file, 'w') as f:
            yaml.dump(self.prefs_dic, f)

    def execute_session(self, script):
        # Execute a custom script
        # in the application environment
        # It write the script in 
        # ~/Documents/wizard/scripts/session.py
        # and reload the "session" module
        with open(user_vars._session_file_, 'w') as f:
                f.write(script)
        try:
            importlib.reload(session)
        except KeyboardInterrupt:
            logger.warning("Execution manually stopped")
        except:
            logger.error(sys.exc_info()[1])

    def execute_py(self, file):
        # Read a .py file and execute the data
        # with "execute_session()"
        if os.path.isfile(file):
            with open(file, 'r') as f:
                data = f.read()
            self.execute_session(data)
        else:
            logger.warning(f"{file} doesn't exists")

def log_user(user_name, password):
    if user_name in site.get_user_names_list():
        user_row = site.get_user_row_by_name(user_name)
        if tools.decrypt_string(user_row['pass'],
                                password):
            site.update_current_ip_data('user_id', user_row['id'])
            environment.build_user_env(user_name)
            logger.info(f'{user_name} signed in')
            return 1
        else:
            logger.warning(f'Wrong password for {user_name}')
            return None
    else:
        logger.error(f"{user_name} doesn't exists")
        return None

def disconnect_user():
    site.update_current_ip_data('user_id', None)
    logger.info('You are now disconnected')

def get_user():
    user_id = site.get_current_ip_data('user_id')
    if user_id:
        environment.build_user_env(user_name=site.get_user_data(user_id,
                                                                'user_name'))
        return 1
    else:
        return None

def log_project(project_name, password, wait_for_restart=False):
    if project_name in site.get_projects_names_list():
        project_row = site.get_project_row_by_name(project_name)
        if tools.decrypt_string(project_row['project_password'],
                                password):
            site.update_current_ip_data('project_id', project_row['id'])
            logger.info(f'Successfully signed in {project_name} project')
            if not wait_for_restart:
                environment.build_project_env(project_name, project_row['project_path'])
                db_utils.modify_db_name('project', project_name)
                project.add_user(site.get_user_row_by_name(environment.get_user(),
                                                                'id'))
            return 1
        else:
            logger.warning(f'Wrong password for {project_name}')
            return None
    else:
        logger.error(f"{project_name} doesn't exists")
        return None

def log_project_without_cred(project_name):
    if project_name in site.get_projects_names_list():
        project_row = site.get_project_row_by_name(project_name)
        site.update_current_ip_data('project_id', project_row['id'])
        environment.build_project_env(project_name, project_row['project_path'])
        db_utils.modify_db_name('project', project_name)
        logger.info(f'Successfully signed in {project_name} project')
        project.add_user(site.get_user_row_by_name(environment.get_user(),
                                                            'id'))
        return 1
    else:
        logger.error(f"{project_name} doesn't exists")
        return None


def disconnect_project():
    site.update_current_ip_data('project_id', None)
    logger.info('Successfully disconnect from project')

def get_project():
    project_id = site.get_current_ip_data('project_id')
    if project_id:
        project_row = site.get_project_row(project_id) 
        environment.build_project_env(project_name=project_row['project_name'],
                                        project_path=project_row['project_path'])
        return 1
    else:
        return None