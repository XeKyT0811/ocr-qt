import sys
import ctypes
import pyperclip

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from PIL import Image
import pytesseract

import cv2
import numpy as np

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("com.xekyt.ocr_qt")

def get_langs():
    lang_list = pytesseract.get_languages(config="")
    lang_list = [l for l in lang_list if l != "osd"]
    return "+".join(lang_list)

ALL_LANGS = get_langs()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Text Extractor")
        self.setFixedSize(1200,600)
        self.setWindowIcon(QIcon("icon.png"))

        root = QWidget()
        self.setCentralWidget(root)
        layout = QGridLayout(root)
        layout.setSpacing(10)

        self.image_container = QScrollArea()
        self.image_container.setWidgetResizable(False)
        self.image_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_container.setFixedWidth(700)
        self.image_label = QLabel("Load an image to extract text")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(self.image_container.width() - 20, self.image_container.height() - 80)
        self.image_container.setWidget(self.image_label)

        self.extracted_text = QPlainTextEdit()
        self.extracted_text.setPlaceholderText("Extracted text will appear here")
        self.extracted_text.setReadOnly(True)

        button_load_image = QPushButton("Load Image")
        button_load_image.setFixedHeight(50)
        button_load_image.clicked.connect(self.load_image)
        button_copy_text = QPushButton("Copy to Clipboard")
        button_copy_text.setFixedHeight(50)
        button_copy_text.clicked.connect(self.copy_text)

        layout.addWidget(self.image_container, 0, 0)
        layout.addWidget(self.extracted_text, 0, 1)
        layout.addWidget(button_load_image, 1, 0)
        layout.addWidget(button_copy_text, 1, 1)

    def message_popup(self, type = "", title = "", message = "", desc = ""):
        error_dialog = QMessageBox(self)
        match type:
            case "normal":
                error_dialog.setIcon(QMessageBox.Icon.Information)
            case "error":
                error_dialog.setIcon(QMessageBox.Icon.Critical)
            case _:
                error_dialog.setIcon(QMessageBox.Icon.NoIcon)
        error_dialog.setWindowTitle(title)
        error_dialog.setText(message)
        error_dialog.setInformativeText(desc)
        error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        error_dialog.exec()

    def decode_image(self, path):
        pil_image = Image.open(path)
        img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
        gray = clahe.apply(gray)
        gray = cv2.normalize(gray, None, 30, 220, cv2.NORM_MINMAX)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        if np.mean(binary) < 127:
            binary = cv2.bitwise_not(binary)
        processed_image = Image.fromarray(binary)
        try:
            extracted_text = pytesseract.image_to_string(processed_image, lang=ALL_LANGS, timeout=10)
        except RuntimeError:
            self.message_popup("error","Error","Timeout error","Text extraction took too long")
            extracted_text = ""
        return extracted_text

    def load_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if (not path):
            return
        pixmap = QPixmap(path)
        pixmap = pixmap.scaled(
                self.image_container.width() - 20,
                pixmap.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
        )
        self.image_label.setPixmap(pixmap)
        self.image_label.resize(pixmap.size())
        self.extracted_text.setPlainText(self.decode_image(path))
    
    def copy_text(self):
        pyperclip.copy(self.extracted_text.toPlainText())
        self.message_popup("normal", "Success", "Text successfully copied to clipboard")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    try:
        pytesseract.get_tesseract_version()
        window.show()
        sys.exit(app.exec())
    except pytesseract.pytesseract.TesseractNotFoundError:
        window.message_popup("error", "Error", "Tesseract not detected!", "Please install Tesseract OCR from the official <a href=\"https://github.com/tesseract-ocr/tesseract\">GitHub Page</a>")
        exit()
    