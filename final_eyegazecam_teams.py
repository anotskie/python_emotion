# LIBRARIES
import numpy as np
# import pandas as pd
import pyvirtualcam
import torch
import cv2
import time
import shutil
import os
import pathlib
# import yolov5

from datetime import datetime, date
from CTkMessagebox import CTkMessagebox

def eyegaze_cam(meeting_time_length):
    model = torch.hub.load('ultralytics/yolov5', 'custom', path = 'Eye_Gaze_Dataset/v12/best.pt', force_reload=True)
    # model = torch.load('ultralytics/yolov5', 'custom', path = 'Eye_Gaze_Dataset/v12/best.pt', force_reload=True)
    # model = YOLO(path='Eye_Gaze_Dataset/v12/best.pt')

    previous = time.time()
    delta = 0
    path_num = 0
    length = 0
    interval = meeting_time_length/20    # Set in seconds

    fmt = pyvirtualcam.PixelFormat.BGR
    with pyvirtualcam.Camera(width=640, height=480, fps=20, fmt=fmt) as cam:
        print(f'Using virtual camera: {cam.device}')
        
        with open('eyegaze_output.csv', 'w') as f:
            line = "xmin,ymin,xmax,ymax,confidence,class,name,date,time,path"
            f.write(line)
            f.write("\n")

        video_capture = cv2.VideoCapture(0)

        while True:
            current = time.time()
            length += current - previous
            delta += current - previous
            previous = current

            if length > meeting_time_length:
                break

            print(f"Delta: {delta}, Interval: {interval}, Total time elapsed: {length}")

            ret, frame = video_capture.read()

            result = model(frame)
            frame = np.squeeze(result.render())

            cam.send(frame)

            if delta > interval:
                result.print()
                result.save()

                result.xyxy[0]
                df = result.pandas().xyxy[0]
                
                df['date'] = date.today()
                df['time'] = datetime.now().strftime("%H:%M:%S")
                if path_num == 0 or 1:
                    df['path'] = "runs\detect\exp"
                else:
                    df['path'] = f"runs\detect\exp{path_num}"
                df.to_csv('eyegaze_output.csv', mode='a', index=False, header=False)

                delta = 0
                path_num += 1
        
        name = info_msg()
        show_info(name)

            # end = time()
            # fps = 1/(end-start)
            # print (fps)

def move_folder():
    batch_num = 1

    while True:
        source = 'runs/detect'
        newpath = f"Eye_Gaze_Batches/batch{batch_num}"

        isExist = os.path.exists(newpath)

        files = os.listdir(source)

        if isExist:
            print("Path already exist!")
            print(f"Current batch number: {batch_num}")

        if not isExist:
            print("Path doesn't exist!")
            print("Creating folder...")
            pathlib.Path(newpath).mkdir(exist_ok=True)
            for file in files:
                shutil.move(os.path.join(source, file), newpath)
            break

        batch_num += 1
        print(f"New batch number: {batch_num}")

def info_msg():
    with open(r'eyegaze_output.csv', 'r') as csv_file:
        last_line = csv_file.readlines()[-1]
        result = []

        result.append(last_line.split(',')[6])

    return result[0]

def show_info(info):
    # Default messagebox for showing some information
    CTkMessagebox(title="Info", message=f"You're last detected level of engagement is '{info}'!")

# move_folder()
# eyegaze_cam(60)
# print(info_msg())