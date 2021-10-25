# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
import os   
import json 
import time

# Wizard modules
from wizard.core import user
from wizard.core import site
from wizard.core import project
from wizard.core import assets
from wizard.core import image
from wizard.core import tools
from wizard.vars import ressources
from wizard.vars import user_vars

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server
from wizard.gui import ticket_history_widget

class tickets_widget(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(tickets_widget, self).__init__(parent)
        self.stage_id = None
        self.ticket_ids = dict()
        self.build_ui()
        self.connect_functions()
        self.show_info_mode("Select or create a stage\nin the project tree !", ressources._select_stage_info_image_)

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_layout)

        self.tickets_area = QtWidgets.QWidget()
        self.tickets_area_layout = QtWidgets.QHBoxLayout()
        self.tickets_area_layout.setSpacing(0)
        self.tickets_area_layout.setContentsMargins(0,0,0,0)
        self.tickets_area.setLayout(self.tickets_area_layout)
        self.main_layout.addWidget(self.tickets_area)

        self.info_widget = gui_utils.info_widget()
        self.info_widget.setVisible(0)
        self.tickets_area_layout.addWidget(self.info_widget)

        self.tickets_list = QtWidgets.QTreeWidget()
        self.tickets_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tickets_list.setObjectName('tree_as_list_widget')
        self.tickets_list.setIconSize(QtCore.QSize(30,30))
        self.tickets_list.setColumnCount(4)
        self.tickets_list.setHeaderLabels(['User', 'Title', 'Date', 'State'])
        self.tickets_list.header().resizeSection(0, 70)
        self.tickets_list.header().resizeSection(1, 300)
        self.tickets_list.header().resizeSection(2, 150)
        self.tickets_list.setIndentation(0)
        self.tickets_list.setAlternatingRowColors(True)
        self.tickets_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.tickets_area_layout.addWidget(self.tickets_list)

        self.ticket_history_widget = ticket_history_widget.ticket_history_widget(self.tickets_list)
        self.ticket_history_widget.show()

        self.infos_widget = QtWidgets.QWidget()
        self.infos_widget.setObjectName('dark_widget')
        self.infos_layout = QtWidgets.QHBoxLayout()
        self.infos_layout.setContentsMargins(8,8,8,0)
        self.infos_layout.setSpacing(4)
        self.infos_widget.setLayout(self.infos_layout)
        self.main_layout.addWidget(self.infos_widget)

        self.infos_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.toggle_visibility_checkBox = QtWidgets.QCheckBox('Show only openned tickets')
        self.toggle_visibility_checkBox.setObjectName('transparent_widget')
        self.toggle_visibility_checkBox.setChecked(1)
        self.infos_layout.addWidget(self.toggle_visibility_checkBox)

        self.tickets_count_label = QtWidgets.QLabel()
        self.tickets_count_label.setObjectName('gray_label')
        self.infos_layout.addWidget(self.tickets_count_label)

        self.openned_count_label = QtWidgets.QLabel()
        self.infos_layout.addWidget(self.openned_count_label)

        self.refresh_label = QtWidgets.QLabel()
        self.refresh_label.setObjectName('gray_label')
        self.infos_layout.addWidget(self.refresh_label)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_widget.setObjectName('dark_widget')
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(8,8,8,8)
        self.buttons_layout.setSpacing(4)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))
        
        self.search_bar = gui_utils.search_bar()
        gui_utils.application_tooltip(self.search_bar, "Search for a specific version")
        self.search_bar.setPlaceholderText('"0023", "user:j.smith", "comment:retake eye"')
        self.buttons_layout.addWidget(self.search_bar)

        self.close_ticket_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.close_ticket_button, "Close ticket(s)")
        self.close_ticket_button.setFixedSize(35,35)
        self.close_ticket_button.setIconSize(QtCore.QSize(30,30))
        self.close_ticket_button.setIcon(QtGui.QIcon(ressources._tool_validate_))
        self.buttons_layout.addWidget(self.close_ticket_button)

    def connect_functions(self):
        self.toggle_visibility_checkBox.stateChanged.connect(self.update_visibility)
        self.tickets_list.itemSelectionChanged.connect(self.selection_changed)
        self.ticket_history_widget.toggle_ticket_signal.connect(self.toggle_ticket)

    def set_context(self):
        show_only_openned = self.toggle_visibility_checkBox.isChecked()
        context_dic = dict()
        context_dic['show_only_openned'] = show_only_openned
        user.user().add_context(user_vars._tickets_context_, context_dic)

    def get_context(self):
        context_dic = user.user().get_context(user_vars._tickets_context_)
        if context_dic is not None and context_dic != dict():
            show_only_openned = context_dic['show_only_openned']
            self.toggle_visibility_checkBox.setChecked(show_only_openned)

    def selection_changed(self):
        selection = self.tickets_list.selectedItems()
        if len(selection) == 1:
            self.ticket_history_widget.change_ticket(selection[0].ticket_row['id'])
        else:
            self.ticket_history_widget.change_ticket(None)

    def resizeEvent(self, event):
        self.ticket_history_widget.set_geometry()

    def toggle_ticket(self):
        selection = self.tickets_list.selectedItems()
        if len(selection) == 1:
            ticket_id = selection[0].ticket_row['id']
            if assets.toggle_ticket(ticket_id):
                gui_server.refresh_ui()

    def show_info_mode(self, text, image):
        self.ticket_history_widget.setVisible(0)
        self.tickets_list.setVisible(0)
        self.info_widget.setVisible(1)
        self.info_widget.setText(text)
        self.info_widget.setImage(image)

    def hide_info_mode(self):
        self.ticket_history_widget.setVisible(1)
        self.info_widget.setVisible(0)
        self.tickets_list.setVisible(1)
        self.selection_changed()

    def refresh_infos(self):
        self.tickets_count_label.setText(f" - {len(self.ticket_ids.keys())} tickets -")
        openned_count = 0
        for ticket_id in self.ticket_ids.keys():
            if self.ticket_ids[ticket_id].ticket_row['state'] == 1:
                openned_count +=1
        self.openned_count_label.setText(f"{openned_count} tickets openned")

    def refresh(self):
        start_time = time.time()
        if self.stage_id is not None:
            tickets_rows = project.get_tickets_by_stage(self.stage_id)
            if tickets_rows is not None:
                if tickets_rows != []:
                    for ticket_row in tickets_rows:
                        if ticket_row['id'] not in self.ticket_ids.keys():
                            ticket_item = custom_ticket_item(ticket_row, self.tickets_list.invisibleRootItem())
                            self.ticket_ids[ticket_row['id']] = ticket_item
                        else:
                            self.ticket_ids[ticket_row['id']].update_ticket_row(ticket_row)
            self.update_visibility()
        else:
            self.show_info_mode("Select or create a stage\nin the project tree !", ressources._select_stage_info_image_)
        self.ticket_history_widget.refresh()
        self.refresh_infos()
        self.update_refresh_time(start_time)

    def update_refresh_time(self, start_time):
        refresh_time = str(round((time.time()-start_time), 3))
        self.refresh_label.setText(f"- refresh : {refresh_time}s")

    def update_visibility(self):
        if self.toggle_visibility_checkBox.isChecked():
            for ticket_id in self.ticket_ids.keys():
                if self.ticket_ids[ticket_id].ticket_row['state'] == 1:
                    self.ticket_ids[ticket_id].setHidden(0)
                else:
                    self.ticket_ids[ticket_id].setHidden(1)
        else:
            self.show_all()
        self.update_info_mode()

    def update_info_mode(self):
        self.hide_info_mode()
        visible_tickets = []
        for ticket_id in self.ticket_ids.keys():
            if not self.ticket_ids[ticket_id].isHidden():
                visible_tickets.append(ticket_id)

        if visible_tickets == []:
            self.show_info_mode("No tickets openned,\nyou're doing it great !", ressources._tickets_info_image_)

    def show_all(self):
        for ticket_id in self.ticket_ids.keys():
            self.ticket_ids[ticket_id].setHidden(0)

    def clear(self):
        self.ticket_ids = dict()
        self.tickets_list.clear()

    def change_stage(self, stage_id):
        self.stage_id = stage_id
        self.clear()
        self.refresh()

class custom_ticket_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, ticket_row, parent=None):
        super(custom_ticket_item, self).__init__(parent)
        self.ticket_row = ticket_row
        self.fill_ui()
        self.refresh()

    def fill_ui(self):
        profile_picture = site.get_user_row_by_name(self.ticket_row['creation_user'], 'profile_picture')
        user_icon = QtGui.QIcon()
        pm = gui_utils.mask_image(image.convert_str_data_to_image_bytes(profile_picture), 'png', 30)
        user_icon.addPixmap(pm)
        self.setIcon(0, user_icon)
        self.setText(1, self.ticket_row['title'])
        day, hour = tools.convert_time(self.ticket_row['creation_time'])
        self.setText(2, f"{day} - {hour}")
        self.setForeground(2, QtGui.QBrush(QtGui.QColor('gray')))
        bold_font=QtGui.QFont()
        bold_font.setBold(True)
        self.setFont(3, bold_font)

    def refresh(self):
        if self.ticket_row['state'] == 1:
            self.setText(3, 'Open')
            self.setForeground(3, QtGui.QBrush(QtGui.QColor('#f0605b')))
        else:
            self.setText(3, 'Closed')
            self.setForeground(3, QtGui.QBrush(QtGui.QColor('#9cf277')))

    def update_ticket_row(self, ticket_row):
        self.ticket_row = ticket_row
        self.refresh()

