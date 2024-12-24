import os
from pathlib import Path
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
import tkinter as tk
from tkinter import messagebox
from concurrent.futures import ThreadPoolExecutor
import logging

# Cấu hình logging
logging.basicConfig(
    filename="decryption_log.txt",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# Khóa riêng RSA được nhập trực tiếp vào mã (thay thế bằng khóa riêng thực của bạn)
PRIVATE_KEY = b"""-----BEGIN RSA PRIVATE KEY-----
    MIIEowIBAAKCAQEAqeK4NJiPiZCZ4h4p3is7r97SDdgikkrK04Mlsz+hv6Rb1+0v
    3XlcozAuFxb/291LNm4k53TYMt83pOFoYE8xLtTNyQSR04vw0FpdpSv5aUco+1Fk
    pF4Lt+jWT4b5kMAjY4d9nXoyQBlIo0VrC0C2rWizIN4euMpSnYwWftkbldNjp2uS
    HEyc5gAYGVJIfzMTbiLYwI9iOk6YgXJ3mbKtutz6ZTSvZeW10iHksbWQx/qEcGBK
    XRTnE/a2deXoE8QhVNMEygLUBaw4DXidBmpbqfIkofNTZT7+crhChqZmbakJ09m7
    fOy5MDnwJ+iM0vPaymmtgnZpkGCP6ZCT9dxzpwIDAQABAoH/esRcWaXmFINqsP0b
    RHH5sB5VrauDUDS8Xh1oISDawqMDvAarkGEjkMpAhG8adsh0keEGyjymAB1PGNfL
    lc2kvTMLgzjKKRX38JldEv+0PWAvPW6UTDOqRDz+onnn37L53/MJ08N6jNe4pkSE
    Fp2tZaNDz3y0ttV+3ltd5kz+okXzLsxWnbadhLbI1ThAPaYOMjCFoqgsl/RyRbbI
    eOArGBcx2F5j/e7iigf4wLPf5kwNrZ9/K817F6qSSNgq/2tnPGsT+WxVfGmU9ttY
    UAYg1MJbCstC0S5CYGIzS2HvIt1CRA9xMWW2RMRUXcjzLWChs4SIACba/snMJwRt
    DA3hAoGBAModEFcbQIgA35MD+U6msXDRlVi6YSrW5ev97tFFmsCQP/tsRZAVixOw
    vZzOAoQSKoeNESULIQ53EPxxen3gr2V/iAG5jLys26yPPHTze5BuUtHd6rlkhkkK
    ainkXuZhaGMkfoJ55mEINtdLxU62Qr3CqVEHynfIw2AseS6krJp3AoGBANct/cu6
    ZxdXhoAs3bQE7SkNrxndzZ1xEXCyV0q9u7XbYRf4J4f7fsg5CD6AhIREGsb0XL3S
    OuaYityuDLD9rymg9Mhm8jSINtnY9SfW62qRkpxhk/G4J048hKY5sFn3xlTclFyj
    xA3k7YM6E5VXvdT28HjSSeUfSQ/+YrQajgxRAoGBAKQ0mrr6ZCJa+0nZN6rD2XO8
    gybUPe9tKt3hsC6L61+5kpH1dErMhfLYbCTCZt7gV3dLj/tVoGS9Laq7k3ZDnpzK
    0Tf9hS8hDVSUBt1JmEFOsLDbKEG5PzSGZpxkcwmfaAzscHAXE6oP32ZppAMAJxc+
    2QsBVmidTsaLO2U+2xCfAoGBAK0CMH4eSIcu+1iROkxkbZ7FftToTkrZPzGCYscY
    WBV25tET2Azwe9ZWbLd8M4/5BiKTFQIWRv9jBLs8Qb4Iqk5pOIbspq7wGlH7q9k1
    ZyDPHLcZiY8fBpNT+z9/QLiFjHRsyejWT2rwdrs89cPswRe62Ev8oCdViTQPz6KJ
    e06RAoGBAI8jB2sR4ph9vg9HSuC8ooqfDvBzSW666fuMnFuBIuoU2FIi4xEzNVkP
    1WouSeHniqsmLxXfl+2Xi5X769gDagk58EZ3EUEREoF3xese0N0gkzSWLb9kNI6R
    o8kbVfIKCmS4K9XX5tiVOebSxIycPFgY+HprUXFsebXH2y0hxCtJ
    -----END RSA PRIVATE KEY-----"""

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
        logging.warning(f"Không thể truy cập {base_dir}: {e}")

def decrypt(data_file: Path):
    '''
    Giải mã file bằng RSA và AES trong chế độ EAX để phát hiện thay đổi không hợp lệ.

    :param data_file: Path to the encrypted file
    :return: Boolean indicating if decryption was successful
    '''
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
