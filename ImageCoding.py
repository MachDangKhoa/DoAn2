import os
import pyodbc
import face_recognition

# Thiết lập kết nối với cơ sở dữ liệu SQL Server
conn = pyodbc.connect('DRIVER={SQL Server};'
                      'SERVER=MSI;'
                      'DATABASE=Face_Recognition;'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()

# Hàm để mã hóa khuôn mặt
def encode_face(image_path):
    image = face_recognition.load_image_file(image_path)
    face_encodings = face_recognition.face_encodings(image)
    if face_encodings:
        # Chuyển đổi mã hóa khuôn mặt thành một mảng numpy
        return face_encodings[0]
    return None

# Hàm để thêm hình ảnh và mã hóa vào cơ sở dữ liệu
def add_and_encode_images(image_directory, id_sinhvien, taikhoan):
    # Lấy ID_KHUONMAT cuối cùng từ cơ sở dữ liệu
    cursor.execute('SELECT MAX(ID_KHUONMAT) FROM KHUONMAT')
    last_id = cursor.fetchone()[0] or 0

    # Bật IDENTITY_INSERT
    cursor.execute('SET IDENTITY_INSERT KHUONMAT ON')
    conn.commit()

    # Duyệt qua tất cả các tệp trong thư mục hình ảnh
    for image_name in os.listdir(image_directory):
        image_path = os.path.join(image_directory, image_name)
        face_encoding = encode_face(image_path)
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

# Thay thế 'path_to_your_images' với đường dẫn thực tế đến thư mục hình ảnh của bạn
add_and_encode_images('D:\\CodePy\\KhuonMat\\images\\duyanh', 7, 'admin')

# Đóng kết nối cơ sở dữ liệu
cursor.close()
conn.close()
