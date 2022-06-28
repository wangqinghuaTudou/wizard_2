# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import time
import logging

# Wizard gui modules
from wizard.gui import gui_server
from wizard.gui import gui_utils
from wizard.gui import logging_widget

# Wizard modules
from wizard.core import repository
from wizard.core import tools
from wizard.core import assets
from wizard.core import project
from wizard.core import launch
from wizard.core import environment
from wizard.core import image
from wizard.core import path_utils
from wizard.vars import ressources
from wizard.vars import assets_vars

logger = logging.getLogger(__name__)

class production_manager(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(production_manager, self).__init__(parent)
        self.asset_ids = dict()
        self.stage_ids = dict()
        self.variant_ids = dict()
        self.init_users_images()
        self.build_ui()
        self.refresh()

    def init_users_images(self):
        self.users_images_dic = dict()
        for user_row in repository.get_users_list():
            user_image =  user_row['profile_picture']
            pixmap = gui_utils.mask_image(image.convert_str_data_to_image_bytes(user_image), 'png', 22)
            self.users_images_dic[user_row['user_name']] = pixmap

    def build_ui(self):
        self.resize(1000,800)
        self.main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.main_layout)

        self.table_widget = QtWidgets.QTableWidget()
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
        self.table_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.main_layout.addWidget(self.table_widget)

    def update_state(self, state):
        print(state)

    def refresh(self):
        start_time = time.time()
        # Props context to modify
        
        asset_rows = project.get_category_childs(2)
        assets_preview_rows = project.get_all_assets_preview()
        assets_preview = dict()
        for assets_preview_row in assets_preview_rows:
            assets_preview[assets_preview_row['asset_id']] = assets_preview_row
        
        # Modify table
        self.table_widget.setColumnCount(6)
        self.table_widget.setHorizontalHeaderLabels(["Name", "Modeling", "Rigging", "Grooming", "Texturing", "Shading"])
        stages_list = ["", "modeling", "rigging", "grooming", "texturing", "shading"]
        self.table_widget.setRowCount(len(asset_rows))

        for asset_row in asset_rows:

            if asset_row['id'] not in self.asset_ids.keys():
                index = asset_rows.index(asset_row)
                widget = asset_widget(asset_row['name'], assets_preview[asset_row['id']])
                self.table_widget.setCellWidget(index, 0, widget)
                self.asset_ids[asset_row['id']] = dict()
                self.asset_ids[asset_row['id']]['table_row_index'] = index
                self.asset_ids[asset_row['id']]['row'] = asset_row
                self.asset_ids[asset_row['id']]['widget'] = widget

        stage_rows = project.get_all_stages()

        for stage_row in stage_rows:
            if stage_row['asset_id'] in self.asset_ids.keys():
                if stage_row['id'] not in self.stage_ids.keys():
                    row_index = self.asset_ids[stage_row['asset_id']]['table_row_index']
                    widget = stage_widget()
                    self.table_widget.setCellWidget(row_index, stages_list.index(stage_row['name']), widget)
                    self.stage_ids[stage_row['id']] = dict()
                    self.stage_ids[stage_row['id']]['row'] = stage_row
                    self.stage_ids[stage_row['id']]['widget'] = widget

        variant_rows = project.get_all_variants()

        for variant_row in variant_rows:
            if variant_row['stage_id'] in self.stage_ids.keys():
                if variant_row['id'] not in self.variant_ids.keys():
                    stage_wid = self.stage_ids[variant_row['stage_id']]['widget']
                    widget = stage_wid.add_variant(variant_row, self.users_images_dic)
                    widget.state_signal.connect(self.update_state)
                    self.variant_ids[variant_row['id']] = dict()
                    self.variant_ids[variant_row['id']]['row'] = variant_row
                    self.variant_ids[variant_row['id']]['widget'] = widget

        self.table_widget.resizeColumnsToContents()
        self.table_widget.resizeRowsToContents()
        print(time.time() - start_time)

class asset_widget(QtWidgets.QWidget):
    def __init__(self, asset_name, preview_row, parent=None):
        super(asset_widget, self).__init__(parent)
        self.asset_name = asset_name
        self.preview_row = preview_row
        self.build_ui()
        self.fill_ui()

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0,0,8,0)
        self.setLayout(self.main_layout)

        self.image_label = QtWidgets.QLabel()
        self.image_label.setFixedWidth(72)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label.setObjectName('production_manager_variant_frame')
        self.main_layout.addWidget(self.image_label)

        self.asset_name_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.asset_name_label)

    def fill_ui(self):
        self.asset_name_label.setText(self.asset_name)

        image = ressources._no_preview_
        if self.preview_row['manual_override'] is None:
            if self.preview_row['preview_path'] is not None:
                image = self.preview_row['preview_path']
        else:
            image = self.preview_row['manual_override']
        self.image_label.setPixmap(QtGui.QIcon(image).pixmap(72, 40))

class stage_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(stage_widget, self).__init__(parent)
        self.build_ui()

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(1)
        self.setLayout(self.main_layout)

    def add_variant(self, variant_row, users_images_dic):
        widget = variant_widget(variant_row, users_images_dic)
        self.main_layout.addWidget(widget)
        return widget

class variant_widget(QtWidgets.QWidget):

    state_signal = pyqtSignal(str)

    def __init__(self, variant_row, users_images_dic, parent=None):
        super(variant_widget, self).__init__(parent)
        self.variant_row = variant_row
        self.users_images_dic = users_images_dic
        self.build_ui()
        self.connect_functions()
        self.fill_ui()

    def connect_functions(self):
        self.state_label.state_signal.connect(self.state_signal.emit)

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(6,6,6,6)
        self.main_layout.setSpacing(4)
        self.setLayout(self.main_layout)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

        self.variant_name = QtWidgets.QLabel()
        self.variant_name.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.variant_name.setObjectName('gray_label')
        self.main_layout.addWidget(self.variant_name)

        self.data_widget = QtWidgets.QWidget()
        self.data_widget.setObjectName('transparent_widget')
        self.data_layout = QtWidgets.QHBoxLayout()
        self.data_layout.setSpacing(2)
        self.data_layout.setContentsMargins(0,0,0,0)
        self.data_widget.setLayout(self.data_layout)
        self.main_layout.addWidget(self.data_widget)

        self.state_label = state_widget()
        self.state_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.state_label.setMinimumHeight(22)
        self.data_layout.addWidget(self.state_label)

        self.user_image_label = QtWidgets.QLabel()
        self.user_image_label.setFixedSize(QtCore.QSize(22,22))
        self.data_layout.addWidget(self.user_image_label)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

    def fill_ui(self):
        self.variant_name.setText(self.variant_row['name'])
        self.state_label.setText(self.variant_row['state'])
        self.state_label.setStyleSheet('#state_label{background-color:%s;border-radius:4px;padding:6px;}'%ressources._states_colors_[self.variant_row['state']])
        self.user_image_label.setPixmap(self.users_images_dic[self.variant_row['assignment']])

class state_widget(QtWidgets.QLabel):

    state_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(state_widget, self).__init__(parent)
        self.setObjectName('state_label')

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.states_menu_requested()

    def states_menu_requested(self):
        menu = gui_utils.QMenu(self)
        menu.addAction(QtGui.QIcon(ressources._state_todo_), 'todo')
        menu.addAction(QtGui.QIcon(ressources._state_wip_), 'wip')
        menu.addAction(QtGui.QIcon(ressources._state_done_), 'done')
        menu.addAction(QtGui.QIcon(ressources._state_error_), 'error')
        action = menu.exec_(QtGui.QCursor().pos())
        if action is not None:
            self.state_signal.emit(action.text())

w=production_manager()
w.show()
