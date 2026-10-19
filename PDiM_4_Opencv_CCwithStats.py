#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import QDockWidget, QWidget, QLabel, QLineEdit, QPushButton, QGridLayout, QRadioButton,\
    QSlider, QCheckBox
from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator


class Form(QWidget):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        # Create an Object for a QDockWidget
        self.dock_image_process = QDockWidget("Components with Stats")

        # Create Objects QPushbutton etc. used in the QDockWidget
        self.Label_Threshold_Max = QLabel("Threshold")
        self.Slide_Threshold_Max = QSlider(Qt.Vertical)    # Horizontal)
        self.Slide_Threshold_Max.setRange(0, 255)
        self.Slide_Threshold_Max.setToolTip("Pixel Values < Filter set to 0")
        self.Label_Value_Threshold = QLabel("Value")
        self.Label_Threshold_Value = QLabel("180")    # Keep start value in sync with self.Slide_Threshold_Max.setValue
        self.Label_MaxValue = QLabel("MaxValue")
        self.Slide_MaxValue = QSlider(Qt.Vertical)    # Horizontal)
        self.Slide_MaxValue.setRange(0, 255)
        self.Slide_MaxValue.setToolTip("Pixel Value if > Threshold")
        self.Label_Value_MaxValue = QLabel("Value")
        self.Label_MaxValue_Value = QLabel("255")
        self.Label_Connect = QLabel("Connectivity")
        self.Radio_Connect = QRadioButton("Checked is 8")
        self.Label_Artifact_Area = QLabel("Artifact Area")
        self.LineE_Artifact_Area = QLineEdit()
        self.LineE_Artifact_Area.setToolTip("Define Largest Size of Area to Remove")
        self.Label_Check_Batch = QLabel("Batch Job")
        self.Check_Batch = QCheckBox()
        self.Check_Batch.setToolTip("Check the Box for Batch Processing")
        self.Label_Analysis = QLabel("Click for")
        self.Button_Analysis = QPushButton("Analysis")
        self.Button_Analysis.setToolTip("Click to Remove Artifacts < Defined Area")

        # Convert CV2 to setPlaceholderText as Hint
        self.Slide_Threshold_Max.setValue(180)
        self.Slide_MaxValue.setValue(255)
        self.LineE_Artifact_Area.setText("90")

        self.Slide_Threshold_Max.setObjectName("From ccwithstats threshold")
        self.Slide_MaxValue.setObjectName("From ccwithstats maxvalue")

    def DockWidget(self):
        """ Create a QDockWidget with QButton for the user """

        # Create an Object for a QWidget
        widget_process = QWidget()
        # Create an Object for a vertical arrangement of widgets
        layout_process = QGridLayout()

        # Create regular expression to limit user mistyping
        rx_thres = QRegularExpression("\\d{1,5}")
        validator_thres = QRegularExpressionValidator(rx_thres, self)

        # Add the widgets to the layout
        layout_process.addWidget(self.Label_Threshold_Max, 1, 0)
        layout_process.addWidget(self.Slide_Threshold_Max, 1, 1)
        layout_process.addWidget(self.Label_Value_Threshold, 2, 0)
        layout_process.addWidget(self.Label_Threshold_Value, 2, 1)
        layout_process.addWidget(self.Label_MaxValue, 3, 0)
        layout_process.addWidget(self.Slide_MaxValue, 3, 1)
        layout_process.addWidget(self.Label_Value_MaxValue, 4, 0)
        layout_process.addWidget(self.Label_MaxValue_Value, 4, 1)
        layout_process.addWidget(self.Label_Connect, 5, 0)
        layout_process.addWidget(self.Radio_Connect, 5, 1)
        layout_process.addWidget(self.Label_Artifact_Area, 6, 0)
        self.LineE_Artifact_Area.setValidator(validator_thres)
        layout_process.addWidget(self.LineE_Artifact_Area, 6, 1)
        layout_process.addWidget(self.Label_Check_Batch, 7, 0)
        layout_process.addWidget(self.Check_Batch, 7, 1)
        layout_process.addWidget(self.Label_Analysis, 8, 0)
        layout_process.addWidget(self.Button_Analysis, 8, 1)

        # Set the layout to the QWidget
        widget_process.setLayout(layout_process)

        # Set areas in the window where the dockwidget object may reside
        self.dock_image_process.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        # Set the Object defined for the QVBoxLayout to the QDockWidget Object
        self.dock_image_process.setWidget(widget_process)

        return self.dock_image_process

    def show_closed_widgets(self, closed_widgets):
        """ Reshow Closed Widgets for the user """

        for item in closed_widgets:
            if item:
                self.dock_image_process.show()  # OR setVisible(True)
