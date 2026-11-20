import cv2 as cv
import numpy as np


def letterbox(pic, new_shape=(640, 640), color=(114, 114, 114)):
    shape = pic.shape[:2]
    ratio = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    new_unpad = (int(shape[1] * ratio), int(shape[0] * ratio))
    dw = new_shape[1] - new_unpad[0]
    dh = new_shape[0] - new_unpad[1]
    
    dw /= 2
    dh /= 2
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    
    resized_pic = cv.resize(pic, new_unpad, interpolation=cv.INTER_LINEAR)
    padded_pic = cv.copyMakeBorder(resized_pic, top, bottom, left, right, cv.BORDER_CONSTANT, value=color)
    
    return padded_pic, ratio, left, top

def detect_objects(frame, net, class_names, input_size, conf_threshold, nms_threshold):    
    letterboxed_pic, ratio, dw, dh = letterbox(frame, new_shape=(input_size, input_size))
    blob = cv.dnn.blobFromImage(letterboxed_pic, 1/255.0, (input_size, input_size), swapRB=True, crop=False)
    net.setInput(blob)
    
    outputs = net.forward()
    # Remove array with dim (axes) length 1
    predictions = np.squeeze(outputs)
    # print(f"Model Output Shape: {predictions.shape}")
    
    # Transpose if format requires it (e.g., standard YOLOv8)
    if predictions.shape[0] < predictions.shape[1]:
        predictions = predictions.T

    # NMS lists
    boxes = []
    confidences = []
    class_ids = []
    code_clr = [(114, 114, 144), (255, 114, 114), (144, 255, 114)]
    
    for row in predictions:
        scores = row[4:]
        confidence = np.max(scores)
        
        if confidence > conf_threshold:
            class_id = np.argmax(scores)
            
            if class_id < len(class_names):
                x_center, y_center, w, h = row[0], row[1], row[2], row[3]
                
                # Convert center-relative values to top-left corner
                x = int((x_center - w / 2 - dw) / ratio)
                y = int((y_center - h / 2 - dh) / ratio)
                width = int(w / ratio)
                height = int(h / ratio)
                
                # Boundary clipping
                x = max(0, x)
                y = max(0, y)
                
                boxes.append([x, y, width, height])
                confidences.append(float(confidence))
                class_ids.append(class_id)
                
    # Non-Maximum Suppression - Filters out redundant overlapping bounding boxes
    indices = cv.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
    
    result_pic = frame.copy()
    box_count = 0
    
    # Draw the indices defined by NMS
    if len(indices) > 0:
        for i in indices.flatten():
            x, y, width, height = boxes[i]
            confidence = confidences[i]
            class_id = class_ids[i]
            
            label = f"{class_names[class_id]}: {confidence:.2f}"
            cv.rectangle(result_pic, (x, y), (x + width, y + height), code_clr[class_id], 1)
            cv.putText(result_pic, label, (x, y + height + 15), cv.FONT_HERSHEY_SIMPLEX, 0.6, code_clr[class_id], 1)
            box_count += 1
                
    # print(f"Total unique bounding boxes drawn (After NMS): {box_count}")
    
    return result_pic


# Main Execution Block
model_path = "best.onnx"
net = cv.dnn.readNet(model_path)
net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)

class_names = ["4B", "5B", "6B"]
pic_path = "/home/model/LabelStudio_Models_venv/Test_Pics/AAAA.png"
output_path = "/home/model/LabelStudio_Models_venv/AAAA_result.png"
pic = cv.imread(pic_path)

if pic is None:
    print("Error: Picture not found or unable to read.")
else:
    print(f"\nProcessing: {pic_path}")
    # Adjust input_size, conf_threshold and nms_threshold parameters
    result = detect_objects(pic, net, class_names, input_size=640, conf_threshold=0.50, nms_threshold=0.40)
    cv.imwrite(output_path, result)
    print(f"\nSuccess! Image saved to: {output_path}\n")

