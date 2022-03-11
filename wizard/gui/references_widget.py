# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import time
import logging

# Wizard gui modules
from wizard.gui import search_reference_widget
from wizard.gui import gui_utils
from wizard.gui import gui_server

# Wizard modules
from wizard.core import assets
from wizard.core import launch
from wizard.core import project
from wizard.vars import ressources

logger = logging.getLogger(__name__)

class references_widget(QtWidgets.QWidget):

    focus_export = pyqtSignal(int)
    focus_on_group_signal = pyqtSignal(int)

    def __init__(self, context='work_env', parent=None):
        super(references_widget, self).__init__(parent)
        self.reference_infos_thread = reference_infos_thread()
        self.context = context
        self.group_item = None
        self.parent_instance_id = None
        self.reference_ids = dict()
        self.referenced_group_ids = dict()
        self.stage_dic = dict()
        self.build_ui()
        self.connect_functions()
        self.show_info_mode("Select or create a stage\nin the project tree !", ressources._select_stage_info_image_)

    def show_info_mode(self, text, image):
        self.list_view.setVisible(0)
        self.info_widget.setVisible(1)
        self.info_widget.setText(text)
        self.info_widget.setImage(image)

    def hide_info_mode(self):
        self.info_widget.setVisible(0)
        self.list_view.setVisible(1)

    def connect_functions(self):
        self.search_sc = QtWidgets.QShortcut(QtGui.QKeySequence('Tab'), self)
        self.search_sc.activated.connect(self.search_reference)
        self.reference_infos_thread.reference_infos_signal.connect(self.update_item_infos)
        self.list_view.itemSelectionChanged.connect(self.refresh_infos)
        self.list_view.itemDoubleClicked.connect(self.item_double_clicked)
        self.list_view.customContextMenuRequested.connect(self.context_menu_requested)

        self.remove_selection_button.clicked.connect(self.remove_selection)
        self.update_button.clicked.connect(self.update_selection)
        self.add_reference_button.clicked.connect(self.search_reference)

    def update_item_infos(self, infos_list):
        reference_id = infos_list[0]
        if reference_id in self.reference_ids.keys():
            self.reference_ids[reference_id].update_item_infos(infos_list)

    def search_reference(self):
        if self.parent_instance_id is not None and self.parent_instance_id != 0:
            self.search_reference_widget = search_reference_widget.search_reference_widget(self)
            self.search_reference_widget.variant_ids_signal.connect(self.create_references_from_variant_ids)
            self.search_reference_widget.groups_ids_signal.connect(self.create_referenced_groups)
            self.search_reference_widget.show()

            if self.context == 'work_env':
                variant_row = project.get_variant_data(project.get_work_env_data(self.parent_instance_id, 'variant_id'))
                stage_row = project.get_stage_data(variant_row['stage_id'])
                asset_row = project.get_asset_data(stage_row['asset_id'])
                category_row = project.get_category_data(asset_row['category_id'])
                self.search_reference_widget.search_asset(f"{category_row['name']}:{asset_row['name']}")
            else:
                self.search_reference_widget.search_asset(f"")

    def create_references_from_variant_ids(self, variant_ids):
        if self.parent_instance_id is not None:
            for variant_id in variant_ids:
                if self.context == 'work_env':
                    if assets.create_references_from_variant_id(self.parent_instance_id, variant_id):
                        gui_server.refresh_ui()
                else:
                    if assets.create_grouped_references_from_variant_id(self.parent_instance_id, variant_id):
                        gui_server.refresh_ui()

    def create_referenced_groups(self, groups_ids):
        if self.context == 'work_env':
            for group_id in groups_ids:
                assets.create_referenced_group(self.parent_instance_id, group_id)
            gui_server.refresh_ui()

    def change_work_env(self, work_env_id):
        self.reference_ids = dict()
        self.referenced_group_ids = dict()
        self.stage_dic = dict()
        self.group_item = None
        self.list_view.clear()
        self.parent_instance_id = work_env_id
        self.refresh()

    def refresh(self):
        start_time = time.time()
        if self.isVisible():
            if self.parent_instance_id is not None and self.parent_instance_id != 0:
                if self.context == 'work_env':
                    reference_rows = project.get_references(self.parent_instance_id)
                    referenced_groups_rows = project.get_referenced_groups(self.parent_instance_id)
                else:
                    reference_rows = project.get_grouped_references(self.parent_instance_id)
                    referenced_groups_rows = []
                if (reference_rows is not None) or (referenced_groups_rows is not None):
                    self.hide_info_mode()
                    if (len(reference_rows) >=1) or (len(referenced_groups_rows) >=1):
                        self.add_references_rows(reference_rows)
                        self.add_referenced_groups_rows(referenced_groups_rows)
                    else:
                        self.show_info_mode("No references\nPress Tab to create a reference !", ressources._references_info_image_)
            elif self.parent_instance_id is None:
                if self.context == 'work_env':
                    self.show_info_mode("You need to init the work environment\nto create references...", ressources._init_work_env_info_image_)
                else:
                    self.show_info_mode("You need to add a group\nto create references...", ressources._add_group_info_image_)
            else:
                self.show_info_mode("Select or create a stage\nin the project tree !", ressources._select_stage_info_image_)
            self.refresh_infos()
        self.update_refresh_time(start_time)

    def add_references_rows(self, reference_rows):
        project_references_id = []
        for reference_row in reference_rows:
            project_references_id.append(reference_row['id'])
            if reference_row['id'] not in self.reference_ids.keys():
                stage = reference_row['stage']
                if stage not in self.stage_dic.keys():
                    stage_item = custom_stage_tree_item(stage, self.list_view.invisibleRootItem())
                    self.stage_dic[stage] = stage_item
                reference_item = custom_reference_tree_item(reference_row, self.context, self.stage_dic[stage])
                self.reference_ids[reference_row['id']] = reference_item
            else:
                self.reference_ids[reference_row['id']].reference_row = reference_row
        references_list_ids = list(self.reference_ids.keys())
        for reference_id in references_list_ids:
            if reference_id not in project_references_id:
                self.remove_reference_item(reference_id)
        self.reference_infos_thread.update_references_rows(reference_rows)
        self.update_stages_items()

    def add_referenced_groups_rows(self, referenced_groups_rows):
        self.add_group_item()
        project_referenced_groups_id = []
        for referenced_group_row in referenced_groups_rows:
            project_referenced_groups_id.append(referenced_group_row['id'])
            if referenced_group_row['id'] not in self.referenced_group_ids.keys():
                referenced_group_item = custom_referenced_group_tree_item(referenced_group_row,
                                                            self.group_item)
                self.referenced_group_ids[referenced_group_row['id']] = referenced_group_item
        referenced_group_list_ids = list(self.referenced_group_ids.keys())
        for referenced_group_id in referenced_group_list_ids:
            if referenced_group_id not in project_referenced_groups_id:
                self.remove_referenced_group_item(referenced_group_id)
        self.update_group_item()

    def update_refresh_time(self, start_time):
        refresh_time = str(round((time.time()-start_time), 3))
        self.refresh_label.setText(f"- refresh : {refresh_time}s")

    def remove_selection(self):
        selected_items = self.list_view.selectedItems()
        for selected_item in selected_items:
            if selected_item.type == 'reference':
                reference_id = selected_item.reference_row['id']
                if self.context == 'work_env':
                    assets.remove_reference(reference_id)
                else:
                    assets.remove_grouped_reference(reference_id)
            elif selected_item.type == 'group':
                referenced_group_id = selected_item.referenced_group_row['id']
                assets.remove_referenced_group(referenced_group_id)
        gui_server.refresh_ui()

    def update_selection(self):
        selected_items = self.list_view.selectedItems()
        for selected_item in selected_items:
            if selected_item.type == 'reference':
                reference_id = selected_item.reference_row['id']
                if self.context == 'work_env':
                    assets.set_reference_last_version(reference_id)
                else:
                    assets.set_grouped_reference_last_version(reference_id)
        gui_server.refresh_ui()

    def update_all(self):
        for reference_id in self.reference_ids.keys():
            if self.context == 'work_env':
                assets.set_reference_last_version(reference_id)
            else:
                assets.set_grouped_reference_last_version(reference_id)
        gui_server.refresh_ui()

    def launch_work_version(self):
        selected_items = self.list_view.selectedItems()
        for selected_item in selected_items:
            if selected_item.type == 'reference':
                export_version_id = selected_item.reference_row['export_version_id']
                export_version_row = project.get_export_version_data(export_version_id)
                if export_version_row['work_version_id'] is not None:
                    launch.launch_work_version(export_version_row['work_version_id'])
        gui_server.refresh_ui()

    def focus_on_export_version(self):
        selected_items = self.list_view.selectedItems()
        for selected_item in selected_items:
            if selected_item.type == 'reference':
                self.focus_export.emit(selected_item.reference_row['export_version_id'])

    def remove_reference_item(self, reference_id):
        if reference_id in self.reference_ids.keys():
            item = self.reference_ids[reference_id]
            item.parent().removeChild(item)
            del self.reference_ids[reference_id]

    def remove_referenced_group_item(self, referenced_group_id):
        if referenced_group_id in self.referenced_group_ids.keys():
            item = self.referenced_group_ids[referenced_group_id]
            item.parent().removeChild(item)
            del self.referenced_group_ids[referenced_group_id]

    def add_group_item(self):
        if self.group_item is None:
            self.group_item = custom_group_tree_item(self.list_view.invisibleRootItem())

    def update_group_item(self):
        if self.group_item is not None:
            childs = self.group_item.childCount()
            if childs == 0:
                pass
                self.list_view.invisibleRootItem().removeChild(self.group_item)
                self.group_item = None

    def update_stages_items(self):
        stages_list = list(self.stage_dic.keys())
        for stage in stages_list:
            item = self.stage_dic[stage]
            childs = item.childCount()
            if childs >= 1:
                item.update_infos(childs)
            else:
                self.list_view.invisibleRootItem().removeChild(item)
                del self.stage_dic[stage]

    def refresh_infos(self):
        references_count = len(self.reference_ids.keys())
        selection_count = len(self.list_view.selectedItems())
        self.references_count_label.setText(f"{references_count} references -")
        self.selection_count_label.setText(f"{selection_count} selected")

    def context_menu_requested(self):
        selection = self.list_view.selectedItems()
        menu = gui_utils.QMenu(self)
        remove_action = None
        update_action = None
        launch_action = None
        focus_action = None
        update_all_action = menu.addAction(QtGui.QIcon(ressources._tool_update_), 'Update all references')
        if len(selection)>=1:
            update_action = menu.addAction(QtGui.QIcon(ressources._tool_update_), 'Update selected references')
            remove_action = menu.addAction(QtGui.QIcon(ressources._tool_archive_), 'Remove selected references')
            if len(selection) == 1:
                if selection[0].type == 'reference':
                    launch_action = menu.addAction(QtGui.QIcon(ressources._launch_icon_), 'Launch related work version')
                    focus_action = menu.addAction(QtGui.QIcon(ressources._tool_focus_), 'Focus on export instance')
        add_action = menu.addAction(QtGui.QIcon(ressources._tool_add_), 'Add references (Tab)')

        action = menu.exec_(QtGui.QCursor().pos())
        if action is not None:
            if action == remove_action:
                self.remove_selection()
            elif action == update_action:
                self.update_selection()
            elif action == add_action:
                self.search_reference()
            elif action == update_all_action:
                self.update_all()
            elif action == launch_action:
                self.launch_work_version()
            elif action == focus_action:
                self.focus_on_export_version()

    def item_double_clicked(self, item):
        if item.type == 'group':
            self.focus_on_group_signal.emit(item.referenced_group_row['group_id'])

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.info_widget = gui_utils.info_widget()
        self.info_widget.setVisible(0)
        self.main_layout.addWidget(self.info_widget)

        self.list_view = QtWidgets.QTreeWidget()
        self.list_view.setAnimated(1)
        self.list_view.setExpandsOnDoubleClick(1)
        self.list_view.setObjectName('tree_as_list_widget')
        self.list_view.setColumnCount(5)
        self.list_view.setIndentation(20)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.setHeaderLabels(['Stage', 'Namespace', 'Variant', 'Exported asset', 'Export version'])
        self.list_view.header().resizeSection(0, 200)
        self.list_view.header().resizeSection(1, 250)
        self.list_view.header().resizeSection(3, 250)
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.list_view_scrollBar = self.list_view.verticalScrollBar()
        self.main_layout.addWidget(self.list_view)

        self.infos_widget = QtWidgets.QWidget()
        self.infos_widget.setObjectName('dark_widget')
        self.infos_layout = QtWidgets.QHBoxLayout()
        self.infos_layout.setContentsMargins(8,8,8,0)
        self.infos_layout.setSpacing(4)
        self.infos_widget.setLayout(self.infos_layout)
        self.main_layout.addWidget(self.infos_widget)

        self.infos_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.references_count_label = QtWidgets.QLabel()
        self.references_count_label.setObjectName('gray_label')
        self.infos_layout.addWidget(self.references_count_label)

        self.selection_count_label = QtWidgets.QLabel()
        self.infos_layout.addWidget(self.selection_count_label)

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
        self.search_bar.setPlaceholderText('"0023", "user:j.smith", "comment:retake eye", "from:houdini"')
        self.buttons_layout.addWidget(self.search_bar)

        self.remove_selection_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.remove_selection_button, "Remove selected references")
        self.remove_selection_button.setFixedSize(35,35)
        self.remove_selection_button.setIconSize(QtCore.QSize(25,25))
        self.remove_selection_button.setIcon(QtGui.QIcon(ressources._tool_archive_))
        self.buttons_layout.addWidget(self.remove_selection_button)

        self.add_reference_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.add_reference_button, "Add references (Tab)")
        self.add_reference_button.setFixedSize(35,35)
        self.add_reference_button.setIconSize(QtCore.QSize(25,25))
        self.add_reference_button.setIcon(QtGui.QIcon(ressources._tool_add_))
        self.buttons_layout.addWidget(self.add_reference_button)

        self.update_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.update_button, "Update selected references")
        self.update_button.setFixedSize(35,35)
        self.update_button.setIconSize(QtCore.QSize(25,25))
        self.update_button.setIcon(QtGui.QIcon(ressources._tool_update_))
        self.buttons_layout.addWidget(self.update_button)     

class custom_stage_tree_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, stage, parent=None):
        super(custom_stage_tree_item, self).__init__(parent)
        self.stage = stage
        self.setFlags(QtCore.Qt.ItemIsEnabled)
        self.setExpanded(1)
        self.fill_ui()

    def fill_ui(self):
        self.setText(0, self.stage)
        self.setIcon(0, QtGui.QIcon(ressources._stage_icons_dic_[self.stage]))

    def update_infos(self, childs):
        self.setText(0, f"{self.stage} ({childs})")

class custom_group_tree_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, parent=None):
        super(custom_group_tree_item, self).__init__(parent)
        self.setFlags(QtCore.Qt.ItemIsEnabled)
        self.setExpanded(1)
        self.setText(0, 'Groups')

class custom_referenced_group_tree_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, referenced_group_row, parent=None):
        super(custom_referenced_group_tree_item, self).__init__(parent)
        self.type = 'group'
        self.referenced_group_row = referenced_group_row
        self.fill_ui()

    def fill_ui(self):
        self.setText(0, self.referenced_group_row['group_name'])
        self.setText(1, self.referenced_group_row['namespace'])
        bold_font=QtGui.QFont()
        bold_font.setBold(True)
        self.setFont(1, bold_font)
        self.setIcon(0, QtGui.QIcon(ressources._group_icon_))

class custom_reference_tree_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, reference_row, context, parent=None):
        super(custom_reference_tree_item, self).__init__(parent)
        self.context = context
        self.type = 'reference'
        self.reference_row = reference_row
        self.fill_ui()
        self.connect_functions()

    def fill_ui(self):
        self.setText(1, self.reference_row['namespace'])
        bold_font=QtGui.QFont()
        bold_font.setBold(True)
        self.setFont(1, bold_font)
        self.variant_widget = editable_data_widget()
        self.treeWidget().setItemWidget(self, 2, self.variant_widget)
        self.export_widget = editable_data_widget()
        self.treeWidget().setItemWidget(self, 3, self.export_widget)
        self.version_widget = editable_data_widget(bold=True)
        self.treeWidget().setItemWidget(self, 4, self.version_widget)

        self.setIcon(0, QtGui.QIcon(ressources._stage_icons_dic_[self.reference_row['stage']]))

    def update_item_infos(self, infos_list):
        self.variant_widget.setText(infos_list[1])
        self.export_widget.setText(infos_list[2])
        self.version_widget.setText(infos_list[3])
        if infos_list[4]:
            self.version_widget.setColor('#9ce87b')
        else:
            self.version_widget.setColor('#f79360')

    def connect_functions(self):
        self.version_widget.button_clicked.connect(self.version_modification_requested)
        self.export_widget.button_clicked.connect(self.export_modification_requested)
        self.variant_widget.button_clicked.connect(self.variant_modification_requested)

    def variant_modification_requested(self, point):
        variant_id = project.get_export_data(self.reference_row['export_id'], 'variant_id')
        stage_id = project.get_variant_data(variant_id, 'stage_id')
        variants_list = project.get_stage_childs(stage_id)
        if variants_list is not None and variants_list != []:
            menu = gui_utils.QMenu()
            for variant in variants_list:
                action = menu.addAction(variant['name'])
                action.id = variant['id']
            action = menu.exec_(QtGui.QCursor().pos())
            if action is not None:
                self.modify_variant(action.id)

    def export_modification_requested(self, point):
        variant_id = project.get_export_data(self.reference_row['export_id'], 'variant_id')
        exports_list = project.get_variant_export_childs(variant_id)
        if exports_list is not None and exports_list != []:
            menu = gui_utils.QMenu()
            for export in exports_list:
                action = menu.addAction(export['name'])
                action.id = export['id']
            action = menu.exec_(QtGui.QCursor().pos())
            if action is not None:
                self.modify_export(action.id)

    def version_modification_requested(self, point):
        versions_list = project.get_export_versions(self.reference_row['export_id'])
        if versions_list is not None and versions_list != []:
            menu = gui_utils.QMenu()
            for version in versions_list:
                if len(version['comment']) > 20:
                    comment = version['comment'][-20:] + '...'
                else:
                    comment = version['comment']
                action = menu.addAction(f"{version['name']} - {comment}")
                action.id = version['id']
            action = menu.exec_(QtGui.QCursor().pos())
            if action is not None:
                self.modify_version(action.id)

    def modify_version(self, export_version_id):
        if self.context == 'work_env':
            project.update_reference(self.reference_row['id'], export_version_id)
        else:
            project.update_grouped_reference(self.reference_row['id'], export_version_id)
        gui_server.refresh_ui()

    def modify_export(self, export_id):
        if self.context == 'work_env':
            project.modify_reference_export(self.reference_row['id'], export_id)
        else:
            project.modify_grouped_reference_export(self.reference_row['id'], export_id)
        gui_server.refresh_ui()

    def modify_variant(self, variant_id):
        if self.context == 'work_env':
            project.modify_reference_variant(self.reference_row['id'], variant_id)
        else:
            project.modify_grouped_reference_variant(self.reference_row['id'], variant_id)
        gui_server.refresh_ui()

class editable_data_widget(QtWidgets.QFrame):

    button_clicked = pyqtSignal(int)

    def __init__(self, parent=None, bold=False):
        super(editable_data_widget, self).__init__(parent)
        self.bold=bold
        self.build_ui()
        self.connect_functions()

    def connect_functions(self):
        self.main_button.clicked.connect(self.button_clicked.emit)

    def build_ui(self):
        self.setObjectName('reference_edit_widget')
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(8,4,4,4)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.label)
        if self.bold:
            bold_font=QtGui.QFont()
            bold_font.setBold(True)
            self.label.setFont(bold_font)

        self.main_button = QtWidgets.QPushButton()
        self.main_button.setObjectName('dropdown_button')
        self.main_button.setFixedSize(QtCore.QSize(14,14))
        self.main_layout.addWidget(self.main_button)

    def setText(self, text):
        self.label.setText(text)

    def setColor(self, color):
        self.setStyleSheet(f'color:{color}')

class reference_infos_thread(QtCore.QThread):

    reference_infos_signal = pyqtSignal(list)

    def __init__(self, parent=None):
        super(reference_infos_thread, self).__init__(parent)
        self.reference_rows = None
        self.running = True

    def run(self):
        if self.reference_rows is not None:
            for reference_row in self.reference_rows:
                export_version_row = project.get_export_version_data(reference_row['export_version_id'])
                export_row = project.get_export_data(export_version_row['export_id'])
                variant_row = project.get_variant_data(export_row['variant_id'])
                last_export_version_id = project.get_last_export_version(export_row['id'], 'id')

                if last_export_version_id[0] != reference_row['export_version_id']:
                    up_to_date = 0
                else:
                    up_to_date = 1

                self.reference_infos_signal.emit([reference_row['id'], variant_row['name'], export_row['name'], export_version_row['name'], up_to_date])

    def update_references_rows(self, reference_rows):
        self.running = False
        self.reference_rows = reference_rows
        self.running = True
        self.start()