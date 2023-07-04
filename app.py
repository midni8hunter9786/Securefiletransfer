import os
from flask import Flask, request, render_template, send_file
from cryptography.fernet import Fernet
from pyngrok import ngrok

app = Flask(__name__)

# Generate a symmetric encryption key
key = Fernet.generate_key()

# Route for file upload
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        
        if file.filename == '':
            return render_template('upload.html', error_message='Please choose a file.')

        file.save(file.filename)

        # Encrypt the uploaded file
        encrypted_filename = encrypt_file(file.filename)

        # Start ngrok to expose the server to the internet
        public_url = ngrok.connect(5000).public_url

        # Construct the secure URL to the encrypted file
        secure_url = f"{public_url}/download/{encrypted_filename}"

        return render_template('upload.html', secure_url=secure_url)
    return render_template('upload.html')

# Encryption function
def encrypt_file(file_path):
    with open(file_path, "rb") as file:
        data = file.read()
        cipher_suite = Fernet(key)
        encrypted_data = cipher_suite.encrypt(data)

    # Save the encrypted file
    encrypted_filename = f"encrypted_{file_path}"
    with open(encrypted_filename, "wb") as file:
        file.write(encrypted_data)

    return encrypted_filename

# Route for file download
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    # Decrypt the file
    decrypted_data = decrypt_file(filename)

    # Save the decrypted file to a temporary directory
    decrypted_filename = filename.replace("encrypted_", "decrypted_")
    with open(decrypted_filename, "wb") as file:
        file.write(decrypted_data)

    # Send the file for download
    return send_file(decrypted_filename, as_attachment=True)

# Decryption function
def decrypt_file(filename):
    with open(filename, "rb") as file:
        encrypted_data = file.read()
        cipher_suite = Fernet(key)
        decrypted_data = cipher_suite.decrypt(encrypted_data)

    return decrypted_data

if __name__ == '__main__':
    # Run the Flask application
    app.run(debug=True)
