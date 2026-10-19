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

#        params = {"hidden_layer_sizes": (400, ), "activation": "relu", "solver": "lbfgs", "alpha": 1e-6,
#                  "random_state": 1, "warm_start": True, 'max_iter': 3000, 'tol': 1e-8}

        params = {"hidden_layer_sizes": (400, 400, 400, 400, 400, 400), "activation": "tanh", "solver": "adam", "alpha": 1e-6,
                  'max_iter': 4500}
        # https://scikit-learn.org/stable/modules/neural_networks_supervised.html#neural-networks-supervised
        self.nn_model = MLPClassifier(**params)
        # https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html#sklearn.svm.SVC
        self.svm_model = svm.SVC(kernel='poly', degree=3, tol=1E-4, C=1, gamma='scale')    # probability=True)

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
            self.label = np.loadtxt(save_path + ml_name + ".label", dtype=np.str_)
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

    def ml_model(self, CV2_Complete, R_Spar, Chord, Shear, Torque, Moment, ml_model):
        """ Data Extraction using NN (Deep Learning) or SVM """

        string = ""
        df_loads = pd.DataFrame.empty

        if self.label.size > 0:
            if ml_model == "NN Extract Digits":
                if not self.data_ex.NN_Learn:
                    self.message_box("Neural Network", "Requires Learning on Data before Digit Extraction!")
                    return df_loads

            # Find Contours
            contours, hierarchy = cv2.findContours(CV2_Complete, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            # Call Function to Sort Contours according to the provided method
            method = "left-to-right"
            contour_sort = sort_contour.sort_contours(contours, method, "Loads_2")
            digits = []
            # initialize sort order
            x_coord = []
            x_w_dist = []
            r_spar = []
            chord = []
            shear = []
            torque = []
            moment = []
            hinge_mt = []
            yy = cv2.boundingRect(contour_sort[1])[1]    # Select y co-ord of the 2nd contour.....
            row_no = 0
            mt_div = 100

            for cntr in contour_sort:
                x, y, w, h = cv2.boundingRect(cntr)
                # Since if Filter_1 or (Filter_2 and Filter_3): Cannot go less than 23 < w otherwise collect decimal points
                if 20 < h < 50 or (23 < w < 35 and 5 < h < 15):
                    ROI = CV2_Complete[y: y + h, x: x + w]
                    ROI_Red = cv2.resize(ROI, (20, 20))
                    ROI_Red = ROI_Red.reshape((1, 400))
                    ROI_Red = np.float32(ROI_Red)
                    if ml_model == "NN Extract Digits":
                        ROI_Red = self.scaler.transform(ROI_Red)
                        results = self.nn_model.predict(ROI_Red)
                        string = str(results[0])  # type(results[0] == 'numpy.str_' so do not need str()
                    elif ml_model == "SVM Extract Digits":
                        results = self.svm_model.predict(ROI_Red)
                        string = str(results[0])  # Keep for Training Data made before change in np.txtsave

                    if (yy - 45) < y < (yy + 45):
                        digits.append((int(x), string))
                        # initialize sort order
                        x_coord.append(int(x))
                        x_w_dist.append((int(x), int(x + 0.75 * w)))    # Most of width......
                    else:
                        yy = y
                        row_no += 1
                        sort_order = sorted(x_coord)
                        # List comprehension to sort according to another list
                        sorted_digits = [sor_d[1] for x in sort_order for sor_d in digits if sor_d[0] == x]
                        sorted_x_w = [sor_x_w[1] for x in sort_order for sor_x_w in x_w_dist if sor_x_w[0] == x]
                        digits = [(int(x), string)]
                        x_coord = [int(x)]
                        x_w_dist = [(int(x), int(x + 0.75 * w))]    # Most of width......
                        r_spar_d = ""
                        chord_d = ""
                        shear_d = ""
                        torque_d = ""
                        moment_d = ""
                        hinge_mt_d = ""
                        flag_chord = flag_shear = flag_torque = flag_moment = flag_hinge_mt = False
                        for i, dig_ext in enumerate(sort_order):
                            # print(f"sorted {sorted_x_w[i]} and {sorted_digits[i]} where y is {y} and yy {yy}")
                            if i == 0:
                                if sorted_digits[i].isdigit() or sorted_digits[i] == "-":
                                    r_spar_d = sorted_digits[i]
                            # if x_i > [x_(i - 1) + w_(i - 1)] it may be 'real' digit
                            if sort_order[i] > sorted_x_w[i - 1]:    # Remove spurious / phantom data
                                if dig_ext < R_Spar:
                                    if sorted_digits[i] == "-":    # and flag_r_spar:
                                        pass
                                    else:
                                        if sorted_digits[i].isdigit():
                                            r_spar_d = r_spar_d + sorted_digits[i]
                                elif R_Spar < dig_ext < Chord:
                                    if not flag_chord:
                                        flag_chord = True
                                        if sorted_digits[i].isdigit() or sorted_digits[i] == "-":
                                            chord_d = chord_d + sorted_digits[i]
                                    else:
                                        if sorted_digits[i] == "-":    # and flag_chord:
                                            pass
                                        else:
                                            if sorted_digits[i].isdigit():
                                                chord_d = chord_d + sorted_digits[i]
                                elif Chord < dig_ext < Shear:
                                    if not flag_shear:
                                        flag_shear = True
                                        if sorted_digits[i].isdigit() or sorted_digits[i] == "-":
                                            shear_d = shear_d + sorted_digits[i]
                                    else:
                                        if sorted_digits[i] == "-":    # and flag_shear:
                                            pass
                                        else:
                                            if sorted_digits[i].isdigit():
                                                shear_d = shear_d + sorted_digits[i]
                                elif Shear < dig_ext < Torque:
                                    if not flag_torque:
                                        flag_torque = True
                                        if sorted_digits[i].isdigit() or sorted_digits[i] == "-":
                                            torque_d = torque_d + sorted_digits[i]
                                    else:
                                        if sorted_digits[i] == "-":    # and flag_torque:
                                            pass
                                        else:
                                            if sorted_digits[i].isdigit():
                                                torque_d = torque_d + sorted_digits[i]
                                elif Torque < dig_ext < Moment:
                                    if not flag_moment:
                                        flag_moment = True
                                        if sorted_digits[i].isdigit() or sorted_digits[i] == "-":
                                            moment_d = moment_d + sorted_digits[i]
                                            # print(f"Delta {(sort_order[i] - sort_order[i - 1])} and {sorted_digits[i]}")
                                            # If gap between last torque digit and first mt digit  < 230
                                            # must be .0 (> 230 is .00)    Ugly, but........                 != "-":
                                            if (sort_order[i] - sort_order[i - 1]) < 230 and sorted_digits[i].isdigit():
                                                mt_div = 10
                                    else:
                                        if sorted_digits[i] == "-":    # and flag_moment:
                                            pass
                                        else:
                                            if sorted_digits[i].isdigit():
                                                moment_d = moment_d + sorted_digits[i]
                                elif Moment < dig_ext:
                                    if not flag_hinge_mt:
                                        flag_hinge_mt = True
                                        if sorted_digits[i].isdigit() or sorted_digits[i] == "-":
                                            hinge_mt_d = hinge_mt_d + sorted_digits[i] 
                                    else:
                                        if sorted_digits[i] == "-":    # and flag_hinge_mt:
                                            pass
                                        else:
                                            if sorted_digits[i].isdigit():
                                                hinge_mt_d = hinge_mt_d + sorted_digits[i]

                        # Use a Try: Except: Block to gracefully manage errors............!!!!??!!
                        # print(f"r_spar {r_spar_d} chord {chord_d} shear {shear_d} torque {torque_d} moment {moment_d} hinge {hinge_mt_d}")
                        r_spar.append(float(r_spar_d + ".0") / 100)
                        chord.append(float(chord_d + ".0") / 100)
                        shear.append(float(shear_d + ".0") / 100)
                        torque.append(float(torque_d + ".0") / 100)
                        moment.append(float(moment_d + ".0") / mt_div)
                        mt_div = 100
                        hinge_mt.append(float(hinge_mt_d + ".0") / 100)

            # Pick up the last Row
            flag_chord = flag_shear = flag_torque = flag_moment = flag_hinge_mt = False
            sort_order = sorted(x_coord)
            sorted_digits = [sor_d[1] for x in sort_order for sor_d in digits if sor_d[0] == x]
            sorted_x_w = [sor_x_w[1] for x in sort_order for sor_x_w in x_w_dist if sor_x_w[0] == x]
            r_spar_d = ""
            chord_d = ""
            shear_d = ""
            torque_d = ""
            moment_d = ""
            hinge_mt_d = ""
            mt_div = 100
            for i, dig_ext in enumerate(sort_order):
                if i == 0:
                    if sorted_digits[i].isdigit() or sorted_digits[i] == "-":
                        r_spar_d = sorted_digits[i]
                # if x_i > [x_(i - 1) + w_(i - 1)] it may be 'real' digit
                if sort_order[i] > sorted_x_w[i - 1]:  # Remove spurious / phantom data
                    if dig_ext < R_Spar:
                        if sorted_digits[i] == "-":    # and flag_r_spar:
                            pass
                        else:
                            if sorted_digits[i].isdigit():
                                r_spar_d = r_spar_d + sorted_digits[i]
                    elif R_Spar < dig_ext < Chord:
                        if not flag_chord:
                            flag_chord = True
                            if sorted_digits[i].isdigit() or sorted_digits[i] == "-":
                                chord_d = chord_d + sorted_digits[i]
                        else:
                            if sorted_digits[i] == "-":    # and flag_chord:
                                pass
                            else:
                                if sorted_digits[i].isdigit():
                                    chord_d = chord_d + sorted_digits[i]
                    elif Chord < dig_ext < Shear:
                        if not flag_shear:
                            flag_shear = True
                            if sorted_digits[i].isdigit() or sorted_digits[i] == "-":
                                shear_d = shear_d + sorted_digits[i]
                        else:
                            if sorted_digits[i] == "-":    # and flag_shear:
                                pass
                            else:
                                if sorted_digits[i].isdigit():
                                    shear_d = shear_d + sorted_digits[i]
                    elif Shear < dig_ext < Torque:
                        if not flag_torque:
                            flag_torque = True
                            if sorted_digits[i].isdigit() or sorted_digits[i] == "-":
                                torque_d = torque_d + sorted_digits[i]
                        else:
                            if sorted_digits[i] == "-":    # and flag_torque:
                                pass
                            else:
                                if sorted_digits[i].isdigit():
                                    torque_d = torque_d + sorted_digits[i]
                    elif Torque < dig_ext < Moment:
                        if not flag_moment:
                            flag_moment = True
                            if sorted_digits[i].isdigit() or sorted_digits[i] == "-":
                                moment_d = moment_d + sorted_digits[i]
                                # Not ideal, but if page format consistent                        != "-":
                                if (sort_order[i] - sort_order[i - 1]) < 230 and sorted_digits[i].isdigit():
                                    mt_div = 10
                        else:
                            if sorted_digits[i] == "-":    # and flag_moment:
                                pass
                            else:
                                if sorted_digits[i].isdigit():
                                    moment_d = moment_d + sorted_digits[i]
                    elif Moment < dig_ext:
                        if not flag_hinge_mt:
                            flag_hinge_mt = True
                            if sorted_digits[i].isdigit() or sorted_digits[i] == "-":
                                hinge_mt_d = hinge_mt_d + sorted_digits[i]
                        else:
                            if sorted_digits[i] == "-":    # and flag_hinge_mt:
                                pass
                            else:
                                if sorted_digits[i].isdigit():
                                    hinge_mt_d = hinge_mt_d + sorted_digits[i]

            # Use a Try: Except: Block to gracefully manage errors............!!!!??!!
            r_spar.append(float(r_spar_d + ".0") / 100)
            chord.append(float(chord_d + ".0") / 100)
            shear.append(float(shear_d + ".0") / 100)
            torque.append(float(torque_d + ".0") / 100)
            moment.append(float(moment_d + ".0") / mt_div)
            hinge_mt.append(float(hinge_mt_d + ".0") / 100)

            df_loads = pd.DataFrame(list(zip(r_spar, chord, shear, torque, moment, hinge_mt)),
                                    columns=['R-Spar', '36% Chord', 'Shear', 'Torque', "Moment", "Hinge Moment"])
        else:
            self.message_box("Training Data", "Empty - Cannot Learn!")

        return df_loads

    def message_box(self, title, txtmess):
        """ Output a Message to the User """

        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setWindowTitle(title)
        msgBox.setText(txtmess)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()
