import tkinter as tk
from tkinter import filedialog
from tkinter import *
from PIL import ImageTk, Image
from tkinter import PhotoImage
import numpy as np
import cv2
import pytesseract as tess
import os

def clean2_plate(plate):
    gray_img = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray_img, 110, 255, cv2.THRESH_BINARY)
    num_contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if num_contours:
        contour_area = [cv2.contourArea(c) for c in num_contours]
        max_cntr_index = np.argmax(contour_area)

        max_cnt = num_contours[max_cntr_index]
        max_cntArea = contour_area[max_cntr_index]
        x, y, w, h = cv2.boundingRect(max_cnt)

        if not ratioCheck(max_cntArea, w, h):
            return plate, None

        final_img = thresh[y:y + h, x:x + w]
        return final_img, [x, y, w, h]

    else:
        return plate, None

def ratioCheck(area, width, height):
    ratio = float(width) / float(height)
    if ratio < 1:
        ratio = 1 / ratio
    # Relaxed thresholds
    if (area < 500 or area > 100000) or (ratio < 1.5 or ratio > 8):
        return False
    return True

def isMaxWhite(plate):
    avg = np.mean(plate)
    return avg >= 115

def ratio_and_rotation(rect):
    (x, y), (width, height), rect_angle = rect
    if width > height:
        angle = -rect_angle
    else:
        angle = 90 + rect_angle

    if abs(angle) > 40:
        return False

    if height == 0 or width == 0:
        return False

    area = height * width
    return ratioCheck(area, width, height)

# GUI Start
top = tk.Tk()
top.geometry('900x700')
top.title('Number Plate Recognition')

# Use a fallback-safe logo or omit iconphoto entirely
if os.path.exists("logo.png"):
    try:
        logo_image = PhotoImage(file="logo.png")
        top.iconphoto(True, logo_image)
    except:
        pass

img = None
if os.path.exists("car.png"):
    try:
        img = ImageTk.PhotoImage(Image.open("car.png"))
    except:
        img = None

top.configure(background='#CDCDCD')
label = Label(top, background='#CDCDCD', font=('arial', 35, 'bold'))
sign_image = Label(top, bd=10)
plate_image = Label(top, bd=10)

def classify(file_path):
    res_text = [""]
    res_img = [None]

    print(f"[INFO] Running OCR on: {file_path}")
    img = cv2.imread(file_path)
    if img is None:
        label.configure(foreground='red', text="❌ Unable to read image")
        return

    img2 = cv2.GaussianBlur(img, (3, 3), 0)
    img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    img2 = cv2.Sobel(img2, cv2.CV_8U, 1, 0, ksize=3)
    _, img2 = cv2.threshold(img2, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    element = cv2.getStructuringElement(shape=cv2.MORPH_RECT, ksize=(17, 3))
    morph_img_threshold = img2.copy()
    cv2.morphologyEx(src=img2, op=cv2.MORPH_CLOSE, kernel=element, dst=morph_img_threshold)

    num_contours, hierarchy = cv2.findContours(morph_img_threshold, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(img2, num_contours, -1, (0, 255, 0), 1)

    for i, cnt in enumerate(num_contours):
        min_rect = cv2.minAreaRect(cnt)
        x, y, w, h = cv2.boundingRect(cnt)
        plate_img = img[y:y + h, x:x + w]
        res_img[0] = plate_img
        cv2.imwrite("result.png", plate_img)

        if ratio_and_rotation(min_rect) or isMaxWhite(plate_img):
            clean_plate, rect = clean2_plate(plate_img)
            if rect:
                x1, y1, w1, h1 = rect
                x, y, w, h = x + x1, y + y1, w1, h1
                plate_im = Image.fromarray(clean_plate)
                text = tess.image_to_string(plate_im, lang='eng', config='--psm 8')
                res_text[0] = text.strip()
                print(f"[INFO] Detected Text: {res_text[0]}")
                break
            else:
                plate_im = Image.fromarray(plate_img)
                text = tess.image_to_string(plate_im, lang='eng', config='--psm 8')
                res_text[0] = text.strip()
                print(f"[INFO] Fallback OCR result: {res_text[0]}")
                break

    if res_text[0] == "":
        label.configure(foreground='red', text="❌ No plate detected")
    else:
        label.configure(foreground='#011638', text=res_text[0])

    if os.path.exists("result.png"):
        uploaded = Image.open("result.png")
        im = ImageTk.PhotoImage(uploaded)
        plate_image.configure(image=im)
        plate_image.image = im
        plate_image.pack()
        plate_image.place(x=560, y=320)

def show_classify_button(file_path):
    classify_b = Button(top, text="Classify Image", command=lambda: classify(file_path), padx=10, pady=5)
    classify_b.configure(background='#364156', foreground='white', font=('arial', 15, 'bold'))
    classify_b.place(x=490, y=550)

def upload_image():
    try:
        file_path = filedialog.askopenfilename()
        uploaded = Image.open(file_path)
        uploaded.thumbnail(((top.winfo_width() / 2.25), (top.winfo_height() / 2.25)))
        im = ImageTk.PhotoImage(uploaded)
        sign_image.configure(image=im)
        sign_image.image = im
        label.configure(text='')
        show_classify_button(file_path)
    except:
        pass

upload = Button(top, text="Upload an image", command=upload_image, padx=10, pady=5)
upload.configure(background='#364156', foreground='white', font=('arial', 15, 'bold'))
upload.pack()
upload.place(x=210, y=550)

sign_image.pack()
sign_image.place(x=70, y=200)

label.pack()
label.place(x=500, y=220)

if img:
    heading = Label(top, image=img)
    heading.configure(background='#CDCDCD', foreground='#364156')
    heading.pack()

top.mainloop()
