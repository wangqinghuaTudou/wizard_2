# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import time
import os
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal

# Wizard modules
from wizard.core import project
from wizard.core import assets
from wizard.core import environment
from wizard.vars import assets_vars

from wizard.core import logging
logging = logging.get_logger(__name__)

# Wizard gui modules
from wizard.gui import menu_widget

class tree_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(tree_widget, self).__init__(parent)

        self.domain_ids=dict()
        self.category_ids=dict()
        self.asset_ids=dict()
        self.stage_ids=dict()
        self.creation_items=[]

        self.build_ui()
        self.connect_functions()
        self.refresh()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.header_widget = QtWidgets.QWidget()
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_widget.setLayout(self.header_layout)

        self.header_layout.addWidget(QtWidgets.QLabel("Project :"))
        self.project_label = QtWidgets.QLabel(environment.get_project_name())
        self.header_layout.addWidget(self.project_label)
        self.spaceItem = QtWidgets.QSpacerItem(150,10,QtWidgets.QSizePolicy.Expanding)
        self.header_layout.addSpacerItem(self.spaceItem)
        self.main_layout.addWidget(self.header_widget)

        self.search_bar = QtWidgets.QLineEdit()
        self.main_layout.addWidget(self.search_bar)

        self.tree = QtWidgets.QTreeWidget()
        self.main_layout.addWidget(self.tree)
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.setHeaderHidden(True)

    def connect_functions(self):
        self.search_bar.textChanged.connect(self.search_asset)
        self.search_thread = search_thread()
        self.search_thread.item_signal.connect(self.add_search_item)
        self.tree.itemDoubleClicked.connect(self.double_click)
        self.tree.customContextMenuRequested.connect(self.context_menu_requested)

    def init_tree(self):
        self.get_context()
        self.domain_ids=dict()
        self.category_ids=dict()
        self.asset_ids=dict()
        self.stage_ids=dict()
        self.tree.clear()

    def get_context(self):
        self.expanded_domains = []
        self.expanded_categories = []
        self.expanded_assets = []
        for domain_id in self.domain_ids.keys():
            if self.domain_ids[domain_id].isExpanded():
                self.expanded_domains.append(domain_id)
        for category_id in self.category_ids.keys():
            if self.category_ids[category_id].isExpanded():
                self.expanded_categories.append(category_id)
        for asset_id in self.asset_ids.keys():
            if self.asset_ids[asset_id].isExpanded():
                self.expanded_assets.append(asset_id)

    def set_context(self):
        for id in self.expanded_domains:
            if id in self.domain_ids.keys():
                self.domain_ids[id].setExpanded(1)
        for id in self.expanded_categories:
            if id in self.category_ids.keys():
                self.category_ids[id].setExpanded(1)
        for id in self.expanded_assets:
            if id in self.asset_ids.keys():
                self.asset_ids[id].setExpanded(1)

    def refresh(self, hard=None):
        if hard:
            self.init_tree()

        self.project_category_ids = []
        self.project_asset_ids = []
        self.project_stage_ids = []

        for domain_row in project.get_domains():
            self.add_domain(domain_row)
        for category_row in project.get_all_categories():
            self.add_category(category_row)
            self.project_category_ids.append(category_row['id'])
        for asset_row in project.get_all_assets():
            self.add_asset(asset_row)
            self.project_asset_ids.append(asset_row['id'])
        for stage_row in project.get_all_stages():
            self.add_stage(stage_row)
            self.project_stage_ids.append(stage_row['id'])

        stage_ids = list(self.stage_ids.keys())
        for id in stage_ids:
            if id not in self.project_stage_ids:
                self.remove_stage(id)  

        asset_ids = list(self.asset_ids.keys())
        for id in asset_ids:
            if id not in self.project_asset_ids:
                self.remove_asset(id)     

        category_ids = list(self.category_ids.keys())
        for id in category_ids:
            if id not in self.project_category_ids:
                self.remove_category(id)

        self.apply_search()
        
        if hard:
            self.set_context()

    def add_domain(self, row):
        if row['id'] not in self.domain_ids.keys():
            domain_item = QtWidgets.QTreeWidgetItem([f"{row['name']}"])
            domain_item.type = 'domain'
            domain_item.id = row['id']
            self.domain_ids[row['id']] = domain_item
            self.tree.addTopLevelItem(domain_item)
            if row['id'] == 3:
                self.add_creation_item(domain_item, 'new', 'category_creation')

    def add_category(self, row):
        if row['id'] not in self.category_ids.keys():
            parent_widget = self.domain_ids[row['domain_id']]
            category_item = QtWidgets.QTreeWidgetItem([f"{row['name']}"])
            category_item.type = 'category'
            category_item.id = row['id']
            self.category_ids[row['id']] = category_item
            parent_widget.addChild(category_item)
            self.add_creation_item(category_item, 'new', 'asset_creation')

    def add_asset(self, row):
        if row['id'] not in self.asset_ids.keys():
            parent_widget = self.category_ids[row['category_id']]
            asset_item = QtWidgets.QTreeWidgetItem([f"{row['name']}"])
            asset_item.type = 'asset'
            asset_item.id = row['id']
            self.asset_ids[row['id']] = asset_item
            parent_widget.addChild(asset_item)
            domain_id = project.get_category_data(row['category_id'], 'domain_id')
            domain_name = project.get_domain_data(domain_id, 'name')
            for stage in assets_vars._stages_rules_dic_[domain_name]:
                self.add_creation_item(asset_item, stage, 'stage_creation')

    def add_stage(self, row):
        if row['id'] not in self.stage_ids.keys():
            parent_widget = self.asset_ids[row['asset_id']]
            stage_item = QtWidgets.QTreeWidgetItem([f"{row['name']}"])
            stage_item.type = 'stage'
            stage_item.id = row['id']
            self.stage_ids[row['id']] = stage_item
            parent_widget.addChild(stage_item)
            self.remove_stage_creation_item(parent_widget, row['name'])

    def remove_stage_creation_item(self, parent_widget, stage_name):
        child_count = parent_widget.childCount()
        for i in range(child_count):
            if stage_name == parent_widget.child(i).text(0) and parent_widget.child(i).type == 'stage_creation':
                self.creation_items.remove(parent_widget.child(i))
                parent_widget.takeChild(i)
                break

    def add_creation_item(self, parent_widget, text, item_type):
        creation_item = QtWidgets.QTreeWidgetItem([text])
        creation_item.type = item_type
        creation_item.parent_id = parent_widget.id
        parent_widget.addChild(creation_item)
        creation_item.setForeground(0, QtGui.QBrush(QtGui.QColor('gray')))
        self.creation_items.append(creation_item)

    def toggle_all_visibility(self, visibility):
        for id in self.domain_ids.keys():
            self.domain_ids[id].setHidden(visibility)
        for id in self.category_ids.keys():
            self.category_ids[id].setHidden(visibility)
        for id in self.asset_ids.keys():
            self.asset_ids[id].setHidden(visibility)

    def filter_stage(self, string):
        if not string or len(string)<2:
            for id in self.asset_ids.keys():
                for i in range(self.asset_ids[id].childCount()):
                    self.asset_ids[id].child(i).setHidden(0)
        else:
            for id in self.asset_ids.keys():
                for i in range(self.asset_ids[id].childCount()):
                    if string not in self.asset_ids[id].child(i).text(0):
                        self.asset_ids[id].child(i).setHidden(1)
                    else:
                        self.asset_ids[id].child(i).setHidden(0)

    def focus_on_item(self, item):
        self.tree.scrollToItem(item)
        self.tree.setCurrentItem(item)
        item.setExpanded(1)

    def apply_search(self):
        search = self.search_bar.text()
        self.search_asset(search)

    def search_asset(self, search):
        stage_filter = None
        if '.' in search:
            stage_filter = search.split('.')[-1]
            search = search.split('.')[0]
        self.filter_stage(stage_filter)
        if len(search) > 2:
            self.toggle_all_visibility(1)
            if ':' in search:
                category_string=search.split(':')[0]
                asset_string=search.split(':')[-1]
            else:
                category_string = None
                asset_string = search
            self.search_thread.update_search(category_string, asset_string)
        else:
            self.search_thread.running=False
            self.toggle_all_visibility(0)


    def double_click(self, item):

        new_stage_id = None
        new_asset_id = None
        new_category_id = None

        if item.type == 'stage_creation':
            stage_name = item.text(0)
            parent_id = item.parent_id
            new_stage_id = assets.create_stage(stage_name, parent_id)
            self.refresh()
        elif item.type == 'asset_creation':
            self.instance_creation_widget = instance_creation_widget(self)
            if self.instance_creation_widget.exec_() == QtWidgets.QDialog.Accepted:
                asset_name = self.instance_creation_widget.name_field.text()
                parent_id = item.parent_id
                new_asset_id = assets.create_asset(asset_name, parent_id)
                self.refresh()
        elif item.type == 'category_creation':
            self.instance_creation_widget = instance_creation_widget(self)
            if self.instance_creation_widget.exec_() == QtWidgets.QDialog.Accepted:
                category_name = self.instance_creation_widget.name_field.text()
                parent_id = item.parent_id
                new_category_id = assets.create_category(category_name, parent_id)
                self.refresh()

        if new_stage_id:
            if new_stage_id in self.stage_ids.keys():
                self.focus_on_item(self.stage_ids[new_stage_id])
        if new_asset_id:
            if new_asset_id in self.asset_ids.keys():
                self.focus_on_item(self.asset_ids[new_asset_id])
        if new_category_id:
            if new_category_id in self.stage_ids.keys():
                self.focus_on_item(self.new_category_id[new_category_id])

    def context_menu_requested(self, point):
        item = self.tree.itemAt(point)
        if item:
            self.menu_widget = menu_widget.menu_widget(self)
            open_folder_action = None
            archive_action = None
            if 'creation' not in item.type:
                open_folder_action = self.menu_widget.add_action(f'Open folder')
            if 'creation' not in item.type and item.type != 'domain':
                archive_action = self.menu_widget.add_action(f'Archive {item.type}')
            if self.menu_widget.exec_() == QtWidgets.QDialog.Accepted:
                if self.menu_widget.function_name is not None:
                    if self.menu_widget.function_name == archive_action:
                        self.archive_instance(item)
                    elif self.menu_widget.function_name == open_folder_action:
                        self.open_folder(item)

    def open_folder(self, item):
        if item.type == 'domain':
            path = assets.get_domain_path(item.id)
        elif item.type == 'category':
            path = assets.get_category_path(item.id)
        elif item.type == 'asset':
            path = assets.get_asset_path(item.id)
        elif item.type== 'stage':
            path = assets.get_stage_path(item.id)
        if os.path.isdir(path):
            os.startfile(path)
        else:
            logging.error(f"{path} not found")

    def archive_instance(self, item):
        if item.type == 'category':
            assets.archive_category(item.id)
        elif item.type == 'asset':
            assets.archive_asset(item.id)
        elif item.type== 'stage':
            assets.archive_stage(item.id)
        self.refresh()

    def remove_category(self, id):
        item = self.category_ids[id]
        item.parent().removeChild(item)
        del self.category_ids[id]

    def remove_asset(self, id):
        item = self.asset_ids[id]
        item.parent().removeChild(item)
        del self.asset_ids[id]

    def remove_stage(self, id):
        item = self.stage_ids[id]
        parent_item = item.parent()
        stage_name = item.text(0)
        parent_item.removeChild(item)
        del self.stage_ids[id]
        self.add_creation_item(parent_item, stage_name, 'stage_creation')

    def add_search_item(self, ids_list):
        self.domain_ids[ids_list[0]].setHidden(0)
        self.category_ids[ids_list[1]].setHidden(0)
        self.asset_ids[ids_list[2]].setHidden(0)

class instance_creation_widget(QtWidgets.QDialog):
    def __init__(self, parent=None, context='assets'):
        super(instance_creation_widget, self).__init__(parent)
        self.build_ui()
        self.connect_functions()
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.move_ui()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.name_field = QtWidgets.QLineEdit()
        self.main_layout.addWidget(self.name_field)
        self.accept_button = QtWidgets.QPushButton('Create')
        self.main_layout.addWidget(self.accept_button)

    def connect_functions(self):
        self.accept_button.clicked.connect(self.accept)

    def move_ui(self):
        win_size = (self.frameSize().width(), self.frameSize().height())
        posx = QtGui.QCursor.pos().x()
        posy = int(QtGui.QCursor.pos().y()) - win_size[1] + 10
        self.move(posx, posy)

class search_thread(QtCore.QThread):

    item_signal = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.category = None
        self.asset = None
        self.running = True

    def update_search(self, category=None, asset=None):
        self.running = False
        self.category = category
        self.asset = asset
        self.running = True
        self.start()

    def run(self):
        process=1
        parent_id = None
        if self.category and len(self.category)>2:
            category_id=project.get_category_data_by_name(self.category, 'id')
            if category_id:
                parent_id = category_id
        if self.category and not parent_id:
            process=None
        if process:
            assets_list = project.search_asset(self.asset, parent_id)
            for asset_row in assets_list:
                if not self.running:
                    break
                domain_id = project.get_category_data(project.get_asset_data(asset_row['id'], 'category_id'), 'domain_id')
                self.item_signal.emit([domain_id, asset_row['category_id'], asset_row['id']])

def main():
    app = QtWidgets.QApplication(sys.argv)
    widget = tree_widget()
    widget.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()