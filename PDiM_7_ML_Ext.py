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
        self.dock_extract = QDockWidget('Loads Ext 1')

        # Create Objects QPushbutton etc. used in the QDockWidget
        self.Label_Train_Data_1 = QLabel("Load Training")
        self.Button_Train_Data_1 = QPushButton("Data")
        self.Button_Train_Data_1.setToolTip("Click to Load Training Data")
        self.Label_NN_Learn_1 = QLabel("Click for NN")
        self.Button_NN_Learn_1 = QPushButton("Learning")  # If change chase through i.e. def ml_ext_data(self):
        self.Button_NN_Learn_1.setToolTip("Click for NN Learning")
        self.Label_Loads_1 = QLabel("Define Demarcation")
        self.Label_Cond_A = QLabel("Condition 'A'")
        self.Line_Cond_A = QLineEdit()
        self.Label_Cond_B = QLabel("Condition 'B'")
        self.Line_Cond_B = QLineEdit()
        self.Label_RLHS = QLabel("Right Left HS")
        self.Line_RLHS = QLineEdit()
        self.Label_SF_FS = QLabel("SF FS")
        self.Line_SF_FS = QLineEdit()
        self.Label_SF_RS = QLabel("SF RS")
        self.Line_SF_RS = QLineEdit()
        self.Line_SF_FS.setToolTip("X Co-ordinate of Shear Flow Front Spar")
        self.Label_ZShear = QLabel("Z-Shear")
        self.Line_ZShear = QLineEdit()
        self.Label_Torque = QLabel("Torque")
        self.Line_Torque = QLineEdit()
        self.Line_Torque.setToolTip("X Co-ordinate of Torque")
        self.Label_Bend = QLabel("Bending")
        self.Line_Bend = QLineEdit()
        self.Line_Bend.setToolTip("X Co-ordinate of Bend")
        self.Label_Batch = QLabel("For Batch Jobs Check the Box")
        self.Check_NN_SVM_1 = QCheckBox()
        self.Label_NN_1 = QLabel("Neural Network")
        self.Button_NN_1 = QPushButton("NN Extract Digits")  # If change chase through
        self.Button_NN_1.setToolTip("Click to use Deep Learning on Digit Prediction")
        self.Label_SVM_1 = QLabel("Support Vector Machine")
        self.Button_SVM_1 = QPushButton("SVM Extract Digits")
        self.Button_SVM_1.setToolTip("Click to use Support Vector Machine on Digit Prediction")

        self.Line_Cond_A.setText("340")
        self.Line_Cond_B.setText("720")
        self.Line_RLHS.setText("870")
        self.Line_SF_FS.setText("1230")
        self.Line_SF_RS.setText("1630")
        self.Line_ZShear.setText("2010")
        self.Line_Torque.setText("2410")
        self.Line_Bend.setText("2790")

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
        layout_pics.addWidget(self.Label_Train_Data_1, 1, 0)
        layout_pics.addWidget(self.Button_Train_Data_1, 2, 1)
        layout_pics.addWidget(self.Label_NN_Learn_1, 3, 0)
        layout_pics.addWidget(self.Button_NN_Learn_1, 4, 1)
        layout_pics.addWidget(self.Label_Loads_1, 5, 0, 1, 0)    # - Stretched across columns
        layout_pics.addWidget(self.Label_Cond_A, 6, 0)
        self.Line_Cond_A.setValidator(validator_coords)
        layout_pics.addWidget(self.Line_Cond_A, 6, 1)
        layout_pics.addWidget(self.Label_Cond_B, 7, 0)
        self.Line_Cond_B.setValidator(validator_coords)
        layout_pics.addWidget(self.Line_Cond_B, 7, 1)
        layout_pics.addWidget(self.Label_RLHS, 8, 0)
        self.Line_RLHS.setValidator(validator_coords)
        layout_pics.addWidget(self.Line_RLHS, 8, 1)
        layout_pics.addWidget(self.Label_SF_FS, 9, 0)
        self.Line_SF_FS.setValidator(validator_coords)
        layout_pics.addWidget(self.Line_SF_FS, 9, 1)
        layout_pics.addWidget(self.Label_SF_RS, 10, 0)
        self.Line_SF_RS.setValidator(validator_coords)
        layout_pics.addWidget(self.Line_SF_RS, 10, 1)
        layout_pics.addWidget(self.Label_ZShear, 11, 0)
        self.Line_ZShear.setValidator(validator_coords)
        layout_pics.addWidget(self.Line_ZShear, 11, 1)
        layout_pics.addWidget(self.Label_Torque, 12, 0)
        self.Line_Torque.setValidator(validator_coords)
        layout_pics.addWidget(self.Line_Torque, 12, 1)
        layout_pics.addWidget(self.Label_Bend, 13, 0)
        self.Line_Bend.setValidator(validator_coords)
        layout_pics.addWidget(self.Line_Bend, 13, 1)
        layout_pics.addWidget(self.Label_Batch, 14, 0, 1, 0)
        layout_pics.addWidget(self.Check_NN_SVM_1, 15, 0)
        layout_pics.addWidget(self.Label_NN_1, 16, 0)
        layout_pics.addWidget(self.Button_NN_1, 17, 0)
        layout_pics.addWidget(self.Label_SVM_1, 18, 0)
        layout_pics.addWidget(self.Button_SVM_1, 19, 0)

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
