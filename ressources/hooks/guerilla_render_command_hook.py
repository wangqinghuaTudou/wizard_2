# coding: utf-8
# Wizard commands hook

import logging
logger = logging.getLogger(__name__)

from guerilla_render_wizard import wizard_tools
from guerilla import Document, Modifier, pynode, Node, Plug

def gnode_command(export_GRP_list, export_file):
    ''' This function is used to store 
    a default gnode export command.
    You can modify it from here
    Be carreful on what you are modifying'''
    grp_node = wizard_tools.get_node_from_name(export_GRP_list[0])
    grp_node.savefile(export_file)

def gproject_command(export_GRP_list, export_file):
    ''' This function is used to store 
    a default gproject export command.
    You can modify it from here
    Be carreful on what you are modifying'''
    for object in wizard_tools.get_all_nodes():
        if object not in export_GRP_list:
            continue
        try:
            pynode(object).delete()
        except:
            pass
    Document().save(export_file)