# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Main wizard module to create a project
# This module basically store the new project
# in the site database, create the project database
# and create the intial instances :
# - assets
#    - characters
#    - props
#    - sets
#    - set_dress
# - library
# - sequences
# It intialize the defaults softwares in the 
# project database and initialize the project settings

# Wizard modules
from wizard.core import project
from wizard.core import assets
from wizard.core import environment
from wizard.core import tools
from wizard.vars import assets_vars
from wizard.vars import project_vars
from wizard.vars import softwares_vars

# Python modules
import os

def create_project(project_name,
                    project_path,
                    project_password,
                    frame_rate=24,
                    image_format=[1920,1080]):
    do_creation = 1

    if project_name == '':
        logger.warning("Please provide a project name")
        do_creation = 0
    if project_path == '':
        logger.warning("Please provide a project path")
        do_creation = 0
    if project_password == '':
        logger.warning("Please provide a password")
        do_creation = 0

    if do_creation: 
        project.create_settings_row(frame_rate, image_format)
        for domain in assets_vars._domains_list_:
            assets.create_domain(domain)
        assets_domain_id = 1
        for category in assets_vars._assets_categories_list_:
            assets.create_category(category, assets_domain_id)
        for software in softwares_vars._softwares_list_:
            software_id = project.add_software(software,
                            softwares_vars._extensions_dic_[software],
                            softwares_vars._file_command_[software],
                            softwares_vars._no_file_command_[software])
            for stage in assets_vars._default_ext_dic_[software].keys():
                extension = assets_vars._default_ext_dic_[software][stage]
                project.create_extension_row(stage, software_id, extension)

        tools.create_folder(project.get_shared_files_folder())
        tools.create_folder(project.get_scripts_folder())
        return 1
    else:
        return None
