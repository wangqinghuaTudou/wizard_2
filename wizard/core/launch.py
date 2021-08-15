# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# The main wizard software launching module
# This module permits to launch a work version ( id )
# It build the command and environment for the Popen
# call

# If no file is found for the given version id
# it launches the software without a file but 
# with the correct environment in order to save
# a version later within the software

# Python modules
import os
import subprocess
import shlex
import json
from threading import Thread

# Wizard modules
from wizard.core import project
from wizard.core import environment
from wizard.vars import softwares_vars

# Wizard gui modules
from wizard.gui import gui_server

from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

def launch_work_version(version_id):
	work_version_row = project.get_version_data(version_id)
	if work_version_row:
		file_path = work_version_row['file_path']
		work_env_id = work_version_row['work_env_id']
		if work_env_id not in environment.get_running_work_envs():
			if not project.get_lock(work_env_id):
				project.set_work_env_lock(work_env_id)
				software_id = project.get_work_env_data(work_env_id, 'software_id')
				software_row = project.get_software_data(software_id)
				command = build_command(file_path, software_row)
				env = build_env(work_env_id, software_row)
				if command :
					thread = software_thread(command,
												env,
												software_row['name'],
												work_env_id)
					thread.start()
					logger.info(f"{software_row['name']} launched")
		else:
			logger.warning(f"You are already running a work instance of this asset")

def build_command(file_path, software_row):
	software_path = software_row['path']
	if software_path != '':
		if os.path.isfile(file_path):
			raw_command = software_row['file_command']
		else:
			raw_command = software_row['no_file_command']
			logger.info("File not existing, launching software with empty scene")

		raw_command = raw_command.replace(softwares_vars._executable_key_, software_path)
		raw_command = raw_command.replace(softwares_vars._file_key_, file_path)
		if software_row['name'] in softwares_vars._scripts_dic_.keys():
			raw_command = raw_command.replace(softwares_vars._script_key_,
								softwares_vars._scripts_dic_[software_row['name']])
		return raw_command

	else:
		logger.warning(f"{software_row['name']} path not defined")
		return None

def build_env(work_env_id, software_row):
	# Building the default software environment for wizard workflow
	env = os.environ.copy()
	env['wizard_work_env_id'] = str(work_env_id)
	env[softwares_vars._script_env_dic_[software_row['name']]] = softwares_vars._main_script_path_
	
	# Getting the project software additionnal environment
	additionnal_script_paths = []
	if software_row['additionnal_scripts']:
		additionnal_script_paths = json.loads(software_row['additionnal_scripts'])
	additionnal_env = dict()
	if software_row['additionnal_env']:
		additionnal_env = json.loads(software_row['additionnal_env'])

	# Merging the project software additionnal environment
	# to the main env variable
	for script_path in additionnal_script_paths:
		env[softwares_vars._script_env_dic_[software_row['name']]] += os.pathsep+script_path
	for key in additionnal_env.keys():
		if key in env.keys():
			env[key] += os.pathsep+additionnal_env[key]
		else:
			env[key] = additionnal_env[key]

	return env

class software_thread(Thread):
	''' A thread that runs until the given software process is active
	When the software process is exited, the thread is deleted
	'''
	def __init__(self, command, env, software, work_env_id):
		super(software_thread, self).__init__()
		self.command = command
		self.env = env
		self.software = software
		self.work_env_id = work_env_id
 
	def run(self):
		environment.add_running_work_env(self.work_env_id)
		self.process = subprocess.Popen(args = shlex.split(self.command), env=self.env, cwd='softwares')
		self.process.wait()
		environment.remove_running_work_env(self.work_env_id)
		project.set_work_env_lock(self.work_env_id, 0)
		gui_server.refresh_ui()
		logger.info(f"{self.software} closed")
