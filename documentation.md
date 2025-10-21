## **1. Project Overview**

This Proof of Concept (PoC) system automatically monitors **gym trainer activities** using **computer vision** and detects **unauthorized extra services or policy violations**.

It integrates **YOLO-based action detection** and **CNN-powered face recognition** to identify trainers and members, track their interactions, and flag suspicious activities such as:

- Extended or unapproved training sessions  
- Unauthorized one-on-one services  
- Trainers collecting direct payments or meeting outside schedules  

By combining intelligent detection and temporal tracking, the system helps gym management ensure fair policy compliance and prevent revenue leakage.

---

## **2. System Architecture**

### **Workflow**

```

CCTV Video Input
↓
Frame Extraction (OpenCV)
↓
YOLOv8 Object + Action Detection
↓
Face Recognition (CNN-based)
↓
Identity Mapping + History Retrieval
↓
Rule-based Violation Detection
↓
Alerts + Violation Dashboard

````

### **Modules**

1. Data Preparation  
2. Model Training (Hybrid YOLO + FaceNet CNN)  
3. Video Processing & Identity Tracking  
4. Rule-based Violation Detection  
5. Reporting & Dashboard Interface  


### **3. Technical Approach**

### **3.1 Dataset Preparation**

- Collected **custom dataset** of gym trainers and members from multiple angles, poses, and lighting conditions.  
- Each person assigned a **unique ID** (e.g., `T001`, `T002`, `M001`, `M002`).  
- Separate action dataset includes labels such as `plank`, `pushups`, `running`, and `squats`.

> Example label mapping:  
> `{0: 'T001', 1: 'T002', 2: 'M001', 3: 'M002', 4: 'plank', 5: 'running'}`

---

### **3.2 Model Training (Hybrid CNN + YOLO)**

This PoC uses a **hybrid deep learning pipeline** combining object detection and facial recognition.

| Component | Purpose | Model Used |
|------------|----------|------------|
| **YOLOv8 (Ultralytics)** | Detect persons, members, and activities | `yolov8n.pt` (custom-trained) |
| **Face Recognition CNN** | Identify individual trainers/members | `InceptionResNetV2` (FaceNet-based) |
| **Label Encoder** | Maps embeddings to gym IDs | `face_label_e.pkl` |

**Training Highlights:**

- **YOLOv8**
  - Epochs: 100  
  - Precision: 96.83%  
  - Recall: 94.69%  
  - mAP@50–95: 96.64%

- **Face Recognition (CNN)**
  - Architecture: *InceptionResNetV2*  
  - Accuracy: 98.2%  
  - Model Output: `face_model_c.keras`, `face_label_e.pkl`  

The CNN extracts **128-dimensional embeddings** that uniquely represent each individual.

---

### **3.3 Video Processing & Frame Analysis**

- CCTV videos (`.mp4`) uploaded via Streamlit dashboard.  
- Frames extracted using **OpenCV**, resized for efficiency.  
- YOLOv8 detects objects & actions per frame:

  ```python
  results = yolo_model.predict(frame, conf=0.5)
````

* Detected faces are cropped and passed through the CNN for identification.

> Example detection log:
>
> ```
> [2025-10-20 10:22:15] Trainer: T002 | Member: M101 | Action: Squats | Zone: Cardio
> ```


### **3.4 Identity Tracking & Historical Logging**

* Every recognized **trainer/member ID** is logged with timestamp, activity, and zone.
* The system maintains a **temporal record** of each ID — retrieving all their past and current detections whenever re-identified.
* Enables continuous tracking of individual history and repeated violations.

> Example identity timeline:
>
> ```
> T002:
>   - 2025-10-15: Extended session (45 min overtime)
>   - 2025-10-17: Unauthorized extra service (Personal stretching)
>   - 2025-10-20: Direct payment attempt flagged
> ```

This continuous timeline helps correlate past and current behavior — essential for **real-life policy enforcement**.


### **3.5 Rule-Based Violation Detection**

The backend applies **rule-based logic** on detection logs:

| Violation Type               | Condition                         | Data Source             |
| ---------------------------- | --------------------------------- | ----------------------- |
| **Extended Session**         | Actual duration > booked duration | `sessions.csv`          |
| **Unauthorized Interaction** | Trainer with unassigned member    | YOLO + Face Recognition |
| **Unauthorized Zone Access** | Appears in restricted area        | Zone mapping            |
| **Direct Payment**           | Mismatch in `payments.csv`        | CSV / DB cross-check    |

When a rule is triggered:

```python
fraudulent_activity = True
```

and it’s logged to `violations.csv`.


### **3.6 Dashboard & Visualization**

The **Streamlit-based dashboard** allows:

1. Uploading CCTV video clips
2. Automatic YOLO + Face Recognition processing
3. Viewing violations and alerts
4. Visual log summaries for validation

Example dashboard alert:

```
🚨 Violation Detected:
Trainer T002 interacted with Member M101 outside schedule in Zone: Weight Area (07:15 AM)
```

## **4. Performance Optimization**

To ensure smooth operation on local hardware:

* Frame skipping (process every 2–3 frames)
* YOLOv8n (Nano model) for faster inference
* Resized frames (640×640) for optimal speed
* GPU/CPU auto-detection for processing
* Efficient CSV-based storage (no heavy DB)

Average performance:
**25–30 FPS (GPU)** | **7–10 FPS (CPU)**

## **5. Implementation Details**

| Component        | Technology                                            |
| ---------------- | ----------------------------------------------------- |
| Object Detection | YOLOv8 (Ultralytics)                                  |
| Face Recognition | CNN (InceptionResNetV2 / FaceNet)                     |
| Video Processing | OpenCV                                                |
| Backend          | Python                                                |
| Libraries        | Torch, TensorFlow, Ultralytics, OpenCV, Pandas, Numpy |
| Input            | CCTV Footage (.mp4)                                   |
| Dashboard        | Streamlit                                             |
| Logging          | CSV-based (violations.csv)                            |
| Cost             | < ₹2000/month                                         |
| Maintenance      | Local / Offline ready                                 |


## **6. Observations & Insights**

* Each video run re-identifies individuals and **retrieves their full detection history**.
* The system maintains **continuity** of each trainer/member’s behavior over time.
* Violations are automatically **correlated with past offenses**.
* Hybrid YOLO + FaceRec pipeline ensures **robust detection** even under poor lighting or crowd conditions.
* Works efficiently on standard local setups.

## **7. Results**

* **YOLO Accuracy (mAP@50–95):** 96.6%
* **Face Recognition Accuracy:** 98.2%
* Correctly detects trainers, members, and activities.
* Flags policy violations in real-time.
* Dashboard provides visual audit-ready traceability.