 
import cv2 
import pytesseract 
import Tkinter as tkinter
import re
from PIL import Image,ImageTk
# 1.creating a video object
count = 0
# 1.creating a video object
cap = cv2.VideoCapture(0)
while cap.isOpened():
    ret, frame = cap.read()
    img1 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(Image.fromarray(img1))
    print("Extracted Text: ", text)
    if ret:
        if text.upper().strip() != "":
            cv2.imwrite("frame%d.jpg" % count, frame)     # save frame as JPEG file
            count += 1
        else:
            count = 0
    else:
        break
    if cv2.waitKey(0) & 0xFF == ord('q'):
        break
    print("Extracted Text: ", text)
cap.release()  