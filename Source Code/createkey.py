from Crypto.PublicKey import RSA

key = RSA.generate(2048)
privateKey = key.export_key()
publicKey = key.publickey().export_key()

# luu private key vo file
with open('private.key', 'wb') as f:
    f.write(privateKey)

# luu public key vo file
with open('public.key', 'wb') as f:
    f.write(publicKey)

print('Done')
print(privateKey)
