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
        self.svm_model = svm.SVC(kernel='poly', degree=3, tol=1E-4, C=1, gamma='scale')   # probability=True)

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

    def ml_model(self, CV2_Complete, Cond_A, Cond_B, RLHS, SF_FS, SF_RS, ZShear, Torque, Bend, ml_model):
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
            contour_sort = sort_contour.sort_contours(contours, method, "Loads_1")
            digits = []
            # initialize sort order
            x_coord = []
            x_w_dist = []
            cond_no = []
            rlhs = []
            sf_fs = []
            sf_rs = []
            zshear = []
            torque = []
            bend_mt = []
            hinge_mt = []
            no_list = ["A", "L", "R", "H", "S"]
            yy = cv2.boundingRect(contour_sort[1])[1]    # Select y co-ord of the 2nd contour.....
            row_no = 0

            for cntr in contour_sort:
                x, y, w, h = cv2.boundingRect(cntr)
                # Since if Filter_1 or (Filter_2 and Filter_3): Cannot do 23 < w otherwise collect decimal points
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
                        cond_no_d_a = ""
                        cond_no_d_b = ""
                        rlhs_d = ""
                        sf_fs_d = ""
                        sf_rs_d = ""
                        zshear_d = ""
                        torque_d = ""
                        bend_mt_d = ""
                        hinge_mt_d = ""
                        flag_cond_b = flag_rlhs = flag_sf_fs = flag_sf_rs = flag_zshear = flag_torque = \
                            flag_bend = flag_hinge_mt = False
                        sf_fs_dp = sf_rs_dp = zshear_dp = torque_dp = bend_mt_dp = hinge_mt_dp = True
                        for i, dig_ext in enumerate(sort_order):
                            # print(f"sorted {sorted_x_w[i]} and {sorted_digits[i]} where y is {y} and yy {yy}")
                            if i == 0:
                                cond_no_d_a = sorted_digits[i]
                            # if x_i > [x_(i - 1) + w_(i - 1)] it may be 'real' digit
                            if sort_order[i] > sorted_x_w[i - 1]:    # Remove spurious / phantom data
                                if dig_ext < Cond_A:
                                    if sorted_digits[i] == "-":
                                        pass
                                    else:
                                        cond_no_d_a = cond_no_d_a + sorted_digits[i]
                                elif Cond_A < dig_ext < Cond_B:
                                    if not flag_cond_b:
                                        flag_cond_b = True
                                        cond_no_d_b = cond_no_d_b + sorted_digits[i]
                                    else:
                                        if sorted_digits[i] == "-":    # and flag_cond_b:
                                            pass
                                        else:
                                            cond_no_d_b = cond_no_d_b + sorted_digits[i]
                                elif Cond_B < dig_ext < RLHS:
                                    if not flag_rlhs:
                                        flag_rlhs = True
                                        if sorted_digits[i] == "-":
                                            rlhs_d = rlhs_d + "L"
                                        else:
                                            rlhs_d = rlhs_d + sorted_digits[i]
                                    else:
                                        if sorted_digits[i] == "-":    # and flag_rlhs:
                                            pass
                                        else:
                                            rlhs_d = rlhs_d + sorted_digits[i]
                                elif RLHS < dig_ext < SF_FS:    # Prevent A, L, R, H & S from being included!!!!
                                    if not flag_sf_fs:
                                        flag_sf_fs = True
                                        if sorted_digits[i].isdigit() or sorted_digits[i] == "-":
                                            sf_fs_d = sorted_digits[i]    # First Character digit or minus
                                        else:
                                            sf_fs_d = "0"    # If not predicted as digit or minus make it 0
                                    else:    # After First character
                                        if sorted_digits[i] == "-" or sorted_digits[i] in no_list:    # and flag_sf_fs:
                                            pass    # Checking "Truth" state of the flag is unnecessary......
                                        else:
                                            if sf_fs_d == "-":    # If first character minus collect next
                                                if sorted_digits[i].isdigit():    # But must be a digit!
                                                    sf_fs_d = sf_fs_d + sorted_digits[i]
                                                else:    # Otherwise substitute 0
                                                    sf_fs_d = sf_fs_d + "0"
                                            else:
                                                if sf_fs_dp:
                                                    sf_fs_dp = False
                                                    if sorted_digits[i] == "E" or sorted_digits[i] in no_list:
                                                        sf_fs_d = sf_fs_d + "." + "8"
                                                    else:
                                                        sf_fs_d = sf_fs_d + "." + sorted_digits[i]
                                                else:
                                                    if sorted_digits[i] == "+" and "E" in sf_fs_d:
                                                        sf_fs_d = sf_fs_d + sorted_digits[i]
                                                    else:
                                                        if sorted_digits[i].isdigit() or sorted_digits[i] == "E":
                                                            if "E" in sf_fs_d and sorted_digits[i] == "E":
                                                                pass
                                                            else:
                                                                sf_fs_d = sf_fs_d + sorted_digits[i]
                                elif SF_FS < dig_ext < SF_RS:
                                    if not flag_sf_rs:    # Flag initially set as False
                                        flag_sf_rs = True
                                        if sorted_digits[i].isdigit() or sorted_digits[i] == "-":
                                            sf_rs_d = sorted_digits[i]
                                        else:
                                            sf_rs_d = "0"
                                    else:    # Now Flag is True (after first character collected)
                                        if sorted_digits[i] == "-" or sorted_digits[i] in no_list:    # and flag_sf_rs:
                                            pass
                                        else:
                                            if sf_rs_d == "-":    # If first character was '-' collect next character
                                                if sorted_digits[i].isdigit():
                                                    sf_rs_d = sf_rs_d + sorted_digits[i]
                                                else:
                                                    sf_rs_d = sf_rs_d + "0"
                                            else:    # Collecting next character if not '-' and include decimal point
                                                if sf_rs_dp:    # Initially set True
                                                    sf_rs_dp = False
                                                    if sorted_digits[i] == "E" or sorted_digits[i] in no_list:
                                                        sf_rs_d = sf_rs_d + "." + "8"
                                                    else:
                                                        sf_rs_d = sf_rs_d + "." + sorted_digits[i]
                                                else:
                                                    if sorted_digits[i] == "+" and "E" in sf_rs_d:
                                                        sf_rs_d = sf_rs_d + sorted_digits[i]
                                                    else:
                                                        if sorted_digits[i].isdigit() or sorted_digits[i] == "E":
                                                            if "E" in sf_rs_d and sorted_digits[i] == "E":
                                                                pass
                                                            else:
                                                                sf_rs_d = sf_rs_d + sorted_digits[i]
                                elif SF_RS < dig_ext < ZShear:
                                    if not flag_zshear:
                                        flag_zshear = True
                                        if sorted_digits[i].isdigit() or sorted_digits[i] == "-":
                                            zshear_d = sorted_digits[i]
                                        else:
                                            zshear_d = "0"
                                    else:
                                        if sorted_digits[i] == "-" or sorted_digits[i] in no_list:    # and flag_zshear:
                                            pass
                                        else:
                                            if zshear_d == "-":
                                                if sorted_digits[i].isdigit():
                                                    zshear_d = zshear_d + sorted_digits[i]
                                                else:
                                                    zshear_d = zshear_d + "0"
                                            else:
                                                if zshear_dp:
                                                    zshear_dp = False
                                                    if sorted_digits[i] == "E" or sorted_digits[i] in no_list:
                                                        zshear_d = zshear_d + "." + "8"
                                                    else:
                                                        zshear_d = zshear_d + "." + sorted_digits[i]
                                                else:
                                                    if sorted_digits[i] == "+" and "E" in zshear_d:
                                                        zshear_d = zshear_d + sorted_digits[i]
                                                    else:
                                                        if sorted_digits[i].isdigit() or sorted_digits[i] == "E":
                                                            if "E" in zshear and sorted_digits[i] == "E":
                                                                pass
                                                            else:
                                                                zshear_d = zshear_d + sorted_digits[i]
                                elif ZShear < dig_ext < Torque:
                                    if not flag_torque:
                                        flag_torque = True
                                        if sorted_digits[i].isdigit() or sorted_digits[i] == "-":
                                            torque_d = sorted_digits[i]
                                        else:
                                            torque_d = "0"
                                    else:
                                        if sorted_digits[i] == "-" or sorted_digits[i] in no_list:    # and flag_torque:
                                            pass
                                        else:
                                            if torque_d == "-":
                                                if sorted_digits[i].isdigit():
                                                    torque_d = torque_d + sorted_digits[i]
                                                else:
                                                    torque_d = torque_d + "0"
                                            else:
                                                if torque_dp:
                                                    torque_dp = False
                                                    if sorted_digits[i] == "E" or sorted_digits[i] in no_list:
                                                        torque_d = torque_d + "." + "8"
                                                    else:
                                                        torque_d = torque_d + "." + sorted_digits[i]
                                                else:
                                                    if sorted_digits[i] == "+" and "E" in torque_d:
                                                        torque_d = torque_d + sorted_digits[i]
                                                    else:
                                                        if sorted_digits[i].isdigit() or sorted_digits[i] == "E":
                                                            if "E" in torque_d and sorted_digits[i] == "E":
                                                                pass
                                                            else:
                                                                torque_d = torque_d + sorted_digits[i]
                                elif Torque < dig_ext < Bend:
                                    if not flag_bend:
                                        flag_bend = True
                                        if sorted_digits[i].isdigit() or sorted_digits[i] == "-":
                                            bend_mt_d = sorted_digits[i]
                                        else:
                                            bend_mt_d = "0"
                                    else:
                                        if sorted_digits[i] == "-" or sorted_digits[i] in no_list:    # and flag_bend:
                                            pass
                                        else:
                                            if bend_mt_d == "-":
                                                if sorted_digits[i].isdigit():
                                                    bend_mt_d = bend_mt_d + sorted_digits[i]
                                                else:
                                                    bend_mt_d = bend_mt_d + "0"
                                            else:
                                                if bend_mt_dp:
                                                    bend_mt_dp = False
                                                    if sorted_digits == "E" or sorted_digits[i] in no_list:
                                                        bend_mt_d = bend_mt_d + "." + "8"
                                                    else:
                                                        bend_mt_d = bend_mt_d + "." + sorted_digits[i]
                                                else:
                                                    if sorted_digits[i] == "+" and "E" in bend_mt_d:
                                                        bend_mt_d = bend_mt_d + sorted_digits[i]
                                                    else:
                                                        if sorted_digits[i].isdigit() or sorted_digits[i] == "E":
                                                            if "E" in bend_mt_d and sorted_digits[i] == "E":
                                                                pass
                                                            else:
                                                                bend_mt_d = bend_mt_d + sorted_digits[i]
                                elif Bend < dig_ext:
                                    if not flag_hinge_mt:
                                        flag_hinge_mt = True
                                        if sorted_digits[i].isdigit() or sorted_digits[i] == "-":
                                            hinge_mt_d = sorted_digits[i]
                                        else:
                                            hinge_mt_d = "0"
                                    else:
                                        if sorted_digits[i] == "-" or sorted_digits[i] in no_list:    # and flag_hinge_mt:
                                            pass
                                        else:
                                            if hinge_mt_d == "-":
                                                if sorted_digits[i].isdigit():
                                                    hinge_mt_d = hinge_mt_d + sorted_digits[i]
                                                else:
                                                    hinge_mt_d = hinge_mt_d + "0"
                                            else:
                                                if hinge_mt_dp:
                                                    hinge_mt_dp = False
                                                    if sorted_digits[i] == "E" or sorted_digits[i] in no_list:
                                                        hinge_mt_d = hinge_mt_d + "." + "8"
                                                    else:
                                                        hinge_mt_d = hinge_mt_d + "." + sorted_digits[i]
                                                else:
                                                    if sorted_digits[i] == "+" and "E" in hinge_mt_d:
                                                        hinge_mt_d = hinge_mt_d + sorted_digits[i]
                                                    else:
                                                        if sorted_digits[i].isdigit() or sorted_digits[i] == "E":
                                                            if "E" in hinge_mt_d and sorted_digits[i] == "E":
                                                                pass
                                                            else:
                                                                hinge_mt_d = hinge_mt_d + sorted_digits[i]

                        # Use a Try: Except: Block to gracefully manage errors............!!!!??!!
                        # print(f"r_spar {r_spar_d} chord {chord_d} shear {shear_d} torque {torque_d} moment {moment_d} hinge {hinge_mt_d}")
                        print(f"cond {cond_no_d_a} {cond_no_d_b} rlhs {rlhs_d} sf_fs {sf_fs_d} sf_rs {sf_rs_d} "
                              f"zshear {zshear_d} torque {torque_d} bend {bend_mt_d} hinge {hinge_mt_d}")
                        cond_no.append(cond_no_d_a + " " + cond_no_d_b)
                        rlhs.append(rlhs_d)
                        if sf_fs_d[-1].isdigit():  # sf_fs_d[-1] get last character in string entry
                            sf_fs.append(float(sf_fs_d))
                        else:
                            sf_fs.append(float(sf_fs_d + "0"))
                        if sf_rs_d[-1].isdigit():
                            sf_rs.append(float(sf_rs_d))
                        else:
                            sf_rs.append(float(sf_rs_d + "0"))
                        if zshear_d[-1].isdigit():
                            zshear.append(float(zshear_d))
                        else:
                            zshear.append(float(zshear_d + "0"))
                        if torque_d[-1].isdigit():
                            torque.append(float(torque_d))
                        else:
                            torque.append(float(torque_d + "0"))
                        if bend_mt_d[-1].isdigit():
                            bend_mt.append(float(bend_mt_d))
                        else:
                            bend_mt.append(float(bend_mt_d + "0"))
                        if hinge_mt_d[-1].isdigit():
                            hinge_mt.append(float(hinge_mt_d))
                        else:
                            hinge_mt.append(float(hinge_mt_d + "0"))

            # Pick up the last Row
            flag_cond_b = flag_rlhs = flag_sf_fs = flag_sf_rs = flag_zshear = flag_torque = \
                flag_bend = flag_hinge_mt = False
            sf_fs_dp = sf_rs_dp = zshear_dp = torque_dp = bend_mt_dp = hinge_mt_dp = True
            sort_order = sorted(x_coord)
            sorted_digits = [sor_d[1] for x in sort_order for sor_d in digits if sor_d[0] == x]
            sorted_x_w = [sor_x_w[1] for x in sort_order for sor_x_w in x_w_dist if sor_x_w[0] == x]
            cond_no_d_a = ""
            cond_no_d_b = ""
            rlhs_d = ""
            sf_fs_d = ""
            sf_rs_d = ""
            zshear_d = ""
            torque_d = ""
            bend_mt_d = ""
            hinge_mt_d = ""
            for i, dig_ext in enumerate(sort_order):
                if i == 0:
                    cond_no_d_a = sorted_digits[i]
                # if x_i > [x_(i - 1) + w_(i - 1)] it may be 'real' digit
                if sort_order[i] > sorted_x_w[i - 1]:  # Remove spurious / phantom data
                    if dig_ext < Cond_A:
                        if sorted_digits[i] == "-":
                            pass
                        else:
                            cond_no_d_a = cond_no_d_a + sorted_digits[i]
                    elif Cond_A < dig_ext < Cond_B:
                        if not flag_cond_b:
                            flag_cond_b = True
                            cond_no_d_b = cond_no_d_b + sorted_digits[i]
                        else:
                            if sorted_digits[i] == "-":    # and flag_cond_b:
                                pass
                            else:
                                cond_no_d_b = cond_no_d_b + sorted_digits[i]
                    elif Cond_B < dig_ext < RLHS:
                        if not flag_rlhs:
                            flag_rlhs = True
                            if sorted_digits[i] == "-":
                                rlhs_d = "L"
                            else:
                                rlhs_d = sorted_digits[i]
                        else:
                            if sorted_digits[i] == "-":    # and flag_rlhs:
                                pass
                            else:
                                rlhs_d = rlhs_d + sorted_digits[i]
                    elif RLHS < dig_ext < SF_FS:
                        if not flag_sf_fs:
                            flag_sf_fs = True
                            if sorted_digits[i].isdigit() or sorted_digits[i] == "-":
                                sf_fs_d = sorted_digits[i]
                            else:
                                sf_fs_d = "0"
                        else:
                            if sorted_digits[i] == "-" or sorted_digits[i] in no_list:    # and flag_sf_fs:
                                pass
                            else:
                                if sf_fs_d == "-":
                                    if sorted_digits[i].isdigit():
                                        sf_fs_d = sf_fs_d + sorted_digits[i]
                                    else:
                                        sf_fs_d = sf_fs_d + "0"
                                else:
                                    if sf_fs_dp:
                                        sf_fs_dp = False
                                        if sorted_digits[i] == "E" or sorted_digits[i] in no_list:
                                            sf_fs_d = sf_fs_d + "." + "8"
                                        else:
                                            sf_fs_d = sf_fs_d + "." + sorted_digits[i]
                                    else:
                                        if sorted_digits[i] == "+" and "E" in sf_fs_d:
                                            sf_fs_d = sf_fs_d + sorted_digits[i]
                                        else:
                                            if sorted_digits[i].isdigit() or sorted_digits[i] == "E":
                                                if "E" in sf_fs_d and sorted_digits[i] == "E":
                                                    pass
                                                else:
                                                    sf_fs_d = sf_fs_d + sorted_digits[i]
                    elif SF_FS < dig_ext < SF_RS:
                        if not flag_sf_rs:
                            flag_sf_rs = True
                            if sorted_digits[i].isdigit() or sorted_digits[i] == "-":
                                sf_rs_d = sorted_digits[i]
                            else:
                                sf_rs_d = "0"
                        else:
                            if sorted_digits[i] == "-" or sorted_digits[i] in no_list:    # and flag_sf_rs:
                                pass
                            else:
                                if sf_rs_d == "-":
                                    if sorted_digits[i].isdigit():
                                        sf_rs_d = sf_rs_d + sorted_digits[i]
                                    else:
                                        sf_rs_d = sf_rs_d + "0"
                                else:
                                    if sf_rs_dp:
                                        sf_rs_dp = False
                                        if sorted_digits[i] == "E" or sorted_digits[i] in no_list:
                                            sf_rs_d = sf_rs_d + "." + "8"
                                        else:
                                            sf_rs_d = sf_rs_d + "." + sorted_digits[i]
                                    else:
                                        if sorted_digits[i] == "+" and "E" in sf_rs_d:
                                            sf_rs_d = sf_rs_d + sorted_digits[i]
                                        else:
                                            if sorted_digits[i].isdigit() or sorted_digits[i] == "E":
                                                if "E" in sf_rs_d and sorted_digits[i] == "E":
                                                    pass
                                                else:
                                                    sf_rs_d = sf_rs_d + sorted_digits[i]
                    elif SF_RS < dig_ext < ZShear:
                        if not flag_zshear:
                            flag_zshear = True
                            if sorted_digits[i].isdigit() or sorted_digits[i] == "-":
                                zshear_d = sorted_digits[i]
                            else:
                                zshear_d = "0"
                        else:
                            if sorted_digits[i] == "-" or sorted_digits[i] in no_list:    # and flag_zshear:
                                pass
                            else:
                                if zshear_d == "-":
                                    if sorted_digits[i].isdigit():
                                        zshear_d = zshear_d + sorted_digits[i]
                                    else:
                                        zshear_d = zshear_d + "0"
                                else:
                                    if zshear_dp:
                                        zshear_dp = False
                                        if sorted_digits[i] == "E" or sorted_digits[i] in no_list:
                                            zshear_d = zshear_d + "." + "8"
                                        else:
                                            zshear_d = zshear_d + "." + sorted_digits[i]
                                    else:
                                        if sorted_digits[i] == "+" and "E" in zshear_d:
                                            zshear_d = zshear_d + sorted_digits[i]
                                        else:
                                            if sorted_digits[i].isdigit() or sorted_digits[i] == "E":
                                                if "E" in zshear_d and sorted_digits[i] == "E":
                                                    pass
                                                else:
                                                    zshear_d = zshear_d + sorted_digits[i]
                    elif ZShear < dig_ext < Torque:
                        if not flag_torque:
                            flag_torque = True
                            if sorted_digits[i].isdigit() or sorted_digits[i] == "-":
                                torque_d = sorted_digits[i]
                            else:
                                torque_d = "0"
                        else:
                            if sorted_digits[i] == "-" or sorted_digits[i] in no_list:    # and flag_torque:
                                pass
                            else:
                                if torque_d == "-":
                                    if sorted_digits[i].isdigit():
                                        torque_d = torque_d + sorted_digits[i]
                                    else:
                                        torque_d = torque_d + "0"
                                else:
                                    if torque_dp:
                                        torque_dp = False
                                        if sorted_digits[i] == "E" or sorted_digits[i] in no_list:
                                            torque_d = torque_d + "." + "8"
                                        else:
                                            torque_d = torque_d + "." + sorted_digits[i]
                                    else:
                                        if sorted_digits[i] == "+" and "E" in torque_d:
                                            torque_d = torque_d + sorted_digits[i]
                                        else:
                                            if sorted_digits[i].isdigit() or sorted_digits[i] == "E":
                                                if "E" in torque_d and sorted_digits[i] == "E":
                                                    pass
                                                else:
                                                    torque_d = torque_d + sorted_digits[i]
                    elif Torque < dig_ext < Bend:
                        if not flag_bend:
                            flag_bend = True
                            if sorted_digits[i].isdigit() or sorted_digits[i] == "-":
                                bend_mt_d = sorted_digits[i]
                            else:
                                bend_mt_d = "0"
                        else:
                            if sorted_digits[i] == "-" or sorted_digits[i] in no_list:    # and flag_bend:
                                pass
                            else:
                                if bend_mt_d == "-":
                                    if sorted_digits[i].isdigit():
                                        bend_mt_d = bend_mt_d + sorted_digits[i]
                                    else:
                                        bend_mt_d = bend_mt_d + "0"
                                else:
                                    if bend_mt_dp:
                                        bend_mt_dp = False
                                        if sorted_digits[i] == "E" or sorted_digits[i] in no_list:
                                            bend_mt_d = bend_mt_d + "." + "8"
                                        else:
                                            bend_mt_d = bend_mt_d + "." + sorted_digits[i]
                                    else:
                                        if sorted_digits[i] == "+" and "E" in bend_mt_d:
                                            bend_mt_d = bend_mt_d + sorted_digits[i]
                                        else:
                                            if sorted_digits[i].isdigit() or sorted_digits[i] == "E":
                                                if "E" in bend_mt_d and sorted_digits[i] == "E":
                                                    pass
                                                else:
                                                    bend_mt_d = bend_mt_d + sorted_digits[i]
                    elif Bend < dig_ext:
                        if not flag_hinge_mt:
                            flag_hinge_mt = True
                            if sorted_digits[i].isdigit() or sorted_digits[i] == "-":
                                hinge_mt_d = sorted_digits[i]
                            else:
                                hinge_mt_d = "0"
                        else:
                            if sorted_digits[i] == "-" or sorted_digits[i] in no_list:    # and flag_hinge_mt:
                                pass
                            else:
                                if hinge_mt_d == "-":
                                    if sorted_digits[i].isdigit():
                                        hinge_mt_d = hinge_mt_d + sorted_digits[i]
                                    else:
                                        hinge_mt_d = hinge_mt_d + "0"
                                else:
                                    if hinge_mt_dp:
                                        hinge_mt_dp = False
                                        if sorted_digits[i] == "E" or sorted_digits[i] in no_list:
                                            hinge_mt_d = hinge_mt_d + "." + "8"
                                        else:
                                            hinge_mt_d = hinge_mt_d + "." + sorted_digits[i]
                                    else:
                                        if sorted_digits[i] == "+" and "E" in hinge_mt_d:
                                            hinge_mt_d = hinge_mt_d + sorted_digits[i]
                                        else:
                                            if sorted_digits[i].isdigit() or sorted_digits[i] == "E":
                                                if "E" in hinge_mt_d and sorted_digits[i] == "E":
                                                    pass
                                                else:
                                                    hinge_mt_d = hinge_mt_d + sorted_digits[i]

            # Use a Try: Except: Block to gracefully manage errors............!!!!??!!
            cond_no.append(cond_no_d_a + " " + cond_no_d_b)
            rlhs.append(rlhs_d)
            if sf_fs_d[-1].isdigit():  # sf_fs_d[-1] get last character in string entry
                sf_fs.append(float(sf_fs_d))
            else:
                sf_fs.append(float(sf_fs_d + "0"))
            if sf_rs_d[-1].isdigit():
                sf_rs.append(float(sf_rs_d))
            else:
                sf_rs.append(float(sf_rs_d + "0"))
            if zshear_d[-1].isdigit():
                zshear.append(float(zshear_d))
            else:
                zshear.append(float(zshear_d + "0"))
            if torque_d[-1].isdigit():
                torque.append(float(torque_d))
            else:
                torque.append(float(torque_d + "0"))
            if bend_mt_d[-1].isdigit():
                bend_mt.append(float(bend_mt_d))
            else:
                bend_mt.append(float(bend_mt_d + "0"))
            if hinge_mt_d[-1].isdigit():
                hinge_mt.append(float(hinge_mt_d))
            else:
                hinge_mt.append(float(hinge_mt_d + "0"))

            df_loads = pd.DataFrame(list(zip(cond_no, rlhs, sf_fs, sf_rs, zshear, torque, bend_mt, hinge_mt)),
                                    columns=['Cond No', 'LRHS', 'SF_FS', 'SF_RS', 'ZShear', 'Torque', "Moment",
                                             "Hinge Moment"])
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
