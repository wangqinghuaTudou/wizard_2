# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import logging
logger = logging.getLogger(__name__)

# Wizard modules
import wizard_communicate
from guerilla_render_wizard import wizard_tools
from guerilla_render_wizard import wizard_export
from guerilla_render_wizard import wizard_reference
from guerilla_render_wizard import guerilla_shader
from guerilla_render_wizard.export import shading
from guerilla_render_wizard.export import custom

# Guerilla modules
from guerilla import Document, pynode

def save_increment():
    wizard_tools.save_increment()

def export():
    stage_name = os.environ['wizard_stage_name']
    scene = wizard_export.save_or_save_increment()
    if stage_name == 'shading':
        shading.main()
    elif stage_name == 'custom':
        custom.main()
    else:
        logger.warning("Unplugged stage : {0}".format(stage_name))
    wizard_export.reopen(scene)

def reference_modeling():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'modeling' in references.keys():
        for modeling_reference in references['modeling']:
            wizard_reference.reference_modeling(modeling_reference['namespace'], modeling_reference['files'])

def update_modeling():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'modeling' in references.keys():
        for modeling_reference in references['modeling']:
            wizard_reference.update_modeling(modeling_reference['namespace'], modeling_reference['files'])

def import_texturing():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'texturing' in references.keys():
        for texturing_reference in references['texturing']:
            guerilla_shader.import_texturing(texturing_reference['namespace'],
                                                texturing_reference['files'],
                                                texturing_reference['asset_name'])

def update_texturing():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'texturing' in references.keys():
        for texturing_reference in references['texturing']:
            guerilla_shader.update_texturing(texturing_reference['namespace'],
                                                texturing_reference['files'],
                                                texturing_reference['asset_name'])

def import_shading():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'shading' in references.keys():
        for modeling_reference in references['shading']:
            wizard_reference.reference_shading(modeling_reference['namespace'], modeling_reference['files'])

def update_shading():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'shading' in references.keys():
        for modeling_reference in references['shading']:
            wizard_reference.update_shading(modeling_reference['namespace'], modeling_reference['files'])

def import_custom():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'custom' in references.keys():
        for modeling_reference in references['custom']:
            wizard_reference.reference_custom(modeling_reference['namespace'], modeling_reference['files'])

def update_custom():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'custom' in references.keys():
        for modeling_reference in references['custom']:
            wizard_reference.update_custom(modeling_reference['namespace'], modeling_reference['files'])