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
        self.dock_crop_etc = QDockWidget('Prepare for Processing')

        # Create Objects QPushbutton etc. used in the QDockWidget
        self.Label_x1 = QLabel("X Co-ord")
        self.LineE_x1 = QLineEdit()
        self.LineE_x1.setToolTip("Enter X Co-ordinate of Top Left Corner")
        self.Label_y1 = QLabel("Y Co-ord")
        self.LineE_y1 = QLineEdit()
        self.LineE_y1.setToolTip("Enter Y Co-ordinate of Top Left Corner")
        self.Label_x2 = QLabel("X Co-ord")
        self.LineE_x2 = QLineEdit()
        self.LineE_x2.setToolTip("Enter X Co-ordinate of Bottom Right Corner")
        self.Label_y2 = QLabel("Y Co-ord")
        self.LineE_y2 = QLineEdit()
        self.LineE_y2.setToolTip("Enter Y Co-ordinate of Bottom Right Corner")
        self.Label_Check_Batch = QLabel("Batch Job")
        self.Check_Batch = QCheckBox()
        self.Check_Batch.setChecked(True)
        self.Check_Batch_Even = QCheckBox("Even Pages")
        self.Check_Batch_Odd = QCheckBox("Odd Pages")
        self.Check_Batch.setToolTip("Uncheck Box for Batch Processing")
        self.Label_Crop = QLabel("Click to")
        self.Button_Crop = QPushButton("Crop")
        self.Button_Crop.setToolTip("Crops the Picture to Defined Limits")
        self.Label_Reset = QLabel("Click to")
        self.Button_Reset = QPushButton("Reset")
        self.Button_Reset.setToolTip("Shows the Original Picture")

        # Convert CV2 to setPlaceholderText as Hint
        self.LineE_x1.setPlaceholderText("500")
        self.LineE_y1.setPlaceholderText("145")
        self.LineE_x2.setPlaceholderText("1375")
        self.LineE_y2.setPlaceholderText("1940")

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
        layout_pics.addWidget(self.Label_x1, 1, 0)
        self.LineE_x1.setValidator(validator_coords)
        layout_pics.addWidget(self.LineE_x1, 1, 1)
        layout_pics.addWidget(self.Label_y1, 2, 0)
        self.LineE_y1.setValidator(validator_coords)
        layout_pics.addWidget(self.LineE_y1, 2, 1)
        layout_pics.addWidget(self.Label_x2, 3, 0)
        self.LineE_x2.setValidator(validator_coords)
        layout_pics.addWidget(self.LineE_x2, 3, 1)
        layout_pics.addWidget(self.Label_y2, 4, 0)
        self.LineE_y2.setValidator(validator_coords)
        layout_pics.addWidget(self.LineE_y2, 4, 1)
        layout_pics.addWidget(self.Label_Check_Batch, 5, 0)
        layout_pics.addWidget(self.Check_Batch, 5, 1)
        layout_pics.addWidget(self.Check_Batch_Even, 6, 1)
        layout_pics.addWidget(self.Check_Batch_Odd, 7, 1)
        layout_pics.addWidget(self.Label_Crop, 8, 0)
        layout_pics.addWidget(self.Button_Crop, 8, 1)
        layout_pics.addWidget(self.Label_Reset, 9, 0)
        layout_pics.addWidget(self.Button_Reset, 9, 1)

        # Set the layout to the QWidget
        widget_pics.setLayout(layout_pics)

        # Set areas in the window where the dockwidget object may reside
        self.dock_crop_etc.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        # Set the Object defined for the QVBoxLayout to the QDockWidget Object
        self.dock_crop_etc.setWidget(widget_pics)

        return self.dock_crop_etc

    def show_closed_widgets(self, closed_widgets):
        """ Reshow Closed Widgets for the User """

        for item in closed_widgets:
            if item:
                self.dock_crop_etc.show()  # OR setVisible(True)
