import os
from pathlib import Path
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
import tkinter as tk
from tkinter import messagebox
from concurrent.futures import ThreadPoolExecutor
import logging

# Cấu hình logging.
logging.basicConfig(
    filename="decryption_log.txt",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# Khóa riêng RSA
PRIVATE_KEY = b"""-----BEGIN RSA PRIVATE KEY-----
MIIEpQIBAAKCAQEA0r5IjHT2zoJsDnq1XrxYsabDObJBB5zDcWTvUVRNKyfSDvxg
WGm4pFQS6wzPMxr4ounFtdQR72CDe935yEyr/1xeWNkNfFQF1HK75GiFHOXemhKP
RiazItiI0Y/KdXArixfGkAhCk52IwUeXVSu5stfEtSy/lJL4sfEVj3a1+JS1UlUm
zyzTr5UBdIB7QvAXIa01YDcKjgWSYgZppbAVHQDL2CSHzks6XBouh8M+R/iGQBR4
sBBsQFVEZhi3ZhfgtM/wOgHlporkU+mOidpS4A52gEq6C/mCMgIxW1GeS/fvetVO
/iM1Ra27scje32NXrcWE4SGjTbot114GwMIMsQIDAQABAoIBABsGaE7MxAas/nbn
4QDWVehoOoJYW9MCVSTiPPdYwHGfkGY4EpHb8t/t4SQv1xVWaNqZcG92E9u27H2S
tHCtdmQPoBC0OvC95KZ/FR3AEovnZYGsDiAAn/nAu2DmV9/yA795S88WJBWCfvJM
QDmdmxl2ZoUWSTYgF9DX2fw1DLZk/f05B5SzjcXimMAvFJ4zR4KvZuiaXzes7sKn
gAM3EGdy5yqUKlVc4wV/KWQsgAsBriLxRT3ifeqCVO7bSBGocKshK7fABCe2YZS0
ErrntgEzW3gWTCqouBMm0XCckvT/rEp86Ul8pJQMJ3KHY6Un+ul/grWiXa+KTKb1
RDo7NZ0CgYEA5dXAFzsuMA204DP02Gc67uLxYm5orDRiScYbFH3CfjjqCkrBe+W7
s8tblJOUj1kxs/V/iiJ2Jgthyxm/iE1PG0gRS00IizqdSXaRHz9CE2feK14MShP+
n4SbEpAUHKP9PwnoAyPm/2UQM6Xmxqsb+YmB2IJF937OCIJzQLnHwpUCgYEA6rwh
aEHzvCmojNDZ1cPOgmcFTspSBofAOSugEv8IOzn6m1b9NB2lprxMQUma9Qm6Rl2y
4HXWC1tJOQFJVsn/R0bm7urVq9n9TGzww3SGmUFdCvZTmZJhrvds/xYcyCm8+2pZ
Tzi0LaHIbZAUkBDlD6UXy72ge9PrIIyUOpPv1q0CgYEA10N6ZMfTHMLZtFw1aTJW
qkP4nZ6XfyKZJEveNTUMozgfTIBz891aDq3bGq+XJyP9P3YifHiGfF+Quq9lCv6N
pxm6yPJfnDfL9XCNv9x5wL86ARhXHlLX2wRSUfKMQ778hLx8h+RqiK5ZnGY4Xb8J
tpCqAuURLxufUa0M0YSvqnkCgYEArATgSoICdwLkVQV8jY3n2WJb3migAc8bzAmv
Thx9UMHlaE8wUS/kxDK7gyDIoQfW7VgfDSTtjfcAyvipYSO4ouhPtgh8O2sNmCNB
sUrElKz03WK00xcV5N3Hj4wJ3ZnQt0IxXsAEMmib88ahew4WfweST6mQYQ5lAb5j
piXhniUCgYEAvMshYiUNWy53oY18CvHFH7HwrjsFBSq6PpaYSGmLv4CvwkHryTRH
4mDDNDZ5fvE80g8gwFJhFV2LA/aShdMd1uqv1kvz+f3YUO+RI8/14K4g2Rreb8DF
RqPuP3GrLa8IThYhtiVy2npiGIKt+Eul+vmSHHIXE6IvAyGmHv9Bgps=
-----END RSA PRIVATE KEY-----"""

# Duyệt đệ quy qua thư mục và trả về danh sách các file.
def scan_recurse(base_dir: Path):
    try:
        for entry in os.scandir(base_dir):
            if entry.is_file():
                yield Path(entry.path)
            elif entry.is_dir():
                yield from scan_recurse(Path(entry.path))
    except (PermissionError, FileNotFoundError) as e:
        logging.warning(f"Không thể truy cập {base_dir}: {e}")

# Giải mã file bằng RSA và AES trong chế độ EAX để phát hiện thay đổi không hợp lệ.
def decrypt(data_file: Path):
    try:
        private_key = RSA.import_key(PRIVATE_KEY)

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

        logging.info(f'File đã giải mã được lưu tại {original_file_name}')

        # Xóa file đã mã hóa
        if data_file.suffix == '.rans':
            os.remove(data_file)
            logging.info(f"Đã xóa file đã mã hóa: {data_file}")

        return True
    except Exception as e:
        logging.error(f"Lỗi khi giải mã {data_file}: {type(e).__name__} - {str(e)}")
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

    include_extension = {'.rans'}
    total_files = 0
    decrypted_files = 0

    with ThreadPoolExecutor() as executor:
        futures = []
        for directory in directories_to_scan:
            if directory.exists():
                for file_path in scan_recurse(directory):
                    if file_path.suffix.lower() in include_extension:
                        total_files += 1
                        futures.append(executor.submit(decrypt, file_path))

        for future in futures:
            if future.result():
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
