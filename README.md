# Qt OCR Wrapper
Qt based GUI for Tesseract OCR made in Python. Nothing groundbreaking, just a simple project for my university.

## Usage
- Install [Tesseract](https://github.com/tesseract-ocr/tesseract)
- Run the program
- Load the image, get the extracted text.

## Building an executable

```bash
pyinstaller --onefile --windowed --icon=icon.ico --name="QtOCR" --add-data "icon.png;." main.py
```

## Libraries used

- PyQt6
- Pytesseract
- Pillow
- Pyperclip
- Numpy
- OpenCV