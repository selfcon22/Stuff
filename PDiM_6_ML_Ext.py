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
        self.dock_extract = QDockWidget('Data Extraction')

        # Create Objects QPushbutton etc. used in the QDockWidget
        self.Label_Train_Data = QLabel("Load Training")
        self.Button_Train_Data = QPushButton("Data")
        self.Button_Train_Data.setToolTip("Click to Load Training Data")
        self.Label_NN_Learn = QLabel("Click for NN")
        self.Button_NN_Learn = QPushButton("Learning")  # If change chase through i.e. def ml_ext_data(self):
        self.Button_NN_Learn.setToolTip("Click for NN Learning")
        self.Label_X_Y_Z = QLabel("Define Demarcation")
        self.Label_X_Y_Z_2 = QLabel("X Coord for:")
        self.Label_Grids = QLabel("GRID ID")
        self.Line_Grids = QLineEdit()
        self.Label_Start_X = QLabel("Start (X, Y, Z)")
        self.Line_Start_X = QLineEdit()
        self.Label_X = QLabel("X Whole Nos")
        self.Line_X = QLineEdit()
        self.Label_x = QLabel("X Decimals")
        self.Line_x = QLineEdit()
        self.Line_x.setToolTip("X Co-ordinate of 'X' Co-ordinate Decimal")
        self.Label_Y = QLabel("Y Whole Nos")
        self.Line_Y = QLineEdit()
        self.Label_y = QLabel("Y Decimals")
        self.Line_y = QLineEdit()
        self.Line_y.setToolTip("X Co-ordinate of 'Y' Co-ordinate Decimal")
        self.Label_Z = QLabel("Z Whole Nos")
        self.Line_Z = QLineEdit()
        self.Line_Z.setToolTip("X Co-ordinate of 'Z' Co-ordinate Decimal")
        self.Label_Batch = QLabel("For Batch Jobs Check the Box")
        self.Check_NN_SVM = QCheckBox()
        self.Label_NN = QLabel("Neural Network")
        self.Button_NN = QPushButton("NN Extract Digits")  # If change chase through
        self.Button_NN.setToolTip("Click to use Deep Learning on Digit Prediction")
        self.Label_SVM = QLabel("Support Vector Machine")
        self.Button_SVM = QPushButton("SVM Extract Digits")
        self.Button_SVM.setToolTip("Click to use Support Vector Machine on Digit Prediction")

        self.Line_Grids.setText("110")
        self.Line_Start_X.setText("340")
        self.Line_X.setText("390")
        self.Line_x.setText("495")
        self.Line_Y.setText("592")
        self.Line_y.setText("665")
        self.Line_Z.setText("725")

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
        layout_pics.addWidget(self.Label_NN_Learn, 3, 0)
        layout_pics.addWidget(self.Button_NN_Learn, 4, 1)
        layout_pics.addWidget(self.Label_X_Y_Z, 5, 0, 1, 0)    # - Stretched across columns
        layout_pics.addWidget(self.Label_X_Y_Z_2, 6, 0)
        layout_pics.addWidget(self.Label_Grids, 7, 0)
        self.Line_Grids.setValidator(validator_coords)
        layout_pics.addWidget(self.Line_Grids, 7, 1)
        layout_pics.addWidget(self.Label_Start_X, 8, 0)
        self.Line_Start_X.setValidator(validator_coords)
        layout_pics.addWidget(self.Line_Start_X, 8, 1)
        layout_pics.addWidget(self.Label_X, 9, 0)
        self.Line_X.setValidator(validator_coords)
        layout_pics.addWidget(self.Line_X, 9, 1)
        layout_pics.addWidget(self.Label_x, 10, 0)
        self.Line_x.setValidator(validator_coords)
        layout_pics.addWidget(self.Line_x, 10, 1)
        layout_pics.addWidget(self.Label_Y, 11, 0)
        self.Line_Y.setValidator(validator_coords)
        layout_pics.addWidget(self.Line_Y, 11, 1)
        layout_pics.addWidget(self.Label_y, 12, 0)
        self.Line_y.setValidator(validator_coords)
        layout_pics.addWidget(self.Line_y, 12, 1)
        layout_pics.addWidget(self.Label_Z, 13, 0)
        self.Line_Z.setValidator(validator_coords)
        layout_pics.addWidget(self.Line_Z, 13, 1)
        layout_pics.addWidget(self.Label_Batch, 14, 0, 1, 0)
        layout_pics.addWidget(self.Check_NN_SVM, 15, 0)
        layout_pics.addWidget(self.Label_NN, 16, 0)
        layout_pics.addWidget(self.Button_NN, 17, 0)
        layout_pics.addWidget(self.Label_SVM, 18, 0)
        layout_pics.addWidget(self.Button_SVM, 19, 0)

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
