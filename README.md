## 📊 Dataset Structure
The custom grocery dataset is structured locally into training and testing splits for YOLOv8 training:
```text
dataset/
├── Training/
│   ├── images/ (Contains trained grocery product photos)
│   └── labels/ (Contains YOLO bounding box text files)
└── Testing/
    ├── images/ (Contains validation product photos)
    └── labels/ (Contains validation bounding box text files)
```
