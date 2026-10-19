#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QMenu, QMenuBar
from PySide6.QtGui import QAction, QIcon
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt


class PDiM(QWidget):
    def __init__(self, ex_data, parent=None):
        super(PDiM, self).__init__(parent)
        """ Class to Create Menu Structure, etc. 
                Enables calls to functions for other classes so the QMainWindow may be populated """

        # Data Exchange between classes
        self.ex_data = ex_data
        self.base_path = self.ex_data.base_path

        # Attribute to access from QMainWindow for plotting
        self.plt = plt

        # A figure instance to plot on
        self.figure = plt.figure()
        self.plot_section = self.figure.add_subplot(111)  # 2d plot

        # The Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.updateGeometry()

        # The Navigation widget - It takes the Canvas widget and a parent
        # https://matplotlib.org/3.2.2/users/navigation_toolbar.html
        # https://scipy-lectures.org/intro/matplotlib/index.html
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Create Menu for User Work Flow
        # Instantiate variables
        self.menuBar = QMenuBar()

        # Create widget
        self.file_menu = QMenu("&File")  # '&' allows ALT + Letter for keyboard shortcut
        self.cv2_menu = QMenu("&OpenCV")
        self.extract_train_menu = QMenu("&Extraction and Training")
        self.view_menu = QMenu("Messages")
        self.help_menu = QMenu("Help")

        # Add each widget to the Menu
        self.menuBar.addMenu(self.file_menu)
        self.menuBar.addMenu(self.cv2_menu)
        self.menuBar.addMenu(self.extract_train_menu)
        self.menuBar.addMenu(self.view_menu)
        self.menuBar.addMenu(self.help_menu)

        # Under File Menu
        # Create an action, shortcut and tip associated with each widget
        self.pdf_pics = QAction(QIcon(self.base_path + "/pics/PDF_to_Pic.png"), 'PDF to Pic', self)
        self.file_menu.addAction(self.pdf_pics)
        self.pdf_pics.setShortcut('Ctrl+P')
        self.pdf_pics.setStatusTip('Converts pdfs to pictures and saves at same path')
        self.file_menu.addSeparator()

        self.load_pdf_pics = QAction(QIcon(self.base_path + "/pics/Camera.png"), 'Load Pic', self)
        self.file_menu.addAction(self.load_pdf_pics)
        self.load_pdf_pics.setShortcut('Ctrl+L')
        self.load_pdf_pics.setStatusTip('Loads pictures to prepare for image processing')

        # Add a subMenu
        self.rotate_menu = QMenu('Rotate Pic')  # Create the Menu
        self.file_menu.addMenu(self.rotate_menu)  # Add the sub_menu to the main QMenu
        # Clockwise
        self.rotate_clockwise_action = QAction(QIcon(self.base_path + "/pics/Rotate_Pic.png"), 'Clockwise', self)
        self.rotate_clockwise_action.setShortcut('Ctrl+C')
        self.rotate_menu.addAction(self.rotate_clockwise_action)  # Pass in the 'sub_menu_action' to the 'sub_menu'
        # Anticlockwise
        self.rotate_anticlock_action = QAction(QIcon(self.base_path + "/pics/Python.png"), 'Anticlockwise', self)
        self.rotate_anticlock_action.setShortcut('Ctrl+A')
        self.rotate_menu.addAction(self.rotate_anticlock_action)

        self.crop_pic = QAction(QIcon(self.base_path + "/pics/Crop_Pic.png"), 'Crop Pic', self)
        self.file_menu.addAction(self.crop_pic)
        self.crop_pic.setShortcut('Ctrl+E')
        self.crop_pic.setStatusTip('Crop Picture')

        self.save_pic = QAction(QIcon(self.base_path + "/pics/Save_Pic.png"), 'Save Pic', self)
        self.file_menu.addAction(self.save_pic)
        self.save_pic.setShortcut('Ctrl+S')
        self.save_pic.setStatusTip('Save Picture')

        self.save_as_pic = QAction(QIcon(self.base_path + "/pics/Save_As_Pic.png"), 'Save As....', self)
        self.file_menu.addAction(self.save_as_pic)
        self.save_as_pic.setStatusTip('Save the Picture with User defined name (no file extension)')
        self.file_menu.addSeparator()

        self.exit_action = self.file_menu.addAction(QIcon(self.base_path + "/pics/Exit_Pic.png"), "E&xit")
        self.file_menu.addAction(self.exit_action)
        self.exit_action.setStatusTip('Quit Application')

        # Under CV2 Menu
        self.erode_pdf_pics = QAction(QIcon(self.base_path + "/pics/Erode_Pic.png"), 'Process Tools', self)
        self.cv2_menu.addAction(self.erode_pdf_pics)
        self.erode_pdf_pics.setStatusTip('Apply Processing to picture')

        self.threshold_pdf_pics = QAction(QIcon(self.base_path + "/pics/Threshold_Pic.png"), 'Threshold Pic', self)
        self.cv2_menu.addAction(self.threshold_pdf_pics)
        self.threshold_pdf_pics.setStatusTip('Apply Threshold Kernel to picture')

        self.cc_stats_pdf_pics = QAction(QIcon(self.base_path + "/pics/Connected_Pic.png"),
                                         'Connected Components with Stats', self)
        self.cv2_menu.addAction(self.cc_stats_pdf_pics)
        self.cc_stats_pdf_pics.setStatusTip('Remove artifacts greater than specified size from picture')

        # Extraction and Training Data
        self.ext_digits_pics = QAction(QIcon(self.base_path + "/pics/Extract_Pic.png"), 'Extract Digits', self)
        self.extract_train_menu.addAction(self.ext_digits_pics)
        self.ext_digits_pics.setStatusTip('Apply Deep Learning or SVM to Extract Digits from picture')
        self.ext_digits_menu = QMenu('Select Format')  # Create the Menu
        self.extract_train_menu.addMenu(self.ext_digits_menu)  # Add the sub_menu to the main QMenu
        self.ext_digits_menu_action_GFEM = QAction(QIcon(self.base_path + "/pics/Extract_Pic.png"), 'GFEM', self)
        # self.ext_digits_menu_action.setStatusTip('Apply Deep Learning or SVM to Extract Digits from picture')
        self.ext_digits_menu.addAction(self.ext_digits_menu_action_GFEM)
        self.ext_digits_menu_action_1 = QAction(QIcon(self.base_path + "/pics/Extract_Pic.png"), 'Loads 1', self)
        self.ext_digits_menu.addAction(self.ext_digits_menu_action_1)
        self.ext_digits_menu_action_2 = QAction(QIcon(self.base_path + "/pics/Extract_Pic.png"), 'Loads 2', self)
        self.ext_digits_menu.addAction(self.ext_digits_menu_action_2)
        self.extract_train_menu.addSeparator()

        self.train_menu = QMenu('Train the')  # Create the Menu
        self.extract_train_menu.addMenu(self.train_menu)  # Add the sub_menu to the main QMenu
        self.train_menu_action = QAction(QIcon(self.base_path + "/pics/Training_Pic.png"), 'Model', self)
        # self.train_menu_action.setShortcut('Ctrl+T')
        self.train_menu.addAction(self.train_menu_action)  # Pass in the 'sub_menu_action' to the 'sub_menu'
        self.train_loads_action = QAction(QIcon(self.base_path + "/pics/Training_Pic.png"), 'Loads', self)
        self.train_menu.addAction(self.train_loads_action)

        # Under Messages Menu (add a checkable item)
        self.view_stat_act = QAction("Statusbar shows when checked", self, checkable=True)
        self.view_menu.addAction(self.view_stat_act)
        self.view_stat_act.setStatusTip('Get tips when Checked')
        self.view_stat_act.setChecked(True)
        self.view_quit = QAction("When checked Quit immediately", self, checkable=True)
        self.view_menu.addAction(self.view_quit)
        self.view_quit.setStatusTip('When Checked Application will Close without Prompting')
        self.view_quit.setChecked(True)

        # Under Help Menu
        self.recover_dock = QAction(QIcon(self.base_path + "/pics/Closed_Docks_Pic.png"), 'Show Closed Docks', self)
        self.help_menu.addAction(self.recover_dock)
        self.recover_dock.setShortcut('Ctrl+D')
        self.recover_dock.setStatusTip('Returns Dock if Closed')

        # Define the Main Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.menuBar)
        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.canvas)

        # Set the layout
        self.setLayout(main_layout)
