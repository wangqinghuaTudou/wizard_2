# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard modules
from wizard.core import tools
from wizard.core import site
from wizard.core import assets
from wizard.core import project
from wizard.vars import ressources
from wizard.vars import assets_vars

# Wizard gui modules
from wizard.gui import gui_server

class asset_tracking_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(asset_tracking_widget, self).__init__(parent)

        self.variant_id = None
        self.variant_row = None
        self.users_ids = dict()
        self.tracking_event_ids = dict()

        self.apply_assignment_modification = None
        self.apply_state_modification = None

        self.build_ui()
        self.refresh_users_dic()
        self.connect_functions()

    def refresh_users_dic(self):
        users_ids = project.get_users_ids_list()
        for user_id in users_ids:
            if user_id not in self.users_ids.keys():
                self.users_ids[user_id] = site.get_user_data(user_id, 'user_name')
                self.assignment_comboBox.addItem(self.users_ids[user_id])

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.setup_widget = QtWidgets.QFrame()
        self.setup_widget.setObjectName('asset_tracking_event_frame')
        self.setup_layout = QtWidgets.QHBoxLayout()
        self.setup_layout.setSpacing(6)
        self.setup_widget.setLayout(self.setup_layout)
        self.main_layout.addWidget(self.setup_widget)

        self.assignment_comboBox = QtWidgets.QComboBox()
        self.assignment_comboBox.setItemDelegate(QtWidgets.QStyledItemDelegate())
        self.setup_layout.addWidget(self.assignment_comboBox)

        self.state_comboBox = QtWidgets.QComboBox()
        self.state_comboBox.setIconSize(QtCore.QSize(14,14))
        self.state_comboBox.setFixedWidth(100)
        self.state_comboBox.setItemDelegate(QtWidgets.QStyledItemDelegate())
        self.setup_layout.addWidget(self.state_comboBox)
        self.state_comboBox.addItem(QtGui.QIcon(ressources._state_todo_), assets_vars._asset_state_todo_)
        self.state_comboBox.addItem(QtGui.QIcon(ressources._state_wip_), assets_vars._asset_state_wip_)
        self.state_comboBox.addItem(QtGui.QIcon(ressources._state_done_), assets_vars._asset_state_done_ )
        self.state_comboBox.addItem(QtGui.QIcon(ressources._state_error_), assets_vars._asset_state_error_)

        self.progress_widget = QtWidgets.QFrame()
        self.progress_widget.setObjectName('asset_tracking_event_frame')
        self.progress_layout = QtWidgets.QHBoxLayout()
        self.progress_layout.setSpacing(6)
        self.progress_widget.setLayout(self.progress_layout)
        self.main_layout.addWidget(self.progress_widget)

        self.events_scrollArea = QtWidgets.QScrollArea()
        self.events_scrollBar = self.events_scrollArea.verticalScrollBar()

        self.events_scrollArea_widget = QtWidgets.QWidget()
        self.events_scrollArea_widget.setObjectName('transparent_widget')
        self.events_scrollArea_layout = QtWidgets.QVBoxLayout()
        self.events_scrollArea_layout.setContentsMargins(0,4,8,4)
        self.events_scrollArea_layout.setSpacing(0)
        self.events_scrollArea_widget.setLayout(self.events_scrollArea_layout)

        self.events_content_widget = QtWidgets.QWidget()
        self.events_content_layout = QtWidgets.QVBoxLayout()
        self.events_content_layout.setContentsMargins(0,0,0,0)
        self.events_content_layout.setSpacing(6)
        self.events_content_widget.setLayout(self.events_content_layout)
        self.events_scrollArea_layout.addWidget(self.events_content_widget)

        self.events_scrollArea_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

        self.events_scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.events_scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.events_scrollArea.setWidgetResizable(True)
        self.events_scrollArea.setWidget(self.events_scrollArea_widget)
        self.main_layout.addWidget(self.events_scrollArea)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(300,0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))

    def change_variant(self, variant_id):
        self.variant_id = variant_id
        self.clear_tracking_events()
        self.refresh()

    def refresh(self):
        if self.variant_id is not None:
            self.variant_row = project.get_variant_data(self.variant_id)
        else:
            self.variant_row = None
        self.refresh_state()
        self.refresh_users_dic()
        self.refresh_user()
        self.refresh_tracking_events()

    def clear_tracking_events(self):
        tracking_event_ids = list(self.tracking_event_ids.keys())
        for tracking_event_id in tracking_event_ids:
            self.tracking_event_ids[tracking_event_id].setParent(None)
            self.tracking_event_ids[tracking_event_id].deleteLater()
            del self.tracking_event_ids[tracking_event_id]

    def refresh_tracking_events(self):
        if self.variant_id is not None:
            tracking_event_rows = project.get_asset_tracking_events(self.variant_id)
            for tracking_event_row in tracking_event_rows:
                if tracking_event_row['id'] not in self.tracking_event_ids.keys():
                    widget = tracking_event_widget(tracking_event_row)
                    self.events_content_layout.addWidget(widget)
                    self.tracking_event_ids[tracking_event_row['id']] = widget

    def refresh_user(self):
        self.apply_assignment_modification = None
        if self.variant_row is not None:
            if self.variant_row['assignment'] is not None:
                self.assignment_comboBox.setCurrentText(self.variant_row['assignment'])
            else:
                self.assignment_comboBox.setCurrentText('Assign user')
        else:
            self.assignment_comboBox.setCurrentText('Assign user')
        self.apply_assignment_modification = 1

    def refresh_state(self):
        self.apply_state_modification = None
        if self.variant_row is not None:
            self.state_comboBox.setCurrentText(self.variant_row['state'])
        else:
            self.state_comboBox.setCurrentText('todo')
        self.apply_state_modification = 1

    def modify_state(self, state):
        if self.variant_id is not None:
            if self.apply_state_modification:
                assets.modify_variant_state(self.variant_id, state)
                gui_server.refresh_ui()

    def modify_assignment(self, user_name):
        if self.variant_id is not None:
            if self.apply_assignment_modification:
                assets.modify_variant_assignment(self.variant_id, user_name)
                gui_server.refresh_ui()

    def connect_functions(self):
        self.state_comboBox.currentTextChanged.connect(self.modify_state)
        self.assignment_comboBox.currentTextChanged.connect(self.modify_assignment)
        self.events_scrollBar.rangeChanged.connect(lambda: self.events_scrollBar.setValue(self.events_scrollBar.maximum()))

class tracking_event_widget(QtWidgets.QFrame):
    def __init__(self, tracking_event_row, parent=None):
        super(tracking_event_widget, self).__init__(parent)
        self.tracking_event_row = tracking_event_row

        self.build_ui()

        if self.tracking_event_row['event_type'] == 'state_switch':
            self.build_state_switch_ui()
        elif self.tracking_event_row['event_type'] == 'assignment':
            self.build_assignment_ui()
        elif self.tracking_event_row['event_type'] == 'work_session':
            self.build_work_session_ui()

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.setObjectName('asset_tracking_event_frame')
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

    def build_work_session_ui(self):
        self.user_label = QtWidgets.QLabel(self.tracking_event_row['creation_user'])
        self.user_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.main_layout.addWidget(self.user_label)

        self.info_label = QtWidgets.QLabel('worked')
        self.info_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.info_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.info_label)

        days, hours, minutes, seconds = tools.convert_seconds_with_day(float(self.tracking_event_row['data']))
        print(days, hours, minutes, seconds)
        if int(days) != 0:
            string_time = f"{days}d, {hours}h"
        if int(hours) != 0 and int(days) == 0:
            string_time = f"{hours}h, {minutes}m"
        if int(minutes) != 0 and int(hours) == 0 and int(days) == 0:
            string_time = f"{minutes}m, {seconds}s"
        if int(seconds) != 0 and int(minutes) == 0 and int(hours) == 0 and int(days) == 0:
            string_time = f"{seconds}s"

        self.work_time_label = QtWidgets.QLabel(string_time)
        self.work_time_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.main_layout.addWidget(self.work_time_label)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

    def build_assignment_ui(self):
        self.user_label = QtWidgets.QLabel(self.tracking_event_row['creation_user'])
        self.user_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.main_layout.addWidget(self.user_label)

        self.info_label = QtWidgets.QLabel('assigned task to')
        self.info_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.info_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.info_label)

        self.assignment_label = QtWidgets.QLabel(self.tracking_event_row['data'])
        self.assignment_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.main_layout.addWidget(self.assignment_label)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

    def build_state_switch_ui(self):
        self.user_label = QtWidgets.QLabel(self.tracking_event_row['creation_user'])
        self.user_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.main_layout.addWidget(self.user_label)

        self.info_label = QtWidgets.QLabel('switched state to')
        self.info_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.info_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.info_label)

        self.state_frame = QtWidgets.QFrame()
        self.state_frame.setObjectName('asset_tracking_event_frame')
        self.state_frame.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.state_frame_layout = QtWidgets.QHBoxLayout()
        self.state_frame_layout.setContentsMargins(8,8,8,8)
        self.state_frame.setLayout(self.state_frame_layout)
        self.main_layout.addWidget(self.state_frame)

        if self.tracking_event_row['data'] == 'todo':
            color = '#8a8a8a'
        elif self.tracking_event_row['data'] == 'wip':
            color = '#ffad4d'
        elif self.tracking_event_row['data'] == 'done':
            color = '#95d859'
        elif self.tracking_event_row['data'] == 'error':
            color = '#ff5d5d'
        self.state_frame.setStyleSheet(f'background-color:{color};')
        
        self.state_label = QtWidgets.QLabel(self.tracking_event_row['data'])
        self.state_label.setObjectName('bold_label')
        self.state_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.state_frame_layout.addWidget(self.state_label)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))
