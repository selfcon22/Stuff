#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from PySide6.QtCore import QObject


class ExchangeData(QObject):
    def __init__(self, parent=None):
        super(ExchangeData, self).__init__(parent)
        """ Exchange of Data between Classes """

        self.base_path = os.getcwd()

        # Path to Original Picture
        self.orig_pic = None
        self.orig_name = None
        self.file_path = None    # e.g. /home/folder/project_folder/

        # Batch Crop Flag
        # Ctrl or Alt key results in a repeat to the batch process is repeated......
        self.batch_crop = True    # Set a flag and make False after processing only set True after loading another pic
        self.pic_list_flag = False    # Set initial flag for list of pictures Batch Crop to False
        self.pic_list = []    # Create an initially empty list
        self.pic_list_process_flag = False
        self.pic_list_process = []

        # Path to ML Training Data
        self.ml_train_data = None  # Source ML Training Data
        self.file_path_ml_data = self.base_path + "/"

        # Has Neural Net Learned?
        self.NN_Learn = False

        # Batch Digit Extraction
        self.batch_NN_SVM = False    # Has a list of pics ending with _processed.png been made
        self.pic_list_extract = []
