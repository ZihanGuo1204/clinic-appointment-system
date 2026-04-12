# 🏥 Clinic Appointment Management System

A full-stack clinic appointment management system using Flask, MySQL, and Google Cloud.

---

## Author
- Zihan Guo

---

## Overview

This system allows users to efficiently manage clinic appointments, including:

- Viewing all appointments  
- Searching and filtering records  
- Adding new appointments  
- Updating appointment details  
- Deleting appointments  
- Adding new patients  

The system ensures data integrity using foreign key constraints and prevents double booking for providers.

---

## Features

### Appointment Management

- View all appointments in a structured table  
- Display:
  - Patient name  
  - Provider name  
  - Clinic name  
  - Time and status  

---

### Search & Filter

- Search by:
  - Appointment ID  
  - Patient ID  
  - Provider ID  
  - Status  

- Sorting options:
  - Date (ascending / descending)  
  - Patient name (A–Z)  
  - Provider name (A–Z)  

---

### Add Appointment

- Select:
  - Patient  
  - Provider  
  - Clinic  

- Choose:
  - Date  
  - Time slot (dropdown)  

- Prevents:
  - Duplicate IDs  
  - Provider double-booking  

---

### Update Appointment

- Modify:
  - Time  
  - Status  

- Keeps database consistent  

---

### Delete Appointment

- Remove appointments safely with confirmation  

---

### Add Patient

- Add new patients into the system  
- Automatically inserted into:
  - PERSON table  
  - PATIENT table  

---

## Tech Stack

- Frontend: HTML, CSS  
- Backend: Flask (Python)  
- Database: MySQL (MariaDB)  
- Deployment: Google Cloud / VM  

---

## Project Structure

```bash
clinic-app/
│
├── app.py
├── requirements.txt
├── README.md
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── appointments.html
│   ├── add.html
│   ├── add_patient.html
│   └── update_appointment.html
│
└── static/
    └── style.css
```

---

## Setup Instructions

### 1️⃣ Clone Repository

```bash
git clone https://github.com/ZihanGuo1204/clinic-appointment-system.git
cd clinic-appointment-system
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Configure Database

Update `app.py` with your database credentials:

```python
db_config = {
    "host": "YOUR_HOST",
    "user": "YOUR_USER",
    "password": "YOUR_PASSWORD",
    "database": "clinic_appointment_db"
}
```

---

### 5️⃣ Run Application

```bash
python app.py
```

---

### Open in Browser

```text
http://127.0.0.1:5000
```

---

## Design Highlights

- Uses foreign key constraints for data consistency  
- Prevents provider double booking  
- Implements search + filtering + sorting  
- Clean UI with reusable layout (`base.html`)  
- Modular structure (templates + static files)  

---

## Limitations / Future Improvements

- Add authentication (login system)  
- Add pagination for large datasets  
- Improve UI with frameworks (Bootstrap / React)  
- Add calendar view for scheduling  