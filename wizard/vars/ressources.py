# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os

# Softwares
_maya_ = 'maya'
_guerilla_render_ = 'guerilla_render'
_substance_painter_ = 'substance_painter'
_substance_designer_ = 'substance_designer'
_nuke_ = 'nuke'
_houdini_ = 'houdini'
_blender_ = 'blender'

_ressources_path_ = os.path.abspath('ressources')
_icons_path_ = os.path.abspath('ressources/icons')
_default_profile_ = os.path.join(_icons_path_, 'default_profile.png')
_default_script_shelf_icon_ = os.path.join(_icons_path_, 'shelf_script.png')
_add_icon_small_ = os.path.join(_icons_path_, 'add_small.png')
_add_icon_ = os.path.join(_icons_path_, 'add_icon.png')
_folder_icon_small_ = os.path.join(_icons_path_, 'folder_small.png')
_folder_icon_ = os.path.join(_icons_path_, 'folder.png')
_search_icon_ = os.path.join(_icons_path_, 'search_icon.png')
_warning_icon_ = os.path.join(_icons_path_, 'warning_icon.png')
_close_icon_ = os.path.join(_icons_path_, 'close_hover.png')
_close_thin_icon_ = os.path.join(_icons_path_, 'close_thin.png')
_admin_badge_ = os.path.join(_icons_path_, 'admin_badge.png')
_rigth_arrow_icon_ = os.path.join(_icons_path_, 'right_arrow.png')
_no_screenshot_ = os.path.join(_icons_path_, 'no_screenshot.png')
_no_screenshot_small_ = os.path.join(_icons_path_, 'no_screenshot_small.png')
_dragdrop_ = os.path.join(_icons_path_, 'dragdrop.png')
_file_icon_ = os.path.join(_icons_path_, 'file.png')
_archive_icon_ = os.path.join(_icons_path_, 'archive.png')
_tool_list_view_ = os.path.join(_icons_path_, 'tool_list_view.png')
_tool_icon_view_ = os.path.join(_icons_path_, 'tool_icon_view.png')
_tool_duplicate_ = os.path.join(_icons_path_, 'tool_duplicate.png')
_tool_add_ = os.path.join(_icons_path_, 'tool_add.png')
_tool_folder_ = os.path.join(_icons_path_, 'tool_folder.png')
_tool_archive_ = os.path.join(_icons_path_, 'tool_archive.png')
_tool_manually_publish_ = os.path.join(_icons_path_, 'tool_manually_publish.png')
_tool_batch_publish_ = os.path.join(_icons_path_, 'tool_batch_publish.png')
_tool_launch_ = os.path.join(_icons_path_, 'tool_launch.png')
_tool_ticket_ = os.path.join(_icons_path_, 'tool_ticket.png')
_random_icon_ = os.path.join(_icons_path_, 'random.png')
_bulb_icon_ = os.path.join(_icons_path_, 'bulb.png')
_info_icon_ = os.path.join(_icons_path_, 'info.png')
_python_icon_ = os.path.join(_icons_path_, 'python.png')
_console_icon_ = os.path.join(_icons_path_, 'console.png')
_console_warning_icon_ = os.path.join(_icons_path_, 'console_warning.png')
_console_error_icon_ = os.path.join(_icons_path_, 'console_error.png')
_console_info_icon_ = os.path.join(_icons_path_, 'console_info.png')
_wall_icon_ = os.path.join(_icons_path_, 'wall.png')
_wall_notification_icon_ = os.path.join(_icons_path_, 'wall_notification.png')
_wizard_icon_small_ = os.path.join(_icons_path_, 'wizard_icon_small.png')
_launch_info_image_ = os.path.join(_icons_path_, 'launch_info.png')
_select_stage_info_image_ = os.path.join(_icons_path_, 'select_stage_info.png')
_empty_info_image_ = os.path.join(_icons_path_, 'info_empty.png')
_tickets_info_image_ = os.path.join(_icons_path_, 'info_tickets.png')
_handshake_icon_ = os.path.join(_icons_path_, 'handshake.png')
_messages_icon_ = os.path.join(_icons_path_, 'messages.png')


# Lock icons
_lock_icons_ = dict()
_lock_icons_[1] = os.path.join(_icons_path_, 'locked.png')
_lock_icons_[0] = os.path.join(_icons_path_, 'unlocked.png')

# Domains icons
_assets_icon_small_ = os.path.join(_icons_path_, 'assets_small.png')
_library_icon_small_ = os.path.join(_icons_path_, 'library_small.png')
_sequences_icon_small_ = os.path.join(_icons_path_, 'sequences_small.png')

# Stages icons
_modeling_icon_small_ = os.path.join(_icons_path_, 'modeling_small.png')
_rigging_icon_small_ = os.path.join(_icons_path_, 'rigging_small.png')
_grooming_icon_small_ = os.path.join(_icons_path_, 'grooming_small.png')
_texturing_icon_small_ = os.path.join(_icons_path_, 'texturing_small.png')
_shading_icon_small_ = os.path.join(_icons_path_, 'shading_small.png')

_layout_icon_small_ = os.path.join(_icons_path_, 'layout_small.png')
_animation_icon_small_ = os.path.join(_icons_path_, 'animation_small.png')
_cfx_icon_small_ = os.path.join(_icons_path_, 'cfx_small.png')
_fx_icon_small_ = os.path.join(_icons_path_, 'fx_small.png')
_lighting_icon_small_ = os.path.join(_icons_path_, 'lighting_small.png')
_compositing_icon_small_ = os.path.join(_icons_path_, 'compositing_small.png')
_camera_icon_small_ = os.path.join(_icons_path_, 'camera_small.png')

# Softwares icons
_sofwares_icons_dic_ = dict()
_sofwares_icons_dic_[_maya_] = os.path.join(_icons_path_, 'maya.png')
_sofwares_icons_dic_[_guerilla_render_] = os.path.join(_icons_path_, 'guerilla_render.png')
_sofwares_icons_dic_[_substance_painter_] = os.path.join(_icons_path_, 'substance_painter.png')
_sofwares_icons_dic_[_substance_designer_] = os.path.join(_icons_path_, 'substance_designer.png')
_sofwares_icons_dic_[_nuke_] = os.path.join(_icons_path_, 'nuke.png')
_sofwares_icons_dic_[_houdini_] = os.path.join(_icons_path_, 'houdini.png')
_sofwares_icons_dic_[_blender_] = os.path.join(_icons_path_, 'blender.png')