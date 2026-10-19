#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import QDockWidget, QWidget, QLabel, QPushButton, QGridLayout
from PySide6.QtCore import Qt


class Form(QWidget):
    def __init__(self, data_ex, status_bar, parent=None):
        super(Form, self).__init__(parent)

        self.data_ex = data_ex
        self.status_bar = status_bar

        # Create an Object for a QDockWidget
        self.dock_training = QDockWidget('Train for Loads Processing')

        # Create Objects QPushbutton etc. used in the QDockWidget
        self.Label_Train = QLabel("Click to ")
        self.Button_Train = QPushButton("Train Loads")
        self.Button_Train.setToolTip("Click to Create a Training Dataset")
        self.Label_Train_Pic = QLabel()
        self.Label_0_Qty = QLabel("0")
        self.Label_1_Qty = QLabel("0")
        self.Label_2_Qty = QLabel("0")
        self.Label_3_Qty = QLabel("0")
        self.Label_4_Qty = QLabel("0")
        self.Label_5_Qty = QLabel("0")
        self.Label_6_Qty = QLabel("0")
        self.Label_7_Qty = QLabel("0")
        self.Label_8_Qty = QLabel("0")
        self.Label_9_Qty = QLabel("0")
        self.Label_Minus_Qty = QLabel("0")
        self.Label_Plus_Qty = QLabel("0")
        self.Label_E_Qty = QLabel("0")
        self.Label_A_Qty = QLabel("0")
        self.Label_L_Qty = QLabel("0")
        self.Label_R_Qty = QLabel("0")
        self.Label_H_Qty = QLabel("0")
        self.Label_S_Qty = QLabel("0")
        self.Label_0 = QLabel("0")
        self.Label_1 = QLabel("1")
        self.Label_2 = QLabel("2")
        self.Label_3 = QLabel("3")
        self.Label_4 = QLabel("4")
        self.Label_5 = QLabel("5")
        self.Label_6 = QLabel("6")
        self.Label_7 = QLabel("7")
        self.Label_8 = QLabel("8")
        self.Label_9 = QLabel("9")
        self.Label_Minus = QLabel("-")
        self.Label_Plus = QLabel("+")
        self.Label_E = QLabel("E")
        self.Label_A = QLabel("A")
        self.Label_L = QLabel("L")
        self.Label_R = QLabel("R")
        self.Label_H = QLabel("H")
        self.Label_S = QLabel("S")

    def DockWidget(self):
        """ Create a QDockWidget with QButton for the user """

        # Create an Object for a QWidget
        widget_pics = QWidget()
        # Create an Object for a vertical arrangement of widgets
        layout_pics = QGridLayout()

        # Need to set up regex so only 0-9 can be entered!!!

        # Add the widgets to the layout
        layout_pics.addWidget(self.Label_Train, 2, 0)
        layout_pics.addWidget(self.Button_Train, 2, 1, 1, 2)
        layout_pics.addWidget(self.Label_Train_Pic, 3, 0, 2, 3)
        layout_pics.addWidget(self.Label_0_Qty, 5, 0)
        layout_pics.addWidget(self.Label_1_Qty, 5, 1)
        layout_pics.addWidget(self.Label_2_Qty, 5, 2)
        layout_pics.addWidget(self.Label_0, 6, 0)
        layout_pics.addWidget(self.Label_1, 6, 1)
        layout_pics.addWidget(self.Label_2, 6, 2)
        layout_pics.addWidget(self.Label_3_Qty, 7, 0)
        layout_pics.addWidget(self.Label_4_Qty, 7, 1)
        layout_pics.addWidget(self.Label_5_Qty, 7, 2)
        layout_pics.addWidget(self.Label_3, 8, 0)
        layout_pics.addWidget(self.Label_4, 8, 1)
        layout_pics.addWidget(self.Label_5, 8, 2)
        layout_pics.addWidget(self.Label_6_Qty, 9, 0)
        layout_pics.addWidget(self.Label_7_Qty, 9, 1)
        layout_pics.addWidget(self.Label_8_Qty, 9, 2)
        layout_pics.addWidget(self.Label_6, 10, 0)
        layout_pics.addWidget(self.Label_7, 10, 1)
        layout_pics.addWidget(self.Label_8, 10, 2)
        layout_pics.addWidget(self.Label_9_Qty, 11, 0)
        layout_pics.addWidget(self.Label_9, 12, 0)
        layout_pics.addWidget(self.Label_Minus_Qty, 11, 1)
        layout_pics.addWidget(self.Label_Minus, 12, 1)
        layout_pics.addWidget(self.Label_Plus_Qty, 11, 2)
        layout_pics.addWidget(self.Label_Plus, 12, 2)
        layout_pics.addWidget(self.Label_E_Qty, 13, 0)
        layout_pics.addWidget(self.Label_E, 14, 0)
        layout_pics.addWidget(self.Label_A_Qty, 13, 1)
        layout_pics.addWidget(self.Label_A, 14, 1)
        layout_pics.addWidget(self.Label_L_Qty, 13, 2)
        layout_pics.addWidget(self.Label_L, 14, 2)
        layout_pics.addWidget(self.Label_R_Qty, 15, 0)
        layout_pics.addWidget(self.Label_R, 16, 0)
        layout_pics.addWidget(self.Label_H_Qty, 15, 1)
        layout_pics.addWidget(self.Label_H, 16, 1)
        layout_pics.addWidget(self.Label_S_Qty, 15, 2)
        layout_pics.addWidget(self.Label_S, 16, 2)

        # Set the layout to the QWidget
        widget_pics.setLayout(layout_pics)

        # Set areas in the window where the dockwidget object may reside
        self.dock_training.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        # Set the Object defined for the QVBoxLayout to the QDockWidget Object
        self.dock_training.setWidget(widget_pics)

        return self.dock_training

    def show_closed_widgets(self, closed_widgets):
        """ Reshow Closed Widgets for the user """

        for item in closed_widgets:
            if item:
                self.dock_training.show()  # OR setVisible(True)
