#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import QDockWidget, QWidget, QLabel, QPushButton, QGridLayout, QSpinBox, QCheckBox
from PySide6.QtCore import Qt


class Form(QWidget):
    def __init__(self, data_ex, status_bar, parent=None):
        super(Form, self).__init__(parent)

        self.data_ex = data_ex
        self.status_bar = status_bar

        # Create an Object for a QDockWidget
        self.dock_process_tools = QDockWidget("Process Tools")

        # Create Objects QPushbutton etc. used in the QDockWidget
        self.Label_Check = QLabel("Batch Job")
        self.Check_Batch = QCheckBox()
        self.Label_Batch_No = QLabel("No Processing")
        self.Button_Batch_No = QPushButton("Click")
        self.Label_Erode_Description = QLabel("Erode Picture")
        self.Label_Erode_Kernel = QLabel("Kernel Value")
        self.Spin_Erode_Kernel = QSpinBox()
        self.Spin_Erode_Kernel.setRange(1, 5)
        self.Label_Erode_Button = QLabel("Click to")
        self.Button_Erode_Kernel = QPushButton("Erode")
        self.Label_Dilate_Description = QLabel("Dilate Picture")
        self.Label_Dilate_Kernel = QLabel("Kernel Value")
        self.Spin_Dilate_Kernel = QSpinBox()
        self.Spin_Dilate_Kernel.setRange(1, 5)
        self.Label_Dilate_Button = QLabel("Click to")
        self.Button_Dilate_Kernel = QPushButton("Dilate")
        self.Label_Opening_Description = QLabel("Opening of Picture")
        self.Label_Opening_Kernel = QLabel("Kernel Value")
        self.Spin_Opening_Kernel = QSpinBox()
        self.Spin_Opening_Kernel.setRange(1, 5)
        self.Label_Opening_Button = QLabel("Click for")
        self.Button_Opening_Kernel = QPushButton("Opening")
        self.Label_Remove_Description = QLabel("Remove Horizontal Lines")
        self.Label_Remove_Kernel = QLabel("Kernel Value")
        self.Spin_Remove_Kernel = QSpinBox()
        self.Spin_Remove_Kernel.setRange(1, 5)
        self.Spin_Remove_Kernel.setValue(3)
        self.Label_Remove_Button = QLabel("Click to Remove")
        self.Button_Remove_Kernel = QPushButton("Lines")

    def DockWidget(self):
        """ Create a QDockWidget with QButton for the user """

        # Create an Object for a QWidget
        widget_process = QWidget()
        # Create an Object for a vertical arrangement of widgets
        layout_process = QGridLayout()

        # Add the widgets to the layout
        layout_process.addWidget(self.Label_Check, 1, 0)
        layout_process.addWidget(self.Check_Batch, 1, 1)
        layout_process.addWidget(self.Label_Batch_No, 2, 0)
        layout_process.addWidget(self.Button_Batch_No, 2, 1)
        layout_process.addWidget(self.Label_Erode_Description, 3, 0, 1, 0)
        layout_process.addWidget(self.Label_Erode_Kernel, 4, 0)
        layout_process.addWidget(self.Spin_Erode_Kernel, 4, 1)
        layout_process.addWidget(self.Label_Erode_Button, 5, 0)
        layout_process.addWidget(self.Button_Erode_Kernel, 5, 1)
        layout_process.addWidget(self.Label_Dilate_Description, 6, 0, 1, 0)
        layout_process.addWidget(self.Label_Dilate_Kernel, 7, 0)
        layout_process.addWidget(self.Spin_Dilate_Kernel, 7, 1)
        layout_process.addWidget(self.Label_Dilate_Button, 8, 0)
        layout_process.addWidget(self.Button_Dilate_Kernel, 8, 1)
        layout_process.addWidget(self.Label_Opening_Description, 9, 0, 1, 0)
        layout_process.addWidget(self.Label_Opening_Kernel, 10, 0)
        layout_process.addWidget(self.Spin_Opening_Kernel, 10, 1)
        layout_process.addWidget(self.Label_Opening_Button, 11, 0)
        layout_process.addWidget(self.Button_Opening_Kernel, 11, 1)
        layout_process.addWidget(self.Label_Remove_Description, 12, 0, 1, 0)
        layout_process.addWidget(self.Label_Remove_Kernel, 13, 0)
        layout_process.addWidget(self.Spin_Remove_Kernel, 13, 1)
        layout_process.addWidget(self.Label_Remove_Button, 14, 0)
        layout_process.addWidget(self.Button_Remove_Kernel, 14, 1)

        # Set the layout to the QWidget
        widget_process.setLayout(layout_process)

        # Set areas in the window where the dockwidget object may reside
        self.dock_process_tools.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        # Set the Object defined for the QVBoxLayout to the QDockWidget Object
        self.dock_process_tools.setWidget(widget_process)

        return self.dock_process_tools

    def show_closed_widgets(self, closed_widgets):
        """ Reshow Closed Widgets for the user """

        for item in closed_widgets:
            if item:
                self.dock_process_tools.show()  # OR setVisible(True)
