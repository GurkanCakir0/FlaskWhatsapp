from flask import Flask, jsonify, request
import os
import logging
import base64
import json
from flask_cors import CORS
from twilio.rest import Client

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG)
UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

account_sid = 'w'
auth_token = 'w'
WHATSAPP_NUMBER = 'whatsapp:+w'
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+17752889659'

# if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not WHATSAPP_NUMBER:
# print("Twilio bilgileriniz eksik, FLASKWHATSAPPS secret'ını kontrol edin")
# exit(1)

client = Client(account_sid, auth_token)


@app.route('/')
def index():
    app.logger.debug("Ana sayfa erişildi")
    return jsonify({"Mesaj": "Hoş Geldiniz"})


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/upload', methods=['POST'])
def upload_file():
    app.logger.debug("Upload endpoint erişildi")
    try:
        if request.is_json:
            data = request.get_json()
            if 'audio' not in data:
                app.logger.error("Eksik 'audio' alanı")
                return jsonify({"error": "Missing 'audio' field in JSON"}), 400

            audio_data = base64.b64decode(data['audio'])
            app.logger.debug("Ses verisi decode edildi")
            file_path = os.path.join(UPLOAD_FOLDER, "uploaded_audio.wav")
            with open(file_path, 'wb') as f:
                f.write(audio_data)
            app.logger.debug(f"Dosya kaydedildi: {file_path}")

            file_url = f"http://{request.host}/uploads/uploaded_audio.wav"

            message = client.messages.create(
                from_=TWILIO_WHATSAPP_NUMBER,
                body='Ses dosyası',
                to=WHATSAPP_NUMBER,
                media_url=['data:audio/wav;base64,' + audio_base64]
            )
            app.logger.debug(f"Dosya yükleme başlatıldı: {blob_name}")

            return jsonify({"message": "Audio file sent via WhatsApp", "sid": message.sid}), 200

        return jsonify({"error": "Invalid request"}), 400
    except Exception as e:
        app.logger.error(f"Hata: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("Environment Variables:", os.environ)
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port, host="0.0.0.0")
