import os
import sys
import cv2
import glob
import argparse
import numpy as np
from ultralytics import YOLO

# Parse user input arguments
parser = argparse.ArgumentParser()
parser.add_argument('--source', help='Image source - image file ("Inference.jpg"), image folder ("Inference_dir")', required=True)

# Parse user inputs
args = parser.parse_args()
img_source = args.source

# Setup inputs
# model_path = "/home/model/LabelStudio_Models_venv/yolo_ml_backend/best.pt"    # Path to YOLO model file
model_path = "/home/model/LabelStudio_Models_venv/best.onnx"    # Path to onnx model file
min_thresh = 0.5   # Minimum confidence threshold for displaying detected objects (must be < 1.00)
img_count = 0

# Load model and get labels
model = YOLO(model_path, task='detect')
labels = model.names

# Determine if image source is valid i.e. in list
img_ext_list = ['.jpg','.JPG','.jpeg','.JPEG','.png','.PNG','.bmp','.BMP']
label_dict = {"4B": 0, "5B": 1, "6B": 2}

if os.path.isdir(img_source):
    source_type = 'directory'
elif os.path.isfile(img_source):
    _, ext = os.path.splitext(img_source)
    if ext in img_ext_list:
        source_type = 'image'
    else:
        print(f'File extension {ext} is not supported.')
        sys.exit(0)
else:
    print(f'Input type {img_source} is not supported')
    sys.exit(0)

# Load image(s)
if source_type == 'image':
    imgs_list = [img_source]
elif source_type == 'directory':
    imgs_list = []
    filelist = glob.glob(img_source + '/*')
    for file in filelist:
        _, file_ext = os.path.splitext(file)
        if file_ext in img_ext_list:
            imgs_list.append(file)

# Set bounding box colors
bbox_colors = [(164,120,87), (68,148,228), (93,97,209), (178,182,133), (88,159,106), 
              (96,202,231), (159,124,168), (169,162,241), (98,118,150), (172,176,184)]

# Begin inference
while True:
    if img_count >= len(imgs_list):
        print('\nInferencing complete!\n')
        sys.exit(0)
    img_filename = imgs_list[img_count]    # Load frame from image source
    frame = cv2.imread(img_filename)
    pic_height, pic_width = frame.shape[:2]
    img_count += 1
    pic = img_filename.split("/")[-1]

    # Run inference on frame
    results = model(frame, verbose=False)
    # Extract results
    detections = results[0].boxes
    # Initialize variable for object counting
    object_count = 0

    # Iterate over detections for bbox coords, confidence, and class
    for i in range(len(detections)):
        # Get bounding box coordinates - Ultralytics returns results in Tensor format, so convert to Python array
        xyxy_tensor = detections[i].xyxy.cpu()    # Detections in Tensor format in CPU memory
        xyxy = xyxy_tensor.numpy().squeeze()     # Convert tensors to Numpy array
        xmin, ymin, xmax, ymax = xyxy.astype(int)     # Extract individual coordinates and convert to int
        bb_x = (xmin + xmax) / 2
        bb_y = (ymin + ymax) / 2
        bb_w = (xmax - xmin)
        bb_h = (ymax - ymin)

        # Get bounding box, class and name
        classidx = int(detections[i].cls.item())
        classname = labels[classidx]

        # Get bounding box confidence
        conf = detections[i].conf.item()

        # Draw box if > confidence threshold
        if conf > min_thresh:
            color = bbox_colors[classidx % 10]
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
            label = f'{classname}: {int(conf * 100)}%'
            nxc = bb_x / pic_width
            nyc = bb_y / pic_height
            nbw = bb_w / pic_width
            nbh = bb_h / pic_height
            # print(f"filename: {img_filename} Pic W & H: {pic_width}, {pic_height}\nlabel: {classname}, {label_dict[classname]} {nxc}, {nyc}, {nbw}, {nbh}")
            print(f"filename: {img_filename} {label_dict[classname]} {nxc}, {nyc}, {nbw}, {nbh}")
            # with open(f"{pic.split('.')[0]}.txt", "a") as label_data:
            #     label_data.write(f"{label_dict[classname]} {nxc}, {nyc}, {nbw}, {nbh}\n")
            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)    # Set font size
            label_ymin = max(ymin, labelSize[1] + 10)    # Ensure label too close to top of window
            cv2.rectangle(frame, (xmin, (label_ymin - labelSize[1] - 10)), ((xmin + labelSize[0]), (label_ymin + baseLine - 10)), color, cv2.FILLED) # Draw box for label text
            cv2.putText(frame, label, (xmin, (label_ymin - 7)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1) # Label text
            # Count number of objects in image
            object_count += 1

    # Display detection results
    cv2.putText(frame, f'Number of objects: {object_count}', (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2) # Total number of detected objects
    cv2.imshow('YOLO Inference', frame) # Display annotated image

    # Wait for user key press before moving to next image
    key = cv2.waitKey()
    
    if key == ord('q') or key == ord('Q'):    # Press 'q' to quit
        print(f"\nUser exited inferencing\n")
        break
    elif key == ord('p') or key == ord('P'): # Press 'p' to save a picture of results on this frame
        print(f"\nSaved inference as 'Inference_{pic}'")
        cv2.imwrite(f'Inference_{pic}', frame)
    
cv2.destroyAllWindows()

