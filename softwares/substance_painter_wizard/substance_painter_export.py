# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import math
import traceback

# Substance Painter modules
import substance_painter.export
import substance_painter.project
import substance_painter.textureset
import substance_painter.js
import substance_painter.logging as logging

# Wizard modules
import wizard_communicate
import wizard_hooks

def export_textures(material, size, file_type) :
    if file_type == 'exr':
        bitdepth = '32'
    else:
        bitdepth = '16'

    export_name = 'main'
    temp_export_path = os.path.dirname(wizard_communicate.request_export(int(os.environ['wizard_work_env_id']),
                                        export_name)).replace('\\', '/')

    js_code = 'alg.mapexport.exportDocumentMaps("%s", "%s", "%s", {resolution:[%s,%s], bitDepth:[%s]})' % ( material, temp_export_path, file_type, size, size, bitdepth )
    try:
        export_result = substance_painter.js.evaluate(js_code)
    except:
        logging.error(str(traceback.format_exc()))
        export_result = None

    if export_result:
        exported_files = []
        files = os.listdir(temp_export_path)
        for file in files:
            exported_files.append(os.path.join(temp_export_path, file))

        export_dir = wizard_communicate.add_export_version(export_name,
                                                                exported_files,
                                                                int(os.environ['wizard_work_env_id']),
                                                                int(os.environ['wizard_version_id']))

        trigger_after_export_hook('texturing', export_dir)

def trigger_after_export_hook(stage_name, export_dir):
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
    wizard_hooks.after_export_hooks('substance_painter', stage_name, export_dir, string_asset, string_asset)
