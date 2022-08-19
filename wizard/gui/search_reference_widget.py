# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import logging
import time

# Wizard modules
from wizard.core import assets
from wizard.core import project
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils

logger = logging.getLogger(__name__)

class search_reference_widget(QtWidgets.QWidget):

    variant_ids_signal = pyqtSignal(list)
    groups_ids_signal = pyqtSignal(list)

    def __init__(self, context, parent = None):
        super(search_reference_widget, self).__init__(parent)

        self.parent = parent
        self.context = context

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Create references")

        self.accept_item_from_thread = True      

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)       

        self.search_thread = search_thread(self.context)
        self.variant_ids = dict()
        self.groups_ids = dict()

        self.build_ui()
        self.connect_functions()

    def move_ui(self):
        cursor = self.mapFromGlobal(QtGui.QCursor.pos())
        area = self.parent.rect()
        if area.contains(cursor):
            screen_minX = area.topLeft().x()
            screen_minY = area.topLeft().y()
            screen_maxX = area.bottomRight().x()
            screen_maxY = area.bottomRight().y()
            win_width = self.frameSize().width()
            win_heigth = self.frameSize().height()

            if (cursor.y() - 30 - win_heigth) <= screen_minY:
                posy = cursor.y() - 15
                angley = 'top'
            else:
                posy = cursor.y() - win_heigth + 15
                angley = 'bottom'
            if (cursor.x() + 30 + win_width) >= screen_maxX:
                posx = cursor.x() - win_width + 15
                anglex = 'right'
            else:
                posx = cursor.x() - 15
                anglex = 'left'

            self.move(posx, posy)
        else:
            self.close()

    def showEvent(self, event):
        self.move_ui()
        self.search_bar.search_bar.setFocus()
        event.accept()

    def clear(self):
        self.search_bar.setText('')

    def leaveEvent(self, event):
        self.close()

    def search_ended(self):
        if self.list_view.invisibleRootItem().childCount() == 0:
            self.show_info_mode('No export found...', ressources._nothing_info_)
        else:
            self.hide_info_mode()

    def search_asset(self, search):
        self.accept_item_from_thread = False
        self.list_view.clear()
        self.variant_ids = dict()
        self.groups_ids = dict()
        if len(search) > 1:
            self.accept_item_from_thread = True
            self.search_thread.update_search(search)
        else:
            self.search_thread.running=False
            self.search_ended()

    def add_item(self, item_list):
        if self.accept_item_from_thread:
            if item_list[3]['id'] not in self.variant_ids.keys():
                variant_item = custom_item(item_list[0], item_list[1], item_list[2], item_list[3], self.list_view.invisibleRootItem())
                self.variant_ids[item_list[3]['id']] = variant_item

    def add_group(self, group_row):
        if self.accept_item_from_thread:
            if group_row['id'] not in self.groups_ids.keys():
                group_item = custom_group_item(group_row, self.list_view.invisibleRootItem())
                self.groups_ids[group_row['id']] = group_item

    def connect_functions(self):
        self.search_bar.textChanged.connect(self.search_asset)
        self.search_thread.item_signal.connect(self.add_item)
        self.search_thread.group_signal.connect(self.add_group)
        self.search_thread.search_ended.connect(self.search_ended)
        self.list_view.itemDoubleClicked.connect(self.return_references)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Down:
            self.list_view.keyPressEvent(event)
        if event.key() == QtCore.Qt.Key_Up:
            self.list_view.keyPressEvent(event)
        if event.key() == QtCore.Qt.Key_Return:
            self.return_references()
        event.accept()

    def return_references(self):
        selected_items = self.list_view.selectedItems()
        if selected_items is not None and len(selected_items)>=1:
            variant_ids = []
            groups_ids = []
            for selected_item in selected_items:
                if selected_item.type == 'variant':
                    variant_ids.append(selected_item.variant_row['id'])
                elif selected_item.type == 'group':
                    groups_ids.append(selected_item.group_row['id'])
            if variant_ids != []:
                self.variant_ids_signal.emit(variant_ids)
            if groups_ids != []:
                self.groups_ids_signal.emit(groups_ids)
            self.close()

    def show_info_mode(self, text, image):
        self.list_view.setVisible(0)
        self.info_widget.setVisible(1)
        self.info_widget.setText(text)
        self.info_widget.setImage(image)

    def hide_info_mode(self):
        self.info_widget.setVisible(0)
        self.list_view.setVisible(1)

    def build_ui(self):
        self.setMinimumWidth(550)
        self.setMinimumHeight(500)
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(12,12,12,12)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.main_widget = QtWidgets.QWidget()
        self.main_widget.setStyleSheet('border-radius:5px;')
        self.main_widget_layout = QtWidgets.QVBoxLayout()
        self.main_widget_layout.setContentsMargins(0,0,0,0)
        self.main_widget_layout.setSpacing(0)
        self.main_widget.setLayout(self.main_widget_layout)
        self.main_layout.addWidget(self.main_widget)

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(12)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 180))
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.main_widget.setGraphicsEffect(self.shadow)

        self.search_bar = gui_utils.search_bar()
        self.search_bar.setPlaceholderText('"asset", "category:asset"')
        self.main_widget_layout.addWidget(self.search_bar)

        self.info_widget = gui_utils.info_widget()
        self.info_widget.setVisible(0)
        self.main_widget_layout.addWidget(self.info_widget)

        self.list_view = QtWidgets.QTreeWidget()
        self.list_view.setObjectName('tree_as_list_widget')
        self.list_view.setStyleSheet('border-top-left-radius:0px;border-top-right-radius:0px;')
        self.list_view.setColumnCount(4)
        self.list_view.setHeaderHidden(True)
        self.list_view.setIndentation(0)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.header().resizeSection(0, 100)
        self.list_view.header().resizeSection(1, 150)
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.main_widget_layout.addWidget(self.list_view)
        self.show_info_mode('No export found...', ressources._nothing_info_)

class search_thread(QtCore.QThread):

    item_signal = pyqtSignal(list)
    group_signal = pyqtSignal(object)
    search_ended = pyqtSignal(int)

    def __init__(self, context):
        super().__init__()
        self.context = context
        self.running = True

    def update_search(self, string):
        self.running = False
        self.string = string
        self.start()

    def run(self):
        self.running = True
        keywords = self.string.split('&') 
        all_export_versions_variant_ids = project.get_all_export_versions('variant_id')
        all_variants = project.get_all_variants()
        all_stages = project.get_all_stages()
        all_assets = project.get_all_assets()
        all_categories = project.get_all_categories()
        stages = dict()
        for stage_row in all_stages:
            stages[stage_row['id']] = stage_row
        assets = dict()
        for asset_row in all_assets:
            assets[asset_row['id']] = asset_row    
        categories = dict()
        for category_row in all_categories:
            categories[category_row['id']] = category_row
        for variant_row in all_variants:
            if variant_row['id'] in all_export_versions_variant_ids:
                if all(keyword.upper() in variant_row['string'].upper() for keyword in keywords):
                    stage_row = stages[variant_row['stage_id']]
                    asset_row = assets[stage_row['asset_id']]
                    category_row = categories[asset_row['category_id']]
                    self.item_signal.emit([category_row, asset_row, stage_row, variant_row])
        if (self.context == 'work_env'):
                groups_rows = project.get_groups()
                for group_row in groups_rows:
                    if all(keyword.upper() in group_row['name'].upper()+'GROUPS' for keyword in keywords):
                        self.group_signal.emit(group_row)
        self.search_ended.emit(1)

class custom_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, category_row, asset_row, stage_row, variant_row, parent=None):
        super(custom_item, self).__init__(parent)
        self.type = 'variant'
        self.category_row = category_row
        self.asset_row = asset_row
        self.stage_row = stage_row
        self.variant_row = variant_row
        self.fill_ui()

    def fill_ui(self):
        self.setText(0, self.category_row['name'])
        self.setText(1, self.asset_row['name'])
        bold_font=QtGui.QFont()
        bold_font.setBold(True)
        self.setFont(1, bold_font)
        self.setText(2, self.stage_row['name'])
        self.setIcon(2, QtGui.QIcon(ressources._stage_icons_dic_[self.stage_row['name']]))
        self.setText(3, self.variant_row['name'])

class custom_group_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, group_row, parent=None):
        super(custom_group_item, self).__init__(parent)
        self.type = 'group'
        self.group_row = group_row
        self.fill_ui()

    def fill_ui(self):
        self.setText(1, self.group_row['name'])
        self.setText(0, 'group')
        self.setIcon(1, gui_utils.QIcon_from_svg(ressources._group_icon_,
                                                    self.group_row['color']))
        bold_font=QtGui.QFont()
        bold_font.setBold(True)
        self.setFont(1, bold_font)
