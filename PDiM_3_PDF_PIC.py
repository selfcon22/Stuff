#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import QWidget, QFileDialog, QLineEdit, QInputDialog, QMessageBox
from pdf2image import convert_from_path
import cv2


class Form(QWidget):
    def __init__(self, data_ex, status_bar, parent=None):
        super(Form, self).__init__(parent)

        self.data_ex = data_ex
        self.status_bar = status_bar

    def open_pdfs(self):
        """ Allow User to Navigate to PDFs for Conversion """

        base_path = self.data_ex.base_path

        self.status_bar.showMessage("Open PDF File for Conversion to a Picture", 9000)

        path_to_pdf, filter_flag = QFileDialog.getOpenFileName(self, "Load PDF", base_path, "PDFs (*.pdf)")

        # If user Cancels!!
        if path_to_pdf:
            file_split = path_to_pdf.split("/")[-1]
            save_name = file_split.replace(".pdf", "")    # Leaves file name (no path or pdf extension)
            save_path = path_to_pdf.replace(save_name + ".pdf", "")    # Leaves path to pdf (no file)

            pages = convert_from_path(path_to_pdf, grayscale=True, dpi=300)   # Increase Dots Per Inch!?!?!
            # Save pdf pages as pictures
            for i, pdf_page in enumerate(pages):
                pages[i].save(save_path + save_name + "_" + str(i + 1) + '.png', 'PNG')
                self.status_bar.showMessage(f"Page {i + 1} Converted and Saved at {save_path}", 4000)
        else:
            self.message_box("PDF to Picture", "User Cancelled PDF Selection for Conversion")

    def open_pic(self):
        """ Allow User to Navigate to Pictures for Processing / Digit Extraction """

        base_path = self.data_ex.base_path

        self.status_bar.showMessage("Open Picture for Image Processing", 9000)

        path_to_pic, filter_flag = QFileDialog.getOpenFileName(self, "Load PIC", base_path, "PIC (*.png)")

        # If user Cancels!!!
        if path_to_pic:
            file_split = path_to_pic.split("/")[-1]
            pic_name = file_split.replace(".png", "")    # Leaves file name (no path or pdf extension)
            save_path = path_to_pic.replace(pic_name + ".png", "")    # Leaves path to pdf (no file)

            self.data_ex.orig_pic = path_to_pic    # Source Picture
            self.data_ex.orig_name = pic_name
            self.data_ex.file_path = save_path    # e.g. /home/folder/project_folder/

            self.status_bar.showMessage(f"Picture {pic_name} loaded from {save_path}", 4000)
        else:
            self.message_box("Load Picture", "User Cancelled Picture Selection for Processing")

    def save_pic(self, crop_pic, save_process):
        """ Save Cropped or Processed Picture """

        path_to_pic = self.data_ex.file_path
        pic_name = self.data_ex.orig_name

        if crop_pic.any():
            if save_process == 'Save Pic':
                save_pic = path_to_pic + pic_name + "_processed.png"
                cv2.imwrite(save_pic, crop_pic)
                self.status_bar.showMessage(f"Saved {pic_name + '_processed'} at {path_to_pic}", 4000)
            else:
                save_name, accept = QInputDialog.getText(self, "Save As.....", 'Enter Name', QLineEdit.Normal)
                if accept:
                    if save_name:    # By default, cv2.imwrite () assumes the value of cv2.IMWRITE_JPEG_QUALITY as 95
                        save_pic = path_to_pic + save_name + ".png"
                        cv2.imwrite(save_pic, crop_pic, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
                        self.status_bar.showMessage(f"Saved {save_name} at {path_to_pic}", 4000)
                    else:
                        save_pic = path_to_pic + pic_name + "_cv2.png"
                        cv2.imwrite(save_pic, crop_pic, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
                        self.status_bar.showMessage(f"Saved {pic_name + '_cv2'} at {path_to_pic}", 4000)
                else:
                    self.message_box("Save As....", "User Cancelled Saving of Picture")
        else:
            self.message_box("Save Picture", "Failed - User did Not Process Picture")

    def batch_save(self, orig_name, crop_pro_pic, save_process):
        """ Save Batch Cropped or Processed Pictures """

        path_to_pic = self.data_ex.file_path

        if crop_pro_pic.any():
            save_pic = path_to_pic + orig_name + save_process + ".png"
            cv2.imwrite(save_pic, crop_pro_pic)
            self.status_bar.showMessage(f"Saved {orig_name + save_process} at {path_to_pic}")
        else:
            self.message_box("Save Picture", "Failed - User did Not Crop / Process Picture")

    def message_box(self, title, txtmess):
        """ Output a Message to the User """

        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setWindowTitle(title)
        msgBox.setText(txtmess)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()
