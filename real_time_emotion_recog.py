from importlib.resources import path
from time import time
from PIL import Image
from matplotlib import pyplot as plt

import torch
import numpy as np
import pandas
import cv2

# def test_cam():
model = torch.hub.load('ultralytics/yolov5', 'custom', path = 'Emotion_Dataset/v3/best.pt', force_reload=True)

cap = cv2.VideoCapture(0)

while cap.isOpened():
    start = time()
    ret, frame = cap.read()
    result = model(frame)
    
    cv2.imshow('Webcam', np.squeeze(result.render()))

    if cv2.waitKey(10) & 0xff == ord('x'):
        break

    if cv2.getWindowProperty("Webcam", cv2.WND_PROP_VISIBLE) < 1:
        break

    end = time()
    fps = 1/(end-start)
    print (fps)

cap.release()
cv2.destroyAllWindows()