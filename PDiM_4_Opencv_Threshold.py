#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import QDockWidget, QWidget, QLabel, QPushButton, QGridLayout, QSlider
from PySide6.QtCore import Qt


class Form(QWidget):
    def __init__(self, data_ex, status_bar, parent=None):
        super(Form, self).__init__(parent)

        self.data_ex = data_ex
        self.status_bar = status_bar

        # Create an Object for a QDockWidget
        self.dock_threshold_image = QDockWidget("Thresholding Process")

        # Create Objects QPushbutton etc. used in the QDockWidget
        self.Label_Description = QLabel("Input Data...")
        self.Label_Threshold_Max = QLabel("Threshold")
        self.Slide_Threshold_Max = QSlider(Qt.Vertical)    # Horizontal)
        self.Slide_Threshold_Max.setRange(0, 255)
        self.Label_Value_Threshold = QLabel("Value")
        self.Label_Threshold_Value = QLabel("180")
        self.Label_MaxValue = QLabel("MaxValue")
        self.Slide_MaxValue = QSlider(Qt.Vertical)    # Horizontal)
        self.Slide_MaxValue.setRange(0, 255)
        self.Label_Value_MaxValue = QLabel("Value")
        self.Label_MaxValue_Value = QLabel("255")
        self.Label_Threshold_Technique = QLabel("Click Technique")
        self.Button_Threshold_Binary = QPushButton("THRESH_BINARY")
        self.Button_Threshold_Trunc = QPushButton("THRESH_TRUNC")
        self.Button_Threshold_Tozero = QPushButton("THRESH_TOZERO")

        # Convert CV2 to setPlaceholderText as Hint
        self.Slide_Threshold_Max.setValue(180)
        self.Slide_MaxValue.setValue(255)

        self.Slide_Threshold_Max.setObjectName("From Threshold threshold")
        self.Slide_MaxValue.setObjectName("From Threshold maxvalue")

    def DockWidget(self):
        """ Create a QDockWidget with QButton for the user """

        # Create an Object for a QWidget
        widget_process = QWidget()
        # Create an Object for a vertical arrangement of widgets
        layout_process = QGridLayout()

        # Add the widgets to the layout
        layout_process.addWidget(self.Label_Threshold_Max, 1, 0)
        layout_process.addWidget(self.Slide_Threshold_Max, 1, 1)
        layout_process.addWidget(self.Label_Value_Threshold, 2, 0)
        layout_process.addWidget(self.Label_Threshold_Value, 2, 1)
        layout_process.addWidget(self.Label_MaxValue, 3, 0)
        layout_process.addWidget(self.Slide_MaxValue, 3, 1)
        layout_process.addWidget(self.Label_Value_MaxValue, 4, 0)
        layout_process.addWidget(self.Label_MaxValue_Value, 4, 1)
        layout_process.addWidget(self.Label_Threshold_Technique, 5, 0, 1, 0)
        layout_process.addWidget(self.Button_Threshold_Binary, 6, 0, 1, 0)
        layout_process.addWidget(self.Button_Threshold_Trunc, 7, 0, 1, 0)
        layout_process.addWidget(self.Button_Threshold_Tozero, 8, 0, 1, 0)

        # Set the layout to the QWidget
        widget_process.setLayout(layout_process)

        # Set areas in the window where the dockwidget object may reside
        self.dock_threshold_image.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        # Set the Object defined for the QVBoxLayout to the QDockWidget Object
        self.dock_threshold_image.setWidget(widget_process)

        return self.dock_threshold_image

    def show_closed_widgets(self, closed_widgets):
        """ Reshow Closed Widgets for the user """

        for item in closed_widgets:
            if item:
                self.dock_threshold_image.show()  # OR setVisible(True)
