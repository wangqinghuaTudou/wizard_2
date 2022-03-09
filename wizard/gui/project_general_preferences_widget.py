# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
import logging

# Wizard modules
from wizard.core import image
from wizard.core import site
from wizard.core import project
from wizard.core import environment
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils

logger = logging.getLogger(__name__)

class project_general_preferences_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(project_general_preferences_widget, self).__init__(parent)
        self.build_ui()
        self.connect_functions()
        self.refresh()

    def refresh(self):
        frame_rate = project.get_frame_rate()
        image_format = project.get_image_format()
        project_name = environment.get_project_name()
        project_path = environment.get_project_path()
        self.frame_rate_spinBox.setValue(frame_rate)
        self.format_width.setValue(image_format[0])
        self.format_height.setValue(image_format[1])
        self.project_name_data.setText(project_name)
        self.project_path_data.setText(project_path)

        project_row = site.get_project_row_by_name(environment.get_project_name())
        project_image = image.convert_str_data_to_image_bytes(project_row['project_image'])
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(project_image)
        icon = QtGui.QIcon(pixmap)
        pm = gui_utils.round_corners_image_button(project_image, (250,140), 4)
        self.image_label.setPixmap(pm)

    def connect_functions(self):
        self.folder_image_button.clicked.connect(self.open_image)
        self.random_image_button.clicked.connect(self.get_random_image)
        self.frame_rate_accept_button.clicked.connect(self.apply_frame_rate)
        self.format_accept_button.clicked.connect(self.apply_format)

    def apply_frame_rate(self):
        frame_rate = self.frame_rate_spinBox.value()
        project.set_frame_rate(frame_rate)

    def apply_format(self):
        width = self.format_width.value()
        height = self.format_height.value()
        project.set_image_format([width, height])

    def get_random_image(self):
        project_name = environment.get_project_name()
        image_file = image.project_random_image(project_name)
        site.modify_project_image(environment.get_project_name(), image_file)
        self.refresh()

    def open_image(self):
        options = QtWidgets.QFileDialog.Options()
        image_file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select project image", "",
                            "All Files (*);;Images Files (*.png);;Images Files (*.jpg);;Images Files (*.jpeg)",
                            options=options)
        if image_file:
            extension = image_file.split('.')[-1].upper()
            if (extension == 'PNG') or (extension == 'JPG') or (extension == 'JPEG'):
                site.modify_project_image(environment.get_project_name(), image_file)
                self.refresh()
            else:
                logger.warning('{} is not a valid image file...'.format(image_file))

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollBar = self.scrollArea.verticalScrollBar()

        self.scrollArea_widget = QtWidgets.QWidget()
        self.scrollArea_widget.setObjectName('transparent_widget')
        self.scrollArea_layout = QtWidgets.QVBoxLayout()
        self.scrollArea_layout.setSpacing(12)
        self.scrollArea_widget.setLayout(self.scrollArea_layout)

        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollArea_widget)

        self.main_layout.addWidget(self.scrollArea)

        self.general_settings_title = QtWidgets.QLabel('General')
        self.general_settings_title.setObjectName('title_label')
        self.scrollArea_layout.addWidget(self.general_settings_title)

        self.scrollArea_layout.addWidget(gui_utils.separator())

        self.infos_frame = QtWidgets.QFrame()
        self.infos_frame.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.infos_layout = QtWidgets.QVBoxLayout()
        self.infos_layout.setContentsMargins(0,0,0,0)
        self.infos_layout.setSpacing(6)
        self.infos_frame.setLayout(self.infos_layout)
        self.scrollArea_layout.addWidget(self.infos_frame)

        self.infos_title = QtWidgets.QLabel('Infos')
        self.infos_title.setObjectName('bold_label')
        self.infos_layout.addWidget(self.infos_title)

        self.infos_subwidget = QtWidgets.QWidget()
        self.infos_sublayout = QtWidgets.QFormLayout()
        self.infos_sublayout.setContentsMargins(0,0,0,0)
        self.infos_sublayout.setSpacing(6)
        self.infos_subwidget.setLayout(self.infos_sublayout)
        self.infos_layout.addWidget(self.infos_subwidget)

        self.project_name_label = QtWidgets.QLabel('Project name')
        self.project_name_label.setObjectName('gray_label')
        self.project_name_data = QtWidgets.QLabel()
        self.project_name_data.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.infos_sublayout.addRow(self.project_name_label, self.project_name_data)

        self.project_path_label = QtWidgets.QLabel('Project path')
        self.project_path_label.setObjectName('gray_label')
        self.project_path_data = QtWidgets.QLabel()
        self.project_path_data.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.infos_sublayout.addRow(self.project_path_label, self.project_path_data)

        self.scrollArea_layout.addWidget(gui_utils.separator())

        self.image_frame = QtWidgets.QFrame()
        self.image_frame.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.image_layout = QtWidgets.QVBoxLayout()
        self.image_layout.setContentsMargins(0,0,0,0)
        self.image_layout.setSpacing(6)
        self.image_frame.setLayout(self.image_layout)
        self.scrollArea_layout.addWidget(self.image_frame)

        self.image_title = QtWidgets.QLabel('Project picture')
        self.image_title.setObjectName('bold_label')
        self.image_layout.addWidget(self.image_title)

        self.image_label = QtWidgets.QLabel()
        self.image_layout.addWidget(self.image_label)

        self.image_buttons_widget = QtWidgets.QWidget()
        self.image_buttons_layout = QtWidgets.QHBoxLayout()
        self.image_buttons_layout.setContentsMargins(0,0,0,0)
        self.image_buttons_layout.setSpacing(4)
        self.image_buttons_widget.setLayout(self.image_buttons_layout)
        self.image_layout.addWidget(self.image_buttons_widget)

        self.folder_image_button = QtWidgets.QPushButton()
        self.folder_image_button.setIcon(QtGui.QIcon(ressources._folder_icon_))
        self.folder_image_button.setIconSize(QtCore.QSize(20,20))
        self.folder_image_button.setFixedSize(28,28)
        self.image_buttons_layout.addWidget(self.folder_image_button)

        self.random_image_button = QtWidgets.QPushButton()
        self.random_image_button.setIcon(QtGui.QIcon(ressources._random_icon_))
        self.random_image_button.setIconSize(QtCore.QSize(20,20))
        self.random_image_button.setFixedSize(28,28)
        self.image_buttons_layout.addWidget(self.random_image_button)

        self.image_buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.scrollArea_layout.addWidget(gui_utils.separator())

        self.frame_rate_frame = QtWidgets.QFrame()
        self.frame_rate_frame.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.frame_rate_layout = QtWidgets.QVBoxLayout()
        self.frame_rate_layout.setContentsMargins(0,0,0,0)
        self.frame_rate_layout.setSpacing(6)
        self.frame_rate_frame.setLayout(self.frame_rate_layout)
        self.scrollArea_layout.addWidget(self.frame_rate_frame)

        self.frame_rate_title = QtWidgets.QLabel('Frame rate')
        self.frame_rate_title.setObjectName('bold_label')
        self.frame_rate_layout.addWidget(self.frame_rate_title)

        self.frame_rate_spinBox = QtWidgets.QSpinBox()
        self.frame_rate_spinBox.setRange(1, 300)
        self.frame_rate_spinBox.setFixedWidth(60)
        self.frame_rate_spinBox.setButtonSymbols(2)
        self.frame_rate_layout.addWidget(self.frame_rate_spinBox)

        self.frame_rate_buttons_widget = QtWidgets.QWidget()
        self.frame_rate_buttons_layout = QtWidgets.QHBoxLayout()
        self.frame_rate_buttons_layout.setContentsMargins(0,0,0,0)
        self.frame_rate_buttons_layout.setSpacing(6)
        self.frame_rate_buttons_widget.setLayout(self.frame_rate_buttons_layout)
        self.frame_rate_layout.addWidget(self.frame_rate_buttons_widget)

        self.frame_rate_buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.frame_rate_accept_button = QtWidgets.QPushButton('Apply')
        self.frame_rate_accept_button.setObjectName('blue_button')
        self.frame_rate_buttons_layout.addWidget(self.frame_rate_accept_button)

        self.scrollArea_layout.addWidget(gui_utils.separator())

        self.format_frame = QtWidgets.QFrame()
        self.format_frame.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.format_layout = QtWidgets.QVBoxLayout()
        self.format_layout.setContentsMargins(0,0,0,0)
        self.format_layout.setSpacing(6)
        self.format_frame.setLayout(self.format_layout)
        self.scrollArea_layout.addWidget(self.format_frame)

        self.format_title = QtWidgets.QLabel('Format')
        self.format_title.setObjectName('bold_label')
        self.format_layout.addWidget(self.format_title)
        
        self.format_widget = QtWidgets.QWidget()
        self.format_layout = QtWidgets.QHBoxLayout()
        self.format_layout.setContentsMargins(0,0,0,0)
        self.format_layout.setSpacing(4)
        self.format_widget.setLayout(self.format_layout)
        self.scrollArea_layout.addWidget(self.format_widget)

        self.format_width = QtWidgets.QSpinBox()
        self.format_width.setRange(1, 100000)
        self.format_width.setButtonSymbols(2)
        self.format_width.setValue(1920)
        self.format_layout.addWidget(self.format_width)

        self.format_height = QtWidgets.QSpinBox()
        self.format_height.setRange(1, 100000)
        self.format_height.setButtonSymbols(2)
        self.format_height.setValue(1080)
        self.format_layout.addWidget(self.format_height)

        self.format_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.format_buttons_widget = QtWidgets.QWidget()
        self.format_buttons_layout = QtWidgets.QHBoxLayout()
        self.format_buttons_layout.setContentsMargins(0,0,0,0)
        self.format_buttons_layout.setSpacing(6)
        self.format_buttons_widget.setLayout(self.format_buttons_layout)
        self.scrollArea_layout.addWidget(self.format_buttons_widget)

        self.format_buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.format_accept_button = QtWidgets.QPushButton('Apply')
        self.format_accept_button.setObjectName('blue_button')
        self.format_buttons_layout.addWidget(self.format_accept_button)

        self.scrollArea_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
