from ultralytics import YOLO

def main():
    model = YOLO("yolov8n.pt")

    model.train(
        # DI SINI TEMPATNYA, di dalam file train.py:
        data=r"C:\Users\user\Downloads\grocery_dataset\data.yaml", 
        epochs=50,             
        imgsz=640,             
        batch=4,               
        workers=2,             
        device="cpu"           
    )
    
    print("TRAINING SUCCESSFULL!")

if __name__ == "__main__":
    main()