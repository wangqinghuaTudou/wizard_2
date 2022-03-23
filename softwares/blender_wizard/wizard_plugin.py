# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os

# Blender modules
import bpy

# Wizard modules
import wizard_communicate
from blender_wizard import wizard_export
from blender_wizard import wizard_reference

def save_increment():
    file_path, version_id = wizard_communicate.add_version(int(os.environ['wizard_work_env_id']))
    if file_path:
        bpy.ops.wm.save_as_mainfile(filepath=file_path)
    else:
    	print('Saving failed')
    if version_id is not None:
    	os.environ['wizard_version_id'] = str(version_id)

def export():
	stage_name = os.environ['wizard_stage_name']
	wizard_export.main(stage_name)

def set_image_size():
	image_format = wizard_communicate.get_image_format()
	bpy.context.scene.render.resolution_x = image_format[0]
	bpy.context.scene.render.resolution_y = image_format[1]

def reference_texturing():
	references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
	if 'texturing' in references.keys():
		for texturing_reference in references['texturing']:
			wizard_reference.reference_texturing(texturing_reference['namespace'], texturing_reference['files'])

def update_texturing():
	references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
	if 'texturing' in references.keys():
		for texturing_reference in references['texturing']:
			wizard_reference.update_texturing(texturing_reference['namespace'], texturing_reference['files'])

def reference_modeling():
	references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
	if 'modeling' in references.keys():
		for modeling_reference in references['modeling']:
			wizard_reference.import_modeling_hard(modeling_reference['namespace'], modeling_reference['files'])