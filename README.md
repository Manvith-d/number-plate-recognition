# Number Plate Recognition

A Python desktop application that detects number plate regions and reads their text using OpenCV and Tesseract OCR.

## Technologies
Python, OpenCV, NumPy, Pillow, Tesseract OCR, and Tkinter.

## Run
1. Install Python with Tkinter support and install the Tesseract executable for your operating system. Make sure `tesseract` is on your PATH.
2. Create a virtual environment and install `pip install -r requirements.txt`.
3. Run `python main.py` from this directory.
4. Choose an image you have permission to use, then click **Classify Image**.

`gui.py` preserves an earlier version with stricter geometry thresholds. Optional `car.png` and `logo.png` can be added locally. Example vehicle photos and generated OCR images are excluded from this source release.

## Method
Gaussian blur, grayscale conversion, Sobel edges, Otsu thresholding, morphological closing, contour filtering, and Tesseract OCR.

## Limitations
This is an educational prototype. Results depend on image quality, lighting, plate orientation, and the contour heuristics. No accuracy benchmark is claimed. The interface is designed for desktop use.

## Validation
Python syntax checked for this release. GUI and OCR execution require a local desktop and Tesseract installation and have not been tested as part of portfolio preparation.
