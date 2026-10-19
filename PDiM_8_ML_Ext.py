#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import QDockWidget, QWidget, QLabel, QPushButton, QLineEdit, QCheckBox, QGridLayout
from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator


class Form(QWidget):
    def __init__(self, data_ex, status_bar, parent=None):
        super(Form, self).__init__(parent)

        self.data_ex = data_ex
        self.status_bar = status_bar

        # Create an Object for a QDockWidget
        self.dock_extract = QDockWidget('Loads Ext 2')

        # Create Objects QPushbutton etc. used in the QDockWidget
        self.Label_Train_Data = QLabel("Load Training")
        self.Button_Train_Data = QPushButton("Data")
        self.Button_Train_Data.setToolTip("Click to Load Training Data")
        self.Label_NN_Learn_2 = QLabel("Click for NN")
        self.Button_NN_Learn_2 = QPushButton("Learning")  # If change chase through i.e. def ml_ext_data(self):
        self.Button_NN_Learn_2.setToolTip("Click for NN Learning")
        self.Label_Loads = QLabel("Define Demarcation")
        self.Label_R_Spar = QLabel("R-Spar")
        self.Line_R_Spar = QLineEdit()
        self.Line_R_Spar.setToolTip("X Co-ordinate to define Demarcation")
        self.Label_Chord = QLabel("36% Chord")
        self.Line_Chord = QLineEdit()
        self.Label_Shear = QLabel("Shear")
        self.Line_Shear = QLineEdit()
        self.Label_Torque = QLabel("Torque")
        self.Line_Torque = QLineEdit()
        self.Label_Moment = QLabel("Moment")
        self.Line_Moment = QLineEdit()
        self.Label_Batch = QLabel("For Batch Jobs Check the Box")
        self.Check_NN_SVM_2 = QCheckBox()
        self.Label_NN_2 = QLabel("Neural Network")
        self.Button_NN_2 = QPushButton("NN Extract Digits")  # If change chase through
        self.Button_NN_2.setToolTip("Click to use Deep Learning on Digit Prediction")
        self.Label_SVM_2 = QLabel("Support Vector Machine")
        self.Button_SVM_2 = QPushButton("SVM Extract Digits")
        self.Button_SVM_2.setToolTip("Click to use Support Vector Machine on Digit Prediction")

        self.Line_R_Spar.setText("340")
        self.Line_Chord.setText("770")
        self.Line_Shear.setText("1230")
        self.Line_Torque.setText("1750")
        self.Line_Moment.setText("2260")

    def DockWidget(self):
        """ Create a QDockWidget with QButton for the user """

        # Create an Object for a QWidget
        widget_pics = QWidget()
        # Create an Object for a vertical arrangement of widgets
        layout_pics = QGridLayout()

        # Create regular expression to limit user mistyping
        rx_coords = QRegularExpression("\\d{1,5}")
        validator_coords = QRegularExpressionValidator(rx_coords, self)

        # Add the widgets to the layout
        layout_pics.addWidget(self.Label_Train_Data, 1, 0)
        layout_pics.addWidget(self.Button_Train_Data, 2, 1)
        layout_pics.addWidget(self.Label_NN_Learn_2, 3, 0)
        layout_pics.addWidget(self.Button_NN_Learn_2, 4, 1)
        layout_pics.addWidget(self.Label_Loads, 5, 0, 1, 0)    # - Stretched across columns
        layout_pics.addWidget(self.Label_R_Spar, 6, 0)
        layout_pics.addWidget(self.Line_R_Spar, 6, 1)
        layout_pics.addWidget(self.Label_Chord, 7, 0)
        self.Line_Chord.setValidator(validator_coords)
        layout_pics.addWidget(self.Line_Chord, 7, 1)
        layout_pics.addWidget(self.Label_Shear, 8, 0)
        self.Line_Torque.setValidator(validator_coords)
        layout_pics.addWidget(self.Line_Shear, 8, 1)
        layout_pics.addWidget(self.Label_Torque, 9, 0)
        self.Line_Torque.setValidator(validator_coords)
        layout_pics.addWidget(self.Line_Torque, 9, 1)
        layout_pics.addWidget(self.Label_Moment, 10, 0)
        self.Line_Moment.setValidator(validator_coords)
        layout_pics.addWidget(self.Line_Moment, 10, 1)
        layout_pics.addWidget(self.Label_Batch, 11, 0, 1, 0)
        layout_pics.addWidget(self.Check_NN_SVM_2, 12, 0)
        layout_pics.addWidget(self.Label_NN_2, 13, 0)
        layout_pics.addWidget(self.Button_NN_2, 14, 0, 1, 0)
        layout_pics.addWidget(self.Label_SVM_2, 15, 0, 1, 0)
        layout_pics.addWidget(self.Button_SVM_2, 16, 0, 1, 0)

        # Set the layout to the QWidget
        widget_pics.setLayout(layout_pics)

        # Set areas in the window where the dockwidget object may reside
        self.dock_extract.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        # Set the Object defined for the QVBoxLayout to the QDockWidget Object
        self.dock_extract.setWidget(widget_pics)

        return self.dock_extract

    def show_closed_widgets(self, closed_widgets):
        """ Reshow Closed Widgets for the user """

        for item in closed_widgets:
            if item:
                self.dock_extract.show()  # OR setVisible(True)
