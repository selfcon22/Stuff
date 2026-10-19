#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import QWidget, QFileDialog, QMessageBox
import numpy as np
import cv2
import S_Sort_Contours as sort_contour
import pandas as pd
from sklearn import svm
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler


class Form(QWidget):
    def __init__(self, data_ex, status_bar, parent=None):
        super(Form, self).__init__(parent)

        self.data_ex = data_ex
        self.status_bar = status_bar

        self.ml_data = None
        self.ml_path = None
        self.samples = np.array([])
        self.label = np.array([])

        params = {"hidden_layer_sizes": (400, ), "activation": "relu", "solver": "lbfgs", "alpha": 1e-6,
                  "random_state": 1, "warm_start": True, 'max_iter': 1000, 'tol': 1e-8}
        # https://scikit-learn.org/stable/modules/neural_networks_supervised.html#neural-networks-supervised
        self.nn_model = MLPClassifier(**params)
        # https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html#sklearn.svm.SVC
        self.svm_model = svm.SVC(kernel='poly', degree=3, tol=1E-4, C=1, probability=True)

        self.scaler = StandardScaler()

    def ml_learn(self):
        """ Allow User to Navigate to Training Data for Digit Extraction """

        base_path = self.data_ex.base_path

        self.status_bar.showMessage("Open Training Data for Digit Extraction", 9000)

        path_to_ml_train, filter_flag = QFileDialog.getOpenFileName(self, "Load Data", base_path, "ML (*.label)")

        # If user Cancels!!!
        if path_to_ml_train:
            file_split = path_to_ml_train.split("/")[-1]
            ml_name = file_split.replace(".label", "")    # Leaves file name (no path or pdf extension)
            save_path = path_to_ml_train.replace(ml_name + ".label", "")    # Leaves path to pdf (no file)
            self.data_ex.ml_train_data = ml_name  # User ML Training Data
            self.data_ex.file_path_ml_data = save_path  # e.g. /home/folder/project_folder/

            self.samples = np.loadtxt(save_path + ml_name + ".sample", np.float32)
            self.label = np.loadtxt(save_path + ml_name + ".label", dtype=np.str)
            if self.label.size > 0:
                # Since fast may as well fit data for the SVM Model
                self.svm_model.fit(self.samples, self.label)
                self.status_bar.showMessage(f"Training Data {ml_name} loaded from {save_path}", 4000)
            else:
                self.message_box("Training Data", "Empty - Cannot Learn!")
        else:
            self.message_box("Load Training Data", "User Cancelled - Cannot Extract Data!")

    def nn_learn(self):
        """ Neural Network Learning """

        nn_samples = self.samples
        self.scaler.fit(nn_samples)  # Not applying scaling to SVM...!?
        nn_samples = self.scaler.transform(nn_samples)
        self.nn_model.fit(nn_samples, self.label)
        self.status_bar.showMessage("Neural Net Learning complete, ready for Digit Extraction...")
        self.data_ex.NN_Learn = True

    def ml_model(self, CV2_Complete, Grids, Start_X, X_value, x_value, Y_value, y_value, Z_value, ml_model):
        """ Data Extraction using NN (Deep Learning) or SVM """

        string = ""
        df_x_y_z = pd.DataFrame.empty

        if self.label.size > 0:
            if ml_model == "NN Extract Digits":
                if not self.data_ex.NN_Learn:
                    self.message_box("Neural Network", "Requires Learning on Data before Digit Extraction!")
                    return df_x_y_z

            # Find Contours
            contours, hierarchy = cv2.findContours(CV2_Complete, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            # Call Function to Sort Contours according to the provided method
            method = "left-to-right"
            # Hard code call for GFEM box size!!!!!!!!!!!!!!!!!!!!!!!!!!
            contour_sort = sort_contour.sort_contours(contours, method, "Train")
            digits = []
            # initialize sort order
            x_coord = []
            grid_id = []
            x_num = []
            y_num = []
            z_num = []
            yy = cv2.boundingRect(contour_sort[0])[1]  # Select y co-ord of the 1st contour.....
            row_no = 0

            for cntr in contour_sort:
                # Need a filter?! e.g. if 20 < h < 50 or (15 < w < 35 and 5 < h < 15):
                [x, y, w, h] = cv2.boundingRect(cntr)
                ROI = CV2_Complete[y: y + h, x: x + w]
                ROI_Red = cv2.resize(ROI, (20, 20))
                ROI_Red = ROI_Red.reshape((1, 400))
                ROI_Red = np.float32(ROI_Red)
                if ml_model == "NN Extract Digits":
                    ROI_Red = self.scaler.transform(ROI_Red)
                    results = self.nn_model.predict(ROI_Red)
                    string = str(results[0])    # type(results[0] == 'numpy.str_' so do not need str()
                elif ml_model == "SVM Extract Digits":
                    results = self.svm_model.predict(ROI_Red)
                    string = str(results[0])    # Keep for Training Data made before change in np.txtsave

                if (yy - 17) < y < (yy + 17):
                    digits.append((int(x), string))
                    # initialize sort order
                    x_coord.append(int(x))
                else:
                    yy = y
                    row_no += 1
                    sort_order = sorted(x_coord)
                    # List comprehension to sort according to another list
                    sorted_digits = [sor_d[1] for x in sort_order for sor_d in digits if sor_d[0] == x]
                    digits = [(int(x), string)]
                    x_coord = [int(x)]
                    Grid_ID = "0"
                    X_str = ""
                    x_str = ""
                    Y_str = ""
                    y_str = ""
                    Z_str = ""
                    z_str = ""
                    for i, dig_ext in enumerate(sort_order):
                        if dig_ext < Grids:
                            if sorted_digits[i].isdigit():
                                Grid_ID = Grid_ID + sorted_digits[i]
                        elif Start_X < dig_ext < X_value:
                            if sorted_digits[i].isdigit():
                                X_str = X_str + sorted_digits[i]
                        elif X_value < dig_ext < x_value:
                            if sorted_digits[i].isdigit():
                                x_str = x_str + sorted_digits[i]
                        elif x_value < dig_ext < Y_value:
                            if sorted_digits[i].isdigit():
                                Y_str = Y_str + sorted_digits[i]
                        elif Y_value < dig_ext < y_value:
                            if sorted_digits[i].isdigit():
                                y_str = y_str + sorted_digits[i]
                        elif y_value < dig_ext < Z_value:
                            if sorted_digits[i].isdigit():
                                Z_str = Z_str + sorted_digits[i]
                        elif Z_value < dig_ext:
                            if sorted_digits[i].isdigit():
                                z_str = z_str + sorted_digits[i]

                    grid_id.append(int(Grid_ID))
                    x_num.append(float(X_str + "." + x_str + "0"))  # Adding "0" ensures no error as X_Str == ""
                    y_num.append(float(Y_str + "." + y_str + "0"))
                    z_num.append(float(Z_str + "." + z_str + "0"))

            # Pick up the last Row
            sort_order = sorted(x_coord)
            sorted_digits = [sor_d[1] for x in sort_order for sor_d in digits if sor_d[0] == x]
            Grid_ID = "0"
            X_str = ""
            x_str = ""
            Y_str = ""
            y_str = ""
            Z_str = ""
            z_str = ""
            for i, dig_ext in enumerate(sort_order):
                if dig_ext < Grids:
                    if sorted_digits[i].isdigit():
                        Grid_ID = Grid_ID + sorted_digits[i]
                elif Start_X < dig_ext < X_value:
                    if sorted_digits[i].isdigit():
                        X_str = X_str + sorted_digits[i]
                elif X_value < dig_ext < x_value:
                    if sorted_digits[i].isdigit():
                        x_str = x_str + sorted_digits[i]
                elif x_value < dig_ext < Y_value:
                    if sorted_digits[i].isdigit():
                        Y_str = Y_str + sorted_digits[i]
                elif Y_value < dig_ext < y_value:
                    if sorted_digits[i].isdigit():
                        y_str = y_str + sorted_digits[i]
                elif y_value < dig_ext < Z_value:
                    if sorted_digits[i].isdigit():
                        Z_str = Z_str + sorted_digits[i]
                elif Z_value < dig_ext:
                    if sorted_digits[i].isdigit():
                        z_str = z_str + sorted_digits[i]

            grid_id.append(int(Grid_ID))
            x_num.append(float(X_str + "." + x_str + "0"))
            y_num.append(float(Y_str + "." + y_str + "0"))
            z_num.append(float(Z_str + "." + z_str + "0"))

            df_x_y_z = pd.DataFrame(list(zip(grid_id, x_num, y_num, z_num)), columns=['GRID', 'X', 'Y', 'Z'])
        else:
            self.message_box("Training Data", "Empty - Cannot Learn!")

        return df_x_y_z

    def message_box(self, title, txtmess):
        """ Output a Message to the User """

        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setWindowTitle(title)
        msgBox.setText(txtmess)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()
