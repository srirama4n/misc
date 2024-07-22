import pyffx
from flask import Flask
import cipher as c

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/encrypt/<string:actual>', methods=['GET', 'POST'])
def encrypt(actual):
    encrypted = c.fpe_encrypt_or_decrypt(actual, "ENCRYPT")
    return encrypted

@app.route('/decrypt/<string:actual>', methods=['GET', 'POST'])
def decrypt(actual):
    decrypted = c.fpe_encrypt_or_decrypt(actual, "DECRYPT")
    return decrypted
