# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
import logging

# Wizard modules
from wizard.core import environment
from wizard.core import user
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils

logger = logging.getLogger(__name__)

class site_widget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(site_widget, self).__init__()

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Enter site")

        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(4)
        self.setLayout(self.main_layout)

        self.infos_label = QtWidgets.QLabel('Enter the wizard site')
        self.infos_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.infos_label)

        self.site_lineEdit = QtWidgets.QLineEdit()
        self.site_lineEdit.setPlaceholderText('Site name')
        self.main_layout.addWidget(self.site_lineEdit)

        self.button_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setSpacing(4)
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.button_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.button_widget)

        self.spaceItem = QtWidgets.QSpacerItem(100,0,QtWidgets.QSizePolicy.Expanding)
        self.buttons_layout.addSpacerItem(self.spaceItem)

        self.quit_button = QtWidgets.QPushButton('Quit')
        self.quit_button.setDefault(False)
        self.quit_button.setAutoDefault(False)
        self.buttons_layout.addWidget(self.quit_button)

        self.continue_button = QtWidgets.QPushButton('Continue')
        self.continue_button.setObjectName('blue_button')
        self.continue_button.setDefault(True)
        self.continue_button.setAutoDefault(True)
        self.buttons_layout.addWidget(self.continue_button)

    def connect_functions(self):
        self.continue_button.clicked.connect(self.apply)
        self.quit_button.clicked.connect(self.reject)

    def apply(self):
        site = self.site_lineEdit.text()
        if user.user().set_site(site):
            self.accept()