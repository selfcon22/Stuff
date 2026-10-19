#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from datetime import datetime
import sys
import re
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QDockWidget, QInputDialog, QLineEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import cv2
import numpy as np
import pandas as pd
from openpyxl import Workbook
from PIL.ImageQt import ImageQt
from PIL import Image
import PDiM_2_Setup as Menus
import PDiM_0_Ex_Data as EX_Data
import PDiM_3_PDF_PIC as PDF_Pic
import PDiM_4_Crop_etc as Crop_Reset
import PDiM_4_Opencv_Tools as CV_Tools
import PDiM_4_Opencv_Threshold as Threshold
import PDiM_4_Opencv_CCwithStats as CCwithStats
import PDiM_5_ML_Train as ML_Train
import PDiM_5_ML_Train_Loads as ML_Train_Loads
import PDiM_6_ML_Ext as ML_Ext
import PDiM_7_ML_Ext as ML_Ext_1
import PDiM_8_ML_Ext as ML_Ext_2
import S_Erode_Dilate as erode_dilate
import S_Sort_Contours as sort_contour
import S_CCwithStats as ccwstats
import S_OCR_NN_SVM as nn_svm
import S_NN_SVM_Loads_1 as nn_svm_loads_1
import S_NN_SVM_Loads_2 as nn_svm_loads_2


class PDiM(QMainWindow):
    def __init__(self, parent=None):
        super(PDiM, self).__init__(parent)
        """ Create a MainWindow to show [QWidget(s)] and QDockWidgets """

        self.setWindowTitle("Data Extraction from PDFs")
        self.setGeometry(600, 100, 1000, 900)    # Set window title, position and its width & height

        # Data Exchange between classes
        self.ex_data = EX_Data.ExchangeData()
        self.base_path = self.ex_data.base_path

        # Define the User Process Selected
        self.user_sel = None

        # ML Model (Neural Network, Support Vector Machine)
        self.ml_model = None

        # QMainWindow supports a status bar (in QMainWindow by default) - create an Object
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Messages, User information shown here.....")

        # Call module - PDiM_2_Setup and its class PDiM(QWidget) - Assign it so can access attributes of class
        self.menu_setup = Menus.PDiM(self.ex_data)

        # Call associated functions when action triggered
        # From File
        self.menu_setup.pdf_pics.triggered.connect(self.user_sel_analysis)
        self.menu_setup.load_pdf_pics.triggered.connect(self.plot_orig_pic)
        self.menu_setup.rotate_clockwise_action.triggered.connect(self.plot_rot_pic)
        self.menu_setup.rotate_anticlock_action.triggered.connect(self.plot_rot_pic)
        self.menu_setup.crop_pic.triggered.connect(self.user_sel_call)
        self.menu_setup.save_pic.triggered.connect(self.save_pic)
        self.menu_setup.save_as_pic.triggered.connect(self.save_pic)
        self.menu_setup.exit_action.triggered.connect(self.cancel_clicked)
        # From CV2
        self.menu_setup.erode_pdf_pics.triggered.connect(self.user_sel_call)
        self.menu_setup.threshold_pdf_pics.triggered.connect(self.user_sel_call)
        self.menu_setup.cc_stats_pdf_pics.triggered.connect(self.user_sel_call)
        # From Extraction and Training
        self.menu_setup.ext_digits_menu_action_GFEM.triggered.connect(self.user_sel_call)
        self.menu_setup.ext_digits_menu_action_1.triggered.connect(self.user_sel_call)
        self.menu_setup.ext_digits_menu_action_2.triggered.connect(self.user_sel_call)
        self.menu_setup.train_menu_action.triggered.connect(self.user_sel_call)
        self.menu_setup.train_loads_action.triggered.connect(self.user_sel_call)
        # From Help
        self.menu_setup.recover_dock.triggered.connect(self.dock_recover)
        self.menu_setup.view_stat_act.triggered.connect(self.show_messageMenu)
        # Call function to get (x, y) co-ords from matplotlib on mouse click
        self.menu_setup.canvas.mpl_connect('button_press_event', self.coords_mouse_click)
        self.menu_setup.canvas.mpl_connect('button_release_event', self.coords_mouse_release)

        # Call module for PDF Conversion
        self.pdf_pic = PDF_Pic.Form(self.ex_data, self.status_bar)

        # Call module for Pic Cropping and Reset
        self.crop_etc = Crop_Reset.Form(self.ex_data, self.status_bar)
        # self.crop_etc.Button_Crop.setDefault(True)
        self.crop_etc.Button_Crop.clicked.connect(self.plot_crop_pics)
        self.crop_etc.Button_Reset.clicked.connect(self.plot_orig_pic)
        # Capture event and call function when Checkbox toggled/pressed
        # self.crop_etc.Check_Batch.pressed.connect(self.batch_cv2_message)
        self.crop_etc.Check_Batch.stateChanged.connect(self.batch_cv2_message)
        self.crop_etc.Check_Batch.setText("Single")

        # Call module for CV2 Pic Processing
        self.cv_tools = CV_Tools.Form(self.ex_data, self.status_bar)
        self.cv_tools.Button_Batch_No.clicked.connect(self.batch_no_processing)
        self.cv_tools.Button_Erode_Kernel.clicked.connect(self.erode_dilate_open_pic)
        self.cv_tools.Button_Dilate_Kernel.clicked.connect(self.erode_dilate_open_pic)
        self.cv_tools.Button_Opening_Kernel.clicked.connect(self.erode_dilate_open_pic)
        self.cv_tools.Button_Remove_Kernel.clicked.connect(self.erode_dilate_open_pic)

        # Call module for Pic Thresholding
        self.threshold = Threshold.Form(self.ex_data, self.status_bar)
        self.threshold.Button_Threshold_Binary.clicked.connect(self.threshold_pic)
        self.threshold.Button_Threshold_Trunc.clicked.connect(self.threshold_pic)
        self.threshold.Button_Threshold_Tozero.clicked.connect(self.threshold_pic)
        self.threshold.Slide_Threshold_Max.valueChanged.connect(self.threshold_value)
        self.threshold.Slide_MaxValue.valueChanged.connect(self.threshold_value)

        # Call module to create Connected Components with Stats Processing Dock
        self.ccwithstats = CCwithStats.Form()
        self.ccwithstats.Button_Analysis.clicked.connect(self.ccwithstats_cv2)
        self.ccwithstats.Slide_Threshold_Max.valueChanged.connect(self.threshold_value)
        self.ccwithstats.Slide_MaxValue.valueChanged.connect(self.threshold_value)
        # Set Variables for CV2
        self.Orig_Pic = None
        self.CV2_Pre_Crop = None
        self.CV2_Complete = None

        # Call module to create Machine Learning Dock and.....
        self.ml_train = ML_Train.Form(self.ex_data, self.status_bar)
        self.ml_train.Button_Train.clicked.connect(self.ml_train_data)
        # Call module to create Loads Machine Learning Dock and.....
        self.ml_train_loads = ML_Train_Loads.Form(self.ex_data, self.status_bar)
        self.ml_train_loads.Button_Train.clicked.connect(self.ml_train_data)

        # Call module to create Data Extraction Dock and.....
        self.ml_ext = ML_Ext.Form(self.ex_data, self.status_bar)
        self.ml_ext.Button_NN.clicked.connect(self.ml_ext_data)
        self.ml_ext.Button_SVM.clicked.connect(self.ml_ext_data)
        self.nn_svm_ext = nn_svm.Form(self.ex_data, self.status_bar)
        self.ml_ext.Button_Train_Data.clicked.connect(self.nn_svm_ext.ml_learn)
        self.ml_ext.Button_NN_Learn.clicked.connect(self.nn_svm_ext.nn_learn)
        # Capture event and call function when Checkbox toggled/pressed
        self.ml_ext.Check_NN_SVM.pressed.connect(self.batch_ext_message)

        # Loads Style 1
        self.ml_ext_1 = ML_Ext_1.Form(self.ex_data, self.status_bar)
        self.ml_ext_1.Button_NN_1.clicked.connect(self.ml_ext_data_1)
        self.ml_ext_1.Button_SVM_1.clicked.connect(self.ml_ext_data_1)
        self.nn_svm_ext_1 = nn_svm_loads_1.Form(self.ex_data, self.status_bar)    # Points to class for "Loads" Style 1
        self.ml_ext_1.Button_Train_Data_1.clicked.connect(self.nn_svm_ext_1.ml_learn)
        self.ml_ext_1.Button_NN_Learn_1.clicked.connect(self.nn_svm_ext_1.nn_learn)
        # Capture event and call function when Checkbox toggled/pressed
        self.ml_ext_1.Check_NN_SVM_1.pressed.connect(self.batch_ext_message)

        # Loads Style 2
        self.ml_ext_2 = ML_Ext_2.Form(self.ex_data, self.status_bar)
        self.ml_ext_2.Button_NN_2.clicked.connect(self.ml_ext_data_2)
        self.ml_ext_2.Button_SVM_2.clicked.connect(self.ml_ext_data_2)
        self.nn_svm_ext_2 = nn_svm_loads_2.Form(self.ex_data, self.status_bar)    # Points to class for "Loads" Style 2
        self.ml_ext_2.Button_Train_Data.clicked.connect(self.nn_svm_ext_2.ml_learn)
        self.ml_ext_2.Button_NN_Learn_2.clicked.connect(self.nn_svm_ext_2.nn_learn)
        # Capture event and call function when Checkbox toggled/pressed
        self.ml_ext_2.Check_NN_SVM_2.pressed.connect(self.batch_ext_message)

        # Collect list of QDockWidget's
        self.dock_list_widgets = []
        self.dock_list_widgets = PDiM.findChildren(self, QDockWidget)

        # Now set the module (variable - self.menu_setup)
        self.setCentralWidget(self.menu_setup)

    def user_sel_call(self):
        """ Define Call for Dock Selection """

        usr_sndr = self.sender().text()

        if usr_sndr == "Crop Pic":
            self.user_sel = "Crop Dock Reset"  # When Dock Called Set the User Sel so Dock can be Recovered when Closed
        if usr_sndr == "Process Tools":
            self.user_sel = "Process Tools"
        if usr_sndr == "Threshold Pic":
            self.user_sel = "Threshold Pic"
        if usr_sndr == "Connected Components with Stats":
            self.user_sel = "Connected Components with Stats"
        if usr_sndr == "GFEM":
            self.user_sel = "GFEM"
        if usr_sndr == "Loads 1":
            self.user_sel = "Loads 1"
        if usr_sndr == "Loads 2":
            self.user_sel = "Loads 2"
        if usr_sndr == "Model":    # Collection of Data for Training of GFEM Style
            self.user_sel = "Model"
        if usr_sndr == "Loads":    # Collection of Data for Training of Loads Style
            self.user_sel = "Loads"

        self.user_sel_analysis()

    def dock_recover(self):
        """ Recover Closed Widgets for Analysis Dock """

        if self.user_sel == "Crop Dock Reset" or self.user_sel == "Process Tools" or \
                self.user_sel == "Threshold Pic" or self.user_sel == "Connected Components with Stats" or \
                self.user_sel == "GFEM" or self.user_sel == "Loads 1" or self.user_sel == "Loads 2" or \
                self.user_sel == "Model" or self.user_sel == "Loads":
            self.user_sel_analysis()

    def dock_crop_reset(self):
        """ When User Selects Process Pictures Using OpenCV """

        dock_crop_etc = self.crop_etc.DockWidget()
        self.addDockWidget(Qt.RightDockWidgetArea, dock_crop_etc)
        self.dock_list_widgets = PDiM.findChildren(self, QDockWidget)  # Collect list of QDockWidget's

    def dock_process_tools(self):
        """ When User Selects Process Pictures Using OpenCV """

        dock_tools = self.cv_tools.DockWidget()
        self.addDockWidget(Qt.RightDockWidgetArea, dock_tools)
        self.dock_list_widgets = PDiM.findChildren(self, QDockWidget)  # Collect list of QDockWidget's

    def dock_threshold(self):
        """ When User Selects Process Pictures Using OpenCV """

        dock_threshold = self.threshold.DockWidget()
        self.addDockWidget(Qt.RightDockWidgetArea, dock_threshold)
        self.dock_list_widgets = PDiM.findChildren(self, QDockWidget)  # Collect list of QDockWidget's

    def dock_ccwithstats(self):
        """ When User Selects Process Pictures Using OpenCV """

        dock_ccwithstats = self.ccwithstats.DockWidget()
        self.addDockWidget(Qt.RightDockWidgetArea, dock_ccwithstats)
        self.dock_list_widgets = PDiM.findChildren(self, QDockWidget)  # Collect list of QDockWidget's

    def dock_ext(self):
        """ When User Selects Extract Data Using Machine Learning Model """

        dock_extract = self.ml_ext.DockWidget()
        self.addDockWidget(Qt.RightDockWidgetArea, dock_extract)
        self.dock_list_widgets = PDiM.findChildren(self, QDockWidget)

    def dock_ext_loads_1(self):
        """ When User Selects Extract Data Using Machine Learning Model """

        dock_extract = self.ml_ext_1.DockWidget()
        self.addDockWidget(Qt.RightDockWidgetArea, dock_extract)
        self.dock_list_widgets = PDiM.findChildren(self, QDockWidget)

    def dock_ext_loads_2(self):
        """ When User Selects Extract Data Using Machine Learning Model """

        dock_extract = self.ml_ext_2.DockWidget()
        self.addDockWidget(Qt.RightDockWidgetArea, dock_extract)
        self.dock_list_widgets = PDiM.findChildren(self, QDockWidget)

    def dock_train(self):
        """ When User Selects Train Data Using Machine Learning Model """

        dock_train = self.ml_train.DockWidget()
        self.addDockWidget(Qt.RightDockWidgetArea, dock_train)
        self.dock_list_widgets = PDiM.findChildren(self, QDockWidget)

    def dock_train_loads(self):
        """ When User Selects Train Data Using Machine Learning Model """

        dock_train = self.ml_train_loads.DockWidget()
        self.addDockWidget(Qt.RightDockWidgetArea, dock_train)
        self.dock_list_widgets = PDiM.findChildren(self, QDockWidget)

    def user_sel_analysis(self):
        """ Shows the Relevant Dock for User Selected Analysis and Creates a List of QDockWidgets """

        sndr = self.sender().text()

        # Clear figure then remove it from canvas.
        self.menu_setup.plot_section.cla()  # or clear()
        self.menu_setup.canvas.figure.clear()  # Removes figure from canvas making canvas available for a new plot type
        active_tool = self.menu_setup.toolbar.mode    # Get status of toolbar button selection

        closed_widgets = []

        if sndr == "PDF to Pic":
            self.status_bar.showMessage("PDF Conversion to Pictures", 9000)
            self.pdf_pic.open_pdfs()
        if sndr == "Crop Pic" or self.user_sel == "Crop Dock Reset":
            self.status_bar.showMessage("Ready to Crop Picture and Save for CV2", 9000)
            if active_tool != 'zoom rect':
                self.menu_setup.toolbar.zoom()  # Select 'zoom' for user to box region to Crop
            if self.user_sel != "Crop Dock Reset":
                # Maybe move under if self.crop_etc.dock_crop_etc not in self.dock_list_widgets:
                self.plot_pics(self.CV2_Complete)
            else:
                # Show Pre Crop Pic and Dock
                self.plot_pics(self.CV2_Pre_Crop)
            for item in self.dock_list_widgets:
                if item.isVisible():
                    item.setVisible(False)
                else:
                    closed_widgets.append(item)
            if self.crop_etc.dock_crop_etc not in self.dock_list_widgets:
                self.dock_crop_reset()
            else:
                self.crop_etc.show_closed_widgets(closed_widgets)
        if sndr == "Process Tools" or self.user_sel == "Process Tools":
            # Show CV2 Pic Processing Dock
            self.plot_pics(self.CV2_Complete)
            for item in self.dock_list_widgets:
                if item.isVisible():
                    item.setVisible(False)
                else:
                    closed_widgets.append(item)
            if self.cv_tools.dock_process_tools not in self.dock_list_widgets:
                self.dock_process_tools()
            else:
                self.cv_tools.show_closed_widgets(closed_widgets)
        if sndr == "Threshold Pic" or self.user_sel == "Threshold Pic":
            # Show Threshold Pic and CV2 Dock
            self.plot_pics(self.CV2_Complete)
            for item in self.dock_list_widgets:
                if item.isVisible():
                    item.setVisible(False)
                else:
                    closed_widgets.append(item)
            if self.threshold.dock_threshold_image not in self.dock_list_widgets:
                self.dock_threshold()
            else:
                self.threshold.show_closed_widgets(closed_widgets)
        if sndr == "Connected Components with Stats" or self.user_sel == "Connected Components with Stats":
            # Show Connected Components with Stats Pic and CV2 Dock
            self.plot_pics(self.CV2_Complete)
            for item in self.dock_list_widgets:
                if item.isVisible():
                    item.setVisible(False)
                else:
                    closed_widgets.append(item)
            if self.ccwithstats.dock_image_process not in self.dock_list_widgets:
                self.dock_ccwithstats()
            else:
                self.ccwithstats.show_closed_widgets(closed_widgets)
        if sndr == "GFEM" or self.user_sel == "GFEM":
            if active_tool == 'zoom rect':
                self.menu_setup.toolbar.zoom()  # UnCheck zoom if still selected
                # print(f"{active_tool} selected")
            # Show Connected Components with Stats Pic and GFEM Dock
            self.plot_pics(self.CV2_Complete)
            for item in self.dock_list_widgets:
                if item.isVisible():
                    item.setVisible(False)
                else:
                    closed_widgets.append(item)
            if self.ml_ext.dock_extract not in self.dock_list_widgets:
                self.dock_ext()
            else:
                self.ml_ext.show_closed_widgets(closed_widgets)
        if sndr == "Loads 1" or self.user_sel == "Loads 1":
            if active_tool == 'zoom rect':
                self.menu_setup.toolbar.zoom()  # UnCheck zoom if still selected
            # Show Processed Pic and Loads Style 1 Dock
            self.plot_pics(self.CV2_Complete)
            for item in self.dock_list_widgets:
                if item.isVisible():
                    item.setVisible(False)
                else:
                    closed_widgets.append(item)
            if self.ml_ext_1.dock_extract not in self.dock_list_widgets:
                self.dock_ext_loads_1()
            else:
                self.ml_ext_1.show_closed_widgets(closed_widgets)
        if sndr == "Loads 2" or self.user_sel == "Loads 2":
            if active_tool == 'zoom rect':
                self.menu_setup.toolbar.zoom()  # UnCheck zoom if still selected
            # Show Processed Pic and Loads Style 2 Dock
            self.plot_pics(self.CV2_Complete)
            for item in self.dock_list_widgets:
                if item.isVisible():
                    item.setVisible(False)
                else:
                    closed_widgets.append(item)
            if self.ml_ext_2.dock_extract not in self.dock_list_widgets:
                self.dock_ext_loads_2()
            else:
                self.ml_ext_2.show_closed_widgets(closed_widgets)
        if sndr == "Model" or self.user_sel == "Model":
            # Show Connected Components with Stats Pic and CV2 Dock
            self.plot_pics(self.CV2_Complete)
            for item in self.dock_list_widgets:
                if item.isVisible():
                    item.setVisible(False)
                else:
                    closed_widgets.append(item)
            if self.ml_train.dock_training not in self.dock_list_widgets:
                self.dock_train()
            else:
                self.ml_train.show_closed_widgets(closed_widgets)
        if sndr == "Loads" or self.user_sel == "Loads":
            # Show Processed Pic and Loads Training Dock
            self.plot_pics(self.CV2_Complete)
            for item in self.dock_list_widgets:
                if item.isVisible():
                    item.setVisible(False)
                else:
                    closed_widgets.append(item)
            if self.ml_train_loads.dock_training not in self.dock_list_widgets:
                self.dock_train_loads()
            else:
                self.ml_train_loads.show_closed_widgets(closed_widgets)

    def plot_pics(self, cv_pics):
        """ Plot Pictures """

        # Clear figure then remove it from canvas.
        self.menu_setup.plot_section.cla()  # or clear()
        self.menu_setup.canvas.figure.clear()  # Removes figure from canvas making canvas available for a new plot
        # print("channel", len(cv_pics.shape))

        # Depends on User work flow i.e. save cropped pics then come back and remove artifacts...
        if isinstance(cv_pics, np.ndarray):    # if cv_pics is a numpy array show, else show the 'Orig_Pic'
            self.menu_setup.plt.imshow(cv_pics, cmap='gray')
        else:
            self.menu_setup.plt.imshow(self.CV2_Pre_Crop, cmap='gray')
        self.menu_setup.plt.xlabel("X", fontsize=10)
        self.menu_setup.plt.ylabel("Y", fontsize=10)
        self.menu_setup.figure.canvas.draw()  # Refresh canvas
        self.menu_setup.figure.canvas.flush_events()

    def plot_orig_pic(self):
        """ Plot the User Selected Picture """

        usr_sel = self.sender().text()

        self.ex_data.batch_crop = True    # Reset flag for batch processing - See def plot_crop_pics(self):
        self.ex_data.batch_NN_SVM = False    # Reset flag for batch processing (collection of _processed.png)
        self.pic_list = []    # Reset list of pictures for Batch processing if loading from a different path

        self.menu_setup.plot_section.cla()  # or clear()

        if usr_sel == "Load Pic":
            self.pdf_pic.open_pic()
            path_orig = self.ex_data.orig_pic
            if path_orig is None:
                self.status_bar.showMessage("No Picture to Show.....")
            else:
                self.Orig_Pic = cv2.imread(path_orig)
                self.Orig_Pic = cv2.cvtColor(self.Orig_Pic, cv2.COLOR_BGR2GRAY)
                self.CV2_Pre_Crop = self.Orig_Pic
                self.CV2_Complete = None  # Reset in case user opens a pre-processed picture
                self.plot_pics(self.CV2_Pre_Crop)  # Call function to Plot Picture
        elif usr_sel == "Reset":
            self.plot_pics(self.CV2_Pre_Crop)  # Call function to Plot Picture

    def plot_rot_pic(self):
        """ Plot the Rotated Picture """

        sndr = self.sender().text()

        self.menu_setup.plot_section.cla()  # or clear()

        if sndr == "Clockwise":
            self.CV2_Pre_Crop = cv2.rotate(self.CV2_Pre_Crop, cv2.ROTATE_90_CLOCKWISE)
            self.status_bar.showMessage("Picture Rotated 90 degrees Clockwise", 4000)
        elif sndr == "Anticlockwise":
            self.CV2_Pre_Crop = cv2.rotate(self.CV2_Pre_Crop, cv2.ROTATE_90_COUNTERCLOCKWISE)
            self.status_bar.showMessage("Picture Rotated 90 degrees Anticlockwise", 4000)

        self.plot_pics(self.CV2_Pre_Crop)  # Call function to Plot Picture

    def plot_crop_pics(self):
        """ Plot the User Defined Cropped Pic """

        if self.ex_data.batch_crop:
            # Set flag to prevent re-execution when Ctrl or Alt key pressed
            self.ex_data.batch_crop = False    # Flag re-set if new pic loaded or reset - See def plot_orig_pic(self):
            user_sel_pic = self.ex_data.orig_pic

            # Empty strings are "False" i.e. considered False in a Boolean context
            if self.crop_etc.LineE_x1.text():
                x1 = int(self.crop_etc.LineE_x1.text())
            else:
                x1 = 0
            if self.crop_etc.LineE_y1.text():
                y1 = int(self.crop_etc.LineE_y1.text())
            else:
                y1 = 0
            if self.crop_etc.LineE_x2.text():
                x2 = int(self.crop_etc.LineE_x2.text())
            else:
                x2 = self.CV2_Pre_Crop.shape[1]
            if self.crop_etc.LineE_y2.text():
                y2 = int(self.crop_etc.LineE_y2.text())
            else:
                y2 = self.CV2_Pre_Crop.shape[0]

            if x2 < x1 or y2 < y1:
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Information)
                msgBox.setWindowTitle("Error Cropping Picture")
                msgBox.setText('X2 and Y2 Must be > X1 and Y1')
                msgBox.setStandardButtons(QMessageBox.Ok)  # .setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                msgBox.exec()
            else:
                if not self.crop_etc.Check_Batch.isChecked():
                    path = self.ex_data.file_path
                    if not self.ex_data.pic_list_flag:    # If Flag initially False call function set True
                        pic_list = self.png_list(path, "Crop_CV2")
                    else:
                        pic_list = self.ex_data.pic_list
                    if not self.crop_etc.Check_Batch_Even.isChecked() and not self.crop_etc.Check_Batch_Odd.isChecked():
                        self.message_box("No Data", "User Must Select Pages to Batch Crop the Pictures!")
                    else:
                        # Determine if Even, Odd or Both for Batch
                        even_p = self.crop_etc.Check_Batch_Even.isChecked()
                        odd_p = self.crop_etc.Check_Batch_Odd.isChecked()
                        for i, pic in enumerate(pic_list):    # Previously sorted alphanumerically
                            orig_name = pic.replace(".png", "")  # Leaves file name (no extension)
                            if even_p and odd_p:
                                pre_crop = cv2.imread(path + pic)
                                # Convert pic for next Step CV2 processing e.g. Connected Components with Stats
                                cv2_cropped = cv2.cvtColor(pre_crop[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY)
                                self.pdf_pic.batch_save(orig_name, cv2_cropped, '_cropped')
                            if even_p and not odd_p:
                                # The % sign is like division only it checks for the remainder, so if the number
                                if i % 2:    # divided by 2 has a remainder of 0 it's even otherwise odd
                                    pre_crop = cv2.imread(path + pic_list[i])
                                    cv2_cropped = cv2.cvtColor(pre_crop[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY)
                                    self.pdf_pic.batch_save(orig_name, cv2_cropped, '_cropped')
                            if not even_p and odd_p:
                                if i % 2:
                                    pass
                                else:
                                    pre_crop = cv2.imread(path + pic_list[i])
                                    cv2_cropped = cv2.cvtColor(pre_crop[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY)
                                    self.pdf_pic.batch_save(orig_name, cv2_cropped, '_cropped')
                    # Show User Picture Selected
                    user_pic = cv2.imread(user_sel_pic)
                    # Convert pic for next Step CV2 processing e.g. Connected Components with Stats
                    self.CV2_Complete = cv2.cvtColor(user_pic[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY)
                    self.plot_pics(self.CV2_Complete)  # Call function to Plot Picture
                else:
                    self.CV2_Complete = self.CV2_Pre_Crop[y1:y2, x1:x2]  # Crop Pic
                    self.plot_pics(self.CV2_Complete)  # Call function to Plot Picture

    def batch_cv2_message(self):
        """ Display Message in Statusbar for User """

        if self.crop_etc.Check_Batch.isChecked():
            self.status_bar.showMessage("Single Page will be Cropped...", 5000)
            self.crop_etc.Check_Batch.setText("Single")
            self.crop_etc.Check_Batch_Even.setChecked(Qt.Unchecked)    # False
            self.crop_etc.Check_Batch_Odd.setChecked(Qt.Unchecked)
        else:
            self.status_bar.showMessage("Batch Pictures will end with '_cropped.png'")
            self.crop_etc.Check_Batch.setText("Batch")
            self.crop_etc.Check_Batch_Even.setChecked(Qt.Checked)    # True
            self.crop_etc.Check_Batch_Odd.setChecked(Qt.Checked)

    def save_pic(self):
        """ Save User Modified Picture for CV2 """

        save_process = self.sender().text()

        if self.CV2_Complete.any():
            self.pdf_pic.save_pic(self.CV2_Complete, save_process)
        else:
            self.pdf_pic.save_pic(self.CV2_Pre_Crop, save_process)

    def batch_no_processing(self):
        """ Save Picture when No CV2 Processing used in Batch """

        path = self.ex_data.file_path

        if self.cv_tools.Check_Batch.isChecked():
            if not self.ex_data.pic_list_process_flag:  # If Flag initially False (ex_data) call function sets True
                pic_list = self.png_list(path, "Processed")
            else:
                pic_list = self.ex_data.pic_list_process
            for i, pic in enumerate(pic_list):  # Previously sorted alphanumerically
                post_crop = cv2.imread(path + pic)
                pic_ready = cv2.cvtColor(post_crop, cv2.COLOR_BGR2GRAY)
                orig_name = pic.replace(".png", "")  # Leaves file name (no extension)
                self.pdf_pic.batch_save(orig_name, pic_ready, '_processed')
        else:
            self.status_bar.showMessage("Requires Batch Processing.......")

    def erode_dilate_open_pic(self):
        """ Erode, Dilate or Opening of Picture using CV2 """

        usr_process = self.sender().text()
        batch_job = self.cv_tools.Check_Batch.isChecked()
        path = self.ex_data.file_path
        pic_list = []

        if batch_job:
            if not self.ex_data.pic_list_process_flag:  # If Flag initially False (ex_data) call function sets True
                pic_list = self.png_list(path, "Processed")
            else:
                pic_list = self.ex_data.pic_list_process

        if usr_process == "Erode":
            kernel_value = self.cv_tools.Spin_Erode_Kernel.value()
            if batch_job:
                for i, pic in enumerate(pic_list):  # Previously sorted alphanumerically
                    post_crop = cv2.imread(path + pic)
                    pic_ready = cv2.cvtColor(post_crop, cv2.COLOR_BGR2GRAY)
                    cv2_erode = erode_dilate.erode_pic(kernel_value, pic_ready)
                    orig_name = pic.replace(".png", "")  # Leaves file name (no extension)
                    self.pdf_pic.batch_save(orig_name, cv2_erode, '_processed')
            else:
                self.CV2_Complete = erode_dilate.erode_pic(kernel_value, self.CV2_Complete)
                self.plot_pics(self.CV2_Complete)
        elif usr_process == "Dilate":
            kernel_value = self.cv_tools.Spin_Dilate_Kernel.value()
            if batch_job:
                for i, pic in enumerate(pic_list):  # Previously sorted alphanumerically
                    post_crop = cv2.imread(path + pic)
                    pic_ready = cv2.cvtColor(post_crop, cv2.COLOR_BGR2GRAY)
                    cv2_dilate = erode_dilate.dilate_pic(kernel_value, pic_ready)
                    orig_name = pic.replace(".png", "")  # Leaves file name (no extension)
                    self.pdf_pic.batch_save(orig_name, cv2_dilate, '_processed')
            else:
                self.CV2_Complete = erode_dilate.dilate_pic(kernel_value, self.CV2_Complete)
                self.plot_pics(self.CV2_Complete)
        elif usr_process == "Opening":
            kernel_value = self.cv_tools.Spin_Opening_Kernel.value()
            if batch_job:
                for i, pic in enumerate(pic_list):  # Previously sorted alphanumerically
                    post_crop = cv2.imread(path + pic)
                    pic_ready = cv2.cvtColor(post_crop, cv2.COLOR_BGR2GRAY)
                    cv2_open = erode_dilate.opening_pic(kernel_value, pic_ready)
                    orig_name = pic.replace(".png", "")  # Leaves file name (no extension)
                    self.pdf_pic.batch_save(orig_name, cv2_open, '_processed')
            else:
                self.CV2_Complete = erode_dilate.opening_pic(kernel_value, self.CV2_Complete)
                self.plot_pics(self.CV2_Complete)
        elif usr_process == "Lines":
            kernel_value = self.cv_tools.Spin_Remove_Kernel.value()
            if batch_job:
                for i, pic in enumerate(pic_list):  # Previously sorted alphanumerically
                    post_crop = cv2.imread(path + pic)
                    pic_ready = cv2.cvtColor(post_crop, cv2.COLOR_BGR2GRAY)
                    cv2_remove = erode_dilate.remove_hori(kernel_value, pic_ready)
                    orig_name = pic.replace(".png", "")  # Leaves file name (no extension)
                    self.pdf_pic.batch_save(orig_name, cv2_remove, '_processed')
            else:
                self.CV2_Complete = erode_dilate.remove_hori(kernel_value, self.CV2_Complete)
                self.plot_pics(self.CV2_Complete)

    def threshold_pic(self):
        """ Threshold of Picture using CV2 """

        usr_process = self.sender().text()

        thres = self.threshold.Slide_Threshold_Max.value()
        max_value = self.threshold.Slide_MaxValue.value()

        if usr_process == "THRESH_BINARY":
            ret, self.CV2_Complete = cv2.threshold(self.CV2_Complete, thres, max_value, cv2.THRESH_BINARY)
            self.plot_pics(self.CV2_Complete)
        elif usr_process == "THRESH_TRUNC":
            ret, self.CV2_Complete = cv2.threshold(self.CV2_Complete, thres, max_value, cv2.THRESH_TRUNC)
            self.plot_pics(self.CV2_Complete)
        elif usr_process == "THRESH_TOZERO":
            ret, self.CV2_Complete = cv2.threshold(self.CV2_Complete, thres, max_value, cv2.THRESH_TOZERO)
            self.plot_pics(self.CV2_Complete)

    def threshold_value(self):
        """ Show User Selected Value of Threshold in a QLabel when Changed """

        snd_name = self.sender().objectName()

        if snd_name == "From Threshold threshold":  # See class "PDiM_4_Opencv_Threshold" for assigned Object Name
            thres = self.threshold.Slide_Threshold_Max.value()
            self.threshold.Label_Threshold_Value.setText(str(thres))
        elif snd_name == "From Threshold maxvalue":  # See class "PDiM_4_Opencv_Threshold" for assigned Object Name
            max_value = self.threshold.Slide_MaxValue.value()
            self.threshold.Label_MaxValue_Value.setText(str(max_value))
        elif snd_name == "From ccwithstats threshold":  # See class "PDiM_4_Opencv_CCwithStats" for Object Name
            thres = self.ccwithstats.Slide_Threshold_Max.value()
            self.ccwithstats.Label_Threshold_Value.setText(str(thres))
        elif snd_name == "From ccwithstats maxvalue":  # See class "PDiM_4_Opencv_CCwithStats" for Object Name
            max_value = self.ccwithstats.Slide_MaxValue.value()
            self.ccwithstats.Label_MaxValue_Value.setText(str(max_value))

    def ccwithstats_cv2(self):
        """ Plot the User Processed Pic """

        Threshold = self.ccwithstats.Slide_Threshold_Max.value()
        MaxValue = self.ccwithstats.Slide_MaxValue.value()

        if self.ccwithstats.Radio_Connect:
            connect = 4
        else:
            connect = 8

        if self.ccwithstats.LineE_Artifact_Area.text():
            Artifact_Area = int(self.ccwithstats.LineE_Artifact_Area.text())
            # Depends on User work flow i.e. save cropped pics then come back and remove artifacts...
            if not isinstance(self.CV2_Complete, np.ndarray):
                img_gray = self.CV2_Pre_Crop
            else:
                img_gray = self.CV2_Complete
            self.CV2_Complete = ccwstats.ccwithstats(img_gray, Threshold, MaxValue, connect, Artifact_Area)
            if self.ccwithstats.Check_Batch.isChecked():
                self.plot_pics(self.CV2_Complete)
                path = self.ex_data.file_path
                if not self.ex_data.pic_list_process_flag:  # If Flag initially False call function set True
                    pic_list = self.png_list(path, "Processed")
                else:
                    pic_list = self.ex_data.pic_list_process
                for i, pic in enumerate(pic_list):    # Previously sorted alphanumerically
                    post_crop = cv2.imread(path + pic)
                    pic_ready = cv2.cvtColor(post_crop, cv2.COLOR_BGR2GRAY)
                    cv2_ccws = ccwstats.ccwithstats(pic_ready, Threshold, MaxValue, connect, Artifact_Area)
                    orig_name = pic.replace(".png", "")  # Leaves file name (no extension)
                    self.pdf_pic.batch_save(orig_name, cv2_ccws, '_processed')
            else:
                self.plot_pics(self.CV2_Complete)
        else:
            self.message_box("No Data", "User Must enter an Integer to Process the Picture!")

    def ml_train_data(self):
        """ Plot the Digits for Training """

        # Get Path and Name of Picture Loaded
        path_to_pic = self.ex_data.file_path

        # Get Processed Picture
        img_gray = self.CV2_Complete
        # OpenCV uses BGR as its default colour order for images, matplotlib uses RGB
        # When displaying an image loaded with OpenCv in matplotlib the channels will be back to front
        img_plt = cv2.cvtColor(img_gray, cv2.COLOR_BGR2RGB)    # Convert for plotting

        img_copy = img_plt.copy()
        # Simple Thresholding - first argument is the source image (should be a grayscale image)
        # threshold value (classify the pixel values), maximum value (assigned to pixel values exceeding threshold)
        ret, img_thresh = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY)

        height, width = np.shape(img_thresh)    # Shape of the page

        # Find Contours
        contours, hierarchy = cv2.findContours(img_thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        # Call Function to Sort Contours according to the provided method
        style = self.sender().text()    # Identify if GFEM or Loads style (format)
        method = "left-to-right"
        # (contours, boundingBoxes) = sort_contour.sort_contours(contours, method, style)
        contour_sort = sort_contour.sort_contours(contours, method, style)

        # Delete From HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        img_copy1 = img_plt.copy()
        for cntr in contour_sort:
            [x, y, w, h] = cv2.boundingRect(cntr)
            if 20 < h < 50 or (15 < w < 35 and 5 < h < 15):
                color = list(np.random.random(size=3) * 256)
                cv2.rectangle(img_copy1, (x, y), (x + w, y + h), color, 4)
                crop_pic = img_copy1[0:height, 0:width]
                cv2.imshow('Each Digit', crop_pic)
        # To HERE When donw!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        self.status_bar.showMessage("Save Training Data by Cancelling rather than entering a Digit")

        samples = np.empty((0, 400))
        labels = []
        Train_Data = True
        count_0 = 0
        count_1 = 0
        count_2 = 0
        count_3 = 0
        count_4 = 0
        count_5 = 0
        count_6 = 0
        count_7 = 0
        count_8 = 0
        count_9 = 0
        count_minus = 0    # For loads Style
        count_plus = 0    # For loads Style
        count_E = 0    # For loads Style
        count_A = 0    # For loads Style
        count_L = 0    # For loads Style
        count_R = 0    # For loads Style
        count_H = 0    # For loads Style
        count_S = 0    # For loads Style

        # See - S_Sort_Contours boundingRect size (height in this case) hard coded!!
        for idx, contour in enumerate(contour_sort):
            if style == "Train":    # GFEM Style / Format
                self.ml_train.Label_0_Qty.setText(str(count_0) + " Samples")
                self.ml_train.Label_1_Qty.setText(str(count_1) + " Samples")
                self.ml_train.Label_2_Qty.setText(str(count_2) + " Samples")
                self.ml_train.Label_3_Qty.setText(str(count_3) + " Samples")
                self.ml_train.Label_4_Qty.setText(str(count_4) + " Samples")
                self.ml_train.Label_5_Qty.setText(str(count_5) + " Samples")
                self.ml_train.Label_6_Qty.setText(str(count_6) + " Samples")
                self.ml_train.Label_7_Qty.setText(str(count_7) + " Samples")
                self.ml_train.Label_8_Qty.setText(str(count_8) + " Samples")
                self.ml_train.Label_9_Qty.setText(str(count_9) + " Samples")
            else:    # Loads Style / Format
                self.ml_train_loads.Label_0_Qty.setText(str(count_0) + " Samples")
                self.ml_train_loads.Label_1_Qty.setText(str(count_1) + " Samples")
                self.ml_train_loads.Label_2_Qty.setText(str(count_2) + " Samples")
                self.ml_train_loads.Label_3_Qty.setText(str(count_3) + " Samples")
                self.ml_train_loads.Label_4_Qty.setText(str(count_4) + " Samples")
                self.ml_train_loads.Label_5_Qty.setText(str(count_5) + " Samples")
                self.ml_train_loads.Label_6_Qty.setText(str(count_6) + " Samples")
                self.ml_train_loads.Label_7_Qty.setText(str(count_7) + " Samples")
                self.ml_train_loads.Label_8_Qty.setText(str(count_8) + " Samples")
                self.ml_train_loads.Label_9_Qty.setText(str(count_9) + " Samples")
                self.ml_train_loads.Label_Minus_Qty.setText(str(count_minus) + " Samples")
                self.ml_train_loads.Label_Plus_Qty.setText(str(count_plus) + " Samples")
                self.ml_train_loads.Label_E_Qty.setText(str(count_E) + " Samples")
                self.ml_train_loads.Label_A_Qty.setText(str(count_A) + " Samples")
                self.ml_train_loads.Label_L_Qty.setText(str(count_L) + " Samples")
                self.ml_train_loads.Label_R_Qty.setText(str(count_R) + " Samples")
                self.ml_train_loads.Label_H_Qty.setText(str(count_H) + " Samples")
                self.ml_train_loads.Label_S_Qty.setText(str(count_S) + " Samples")
            if not Train_Data:
                self.save_train(labels, samples, path_to_pic)
                self.message_box("Training Data", 'Sampling Completed')
                break
            else:
                x, y, w, h = cv2.boundingRect(contour)
                if 20 < h < 50 or (15 < w < 35 and 5 < h < 15):
                    color = list(np.random.random(size=3) * 256)
                    cv2.rectangle(img_plt, (x, y), (x + w, y + h), color, 2)
                    self.menu_setup.plt.imshow(img_plt)  # Gets slower - Re-drawing!?!?!?!
                    self.menu_setup.figure.canvas.draw()  # Refresh canvas
                    self.menu_setup.canvas.flush_events()
                    ROI = img_thresh[y: y + h, x: x + w]  # Cropping Specific Digit
                    ROI_Red = cv2.resize(ROI, (20, 20))
                    if y - 3 < 0 or y + h + 4 > height or x - 3 < 0 or x + w + 4 > width:
                        digit_pic = img_copy[y:y + h, x:x + w]  # Cropping Specific Digit to show User
                    else:
                        digit_pic = img_copy[y - 3:y + h + 3, x - 3:x + w + 3]
                    PIL_image = Image.fromarray(digit_pic)
                    Pix_Pic = ImageQt(PIL_image)
                    train_digit = QPixmap(QPixmap.fromImage(Pix_Pic))
                    if style == "Train":  # GFEM Style / Format
                        self.ml_train.Label_Train_Pic.setPixmap(
                            train_digit.scaled(150, 150, Qt.KeepAspectRatioByExpanding))
                    else:  # Loads Style / Format
                        self.ml_train_loads.Label_Train_Pic. \
                            setPixmap(train_digit.scaled(150, 150, Qt.KeepAspectRatioByExpanding))
                    digit_value, accept = QInputDialog.getText(self.parent(),  # Needed .parent() to move the popup
                                                               'Machine Training...', 'Enter Digit', QLineEdit.Normal)
                    if accept:
                        img_plt = cv2.cvtColor(img_gray, cv2.COLOR_BGR2RGB)    # Provide Clean Pic for plotting
                        if digit_value.isdigit():
                            if len(digit_value) == 1 and 0 <= int(digit_value) <= 9:
                                int_dig_val = int(digit_value)
                                labels.append(int_dig_val)
                                sample = ROI_Red.reshape((1, 400))
                                samples = np.append(samples, sample, 0)
                                if int_dig_val == 0:
                                    count_0 += 1
                                if int_dig_val == 1:
                                    count_1 += 1
                                if int_dig_val == 2:
                                    count_2 += 1
                                if int_dig_val == 3:
                                    count_3 += 1
                                if int_dig_val == 4:
                                    count_4 += 1
                                if int_dig_val == 5:
                                    count_5 += 1
                                if int_dig_val == 6:
                                    count_6 += 1
                                if int_dig_val == 7:
                                    count_7 += 1
                                if int_dig_val == 8:
                                    count_8 += 1
                                if int_dig_val == 9:
                                    count_9 += 1
                            else:
                                self.message_box("Training Data", 'Not valid - Passed on Data Collection')
                        elif style != "Train" and digit_value == "-":
                            labels.append(digit_value)
                            sample = ROI_Red.reshape((1, 400))
                            samples = np.append(samples, sample, 0)
                            count_minus += 1
                        elif style != "Train" and digit_value == "+":
                            labels.append(digit_value)
                            sample = ROI_Red.reshape((1, 400))
                            samples = np.append(samples, sample, 0)
                            count_plus += 1
                        elif style != "Train" and digit_value.upper() == "E":
                            labels.append(digit_value)
                            sample = ROI_Red.reshape((1, 400))
                            samples = np.append(samples, sample, 0)
                            count_E += 1
                        elif style != "Train" and digit_value.upper() == "A":
                            labels.append(digit_value)
                            sample = ROI_Red.reshape((1, 400))
                            samples = np.append(samples, sample, 0)
                            count_A += 1
                        elif style != "Train" and digit_value.upper() == "L":
                            labels.append(digit_value)
                            sample = ROI_Red.reshape((1, 400))
                            samples = np.append(samples, sample, 0)
                            count_L += 1
                        elif style != "Train" and digit_value.upper() == "R":
                            labels.append(digit_value)
                            sample = ROI_Red.reshape((1, 400))
                            samples = np.append(samples, sample, 0)
                            count_R += 1
                        elif style != "Train" and digit_value.upper() == "H":
                            labels.append(digit_value)
                            sample = ROI_Red.reshape((1, 400))
                            samples = np.append(samples, sample, 0)
                            count_H += 1
                        elif style != "Train" and digit_value.upper() == "S":
                            labels.append(digit_value)
                            sample = ROI_Red.reshape((1, 400))
                            samples = np.append(samples, sample, 0)
                            count_S += 1
                        else:
                            self.message_box("Training Data", 'Empty Entry - Passed on Data Collection')
                    else:
                        Train_Data = False
            if idx == len(contour_sort) - 1:
                self.message_box("Training Data", 'Last Digit Sampled, Save Data...')
                self.save_train(labels, samples, path_to_pic)

    def save_train(self, labels, samples, path_to_pic):
        """ Save Training Sample Digits """

        save_train, accept = QInputDialog.getText(self.parent(),  # Needed .parent() to move the popup
                                                  'Save Training Data', 'Enter File Name',
                                                  QLineEdit.Normal)
        if accept:
            labels = np.array(labels, str)    # Save String to accommodate minus sign and E
            labels = labels.reshape((labels.size, 1))
            if save_train:
                np.savetxt(path_to_pic + "/" + save_train + '.sample', samples)
                np.savetxt(path_to_pic + "/" + save_train + '.label', labels, fmt='%1s')    # Save String
            else:
                self.message_box("Training Data", 'Was Not Saved!')
        else:
            self.message_box("Training Data", 'Not Saved')

        self.status_bar.showMessage("Ready for Digit Extraction.....")

    def ml_ext_data(self):
        """ Extract Digits from GFEM and Populate Spreadsheet """

        model = self.sender().text()
        model_txt = ""

        if model == "NN Extract Digits":
            model_txt = "Neural Network"
        elif model == "SVM Extract Digits":
            model_txt = "Support Vector Machine"

        Grids = 0
        Start_X = 0
        X_value = 0
        x_value = 0
        Y_value = 0
        y_value = 0
        Z_value = 0

        # Get Demarcation
        if self.ml_ext.Line_Grids.text():
            Grids = int(self.ml_ext.Line_Grids.text())
        if self.ml_ext.Line_Start_X.text():
            Start_X = int(self.ml_ext.Line_Start_X.text())
        if self.ml_ext.Line_X.text():
            X_value = int(self.ml_ext.Line_X.text())
        if self.ml_ext.Line_x.text():
            x_value = int(self.ml_ext.Line_x.text())
        if self.ml_ext.Line_Y.text():
            Y_value = int(self.ml_ext.Line_Y.text())
        if self.ml_ext.Line_y.text():
            y_value = int(self.ml_ext.Line_y.text())
        if self.ml_ext.Line_Z.text():
            Z_value = int(self.ml_ext.Line_Z.text())

        if Grids > Start_X or Grids > X_value or Grids > x_value or Grids > Y_value or Grids > y_value \
                or Grids > Z_value:
            self.message_box("For Demarcation", "Coord for Grids Must be < Coord for Start (X, Y, Z), X, x etc.")
        elif Start_X < Grids or Start_X > X_value or Start_X > x_value or Start_X > Y_value \
                or Start_X > y_value or Start_X > Z_value:
            self.message_box("For Demarcation", "Coord for Start (X, Y, Z) Must be > Grids and < Coord for X, x etc.")
        elif X_value < Grids or X_value < Start_X or X_value > x_value or X_value > Y_value \
                or X_value > y_value or X_value > Z_value:
            self.message_box("For Demarcation", "Coord for X Must be > Grids etc. and < Coord for x, Y etc.")
        elif x_value < Grids or x_value < Start_X or x_value < X_value or x_value > Y_value \
                or x_value > y_value or x_value > Z_value:
            self.message_box("For Demarcation", "Coord for x Must be > Grids etc. and < Coord for Y, y etc.")
        elif Y_value < Grids or Y_value < Start_X or Y_value < X_value or Y_value < x_value \
                or Y_value > y_value or Y_value > Z_value:
            self.message_box("For Demarcation", "Coord for Y Must be > Grids etc. and < Coord for y etc.")
        elif y_value < Grids or y_value < Start_X or y_value < X_value or y_value < x_value \
                or y_value < Y_value or y_value > Z_value:
            self.message_box("For Demarcation", "Coord for y Must be > Grids etc and < Coord for Z")
        elif Z_value < Grids or Z_value < Start_X or Z_value < X_value or Z_value < x_value \
                or Z_value < Y_value or Z_value < y_value:
            self.message_box("For Demarcation", "Coord for Z Must be < Coord for Grids, Start (X, Y, Z), X, x etc.")
        else:
            path = self.ex_data.file_path    # Save output to folder with cleaned pictures
            if self.ml_ext.Check_NN_SVM.isChecked() and self.ex_data.ml_train_data:    # Training Data Must be Loaded
                if not self.ex_data.batch_NN_SVM:    # Check Status of 'flag' so the list is not Re-made
                    pic_list = self.png_list(path, "Extract")
                else:
                    pic_list = self.ex_data.pic_list_extract
                if model == "NN Extract Digits" and not self.ex_data.NN_Learn:    # If NN not learnt warn user!
                    self.message_box("Neural Network", "Requires Learning on Data before Digit Extraction!")
                else:
                    # Call function to loop i.e. pic in list is (cropped & processed) ready for digit extraction!!!!
                    batch_dig_ext = self.batch_ext(path, pic_list, Grids, Start_X, X_value, x_value,
                                                   Y_value, y_value, Z_value, model)
                    self.status_bar.showMessage(batch_dig_ext)
            else:    # Manual work flow i.e. Open Picture (either pre-processed or original)
                if isinstance(self.CV2_Complete, np.ndarray):    # Pic opened, Processed then Digits Extracted
                    pic_concat = ccwstats.pic_stitch(self.CV2_Complete, Grids, Start_X)
                    df_x_y_z = self.nn_svm_ext.ml_model(pic_concat, Grids, Start_X, X_value, x_value,
                                                        Y_value, y_value, Z_value, model)
                else:    # For the previously 'cleaned' Pictures the "Pre_Crop" version is required
                    pic_concat = ccwstats.pic_stitch(self.CV2_Pre_Crop, Grids, Start_X)
                    df_x_y_z = self.nn_svm_ext.ml_model(pic_concat, Grids, Start_X, X_value, x_value,
                                                        Y_value, y_value, Z_value, model)
                if isinstance(df_x_y_z, pd.DataFrame) and not df_x_y_z.empty:
                    df_x_y_z.to_excel(path + 'A_Grid_Coords.xlsx', index=False, sheet_name='X_Y_Z')
                    self.status_bar.showMessage(f"Results for - {model_txt} - located at {path}", 9000)
                else:
                    self.status_bar.showMessage("Check Training Data - DataFrame is empty...", 4000)
                    self.message_box("No Data", "Verify Training Data or Processed Picture!")

    def ml_ext_data_1(self):
        """ Extract Digits from Loads Style 1 and Populate Spreadsheet """

        model = self.sender().text()
        model_txt = ""

        if model == "NN Extract Digits":
            model_txt = "Neural Network"
        elif model == "SVM Extract Digits":
            model_txt = "Support Vector Machine"

        Cond_A = 0
        Cond_B = 0
        RLHS = 0
        SF_FS = 0
        SF_RS = 0
        ZShear = 0
        Torque = 0
        Bend = 0

        # Get Demarcation
        if self.ml_ext_1.Line_Cond_A.text():
            Cond_A = int(self.ml_ext_1.Line_Cond_A.text())
        if self.ml_ext_1.Line_Cond_B.text():
            Cond_B = int(self.ml_ext_1.Line_Cond_B.text())
        if self.ml_ext_1.Line_RLHS.text():
            RLHS = int(self.ml_ext_1.Line_RLHS.text())
        if self.ml_ext_1.Line_SF_FS.text():
            SF_FS = int(self.ml_ext_1.Line_SF_FS.text())
        if self.ml_ext_1.Line_SF_RS.text():
            SF_RS = int(self.ml_ext_1.Line_SF_RS.text())
        if self.ml_ext_1.Line_ZShear.text():
            ZShear = int(self.ml_ext_1.Line_ZShear.text())
        if self.ml_ext_1.Line_Torque.text():
            Torque = int(self.ml_ext_1.Line_Torque.text())
        if self.ml_ext_1.Line_Bend.text():
            Bend = int(self.ml_ext_1.Line_Bend.text())

        if Cond_A > Cond_B or Cond_A > RLHS or Cond_A > SF_FS or Cond_A > SF_RS or Cond_A > ZShear or \
                Cond_A > Torque or Cond_A > Bend:
            self.message_box("For Demarcation", "Coord for Cond 'A' Must be < Coord for Shear Flow etc.")
        elif Cond_B < Cond_A or Cond_B > RLHS or Cond_B > SF_FS or Cond_B > SF_RS or Cond_B > ZShear \
                or Cond_B > Torque or Cond_B > Bend:
            self.message_box("For Demarcation", "Coord for Cond 'B' Must be > Cond No and < Coord for Loads etc.")
        elif RLHS < Cond_A or RLHS < Cond_B or RLHS > SF_FS or RLHS > SF_RS or RLHS > ZShear \
                or RLHS > Torque or RLHS > Bend:
            self.message_box("For Demarcation", "Coord for RLHS Must be > Cond No and < Coord for Loads etc.")
        elif SF_FS < Cond_A or SF_FS < Cond_B or SF_FS < RLHS or SF_FS > SF_RS or SF_FS > ZShear \
                or SF_FS > Torque or SF_FS > Bend:
            self.message_box("For Demarcation", "Coord for SF_FS Must be > Cond No etc. and < Coord for Loads etc.")
        elif SF_RS < Cond_A or SF_RS < Cond_B or SF_RS < RLHS or SF_RS < SF_FS or SF_RS > ZShear \
                or SF_RS > Torque or SF_RS > Bend:
            self.message_box("For Demarcation", "Coord for SF_RS Must be > Cond No etc. and < Coord for Loads etc.")
        elif ZShear < Cond_A or ZShear < Cond_B or ZShear < RLHS or ZShear < SF_FS or ZShear < SF_RS \
                or ZShear > Torque or ZShear > Bend:
            self.message_box("For Demarcation", "Coord for ZShear Must be > Cond No etc. and < Coord for Loads etc.")
        elif Torque < Cond_A or Torque < Cond_B or Torque < RLHS or Torque < SF_FS or Torque < SF_RS \
                or Torque < ZShear or Torque > Bend:
            self.message_box("For Demarcation", "Coord for Torque Must be > Cond No etc and < Coord for Bend")
        elif Bend < Cond_A or Bend < Cond_B or Bend < RLHS or Bend < SF_FS or Bend < SF_RS \
                or Bend < ZShear or Bend < Torque:
            self.message_box("For Demarcation", "Coord for Bend Must be < Coord for Cond No, Loads etc.")
        else:
            path = self.ex_data.file_path    # Save output to folder with cleaned pictures
            if self.ml_ext_1.Check_NN_SVM_1.isChecked() and self.ex_data.ml_train_data:    # Training Data Loaded?
                if not self.ex_data.batch_NN_SVM:    # Check Status of 'flag' so the list is not Re-made
                    pic_list = self.png_list(path, "Extract")
                else:
                    pic_list = self.ex_data.pic_list_extract
                if model == "NN Extract Digits" and not self.ex_data.NN_Learn:    # If NN not learnt warn user!
                    self.message_box("Neural Network", "Requires Learning on Data before Digit Extraction!")
                else:
                    pass
                    # Call function to loop i.e. pic in list is (cropped & processed) ready for digit extraction!!!!
                    batch_dig_ext = self.batch_ext_1(path, pic_list, Cond_A, Cond_B, RLHS, SF_FS, SF_RS,
                                                     ZShear, Torque, Bend, model)
                    self.status_bar.showMessage(batch_dig_ext)
            else:    # Manual work flow i.e. Open Picture (either pre-processed or original)
                if isinstance(self.CV2_Complete, np.ndarray):    # Pic opened, Processed then Digits Extracted
                    df_loads = self.nn_svm_ext_1.ml_model(self.CV2_Complete, Cond_A, Cond_B, RLHS, SF_FS, SF_RS,
                                                          ZShear, Torque, Bend, model)
                else:    # For the previously 'cleaned' Pictures the "Pre_Crop" version is required
                    df_loads = self.nn_svm_ext_1.ml_model(self.CV2_Pre_Crop, Cond_A, Cond_B, RLHS, SF_FS, SF_RS,
                                                          ZShear, Torque, Bend, model)
                if isinstance(df_loads, pd.DataFrame) and not df_loads.empty:
                    df_loads.to_excel(path + 'A_Loads_1.xlsx', index=False, sheet_name='Loads_Mt')
                    self.status_bar.showMessage(f"Results for - {model_txt} - located at {path}", 9000)
                else:
                    self.status_bar.showMessage("Check Training Data - DataFrame is empty...", 4000)
                    self.message_box("No Data", "Verify Training Data or Processed Picture!")

    def ml_ext_data_2(self):
        """ Extract Digits from Loads Style 2 and Populate Spreadsheet """

        model = self.sender().text()
        model_txt = ""

        if model == "NN Extract Digits":
            model_txt = "Neural Network"
        elif model == "SVM Extract Digits":
            model_txt = "Support Vector Machine"

        R_Spar = 0
        Chord = 0
        Shear = 0
        Torque = 0
        Moment = 0

        # Get Demarcation
        if self.ml_ext_2.Line_R_Spar.text():
            R_Spar = int(self.ml_ext_2.Line_R_Spar.text())
        if self.ml_ext_2.Line_Chord.text():
            Chord = int(self.ml_ext_2.Line_Chord.text())
        if self.ml_ext_2.Line_Shear.text():
            Shear = int(self.ml_ext_2.Line_Shear.text())
        if self.ml_ext_2.Line_Torque.text():
            Torque = int(self.ml_ext_2.Line_Torque.text())
        if self.ml_ext_2.Line_Moment.text():
            Moment = int(self.ml_ext_2.Line_Moment.text())

        if R_Spar > Chord or R_Spar > Shear or R_Spar > Torque or R_Spar > Moment:
            self.message_box("For Demarcation", "Coord for R-Spar Must be < Coord for Loads")
        elif Chord < R_Spar or Chord > Shear or Chord > Torque or R_Spar > Moment:
            self.message_box("For Demarcation", "Coord for Chord Must be > R-Spar and < Coord for Loads")
        elif Shear < R_Spar or Shear < Chord or Shear > Torque or Shear > Moment:
            self.message_box("For Demarcation", "Coord for Shear Must be > R-Spar etc. and < Coord for Torque etc.")
        elif Torque < R_Spar or Torque < Chord or Torque < Shear or Torque > Moment:
            self.message_box("For Demarcation", "Coord for Torque Must be > R-Spar etc. and < Coord for Moment")
        elif Moment < R_Spar or Moment < Chord or Moment < Shear or Moment < Torque:
            self.message_box("For Demarcation", "Coord for Moment Must be > R-Spar etc.")
        else:
            path = self.ex_data.file_path    # Save output to folder with cleaned pictures
            if self.ml_ext_2.Check_NN_SVM_2.isChecked() and self.ex_data.ml_train_data:    # Training Data Loaded?
                if not self.ex_data.batch_NN_SVM:    # Check Status of 'flag' so the list is not Re-made
                    pic_list = self.png_list(path, "Extract")
                else:
                    pic_list = self.ex_data.pic_list_extract
                if model == "NN Extract Digits" and not self.ex_data.NN_Learn:    # If NN not learnt warn user!
                    self.message_box("Neural Network", "Requires Learning on Data before Digit Extraction!")
                else:
                    pass
                    # Call function to loop i.e. pic in list is (cropped & processed) ready for digit extraction!!!!
                    batch_dig_ext = self.batch_ext_2(path, pic_list, R_Spar, Chord, Shear, Torque, Moment, model)
                    self.status_bar.showMessage(batch_dig_ext)
            else:    # Manual work flow i.e. Open Picture (either pre-processed or original)
                if isinstance(self.CV2_Complete, np.ndarray):    # Pic opened, Processed then Digits Extracted
                    df_loads = self.nn_svm_ext_2.ml_model(self.CV2_Complete, R_Spar, Chord, Shear, Torque,
                                                          Moment, model)
                else:    # For the previously 'cleaned' Pictures the "Pre_Crop" version is required
                    df_loads = self.nn_svm_ext_2.ml_model(self.CV2_Pre_Crop, R_Spar, Chord, Shear, Torque,
                                                          Moment, model)
                if isinstance(df_loads, pd.DataFrame) and not df_loads.empty:
                    df_loads.to_excel(path + 'A_Loads.xlsx', index=False, sheet_name='Loads_Mt')
                    self.status_bar.showMessage(f"Results for - {model_txt} - located at {path}", 9000)
                else:
                    self.status_bar.showMessage("Check Training Data - DataFrame is empty...", 4000)
                    self.message_box("No Data", "Verify Training Data or Processed Picture!")

    def png_list(self, path, pro_call):
        """ Get list of Pictures in folder for a Batch Extraction """

        pic_list = []

        # May need to ensure the directory is not empty......
        for file_name in os.listdir(path):
            if pro_call == "Crop_CV2" and file_name.endswith(".png"):
                pic_list.append(file_name)
            elif pro_call == "Processed" and file_name.endswith("_cropped.png"):
                pic_list.append(file_name)
            elif pro_call == "Extract" and file_name.endswith("_processed.png"):
                pic_list.append(file_name)

        # https://stackoverflow.com/questions/2669059/how-to-sort-alpha-numeric-set-in-python
        pic_list.sort(key=self.alphanumeric_sort)

        if pro_call == "Crop_CV2":
            self.ex_data.pic_list = pic_list
            self.ex_data.pic_list_flag = True
        elif pro_call == "Processed":
            self.ex_data.pic_list_process = pic_list
            self.ex_data.pic_list_process_flag = True
        elif pro_call == "Extract":
            self.ex_data.pic_list_extract = pic_list
            self.ex_data.batch_NN_SVM = True

        return pic_list

    def alphanumeric_sort(self, dir_list):
        """ Sorted Directory Listing Alphanumerically """

        dir_sort = ''.join([format(int(x), '05d') if x.isdigit() else x for x in re.split(r'(\d+)', dir_list)])

        return dir_sort

    def batch_ext(self, path, pic_list, Grids, Start_X, X_value, x_value, Y_value, y_value, Z_value, model):
        """ Batch Digit Extraction for GFEM - Writing Data to a Spreadsheet """

        file_time = datetime.now()
        file_unqiue = file_time.strftime('%Y_%m_%d_%H_%M_%S')
        spreadsheet_name = "Batch_Grid_Coords_" + file_unqiue + ".xlsx"
        dig_ext = path + spreadsheet_name
        ext_dig = "Digits were Extracted from Pictures shown in the Tabs"

        workbook = Workbook()
        f_sheet = workbook["Sheet"]
        f_sheet.title = "Digit Pics"
        f_sheet[f"A{1}"] = ext_dig
        workbook.save(filename=dig_ext)

        for i, pic_dig in enumerate(pic_list):
            pic_png = cv2.imread(path + pic_dig)
            # Convert pic for next Step CV2 processing
            CV2_Complete = cv2.cvtColor(pic_png, cv2.COLOR_BGR2GRAY)
            pic_concat = ccwstats.pic_stitch(CV2_Complete, Grids, Start_X)
            df_x_y_z = self.nn_svm_ext.ml_model(pic_concat, Grids, Start_X, X_value, x_value,
                                                Y_value, y_value, Z_value, model)
            with pd.ExcelWriter(dig_ext, mode='a') as writer:
                df_x_y_z.to_excel(writer, index=False, sheet_name=pic_dig.strip("_cropped_processed.png"))

        return f"Extracted Digits saved in - {spreadsheet_name} - at: {path}"

    def batch_ext_1(self, path, pic_list, Cond_A, Cond_B, RLHS, SF_FS, SF_RS, ZShear, Torque, Bend, model):
        """ Batch Digit Extraction for Loads Style 1 - Writing Data to a Spreadsheet """

        file_time = datetime.now()
        file_unqiue = file_time.strftime('%Y_%m_%d_%H_%M_%S')
        spreadsheet_name = "Batch_Loads_1_" + file_unqiue + ".xlsx"
        dig_ext = path + spreadsheet_name
        ext_dig = "Digits were Extracted from Pictures shown in the Tabs"

        workbook = Workbook()
        f_sheet = workbook["Sheet"]
        f_sheet.title = "Digit Pics"
        f_sheet[f"A{1}"] = ext_dig
        workbook.save(filename=dig_ext)

        for i, pic_dig in enumerate(pic_list):
            pic_png = cv2.imread(path + pic_dig)
            # Convert pic for next Step CV2 processing
            cv2_complete = cv2.cvtColor(pic_png, cv2.COLOR_BGR2GRAY)
            df_loads = self.nn_svm_ext_1.ml_model(cv2_complete, Cond_A, Cond_B, RLHS, SF_FS, SF_RS, ZShear, Torque,
                                                  Bend, model)
            with pd.ExcelWriter(dig_ext, mode='a') as writer:
                df_loads.to_excel(writer, index=False, sheet_name=pic_dig.strip("_cropped_processed.png"))

        return f"Extracted Digits saved in - {spreadsheet_name} - at: {path}"

    def batch_ext_2(self, path, pic_list, R_Spar, Chord, Shear, Torque, Moment, model):
        """ Batch Digit Extraction for Loads Style 2 - Writing Data to a Spreadsheet """

        file_time = datetime.now()
        file_unqiue = file_time.strftime('%Y_%m_%d_%H_%M_%S')
        spreadsheet_name = "Batch_Loads_2_" + file_unqiue + ".xlsx"
        dig_ext = path + spreadsheet_name
        ext_dig = "Digits were Extracted from Pictures shown in the Tabs"

        workbook = Workbook()
        f_sheet = workbook["Sheet"]
        f_sheet.title = "Digit Pics"
        f_sheet[f"A{1}"] = ext_dig
        workbook.save(filename=dig_ext)

        for i, pic_dig in enumerate(pic_list):
            pic_png = cv2.imread(path + pic_dig)
            # Convert pic for next Step CV2 processing
            cv2_complete = cv2.cvtColor(pic_png, cv2.COLOR_BGR2GRAY)
            df_loads = self.nn_svm_ext_2.ml_model(cv2_complete, R_Spar, Chord, Shear, Torque, Moment, model)
            with pd.ExcelWriter(dig_ext, mode='a') as writer:
                df_loads.to_excel(writer, index=False, sheet_name=pic_dig.strip("_cropped_processed.png"))

        return f"Extracted Digits saved in - {spreadsheet_name} - at: {path}"

    def message_box(self, title, txtmess):
        """ Output a Message to the User """

        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setWindowTitle(title)
        msgBox.setText(txtmess)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()

    def show_messageMenu(self, state):
        """ Toggles Status Bar on/off per User """

        if state:
            self.status_bar.show()
        else:
            self.status_bar.hide()  # Or could still use the QStatusBar

    def batch_ext_message(self):
        """ Display Message in StatusBar for User """

        if self.ml_ext.Check_NN_SVM.isChecked():
            self.status_bar.showMessage("Cancelled Batch Processing...", 5000)
        else:
            self.status_bar.showMessage("Pictures Must end with '_processed.png' to be processed!")

    def cancel_clicked(self):
        """ If the user wants to Exit the application via File 'x' """

        print("Goodbye...")
        self.closeEvent(event=quit())    # Pass the event as 'quit()' so no QMessagebox

    def closeEvent(self, event):
        """ If the user clicks the 'x' (close) in the top right grab the event and show a message """

        if not self.menu_setup.view_quit.isChecked():
            quit_msg = "Leave the Application?"
            reply = QMessageBox.question(self, 'Message', quit_msg, QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                app.quit()
                print("Prompt Exit...")
            else:
                event.ignore()
        else:
            app.quit()
            print("Exit...")

    def keyPressEvent(self, event):
        """ When User hits Enter on a Button in Focus call appropriate function """

        if self.crop_etc.dock_crop_etc.isVisible():    # if the Dock Widget for Cropping is open
            if event.key() == Qt.Key_Return or Qt.Key_Enter:
                if self.crop_etc.Button_Crop.hasFocus():
                    self.plot_crop_pics()    # Call function to crop the Picture
                elif self.crop_etc.Button_Reset.hasFocus():
                    # Fails because self.sender is None from here i.e Button not clicked
                    print("self.plot_orig_pic()")

        if self.ccwithstats.dock_image_process.isVisible():    # if the Dock Widget for CV2 Connect Comp... is open
            if event.key() == Qt.Key_Return or Qt.Key_Enter:
                if self.ccwithstats.Button_Analysis.hasFocus():
                    self.ccwithstats_cv2()    # Call function to process the Picture

        event.accept()

    def coords_mouse_click(self, event):
        """ Get (x, y) co-ords from matplotlib on mouse click """

        # https://matplotlib.org/stable/users/explain/event_handling.html

        if event.xdata and event.ydata:
            x_coord, y_coord = int(event.xdata), int(event.ydata)
            for item in self.dock_list_widgets:
                if item.isVisible():
                    if item.windowTitle() == "Prepare for Processing":
                        self.crop_etc.LineE_x1.setText(str(x_coord))
                        self.crop_etc.LineE_y1.setText(str(y_coord))
                    if item.windowTitle() == "Data Extraction":
                        if self.ml_ext.Line_Grids.hasFocus():
                            self.ml_ext.Line_Grids.setText(str(x_coord))
                        elif self.ml_ext.Line_Start_X.hasFocus():
                            self.ml_ext.Line_Start_X.setText(str(x_coord))
                        elif self.ml_ext.Line_X.hasFocus():
                            self.ml_ext.Line_X.setText(str(x_coord))
                        elif self.ml_ext.Line_x.hasFocus():
                            self.ml_ext.Line_x.setText(str(x_coord))
                        elif self.ml_ext.Line_Y.hasFocus():
                            self.ml_ext.Line_Y.setText(str(x_coord))
                        elif self.ml_ext.Line_y.hasFocus():
                            self.ml_ext.Line_y.setText(str(x_coord))
                        elif self.ml_ext.Line_Z.hasFocus():
                            self.ml_ext.Line_Z.setText(str(x_coord))
                    if item.windowTitle() == "Loads Ext 2":
                        if self.ml_ext_2.Line_R_Spar.hasFocus():
                            self.ml_ext_2.Line_R_Spar.setText(str(x_coord))
                        elif self.ml_ext_2.Line_Chord.hasFocus():
                            self.ml_ext_2.Line_Chord.setText(str(x_coord))
                        elif self.ml_ext_2.Line_Shear.hasFocus():
                            self.ml_ext_2.Line_Shear.setText(str(x_coord))
                        elif self.ml_ext_2.Line_Torque.hasFocus():
                            self.ml_ext_2.Line_Torque.setText(str(x_coord))
                        elif self.ml_ext_2.Line_Moment.hasFocus():
                            self.ml_ext_2.Line_Moment.setText(str(x_coord))
        else:
            self.status_bar.showMessage("Please Select from within the Picture!", 5000)

    def coords_mouse_release(self, event):
        """ Get (x, y) co-ords from matplotlib on mouse release """

        if event.xdata and event.ydata:
            x_coord, y_coord = int(event.xdata), int(event.ydata)
            for item in self.dock_list_widgets:
                if item.isVisible():
                    if item.windowTitle() == "Prepare for Processing":
                        x_click = int(self.crop_etc.LineE_x1.text())
                        y_click = int(self.crop_etc.LineE_y1.text())
                        if x_click > x_coord:
                            self.crop_etc.LineE_x2.setText(str(x_click))
                            self.crop_etc.LineE_x1.setText(str(x_coord))
                        else:
                            self.crop_etc.LineE_x2.setText(str(x_coord))
                        if y_click > y_coord:
                            self.crop_etc.LineE_y2.setText(str(y_click))
                            self.crop_etc.LineE_y1.setText(str(y_coord))
                        else:
                            self.crop_etc.LineE_y2.setText(str(y_coord))

                        self.status_bar.showMessage("Click 'Crop' then Select OpenCV "
                                                    "from Menu or 'Reset' and try again")
        else:
            self.status_bar.showMessage("Please Select from within the Picture!", 5000)


if __name__ == "__main__":
    app = QApplication(sys.argv)    # Create the Qt Application
    form = PDiM()    # Create and show the form
    form.show()
    sys.exit(app.exec())    # Run the main Qt loop
