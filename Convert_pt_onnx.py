from ultralytics import YOLO

model = YOLO("/home/model/LabelStudio_Models_venv/best_copy.pt")

model.export(format="onnx")

