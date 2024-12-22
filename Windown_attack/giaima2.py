import os
from pathlib import Path
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES


privateKeyFile = 'private.pem'


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
    extension = dataFile.suffix.lower()  # Lấy phần mở rộng của file
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
    
    # Remove the '.ransomware' suffix and keep the original extension (e.g., .pdf, .txt)
    if dataFile.endswith('.ransomware'):
        fileName = dataFile[:-10]  # Remove the '.ransomware' part (length of '.ransomware' is 8)
    else:
        fileName = dataFile  # If the file doesn't have the '.ransomware' extension, keep the name as is

    with open(fileName, 'wb') as f:
        f.write(data)

    print('Decrypted file saved to ' + fileName)

    # Delete the original encrypted file with '.ransomware' extension
    if dataFile.endswith('.ransomware'):
        os.remove(dataFile)  # Remove the encrypted file after decryption
        print(f"Deleted the encrypted file: {dataFile}")


# Define the list of directories to scan (Desktop, Downloads, Documents, Pictures, Music, Videos)
user_home = Path.home()  # Get the user's home directory
directories_to_scan = [
    user_home / "Desktop",
    user_home / "Downloads",
    user_home / "Documents",
    user_home / "Pictures",
    user_home / "Music",
    user_home / "Videos"
]

# Focus on files with .ransomware extension for decryption
includeExtension = ['.ransomware']  # Make sure the extension is lowercase

for directory in directories_to_scan:
    if directory.exists():  # Check if the directory exists
        for item in scanRecurse(directory):
            filePath = Path(item)
            fileType = filePath.suffix.lower()
            # Run the decryptor only if the file has .ransomware extension
            if fileType in includeExtension:
                decrypt(filePath, privateKeyFile)
