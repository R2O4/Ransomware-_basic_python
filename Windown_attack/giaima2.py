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
    
    # Remove the '.L0v3sh3' suffix and keep the original extension (e.g., .pdf, .txt)
    if dataFile.endswith('.L0v3sh3'):
        fileName = dataFile[:-8]  # Remove the '.L0v3sh3' part (length of '.L0v3sh3' is 8)
    else:
        fileName = dataFile  # If the file doesn't have the '.L0v3sh3' extension, keep the name as is

    with open(fileName, 'wb') as f:
        f.write(data)

    print('Decrypted file saved to ' + fileName)

    # Delete the original encrypted file with '.L0v3sh3' extension
    if dataFile.endswith('.L0v3sh3'):
        os.remove(dataFile)  # Remove the encrypted file after decryption
        print(f"Deleted the encrypted file: {dataFile}")


directory = './'  # CHANGE THIS

# Focus on files with .L0v3sh3 extension for decryption
includeExtension = ['.l0v3sh3']  # Make sure the extension is lowercase

for item in scanRecurse(directory): 
    filePath = Path(item)
    fileType = filePath.suffix.lower()
    # Run the decryptor only if the file has .L0v3sh3 extension
    if fileType in includeExtension:
        decrypt(filePath, privateKeyFile)
