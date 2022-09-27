# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard modules
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import tags_widget

class comment_widget(QtWidgets.QDialog):
    def __init__(self, parent=None, title='Add comment', old_comment='', propose_tags=True):
        super(comment_widget, self).__init__(parent)
        self.old_comment = old_comment
        self.build_ui(title)
        self.connect_functions()

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Comment")
        
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    def showEvent(self, event):
        gui_utils.move_ui(self)
        self.comment_field.setFocus()

    def build_ui(self, title):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(8,8,8,8)
        self.setLayout(self.main_layout)
        self.main_frame = QtWidgets.QFrame()
        self.main_frame.setObjectName('instance_creation_frame')
        self.frame_layout = QtWidgets.QVBoxLayout()
        self.frame_layout.setSpacing(6)
        self.main_frame.setLayout(self.frame_layout)
        self.main_layout.addWidget(self.main_frame)

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(70)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 80))
        self.shadow.setXOffset(2)
        self.shadow.setYOffset(2)
        self.main_frame.setGraphicsEffect(self.shadow)

        self.close_frame = QtWidgets.QFrame()
        self.close_layout = QtWidgets.QHBoxLayout()
        self.close_layout.setContentsMargins(2,2,2,2)
        self.close_layout.setSpacing(2)
        self.close_frame.setLayout(self.close_layout)
        self.close_layout.addWidget(QtWidgets.QLabel(title))
        self.spaceItem = QtWidgets.QSpacerItem(100,10,QtWidgets.QSizePolicy.Expanding)
        self.close_layout.addSpacerItem(self.spaceItem)
        self.close_pushButton = gui_utils.transparent_button(ressources._close_tranparent_icon_, ressources._close_icon_)
        self.close_pushButton.setFixedSize(16,16)
        self.close_pushButton.setIconSize(QtCore.QSize(12,12))
        self.close_layout.addWidget(self.close_pushButton)
        self.frame_layout.addWidget(self.close_frame)

        self.comment_field = QtWidgets.QTextEdit()
        self.comment_field.setText(self.old_comment)
        self.frame_layout.addWidget(self.comment_field)

        self.accept_button = QtWidgets.QPushButton('Comment')
        self.accept_button.setObjectName("blue_button")
        self.accept_button.setDefault(True)
        self.accept_button.setAutoDefault(True)
        self.frame_layout.addWidget(self.accept_button)

    def confirm(self):
    	self.comment = self.comment_field.toPlainText()
    	self.accept()

    def propose_tags(self):
        text = self.comment_field.toPlainText()
        if text.endswith('@'):
            position_rect = self.comment_field.cursorRect()
            pos = self.comment_field.mapToGlobal(QtCore.QPoint(position_rect.x()+20, position_rect.y()))
            self.tags_widget = tags_widget.tags_widget(pos)
            action = self.tags_widget.exec_()
            if action is not None:
                self.comment_field.insertHtml(f"<strong>{action.text()}</strong> ")

    def connect_functions(self):
        self.accept_button.clicked.connect(self.confirm)
        self.close_pushButton.clicked.connect(self.reject)
        self.comment_field.textChanged.connect(self.propose_tags)
