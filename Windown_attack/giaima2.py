import os
from pathlib import Path
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
import tkinter as tk
from tkinter import messagebox

PRIVATE_KEY_FILE = 'private.pem'

def scan_recurse(base_dir: Path):
    '''
    Duyệt qua thư mục và trả về danh sách các file.
    
    :param base_dir: Path object of the directory to scan
    :return: Generator yielding file paths
    '''
    try:
        for entry in os.scandir(base_dir):
            if entry.is_file():
                yield Path(entry.path)
            elif entry.is_dir():
                yield from scan_recurse(Path(entry.path))
    except (PermissionError, FileNotFoundError) as e:
        print(f"Không thể truy cập {base_dir}: {e}")

def decrypt(data_file: Path, private_key_file: str):
    '''
    Giải mã file bằng RSA và AES trong chế độ EAX để phát hiện thay đổi không hợp lệ.

    :param data_file: Path to the encrypted file
    :param private_key_file: Path to the private key file
    '''
    try:
        with open(private_key_file, 'rb') as f:
            private_key = RSA.import_key(f.read())

        with open(data_file, 'rb') as f:
            encrypted_session_key, nonce, tag, ciphertext = [ f.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1) ]

        # Giải mã khóa phiên
        cipher_rsa = PKCS1_OAEP.new(private_key)
        session_key = cipher_rsa.decrypt(encrypted_session_key)

        # Giải mã dữ liệu
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce=nonce)
        data = cipher_aes.decrypt_and_verify(ciphertext, tag)

        # Lưu file đã giải mã
        original_file_name = data_file.with_suffix('')
        with open(original_file_name, 'wb') as f:
            f.write(data)

        print(f'File đã giải mã được lưu tại {original_file_name}')

        # Xóa file đã mã hóa
        if data_file.suffix == '.rans':
            os.remove(data_file)
            print(f"Đã xóa file đã mã hóa: {data_file}")

        return True
    except Exception as e:
        print(f"Lỗi khi giải mã {data_file}: {type(e).__name__} - {str(e)}")
        return False

def main():
    # Danh sách các thư mục để quét (Desktop, Downloads, Documents, Pictures, Music, Videos)
    user_home = Path.home()
    directories_to_scan = [
        user_home / "Desktop",
        user_home / "Downloads",
        user_home / "Documents",
        user_home / "Pictures",
        user_home / "Music",
        user_home / "Videos"
    ]

    # Tập trung vào các file có phần mở rộng '.rans'
    include_extension = {'.rans'}  # Đảm bảo phần mở rộng là chữ thường
    total_files = 0
    decrypted_files = 0

    for directory in directories_to_scan:
        if directory.exists():
            for file_path in scan_recurse(directory):
                if file_path.suffix.lower() in include_extension:
                    total_files += 1
                    if decrypt(file_path, PRIVATE_KEY_FILE):
                        decrypted_files += 1

    # Hiển thị thông báo GUI
    if total_files > 0:
        if decrypted_files == total_files:
            messagebox.showinfo("Giải mã thành công", f"Đã giải mã thành công {decrypted_files}/{total_files} file.")
        else:
            messagebox.showwarning("Giải mã hoàn tất", f"Đã giải mã {decrypted_files}/{total_files} file. Một số file không thể giải mã.")
    else:
        messagebox.showinfo("Giải mã", "Không tìm thấy file nào cần giải mã.")

if __name__ == "__main__":
    main()
