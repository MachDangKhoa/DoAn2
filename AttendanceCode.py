import os
import face_recognition
import pyodbc
import pickle
from sklearn import svm
from sklearn.model_selection import GridSearchCV
from datetime import datetime
import numpy as np

# Kết nối đến cơ sở dữ liệu SQL Server
conn_str = (
    'DRIVER={SQL Server};'
    'SERVER=MSI;'
    'DATABASE=Face_Recognition;'
    'Trusted_Connection=yes;')

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
except Exception as e:
    print(f"Không thể kết nối đến cơ sở dữ liệu: {e}")
    exit()

# Huấn luyện mô hình SVM với encoding và nhãn
def train_svm_model():
    try:
        cursor.execute('SELECT ID_SINHVIEN, ENCODING FROM KHUONMAT')
        faces_data = cursor.fetchall()
    except Exception as e:
        print(f"Không thể truy vấn dữ liệu khuôn mặt: {e}")
        return [], None

    encodings = []
    labels = []

    for student_id, encoding_bytes in faces_data:
        encoding = np.frombuffer(encoding_bytes, dtype=np.float64)
        encodings.append(encoding)
        labels.append(student_id)

    if encodings:
        parameters = {'C': [1, 10, 100, 1000], 'gamma': ['scale', 'auto'], 'kernel': ['linear', 'rbf']}
        svc = svm.SVC(probability=True)
        clf = GridSearchCV(svc, parameters)
        clf.fit(encodings, labels)
        with open('face_recognition_model.pkl', 'wb') as file:
            pickle.dump(clf, file)
    else:
        print("Không có dữ liệu khuôn mặt để huấn luyện mô hình.")
        return [], None

    id = set(labels)
    print(f"label: {id}")

    return id, clf.best_estimator_

trained_labels, clf = train_svm_model()

# Hàm để ghi nhận điểm danh vào cơ sở dữ liệu
def recognize_and_record_attendance(image_path, labels, clf):
    if not os.path.isfile(image_path) or not image_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        print("Đường dẫn hình ảnh không hợp lệ hoặc không phải là hình ảnh.")
        return

    try:
        unknown_image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(unknown_image)
    except Exception as e:
        print(f"Không thể tải hoặc mã hóa hình ảnh: {e}")
        return

    print(f"Face encodings: {face_encodings}")
    present_students = set()

    for encoding in face_encodings:
        predictions = clf.predict_proba([encoding])[0]
        # Thêm print để kiểm tra predictions
        print(f"Predictions: {predictions}")
        best_match_index = np.argmax(predictions)
        print(f"ID sinh vien: {best_match_index}")
        best_match_probability = predictions[best_match_index]
        student_id = list(labels)[best_match_index]
        print(f"Best match probability for student {student_id}: {best_match_probability}")
        if best_match_probability > 0.7:
            present_students.add(student_id)


    for student_id in labels:
        status = 'Present' if student_id in present_students else 'Absent'
        # Thêm print để kiểm tra status
        print(f"Attendance status for student {student_id}: {status}")
        record_attendance(student_id, status, image_path)

def record_attendance(student_id, status, image_path):
    try:
        cursor.execute(
            'SELECT ID_LOP FROM SINHVIEN LEFT JOIN KHUONMAT ON SINHVIEN.ID_SINHVIEN = KHUONMAT.ID_SINHVIEN WHERE SINHVIEN.ID_SINHVIEN = ?',
            (student_id,))
        idLop = cursor.fetchone()[0]
        modified_timestamp = os.path.getmtime(image_path)
        modified_time = datetime.fromtimestamp(modified_timestamp)
        cursor.execute('''
            INSERT INTO DIEMDANH (ID_LOP, ID_SINHVIEN, TAIKHOAN, THOIGIAN, TRANGTHAI)
            VALUES (?, ?, ?, ?, ?)
        ''', (idLop, student_id, 'admin', modified_time, status))
        conn.commit()
    except Exception as e:
        print(f"Không thể ghi nhận điểm danh: {e}")

def close_connection():
    cursor.close()
    conn.close()


image_path = 'D:\\CodePy\\KhuonMat\\DiemDanh\\demo1.jpg'
recognize_and_record_attendance(image_path, trained_labels, clf)
close_connection()
