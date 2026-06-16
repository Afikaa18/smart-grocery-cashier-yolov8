# Smart Grocery Cashier (YOLOv8 & Google Sheets Integration)

An AI-powered Smart Cashier System that detects grocery items in real-time using a webcam and a custom-trained **YOLOv8** model. The system automatically updates a digital shopping cart, calculates the total price, and saves transaction records directly to **Google Sheets** upon checkout.

---

## Key Features
*   **Real-time Object Detection:** Instantly identifies products in front of the camera using YOLOv8.
*   **Auto Add to Cart:** Seamlessly adds items to the shopping cart with an anti-double scan protection mechanism (1-second delay).
*   **Interactive POS Display:** Renders a digital checkout receipt interface directly onto the live camera stream using an OpenCV overlay.
*   **Google Sheets Integration:** Automatically sends and appends final transaction details to a cloud spreadsheet.
*   **Multi-Payment Support:** Handles distinct checkout sessions for both Cash (`CASH`) and QRIS (`QRIS`) payments.

---

## Model Training Pipeline

Before launching the cashier interface, the YOLOv8 model is trained on a custom grocery dataset. This process is managed via the `train.py` script:

```python
from ultralytics import YOLO

def main():
    # Load base pre-trained model
    model = YOLO("yolov8n.pt")

    # Start the training process
    model.train(
        data=r"C:\Users\user\Downloads\grocery_dataset\data.yaml", 
        epochs=50,             
        imgsz=640,             
        batch=4,               
        workers=2,             
        device="cpu"           
    )
    
    print("TRAINING SUCCESSFUL!")

if __name__ == "__main__":
    main()
```

*The execution of this script generates the optimized model weights saved as `best.pt`.*

---

## Core Cashier System (Detection)

The primary application script `detect.py` handles the camera initialization, processes object detection frame-by-frame, displays the cashier user interface, and sends the finalized transaction payload.

### Registered Products & Prices:

| Product Name | Price |
| :--- | :--- |
| Bottle | Rp 5,000 |
| FresheCare_Matcha | Rp 7,000 |
| Mie_Sedaap_Goreng | Rp 3,500 |

### Application Controls:
*   Press **`C`** to finalize the transaction using **CASH** payment.
*   Press **`P`** to finalize the transaction using **QRIS** payment.
*   Press **`Q`** to **Quit** and close the application window.

---

## Google Spreadsheet Integration (Apps Script)

To bridge the local Python application with your online Google Sheet, a web app powered by **Google Apps Script** is utilized.

### Apps Script Code:
Deploy the following JavaScript code via **Extensions > Apps Script** in your target Google Spreadsheet:

```javascript
function doPost(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var data = JSON.parse(e.postData.contents);
    
    // Loop through the array of transactional items
    for (var i = 0; i < data.length; i++) {
      sheet.appendRow([
        data[i].timestamp,
        data[i].item,
        data[i].qty,
        data[i].subtotal,
        data[i].payment_method
      ]);
    }
    
    return ContentService.createTextOutput(JSON.stringify({"status": "SUCCESS"}))
                         .setMimeType(ContentService.MimeType.JSON);
  } catch(error) {
    return ContentService.createTextOutput(JSON.stringify({"status": "ERROR", "message": error.toString()}))
                         .setMimeType(ContentService.MimeType.JSON);
  }
}
```

---

## Prerequisites & Installation

Ensure you have the required external dependencies installed in your environment before executing the program:

```bash
pip install ultralytics opencv-python requests
```

---

## How to Run

1. Conduct model training first by executing:
   ```bash
   python train.py
   ```
2. Verify that the output model file `best.pt` is mapped to the correct directory path inside `detect.py`.
3. Launch the smart cashier system using:
   ```bash
   python detect.py
   ```
4. Place items in front of your camera, and press **`C`** or **`P`** to log your transaction data straight into Google Sheets!
