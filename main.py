import os
import face_recognition
import pyodbc
import pickle
from sklearn import svm
from sklearn.model_selection import GridSearchCV
from datetime import datetime
import numpy as np
from PyQt6 import QtCore,QtGui,QtWidgets,uic
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPixmap
from PyQt6.uic import loadUi
import sys

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
    QMessageBox.information("Thông báo", f"Không thể kết nối cơ sở dữ liệu. Lỗi {e}")
    exit()

taiKhoanDangNhap = None

class Login_w(QMainWindow):
    def __init__(self):
        super(Login_w, self).__init__()
        uic.loadUi('Login.ui', self)
        self.btnDangNhap.clicked.connect(self.login)
        self.btnThoat.clicked.connect(self.exit)


        screen_geometry = QtWidgets.QApplication.primaryScreen().geometry()
        self.setGeometry(
            screen_geometry.center().x() - self.width() // 2,
            screen_geometry.center().y() - self.height() // 2,
            self.width(),
            self.height()
        )

    def login(self):
        global taiKhoanDangNhap
        txtUser = self.fiTaikhoan.text()
        txtPassWord = self.fiMatkhau.text()
        cursor.execute(f"SELECT TAIKHOAN, MATKHAU FROM TAIKHOAN WHERE TAIKHOAN = '{txtUser}' AND MATKHAU = '{txtPassWord}'")
        taiKhoan = cursor.fetchone()
        if taiKhoan:
            QMessageBox.information(self, "Thông báo", "Đăng nhập thành công")
            taiKhoanDangNhap = txtUser
            widget.setCurrentIndex(1)
            self.fiTaikhoan.clear()
            self.fiMatkhau.clear()
            Loginsc_f.show_username()
            Student_f.display_student()
            Subjects_f.display_subjects()
        else:
            QMessageBox.information(self, "Thông báo", "Đăng nhập thất bại")
            self.fiTaikhoan.setFocus()

    def exit(self):
        QtWidgets.QApplication.quit()


class Loginsc_w(QMainWindow):
    def __init__(self):
        super(Loginsc_w, self).__init__()
        uic.loadUi('Loginsc.ui', self)
        self.btnLophoc.clicked.connect(self.show_Class)
        self.btnSinhvien.clicked.connect(self.show_Student)
        self.btnMahoa.clicked.connect(self.show_Encode)
        self.btnDiemdanh.clicked.connect(self.show_Attendance)
        self.btnThongke.clicked.connect(self.show_Statistical)
        self.btnMonHoc.clicked.connect(self.show_subjects)
        self.lblTaikhoan = self.findChild(QLabel, 'lblTaikhoan')
        self.btnDangxuat.clicked.connect(self.logout_user)

    def show_username(self):
        global taiKhoanDangNhap
        self.lblTaikhoan.setText('Tài khoản: ' + str(taiKhoanDangNhap))

    def logout_user(self):
        result = QMessageBox.question(self, 'Xác nhận đăng xuất', 'Bạn có chắc chắn muốn đăng xuất?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if result == QMessageBox.StandardButton.Yes:
            widget.setCurrentIndex(0)
            Student_f.clear_table()
            Subjects_f.clear_table1()
    def show_Class(self):
        widget.setCurrentIndex(2)
    def show_Student(self):
        widget.setCurrentIndex(3)
    def show_Encode(self):
        widget.setCurrentIndex(4)
    def show_Attendance(self):
        widget.setCurrentIndex(5)
    def show_Statistical(self):
        widget.setCurrentIndex(6)
    def show_subjects(self):
        widget.setCurrentIndex(7)

class Class_w(QMainWindow):
    def __init__(self):
        super(Class_w, self).__init__()
        uic.loadUi('class.ui', self)
        self.btnTrolai.clicked.connect(self.back)
        self.tblLophoc = self.findChild(QTableWidget, 'tblLophoc')
        self.fiIDlop = self.findChild(QLineEdit, 'fiIDlop')
        self.fiTenlop = self.findChild(QLineEdit, 'fiTenlop')
        self.btnThem.clicked.connect(self.insert_class)
        self.btnSua.clicked.connect(self.update_class)
        self.btnXoa.clicked.connect(self.delete_class)
        self.display_class()

    def back(self):
        widget.setCurrentIndex(1)
        self.fiIDlop.clear()
        self.fiTenlop.clear()

    def display_class(self):
        try:
            cursor.execute(
                "SELECT * FROM LOPHOC ")
            class_data = cursor.fetchall()
            num_rows = len(class_data)
            num_columns = len(class_data[0])
            column_width = self.tblLophoc.width() // num_columns
            self.tblLophoc.setRowCount(num_rows)
            self.tblLophoc.setColumnCount(num_columns)
            self.tblLophoc.setHorizontalHeaderLabels(
                ['ID Lớp học', 'Tên lớp học'])
            for row in range(num_rows):
                for col in range(num_columns):
                    item = QTableWidgetItem(str(class_data[row][col]))
                    self.tblLophoc.setItem(row, col, item)

            for col in range(num_columns):
                self.tblLophoc.setColumnWidth(col, column_width)

        except Exception as e:
            QMessageBox.information(self, "Thông báo", f"Không thể truy vấn dữ liệu điểm danh. Lỗi {e}")

    def insert_class(self):
        try:
            idLop = self.fiIDlop.text()
            tenLop = self.fiTenlop.text()
            cursor.execute('INSERT INTO LOPHOC (ID_LOP, TENLOP) VALUES (?, ?)', (idLop, tenLop))
            conn.commit()
            QMessageBox.information(self, "Thông báo", "Thêm thành công")
            self.fiIDlop.clear()
            self.fiTenlop.clear()
            self.display_class()
        except Exception as e:
            QMessageBox.information(self, "Thông báo", f"Thêm thất bại. Lỗi {e}!")

    def update_class(self):
        try:
            # Lấy thông tin từ hàng được chọn trong QTableWidget
            selected_items = self.tblLophoc.selectedItems()
            if len(selected_items) == 0:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một hàng để cập nhật.")
                return

            # Lấy ID lớp học từ hàng được chọn
            row = selected_items[0].row()
            idLop = self.tblLophoc.item(row, 0).text()
            tenLop = self.tblLophoc.item(row, 1).text()
            cursor.execute('SELECT ID_LOP FROM LOPHOC WHERE ID_LOP = ?', (idLop))
            id_Lop = cursor.fetchall()
            if id_Lop:
                # Cập nhật thông tin trong cơ sở dữ liệu
                cursor.execute('UPDATE LOPHOC SET TENLOP = ? WHERE ID_LOP = ?', (tenLop, idLop))
                conn.commit()
                # Hiển thị thông báo và cập nhật lại bảng
                QMessageBox.information(self, "Thông báo", "Cập nhật thành công")
                self.display_class()

            elif id_Lop == []:
                QMessageBox.warning(self, "Thông báo", "Lỗi! Không thể cập nhật ID_LOP")
                self.display_class()

        except Exception:
            QMessageBox.information(self, "Thông báo", f"Cập nhật thất bại. Lỗi!")
            self.display_class()

    def delete_class(self):
        try:
            # Lấy thông tin từ hàng được chọn trong QTableWidget
            selected_items = self.tblLophoc.selectedItems()
            if len(selected_items) == 0:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một hàng để xoá.")
                return

            # Lấy ID lớp học từ hàng được chọn
            row = selected_items[0].row()
            idLop = self.tblLophoc.item(row, 0).text()

            cursor.execute('DELETE FROM LOPHOC WHERE ID_LOP = ?', (idLop))
            conn.commit()

            # Hiển thị thông báo và cập nhật lại bảng
            QMessageBox.information(self, "Thông báo", "Xoá thành công")
            self.display_class()
        except Exception as e:
            QMessageBox.information(self, "Thông báo", f"Xoá thất bại. Lỗi {e}!")


class Student_w(QMainWindow):
    def __init__(self):
        super(Student_w, self).__init__()
        uic.loadUi('student.ui', self)
        self.btnTrolai.clicked.connect(self.back)
        self.tblSinhvien = self.findChild(QTableWidget, 'tblSinhvien')
        self.fiIDsinhvien = self.findChild(QLineEdit, 'fiIDsinhvien')
        self.fiIDlop = self.findChild(QLineEdit, 'fiIDlop')
        self.fiTensinhvien = self.findChild(QLineEdit, 'fiTensinhvien')
        self.btnThem.clicked.connect(self.insert_student)
        self.btnSua.clicked.connect(self.update_student)
        self.btnXoa.clicked.connect(self.delete_student)
        self.display_student()

    def clear_table(self):
        self.tblSinhvien.clearContents()
        self.tblSinhvien.setRowCount(0)
        self.fiIDlop.clear()
        self.fiIDsinhvien.clear()
        self.fiTensinhvien.clear()

    def back(self):
        widget.setCurrentIndex(1)
        self.fiIDlop.clear()
        self.fiTensinhvien.clear()
        self.fiIDsinhvien.clear()


    def display_student(self):
        try:
            global taiKhoanDangNhap
            taikhoan = taiKhoanDangNhap
            cursor.execute(
                "SELECT ID_SINHVIEN, ID_LOP, HOTEN FROM SINHVIEN WHERE TAIKHOAN = ?", (str(taikhoan),))
            student_data = cursor.fetchall()
            if student_data:
                num_rows = len(student_data)
                num_columns = len(student_data[0])
                column_width = self.tblSinhvien.width() // num_columns
                self.tblSinhvien.setRowCount(num_rows)
                self.tblSinhvien.setColumnCount(num_columns)
                self.tblSinhvien.setHorizontalHeaderLabels(
                    ['ID Sinh viên', 'ID Lớp', 'Họ tên sinh viên'])
                for row, record in enumerate(student_data):
                    for col, value in enumerate(record):
                        item = QTableWidgetItem(str(value))
                        self.tblSinhvien.setItem(row, col, item)
                for col in range(num_columns):
                    self.tblSinhvien.setColumnWidth(col, column_width)
        except Exception as e:
            QMessageBox.information(self, "Thông báo", f"Không thể truy vấn dữ liệu điểm danh. Lỗi {e}")

    def insert_student(self):
        try:
            global taiKhoanDangNhap
            idSV = self.fiIDsinhvien.text()
            idLop = self.fiIDlop.text()
            tenSV = self.fiTensinhvien.text()
            cursor.execute('SELECT ID_LOP FROM LOPHOC WHERE ID_LOP = ?', (idLop,))
            existing_id = cursor.fetchone()
            taikhoan = taiKhoanDangNhap
            if existing_id:
                cursor.execute('INSERT INTO SINHVIEN (ID_SINHVIEN, ID_LOP, TAIKHOAN, HOTEN) VALUES (?, ?, ?, ?)', (idSV, idLop, taikhoan, tenSV))
                conn.commit()
                QMessageBox.information(self, "Thông báo", "Thêm thành công")
                self.fiIDsinhvien.clear()
                self.fiIDlop.clear()
                self.fiTensinhvien.clear()
                self.display_student()
            else:
                QMessageBox.information(self, "Thông báo", "Thêm thất bại.")
        except Exception as e:
            QMessageBox.information(self, "Thông báo", f"Thêm thất bại. Lỗi {e}!")

    def update_student(self):
        try:
            # Lấy thông tin từ hàng được chọn trong QTableWidget
            selected_items = self.tblSinhvien.selectedItems()
            if len(selected_items) == 0:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một hàng để cập nhật.")
                return

            # Lấy ID lớp học từ hàng được chọn
            row = selected_items[0].row()
            idSV = self.tblSinhvien.item(row, 0).text()
            idLop = self.tblSinhvien.item(row, 1).text()
            tenSV = self.tblSinhvien.item(row, 2).text()

            cursor.execute('SELECT ID_SINHVIEN FROM SINHVIEN WHERE ID_SINHVIEN = ?', (idSV))
            existing_id = cursor.fetchall()
            taikhoan = taiKhoanDangNhap
            if existing_id:
                # Cập nhật thông tin trong cơ sở dữ liệu
                cursor.execute('UPDATE SINHVIEN SET ID_LOP = ?, HOTEN = ? WHERE ID_SINHVIEN = ? AND TAIKHOAN = ?', (idLop, tenSV, idSV, taikhoan))
                conn.commit()

                # Hiển thị thông báo và cập nhật lại bảng
                QMessageBox.information(self, "Thông báo", "Cập nhật thành công")
                self.display_student()
            elif existing_id == []:
                QMessageBox.information(self, "Thông báo", "Cập nhật thất bại.")
                self.display_student()

        except Exception as e:
            QMessageBox.information(self, "Thông báo", f"Cập nhật thất bại. Lỗi {e}!")
            self.display_student()

    def delete_student(self):
        try:
            global taiKhoanDangNhap
            taikhoan = taiKhoanDangNhap
            # Lấy thông tin từ hàng được chọn trong QTableWidget
            selected_items = self.tblSinhvien.selectedItems()
            if len(selected_items) == 0:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một hàng để xoá.")
                return

            # Lấy ID lớp học từ hàng được chọn
            row = selected_items[0].row()
            idSV = self.tblSinhvien.item(row, 0).text()

            cursor.execute('DELETE FROM SINHVIEN WHERE ID_SINHVIEN = ?', (idSV))
            conn.commit()

            # Hiển thị thông báo và cập nhật lại bảng
            QMessageBox.information(self, "Thông báo", "Xoá thành công")
            cursor.execute('SELECT TAIKHOAN FROM SINHVIEN WHERE TAIKHOAN = ? AND ID_SINHVIEN = ?', (taikhoan, idSV))
            user = cursor.fetchall()
            if not user:
                self.tblSinhvien.clearContents()
                self.tblSinhvien.setRowCount(0)
                self.display_student()
        except Exception as e:
            QMessageBox.information(self, "Thông báo", f"Xoá thất bại. Lỗi {e}!")

class Encode_w(QMainWindow):
    def __init__(self):
        super(Encode_w, self).__init__()
        uic.loadUi('mahoa.ui', self)
        self.btnChonanh.clicked.connect(self.choose_directory)
        self.btnMahoa.clicked.connect(self.encode_faces)
        self.image_directory = ''
        self.lblChonanh = self.findChild(QLabel, 'lblChonanh')
        self.fiNhapid = self.findChild(QLineEdit, 'fiNhapid')
        self.btnTrolai.clicked.connect(self.back)

    def back(self):
        widget.setCurrentIndex(1)
        self.fiNhapid.clear()
        self.lblChonanh.clear()

    def choose_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Chọn thư mục")
        if directory:
            self.image_directory = directory
            self.lblChonanh.setText(directory)

    def encode_faces(self):
        global taiKhoanDangNhap
        taikhoan = taiKhoanDangNhap
        id_sinhvien = self.fiNhapid.text()
        if not id_sinhvien:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập ID sinh viên")
            self.fiNhapid.setFocus()
            return

        if self.image_directory:
            cursor.execute(f'SELECT TAIKHOAN FROM SINHVIEN WHERE ID_SINHVIEN = ? AND TAIKHOAN = ?', (id_sinhvien, taikhoan))
            u_name = cursor.fetchall()
            if u_name:
                self.add_and_encode_images(self.image_directory, id_sinhvien, taikhoan)
                QMessageBox.information(self, "Thông báo", "Hoàn tất mã hoá hình ảnh")
                self.fiNhapid.clear()
                self.lblChonanh.clear()
            else:
                QMessageBox.information(self, "Thông báo", "Tài khoản không có hình ảnh để mã hoá.")
        else:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn thư mục hình ảnh")
    def encode_face(self,image_path):
        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)
        if face_encodings:
            # Chuyển đổi mã hóa khuôn mặt thành một mảng numpy
            return face_encodings[0]
        return None

    # Hàm để thêm hình ảnh và mã hóa vào cơ sở dữ liệu
    def add_and_encode_images(self,image_directory, id_sinhvien, taikhoan):
        # Lấy ID_KHUONMAT cuối cùng từ cơ sở dữ liệu
        cursor.execute('SELECT MAX(ID_KHUONMAT) FROM KHUONMAT')
        last_id = cursor.fetchone()[0] or 0

        # Bật IDENTITY_INSERT
        cursor.execute('SET IDENTITY_INSERT KHUONMAT ON')
        conn.commit()

        # Duyệt qua tất cả các tệp trong thư mục hình ảnh
        for image_name in os.listdir(image_directory):
            image_path = os.path.join(image_directory, image_name)
            face_encoding = self.encode_face(image_path)
            if face_encoding is not None:
                last_id += 1
                # Chuyển đổi mảng numpy thành chuỗi byte
                face_encoding_bytes = face_encoding.tobytes()
                cursor.execute('''
                    INSERT INTO KHUONMAT (ID_KHUONMAT, ID_SINHVIEN, TAIKHOAN, IMAGE, ENCODING)
                    VALUES (?, ?, ?, ?, ?)
                ''', (last_id, id_sinhvien, taikhoan, image_path, face_encoding_bytes))
                conn.commit()



        # Tắt IDENTITY_INSERT
        cursor.execute('SET IDENTITY_INSERT KHUONMAT OFF')
        conn.commit()

class Attendance_w(QMainWindow):
    def __init__(self):
        super(Attendance_w, self).__init__()
        uic.loadUi('attendance.ui', self)
        self.btnChonanh.clicked.connect(self.choose_image)
        self.btnDiemdanh.clicked.connect(self.mark_attendance)
        self.image_path = ''
        self.lblChonanh = self.findChild(QLabel, 'lblChonanh')
        self.tblDiemdanh = self.findChild(QTableWidget, 'tblDiemdanh')
        self.cbMon = self.findChild(QComboBox, 'cbMon')
        self.btnTrolai.clicked.connect(self.back)
        self.list_subject()

    def clear_all(self):
        self.tblDiemdanh.clearContents()
        self.tblDiemdanh.setRowCount(0)
        self.lblChonanh.clear()

    def back(self):
        self.clear_all()
        widget.setCurrentIndex(1)
    def choose_image(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilters(["Images (*.png *.xpm *.jpg *.jpeg)"])
        if file_dialog.exec():
            file_names = file_dialog.selectedFiles()
            if file_names:
                self.image_path = file_names[0]
                self.lblChonanh.setPixmap(QPixmap(self.image_path).scaled(200, 200, QtCore.Qt.AspectRatioMode.KeepAspectRatio))

    def train_svm_model(self):
        try:
            global taiKhoanDangNhap
            taikhoan = taiKhoanDangNhap
            cursor.execute('SELECT ID_SINHVIEN, ENCODING FROM KHUONMAT WHERE TAIKHOAN = ? ', (taikhoan))
            faces_data = cursor.fetchall()
        except Exception as e:
            QMessageBox.information(self, "Thông báo", f"Không thể truy vấn dữ liệu khuôn mặt. Lỗi {e}")
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
            #QMessageBox.information(self, "Thông báo", f"Không có dữ liệu khuôn mặt để huấn luyện mô hình.")
            return [], None

        id = set(labels)

        return id, clf.best_estimator_
    # Hàm để ghi nhận điểm danh vào cơ sở dữ liệu
    def recognize_and_record_attendance(self, image_path, labels, clf):
        if not os.path.isfile(image_path) or not image_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            return

        try:
            unknown_image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(unknown_image)
        except Exception as e:
            QMessageBox.information(self, "Thông báo", f"Không thể tải hoặc mã hóa hình ảnh: {e}")
            return

        present_students = set()

        for encoding in face_encodings:
            predictions = clf.predict_proba([encoding])[0]
            best_match_index = np.argmax(predictions)
            best_match_probability = predictions[best_match_index]
            student_id = list(labels)[best_match_index]
            if best_match_probability > 0.7:
                present_students.add(student_id)

        modified_timestamp = os.path.getmtime(image_path)
        modified_time = datetime.fromtimestamp(modified_timestamp)
        cursor.execute(
            'SELECT THOIGIAN FROM DIEMDANH WHERE THOIGIAN = ? ', (modified_time))
        time = cursor.fetchone()
        if time is None:
            for student_id in labels:
                status = 'Present' if student_id in present_students else 'Absent'
                self.record_attendance(student_id, status, image_path)
            list_subject = self.cbMon.currentText()
            cursor.execute('SELECT ID_MON FROM MONHOC WHERE TENMON = ?', (list_subject))
            idMon = cursor.fetchone()[0]
            cursor.execute('SELECT ID_CHITIET FROM CHITIETMONHOC WHERE ID_MON = ?',
                           (idMon))
            idCT = cursor.fetchone()
            if not idCT:
                QMessageBox.information(self, "Thông báo", f"Không có sinh viên học môn học {list_subject}")
                return
            else:
                QMessageBox.information(self, "Thông báo", "Điểm danh hoàn tất")

            self.display_attendance()
        else:
            QMessageBox.information(self, "Thông báo", "Hình ảnh này đã được điểm danh.")
            self.lblChonanh.clear()

    def record_attendance(self, student_id, status, image_path):
        try:
            global taiKhoanDangNhap
            taikhoan = taiKhoanDangNhap
            list_subject = self.cbMon.currentText()
            cursor.execute('SELECT ID_MON FROM MONHOC WHERE TENMON = ?', (list_subject))
            idMon = cursor.fetchone()[0]
            cursor.execute(
                'SELECT ID_LOP FROM SINHVIEN LEFT JOIN KHUONMAT ON SINHVIEN.ID_SINHVIEN = KHUONMAT.ID_SINHVIEN WHERE SINHVIEN.ID_SINHVIEN = ?',
                (student_id,))
            idLop = cursor.fetchone()[0]
            cursor.execute('SELECT ID_CHITIET FROM CHITIETMONHOC WHERE ID_MON = ? AND ID_SINHVIEN = ?', (idMon, student_id))
            idCT = cursor.fetchone()
            if not idCT:
                return
            idCT = idCT[0]
            modified_timestamp = os.path.getmtime(image_path)
            modified_time = datetime.fromtimestamp(modified_timestamp)
            cursor.execute('''
                INSERT INTO DIEMDANH (ID_LOP, ID_SINHVIEN, TAIKHOAN, ID_CHITIET, THOIGIAN, TRANGTHAI)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (idLop, student_id, taikhoan, idCT, modified_time, status))
            conn.commit()

        except Exception as e:
            QMessageBox.information(self, "Thông báo", f"Không thể ghi nhận điểm danh. Lỗi {e}")

    def list_subject(self):
        cursor.execute('SELECT TENMON FROM MONHOC')
        subjects = cursor.fetchall()
        for subject in subjects:
            self.cbMon.addItem(subject[0])

    def mark_attendance(self):
        if not self.image_path:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ảnh trước khi điểm danh")
            return

        self.trained_labels, self.clf = self.train_svm_model()
        if not self.trained_labels:
            QMessageBox.information(self, "Thông báo", "Không có dữ liệu khuôn mặt để huấn luyện mô hình.")
            return

        self.recognize_and_record_attendance(self.image_path, self.trained_labels, self.clf)


    def display_attendance(self):
        try:
            modified_timestamp = os.path.getmtime(self.image_path)
            modified_time = datetime.fromtimestamp(modified_timestamp)
            cursor.execute(
                'SELECT B.ID_DIEMDANH, B.ID_SINHVIEN, HOTEN, TENMON, THOIGIAN, TRANGTHAI FROM SINHVIEN A, DIEMDANH B, CHITIETMONHOC C, MONHOC D WHERE A.ID_SINHVIEN = B.ID_SINHVIEN AND B.ID_CHITIET = C.ID_CHITIET AND C.ID_MON = D.ID_MON AND THOIGIAN = ?', (modified_time))
            diemdanh_data = cursor.fetchall()
            num_rows = len(diemdanh_data)
            num_columns = len(diemdanh_data[0])
            column_width = self.tblDiemdanh.width() // num_columns
            self.tblDiemdanh.setRowCount(num_rows)
            self.tblDiemdanh.setColumnCount(num_columns)
            self.tblDiemdanh.setHorizontalHeaderLabels(
                ['ID Điểm Danh', 'ID Sinh Viên', 'Họ Tên Sinh Viên', 'Tên môn học', 'Thời Gian', 'Trạng Thái'])
            for row in range(num_rows):
                for col in range(num_columns):
                    item = QTableWidgetItem(str(diemdanh_data[row][col]))
                    self.tblDiemdanh.setItem(row, col, item)

            for col in range(num_columns):
                self.tblDiemdanh.setColumnWidth(col, column_width)
        except Exception as e:
            QMessageBox.information(self, "Thông báo", f"Không thể truy vấn dữ liệu điểm danh. Lỗi {e}")
class Statistical_w(QMainWindow):
    def __init__(self):
        super(Statistical_w, self).__init__()
        uic.loadUi('thongke.ui', self)
        self.btnTrolai.clicked.connect(self.back)
        self.tblThongke = self.findChild(QTableWidget, 'tblThongke')
        self.fiNhapid = self.findChild(QLineEdit, 'fiNhapid')
        self.fiTrangthai = self.findChild(QLineEdit, 'fiTrangthai')
        self.btnThongke.clicked.connect(self.display_statistical)
    def clear_all(self):
        self.tblThongke.clearContents()
        self.tblThongke.setRowCount(0)
        self.fiNhapid.clear()
        self.fiTrangthai.clear()

    def back(self):
        self.clear_all()
        widget.setCurrentIndex(1)

    def display_statistical(self):
        try:
            global taiKhoanDangNhap
            taikhoan = taiKhoanDangNhap
            idSV = self.fiNhapid.text()
            trangThai = self.fiTrangthai.text()
            cursor.execute('SELECT ID_DIEMDANH, TENLOP, TENMON, C.ID_SINHVIEN, HOTEN, THOIGIAN, TRANGTHAI '
                           'FROM LOPHOC A, SINHVIEN B, DIEMDANH C, CHITIETMONHOC D, MONHOC E '
                           'WHERE A.ID_LOP = B.ID_LOP AND B.ID_SINHVIEN = C.ID_SINHVIEN AND C.ID_CHITIET = D.ID_CHITIET '
                           'AND D.ID_MON = E.ID_MON AND C.ID_SINHVIEN = ? AND TRANGTHAI = ? AND C.TAIKHOAN = ?',
                           (idSV, trangThai, taikhoan))
            sta_data = cursor.fetchall()
            if sta_data:
                QMessageBox.information(self, "Thông báo", f"Thống kê thành công")
                num_rows = len(sta_data)
                num_columns = len(sta_data[0])
                column_width = self.tblThongke.width() // num_columns
                self.tblThongke.setRowCount(num_rows)
                self.tblThongke.setColumnCount(num_columns)
                self.tblThongke.setHorizontalHeaderLabels(
                    ['ID Điểm danh', 'Tên lớp', 'Tên môn', 'ID Sinh viên', 'Họ tên sinh viên', 'Thời gian điểm danh', 'Trạng thái'])
                for row in range(num_rows):
                    for col in range(num_columns):
                        item = QTableWidgetItem(str(sta_data[row][col]))
                        self.tblThongke.setItem(row, col, item)

                for col in range(num_columns):
                    self.tblThongke.setColumnWidth(col, column_width)
                self.fiNhapid.clear()
                self.fiTrangthai.clear()
            else:
                QMessageBox.information(self, "Thông báo", f"Không có dữ liệu để thống kê!")
                self.clear_all()
        except Exception as e:
            QMessageBox.information(self, "Thông báo", f"Thống kê thất bại. Lỗi {e}!")

class Subjects_w(QMainWindow):
    def __init__(self):
        super(Subjects_w, self).__init__()
        uic.loadUi('subject.ui', self)
        self.btnTrolai.clicked.connect(self.back)
        self.tblMonHoc = self.findChild(QTableWidget, 'tblMonHoc')
        self.fiIDSinhVien = self.findChild(QLineEdit, 'fiIDSinhVien')
        self.fiIDMon = self.findChild(QLineEdit, 'fiIDMon')
        self.fiTenMon = self.findChild(QLineEdit, 'fiTenMon')
        self.btnThem.clicked.connect(self.insert_subjects)
        self.btnSua.clicked.connect(self.update_subjects)
        self.btnXoa.clicked.connect(self.delete_subjects)
        self.display_subjects()

    def clear_table1(self):
        self.tblMonHoc.clearContents()
        self.tblMonHoc.setRowCount(0)
        self.fiIDSinhVien.clear()
        self.fiIDMon.clear()
        self.fiTenMon.clear()

    def back(self):
        widget.setCurrentIndex(1)
        self.fiIDSinhVien.clear()
        self.fiIDMon.clear()
        self.fiTenMon.clear()


    def display_subjects(self):
        try:
            global taiKhoanDangNhap
            taikhoan = taiKhoanDangNhap
            cursor.execute(
                "SELECT ID_CHITIET, B.ID_MON, TENMON, B.ID_SINHVIEN FROM MONHOC A, CHITIETMONHOC B WHERE A.ID_MON = B.ID_MON AND TAIKHOAN = ?", (str(taikhoan),))
            subjects_data = cursor.fetchall()
            if subjects_data:
                num_rows = len(subjects_data)
                num_columns = len(subjects_data[0])
                column_width = self.tblMonHoc.width() // num_columns
                self.tblMonHoc.setRowCount(num_rows)
                self.tblMonHoc.setColumnCount(num_columns)
                self.tblMonHoc.setHorizontalHeaderLabels(
                    ['ID Chi tiết','ID Môn học', 'Tên môn học', 'ID sinh viên'])
                for row, record in enumerate(subjects_data):
                    for col, value in enumerate(record):
                        item = QTableWidgetItem(str(value))
                        self.tblMonHoc.setItem(row, col, item)
                for col in range(num_columns):
                    self.tblMonHoc.setColumnWidth(col, column_width)
        except Exception as e:
            QMessageBox.information(self, "Thông báo", f"Không thể truy vấn dữ liệu điểm danh. Lỗi {e}")

    def insert_subjects(self):
        try:
            global taiKhoanDangNhap
            taikhoan = taiKhoanDangNhap
            idSV = self.fiIDSinhVien.text()
            idMon = self.fiIDMon.text()
            tenMon = self.fiTenMon.text()
            cursor.execute('SELECT ID_MON FROM MONHOC WHERE ID_MON = ? AND TENMON = ?', (idMon, tenMon))
            mon_Hoc = cursor.fetchall()
            cursor.execute('SELECT TAIKHOAN FROM SINHVIEN WHERE ID_SINHVIEN = ? AND TAIKHOAN = ? ',
                           (idSV, taikhoan))
            user = cursor.fetchall()
            if mon_Hoc == []:
                cursor.execute('INSERT INTO MONHOC(ID_MON, TENMON) VALUES (?,?)', (idMon, tenMon))
                conn.commit()
                cursor.execute('SELECT ID_MON, TENMON FROM MONHOC WHERE ID_MON = ? AND TENMON = ?', (idMon, tenMon))
                kiemTra = cursor.fetchone()[0]
                if kiemTra:
                    if user:
                        cursor.execute('INSERT INTO CHITIETMONHOC (ID_SINHVIEN, ID_MON, TAIKHOAN) VALUES (?, ?, ?)', (idSV, idMon, taikhoan))
                        conn.commit()
                        QMessageBox.information(self, "Thông báo", "Thêm thành công")
                        self.fiIDSinhVien.clear()
                        self.fiIDMon.clear()
                        self.fiTenMon.clear()
                        self.display_subjects()
                    else:
                        QMessageBox.information(self, "Thông báo", "Thêm không thành công! ID_SINHVIEN không khớp.")
            elif mon_Hoc != []:
                if user:
                    cursor.execute('INSERT INTO CHITIETMONHOC (ID_SINHVIEN, ID_MON, TAIKHOAN) VALUES (?, ?, ?)',
                                   (idSV, idMon, taikhoan))
                    conn.commit()
                    QMessageBox.information(self, "Thông báo", "Thêm thành công")
                    self.fiIDSinhVien.clear()
                    self.fiIDMon.clear()
                    self.fiTenMon.clear()
                    self.display_subjects()
                else:
                    QMessageBox.information(self, "Thông báo", "Thêm không thành công! ID_SINHVIEN không khớp.")
            else:
                QMessageBox.information(self, "Thông báo", "Thêm thất bại.")
        except Exception as e:
            QMessageBox.information(self, "Thông báo", f"Thêm thất bại. Lỗi {e}!")

    def update_subjects(self):
        try:
            # Lấy thông tin từ hàng được chọn trong QTableWidget
            selected_items = self.tblMonHoc.selectedItems()
            if len(selected_items) == 0:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một hàng để cập nhật.")
                return

            row = selected_items[0].row()
            idCT = self.tblMonHoc.item(row, 0).text()
            idMon = self.tblMonHoc.item(row, 1).text()
            tenMon = self.tblMonHoc.item(row, 2).text()
            idSinhVien = self.tblMonHoc.item(row, 3).text()

            cursor.execute('SELECT ID_CHITIET FROM CHITIETMONHOC WHERE ID_CHITIET = ?', (idCT))
            existing_id = cursor.fetchall()
            taikhoan = taiKhoanDangNhap
            if existing_id:
                cursor.execute('SELECT ID_SINHVIEN FROM SINHVIEN WHERE ID_SINHVIEN = ?', (idSinhVien))
                id_test = cursor.fetchall()
                if id_test == []:
                    QMessageBox.information(self, "Thông báo", "Lỗi! Cập nhật ID_SINHVIEN thất bại.")
                    self.display_subjects()
                else:
                    cursor.execute('SELECT ID_MON FROM MONHOC WHERE ID_MON = ?', (idMon))
                    idMon_test = cursor.fetchall()
                    if idMon_test:
                        cursor.execute('UPDATE MONHOC SET TENMON = ? WHERE ID_MON = ?', (tenMon, idMon))
                        conn.commit()
                        cursor.execute('SELECT TENMON FROM MONHOC WHERE TENMON = ?', (tenMon))
                        tenMon_test = cursor.fetchall()
                        if tenMon_test == []:
                            QMessageBox.information(self, "Thông báo", "Lỗi! Không cập nhật được tên môn vào bảng MONHOC.")
                            self.display_subjects()
                        else:
                            cursor.execute('SELECT ID_SINHVIEN FROM CHITIETMONHOC WHERE ID_SINHVIEN = ? AND ID_CHITIET != ?', (idSinhVien, idCT))
                            test_id = cursor.fetchall()
                            if test_id:
                                QMessageBox.information(self, "Thông báo", "Lỗi! Cập nhật danh sách thất bại.")
                                self.display_subjects()
                            else:
                                # Cập nhật thông tin trong cơ sở dữ liệu
                                cursor.execute(
                                    'UPDATE CHITIETMONHOC SET ID_MON = ?, ID_SINHVIEN = ?, TAIKHOAN = ? WHERE ID_CHITIET = ?',
                                    (idMon, idSinhVien, taikhoan, idCT))
                                conn.commit()

                                # Hiển thị thông báo và cập nhật lại bảng
                                QMessageBox.information(self, "Thông báo", "Cập nhật thành công")
                                self.display_subjects()
                    else:
                        QMessageBox.information(self, "Thông báo", "Lỗi! Cập nhật ID_MON thất bại.")
                        self.display_subjects()
            elif existing_id == []:
                QMessageBox.information(self, "Thông báo", "Cập nhật thất bại.")
                self.display_subjects()

        except Exception as e:
            QMessageBox.information(self, "Thông báo", f"Cập nhật thất bại. Lỗi {e}!")
            self.display_subjects()

    def delete_subjects(self):
        try:
            global taiKhoanDangNhap
            taikhoan = taiKhoanDangNhap
            # Lấy thông tin từ hàng được chọn trong QTableWidget
            selected_items = self.tblMonHoc.selectedItems()
            if len(selected_items) == 0:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một hàng để xoá.")
                return

            # Lấy ID lớp học từ hàng được chọn
            row = selected_items[0].row()
            idCT = self.tblMonHoc.item(row, 0).text()

            cursor.execute('DELETE FROM CHITIETMONHOC WHERE ID_CHITIET = ?', (idCT))
            conn.commit()

            # Hiển thị thông báo và cập nhật lại bảng
            QMessageBox.information(self, "Thông báo", "Xoá thành công")
            cursor.execute('SELECT TAIKHOAN FROM CHITIETMONHOC WHERE TAIKHOAN = ? AND ID_CHITIET = ?', (taikhoan, idCT))
            user = cursor.fetchall()
            if not user:
                self.tblMonHoc.clearContents()
                self.tblMonHoc.setRowCount(0)
                self.display_subjects()
        except Exception as e:
            QMessageBox.information(self, "Thông báo", f"Xoá thất bại. Lỗi {e}!")

app = QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()

Login_f = Login_w()
Loginsc_f = Loginsc_w()
Class_f = Class_w()
Student_f = Student_w()
Encode_f = Encode_w()
Attendance_f = Attendance_w()
Statistical_f = Statistical_w()
Subjects_f = Subjects_w()

widget.addWidget(Login_f)
widget.addWidget(Loginsc_f)
widget.addWidget(Class_f)
widget.addWidget(Student_f)
widget.addWidget(Encode_f)
widget.addWidget(Attendance_f)
widget.addWidget(Statistical_f)
widget.addWidget(Subjects_f)

widget.setCurrentIndex(0)
widget.setFixedHeight(800)
widget.setFixedWidth(1200)
widget.show()
app.exec()
def close_connection():
    cursor.close()
    conn.close()

close_connection()