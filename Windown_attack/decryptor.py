import os
from pathlib import Path
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP, AES
import tkinter as tk
from tkinter import simpledialog

privateKeyFile = 'private.pem'  # Đảm bảo rằng bạn có file private.pem sẵn có

def scanRecurse(baseDir):
    '''
    Scan a directory and return a list of all files
    return: list of files
    '''
    for entry in os.scandir(baseDir):
        if entry.is_file():
            yield entry
        else:
            yield from scanRecurse(entry.path)

def decrypt(dataFile, privateKeyFile):
    '''
    use EAX mode to allow detection of unauthorized modifications
    '''

    # read private key from file
    extension = dataFile.suffix.lower()
    with open(privateKeyFile, 'rb') as f:
        privateKey = f.read()
        # create private key object
        key = RSA.import_key(privateKey)

    # read data from file
    with open(dataFile, 'rb') as f:
        # read the session key
        encryptedSessionKey, nonce, tag, ciphertext = [ f.read(x) for x in (key.size_in_bytes(), 16, 16, -1) ]

    # decrypt the session key
    cipher = PKCS1_OAEP.new(key)
    sessionKey = cipher.decrypt(encryptedSessionKey)

    # decrypt the data with the session key
    cipher = AES.new(sessionKey, AES.MODE_EAX, nonce)
    data = cipher.decrypt_and_verify(ciphertext, tag)

    # save the decrypted data to file
    dataFile = str(dataFile)
    fileName = dataFile.split(extension)[0]
    fileExtension = '.decrypted'  # mark the file was decrypted
    decryptedFile = fileName + fileExtension
    with open(decryptedFile, 'wb') as f:
        f.write(data)

    print('Decrypted file saved to ' + decryptedFile)

# Tạo cửa sổ GUI với tkinter
root = tk.Tk()
root.withdraw()  # Ẩn cửa sổ chính của tkinter

# Sử dụng hộp thoại để yêu cầu người dùng nhập thư mục cần quét
directory = simpledialog.askstring("Input", "Enter the directory to scan (default is './'):")

# Nếu người dùng không nhập gì, sử dụng thư mục mặc định
if not directory:
    directory = './'

includeExtension = ['.l0v3sh3']  # Chỉ giải mã các file có đuôi '.l0v3sh3'

for item in scanRecurse(directory):
    filePath = Path(item)
    fileType = filePath.suffix.lower()
    if fileType in includeExtension:
        decrypt(filePath, privateKeyFile)
