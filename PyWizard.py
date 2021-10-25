# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# PyWizard is the wizard application without GUI
# Use PyWizard to execute batch commands like
# large amount of instances creation or archiving

# Python modules
import sys
import os
import traceback
import code

# Append current dir to sys.path
sys.path.append(os.path.abspath(''))

# Wizard modules
from wizard.core import user
from wizard.core import project
from wizard.core import site
from wizard.core import tools
from wizard.core import create_project
from wizard.core import communicate
from wizard.core import environment
from wizard.core import launch
from wizard.core import db_core
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

while not user.user().get_psql_dns():
    psql_host = tools.flushed_input("PostgreSQL host : ")
    psql_port = tools.flushed_input("PostgreSQL port : ")
    psql_user = tools.flushed_input("PostgreSQL user : ")
    psql_password = tools.flushed_input("PostgreSQL password : ")
    user.user().set_psql_dns(
                            psql_host,
                            psql_port,
                            psql_user,
                            psql_password
                            )

db_server = db_core.db_server()
db_server.start()

if not site.is_site_database():
    while not site.is_site_database():
        init_site = tools.flushed_input("Site database doesn't exists, init database (y/n) ? : ")
        if init_site == 'y':
            admin_password = tools.flushed_input('Administator password : ')
            admin_email = tools.flushed_input('Administator email : ')
            site.create_site_database()
            db_server.site='site'
            site.init_site(admin_password, admin_email)

db_server.site='site'
site.add_ip_user()

while not user.get_user():
    do_create_user = tools.flushed_input('Create user (y/n) ? : ')
    if do_create_user == 'y':
        user_name = tools.flushed_input('User name : ')
        password = tools.flushed_input('Password : ')
        email = tools.flushed_input('Email : ')
        profile_picture = tools.flushed_input('Profile picture ( without any "\\" ) ( Optional ) : ')
        administrator_pass = tools.flushed_input('Administrator pass ( Optional ) : ')
        site.create_user(user_name,
                                password,
                                email,
                                administrator_pass,
                                profile_picture)
    else:
        user_name = tools.flushed_input('User name : ')
        password = tools.flushed_input('Password : ')
        user.log_user(user_name, password)

while not user.get_project():
    do_create_project = tools.flushed_input('Create project (y/n) ? : ')
    if do_create_project == 'y':
        project_name = tools.flushed_input('Project name : ')
        project_path = tools.flushed_input('Project path : ')
        project_password = tools.flushed_input('Project password : ')
        create_project.create_project(project_name, project_path, project_password)
    else:
        project_name = tools.flushed_input('Project name : ')
        project_password = tools.flushed_input('Project password : ')
        user.log_project(project_name, project_password)

db_server.project_name = environment.get_project_name()
softwares_server = launch.softwares_server()
softwares_server.start()

if len(sys.argv) == 2:
    try:
        exec(open(sys.argv[1]).read())
    except:
        print(str(traceback.format_exc()))
    finally:
        db_server.stop()
        softwares_server.stop()
else:
    console = code.InteractiveConsole()
    console.interact(banner=None, exitmsg=None)
    db_server.stop()
    softwares_server.stop()