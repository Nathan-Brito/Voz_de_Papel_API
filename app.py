import tempfile
from flask import Flask, request, jsonify, send_file, after_this_request
import os
import sys
from dotenv import load_dotenv
import cv2
import pytesseract
import google.generativeai as genai
import azure.cognitiveservices.speech as speechsdk
import numpy as np
import psycopg2
import base64

app = Flask(__name__)

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_KEY"))

subscription_key = os.getenv("AZURE_KEY")
region = os.getenv("AZURE_REGION")
speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=region)
speech_config.speech_synthesis_voice_name = "pt-BR-FranciscaNeural"

if sys.platform == "win32":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

def connect_to_db():
    try:
        connection = psycopg2.connect(
            dbname="bdvozdepapel",
            user="vozpapeladm",
            password="VozPapelAdm",
            host="172.26.233.101",
            port=5432
        )
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        connection = None
    return connection

def insert_log(ip, image_data, extracted_text):
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO logs (ip, image, extracted_text)
        VALUES (%s, %s, %s);
    """, (ip, image_data, extracted_text))
    connection.commit()
    cursor.close()
    connection.close()

def refine_with_gemini(text):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash-8b")
        response = model.generate_content(
            f"Corrija e melhore a gramática deste texto, não me devolva nenhuma informação além do texto corrigido: {text}"
        )
        return response.text
    except Exception as e:
        print(f"Erro ao chamar a API do Gemini: {e}")
        return text

def generate_audio_with_azure(text, filename):
    try:
        audio_config = speechsdk.audio.AudioOutputConfig(filename=filename)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        result = synthesizer.speak_text_async(text).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"Áudio salvo como {filename}")
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(f"Falha na síntese de fala: {cancellation_details.error_details}")
    except Exception as e:
        print(f"Erro ao gerar áudio com Azure: {e}")

def preprocess_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    binary_img = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 10)
    kernel = np.ones((2, 2), np.uint8)
    binary_img = cv2.erode(binary_img, kernel, iterations=1)
    binary_img = cv2.dilate(binary_img, kernel, iterations=1)
    return binary_img

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

def image_to_audio(image_path, audio_path):
    processed_image = preprocess_image(image_path)
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(processed_image, config=custom_config)
    if text.strip():
        text = refine_with_gemini(text)
        generate_audio_with_azure(text, audio_path)
        
        return text
    else:
        raise ValueError("Nenhum texto encontrado na imagem.")

@app.route('/')
def home():
    return "Aplicação rodando!"

@app.route('/logs', methods=['GET'])
def view_logs():
    connection = connect_to_db()
    if not connection:
        return jsonify({"error": "Erro ao conectar ao banco de dados"}), 500

    cursor = connection.cursor()
    cursor.execute("SELECT id, ip, created_at, LENGTH(image) AS image_size, extracted_text FROM logs;")
    logs = cursor.fetchall()

    logs_list = []
    for log in logs:
        log_data = {
            "id": log[0],
            "ip": log[1],
            "created_at": log[2],
            "image_size": log[3],
            "extracted_text": log[4]
        }
        logs_list.append(log_data)

    cursor.close()
    connection.close()

    return jsonify(logs_list)

@app.route('/image_to_audio', methods=['POST'])
def app_process():
    if 'image' not in request.files:
        return jsonify({"error": "Nenhuma imagem enviada."}), 400

    image = request.files['image']
    image_path = "./temp_image.jpg"
    audio_filename = "output_audio.mp3"
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
        audio_path = temp_audio_file.name

    image.save(image_path)

    ip = request.remote_addr

    try:
        refined_text = image_to_audio(image_path, audio_path)
        encoded_image = image_to_base64(image_path)

        insert_log(ip, encoded_image, refined_text)

    except Exception as e:
        return jsonify({"error": f"Erro ao processar a imagem: {str(e)}"}), 500
    
    response = send_file(audio_path, as_attachment=True, download_name="output_audio.mp3")

    @after_this_request
    def remove_files(response):
        try:
            os.remove(image_path)
            os.remove(audio_path)
            print("Arquivos temporários removidos com sucesso.")
        except Exception as e:
            print(f"Erro ao remover os arquivos temporários: {e}")
        return response

    response.headers["X-Message"] = "Funcionou!"
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
