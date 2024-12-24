from Crypto.PublicKey import RSA

key = RSA.generate(2048)
privateKey = key.export_key()
publicKey = key.publickey().export_key()

# luu private key vo file
with open('private.pem', 'wb') as f:
    f.write(privateKey)

# luu public key vo file
with open('public.pem', 'wb') as f:
    f.write(publicKey)

print('Private key saved to private.pem')
print('Public key saved to public.pem')
print('Done')
print(privateKey)
