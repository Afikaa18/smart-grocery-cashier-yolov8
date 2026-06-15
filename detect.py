from ultralytics import YOLO
import cv2
import time
from datetime import datetime
import requests  # Library for sending the data to Google Sheets

# CONFIGURATION GOOGLE SHEETS
GSHEET_URL = "https://script.google.com/macros/s/AKfycbx-6NQMd0rdDHsW0LL4_iXFrSNCB7VlkjtCfWtcdVZd8HU9a6upolJ5uBC_sKf-2g6t/exec"

def send_to_spreadsheet(cart_data, payment_method):
    """the Fungsi untuk mengirim struk belanja ke Google Spreadsheet"""
    if not cart_data:
        return

    payload = []
    # Record the real-time time when the transaction is successful and the C/P button is pressed
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for item, data in cart_data.items():
        qty = data["qty"]
        subtotal = qty * data["price"]
        
        # Format the data by row
        payload.append({
            "timestamp": current_timestamp,
            "item": item,
            "qty": qty,
            "subtotal": subtotal,
            "payment_method": payment_method
        })

    try:
        print(" Sending transaction data to Google Spreadsheets ")
        response = requests.post(GSHEET_URL, json=payload, timeout=10)
        if response.status_code == 200:
            print(" The data has been successfully saved to the spreadsheet!")
        else:
            print(f" Failed to send data. Status Code: {response.status_code}")
    except Exception as e:
        print(f" Connection error to the spreadsheet: {e}")

# LOAD MODEL
model = YOLO(
    r"C:\Users\user\Downloads\grocery_dataset\best.pt"
)

# PRODUCT PRICE 
PRODUCT_PRICES = {
    "Bottle": 5000,
    "FresheCare_Matcha": 7000,
    "Mie_Sedaap_Goreng": 3500
}

# CART & ANTI DOUBLE SCAN
cart = {}
last_detected = None
last_added_time = 0

# CAMERA
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# MAIN LOOP
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Anti-Mirroring & Resize
    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (1024, 576))

    # YOLO Detection
    results = model(frame, imgsz=640, verbose=False)
    detected_now = None

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])

            if conf > 0.5:
                label = model.names[cls_id]
                detected_now = label
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} ({conf:.2f})", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Auto Add To Cart Logic
    if detected_now:
        current_time = time.time()
        if detected_now != last_detected:
            last_detected = detected_now
            last_added_time = current_time
        elif current_time - last_added_time > 1:
            price = PRODUCT_PRICES.get(detected_now, 0)
            if detected_now in cart:
                cart[detected_now]["qty"] += 1
            else:
                cart[detected_now] = {"price": price, "qty": 1}
            print(f" {detected_now} enter cart")
            last_detected = None

    # UI Right Panel
    overlay = frame.copy()
    cv2.rectangle(overlay, (720, 15), (1004, 555), (255, 255, 255), -1)
    frame = cv2.addWeighted(overlay, 0.85, frame, 0.15, 0)

    # UI Render Text
    cv2.putText(frame, "SMART GROCERY CASHIER", (735, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    cv2.line(frame, (730, 95), (990, 95), (150, 150, 150), 1)

    y = 125
    total = 0
    for idx, (item, data) in enumerate(cart.items(), start=1):
        qty = data["qty"]
        price = data["price"]
        subtotal = qty * price
        total += subtotal

        if y < 380:
            cv2.putText(frame, str(idx), (735, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
            cv2.putText(frame, item[:12], (770, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
            cv2.putText(frame, f"{qty}x", (880, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
            cv2.putText(frame, f"Rp{subtotal}", (930, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
            y += 30

    cv2.line(frame, (730, 390), (990, 390), (0, 0, 0), 1)
    cv2.putText(frame, "TOTAL", (735, 425), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    cv2.putText(frame, f"Rp {total}", (860, 425), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    cv2.line(frame, (730, 455), (990, 455), (200, 200, 200), 1)
    cv2.putText(frame, "C = CASH", (740, 485), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (80, 80, 80), 1)
    cv2.putText(frame, "P = QRIS", (740, 515), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (80, 80, 80), 1)
    cv2.putText(frame, "Q = QUIT", (880, 485), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (80, 80, 80), 1)

    cv2.imshow("SMART GROCERY CASHIER", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

    elif key == ord("c"):
        print("\n CASH PAYMENT ")
        send_to_spreadsheet(cart, "CASH")
        cart.clear()

    elif key == ord("p"):
        print("\n QRIS PAYMENT ")
        send_to_spreadsheet(cart, "QRIS")
        cart.clear()

cap.release()
cv2.destroyAllWindows()