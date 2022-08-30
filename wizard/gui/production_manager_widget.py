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
from wizard.gui import overview_widget
from wizard.gui import production_table_widget
from wizard.gui import custom_tab_widget

# Wizard core modules
from wizard.core import user
from wizard.vars import ressources
from wizard.vars import user_vars

logger = logging.getLogger(__name__)

class production_manager_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(production_manager_widget, self).__init__(parent)

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Production manager")

        self.overview_widget = overview_widget.overview_widget()
        self.production_table_widget = production_table_widget.production_table_widget()
        self.build_ui()

    def build_ui(self):
        self.resize(1300,1000)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.tabs_widget = custom_tab_widget.custom_tab_widget()
        self.main_layout.addWidget(self.tabs_widget)

        self.production_table_index = self.tabs_widget.addTab(self.production_table_widget, '', QtGui.QIcon(ressources._table_viewer_icon_))
        self.overview_index = self.tabs_widget.addTab(self.overview_widget, '', QtGui.QIcon(ressources._chart_icon_))

    def set_context(self):
        current_tab = self.tabs_widget.current_index()
        context_dic = dict()
        context_dic['current_tab'] = current_tab
        user.user().add_context(user_vars._production_manager_context_, context_dic)

    def get_context(self):
        context_dic = user.user().get_context(user_vars._production_manager_context_)
        if context_dic is not None and context_dic != dict():
            current_tab = context_dic['current_tab']
            self.tabs_widget.tab_selected(current_tab)

    def refresh(self):
        self.overview_widget.refresh()
        self.production_table_widget.refresh()

    def toggle(self):
        if self.isVisible():
            if not self.isActiveWindow():
                self.show()
                self.raise_()
                self.refresh()
            else:
                self.hide()
        else:
            self.show()
            self.raise_()
            self.refresh()