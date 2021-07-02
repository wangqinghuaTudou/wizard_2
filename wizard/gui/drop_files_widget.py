# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import os

# Wizard modules
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils

class drop_files_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(drop_files_widget, self).__init__(parent)
        self.files_widgets = []
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(6)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_layout)

        self.files_scrollArea = QtWidgets.QScrollArea()
        self.files_scrollArea.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.files_scrollArea.setVisible(False)

        self.files_scrollArea_widget = QtWidgets.QWidget()
        self.files_scrollArea_layout = QtWidgets.QHBoxLayout()
        self.files_scrollArea_layout.setSpacing(6)
        self.files_scrollArea_layout.setContentsMargins(0,0,0,0)
        self.files_scrollArea_widget.setLayout(self.files_scrollArea_layout)

        self.files_scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.files_scrollArea.setWidgetResizable(True)
        self.files_scrollArea.setWidget(self.files_scrollArea_widget)

        self.main_layout.addWidget(self.files_scrollArea)

        self.drop_files_button = drop_files_button()
        self.main_layout.addWidget(self.drop_files_button)

    def files(self):
        files_list = []
        for file_widget in self.files_widgets:
            files_list.append(file_widget.file)
        return files_list

    def connect_functions(self):
        self.drop_files_button.new_file.connect(self.add_file)
        self.drop_files_button.clicked.connect(self.open_files)

    def open_files(self):
        options = QtWidgets.QFileDialog.Options()
        fileList, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "",
                                                  "All Files (*);", options=options)
        if fileList:
            for file in fileList:
                self.add_file(file)

    def add_file(self, file):
        new_file_widget = file_widget(file)
        new_file_widget.remove_file.connect(self.remove_file)
        self.files_widgets.append(new_file_widget)
        self.files_scrollArea_layout.addWidget(new_file_widget)
        self.update_files_visibility()

    def remove_file(self, file_widget):
        if file_widget in self.files_widgets:
            self.files_widgets.remove(file_widget)
        file_widget.setParent(None)
        file_widget.deleteLater()
        self.update_files_visibility()

    def update_files_visibility(self):
        if len(self.files_widgets)>=1:
            self.files_scrollArea.setVisible(1)
        else:
            self.files_scrollArea.setVisible(0)

class file_widget(QtWidgets.QFrame):

    remove_file = pyqtSignal(object)

    def __init__(self, file, parent=None):
        super(file_widget, self).__init__(parent)
        self.file = file
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.setObjectName('file_frame')
        self.setMaximumHeight(30)
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(6,6,6,6)
        self.main_layout.setSpacing(4)
        self.setLayout(self.main_layout)
        
        self.main_label = QtWidgets.QLabel(os.path.basename(self.file))
        self.main_layout.addWidget(self.main_label)

        self.remove_file_button = QtWidgets.QPushButton()
        self.remove_file_button.setIcon(QtGui.QIcon(ressources._close_thin_icon_))
        self.remove_file_button.setIconSize(QtCore.QSize(18,18))
        self.remove_file_button.setFixedSize(18,18)
        self.main_layout.addWidget(self.remove_file_button)

    def connect_functions(self):
        self.remove_file_button.clicked.connect(lambda:self.remove_file.emit(self))

class drop_files_button(QtWidgets.QPushButton):

    new_file = pyqtSignal(str)

    def __init__(self, parent=None):
        super(drop_files_button, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName('drop_files_button')
        self.setIcon(QtGui.QIcon(ressources._dragdrop_))
        self.setIconSize(QtCore.QSize(40,40))
        self.setMinimumHeight(50)
        self.setText('Drop files here or click to attach files')

    def dragEnterEvent(self, event):
        self.setStyleSheet('background-color: #4b4b57;')
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.setStyleSheet('')

    def dropEvent(self, event):
        self.setStyleSheet('')
        data = event.mimeData()
        urls = data.urls()

        for url in urls:
            if url and url.scheme() == 'file':
                path = str(url.path())[1:]
                self.new_file.emit(path)
