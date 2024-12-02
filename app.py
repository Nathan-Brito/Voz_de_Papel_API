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
import time
import glob

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

TEMP_DIR = "./temp"

if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)
    
def clean_old_temp_files():
    current_time = time.time()
    for temp_file in glob.glob(os.path.join(TEMP_DIR, "audio_*.mp3")):
        file_creation_time = os.path.getctime(temp_file)
        if current_time - file_creation_time > 10:  
            try:
                os.remove(temp_file)
                print(f"Arquivo temporário {temp_file} removido.")
            except Exception as e:
                print(f"Erro ao remover o arquivo {temp_file}: {e}")
                
    for temp_file in glob.glob(os.path.join(TEMP_DIR, "image_*.jpg")):
        file_creation_time = os.path.getctime(temp_file)
        if current_time - file_creation_time > 10:  
            try:
                os.remove(temp_file)
                print(f"Arquivo temporário {temp_file} removido.")
            except Exception as e:
                print(f"Erro ao remover o arquivo {temp_file}: {e}")

def connect_to_db():
    try:
        connection = psycopg2.connect(
            dbname="DBNAME",
            user="DBUSER",
            password="DBKEY",
            host="DBHOST",
            port=5432
        )
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        connection = None
    return connection

def insert_log(ip, image_data, extracted_text):
    connection = connect_to_db()
    if not connection:
        print("Erro ao conectar ao banco de dados.")
        return
    
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO logs (ip, image, extracted_text)
        VALUES (%s, %s, %s);
    """, (ip, psycopg2.Binary(image_data), extracted_text))
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

def is_text_valid(text):
    text = text.strip()
    if len(text) < 10:
        return False

    words = text.split()
    if len(words) < 2:
        return False
    
    alnum_words = sum(1 for word in words if any(char.isalnum() for char in word))
    if alnum_words < len(words) * 0.5:
        return False

    if sum(1 for char in text if not char.isalnum() and char not in " .,!?") > len(text) * 0.3:
        return False

    return True

def image_to_audio(image_path, audio_path):
    processed_image = preprocess_image(image_path)
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(processed_image, config=custom_config)
    if is_text_valid(text):
        text = refine_with_gemini(text)
        generate_audio_with_azure(text, audio_path)
        
        return text
    else:
        raise ValueError("Nenhum texto encontrado na imagem.")
    
def generate_default_audio(audio_path, message):
    try:
        audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_path)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        result = synthesizer.speak_text_async(message).get()
    except Exception as e:
        print(f"Erro ao gerar áudio padrão com Azure: {e}")

@app.route('/')
def home():
    clean_old_temp_files()
    return "Aplicação rodando!"

@app.route('/logs', methods=['POST'])
def execute_query():
    clean_old_temp_files()
    
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Nenhum comando SQL fornecido no corpo da requisição."}), 400
    
    query = data['query']
    
    if not query.strip().lower().startswith("select"):
        return jsonify({"error": "Apenas comandos SELECT são permitidos."}), 403

    connection = connect_to_db()
    if not connection:
        return jsonify({"error": "Erro ao conectar ao banco de dados"}), 500

    try:
        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()

        columns = [desc[0] for desc in cursor.description]
        response_data = [dict(zip(columns, row)) for row in results]

        cursor.close()
        connection.close()
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": f"Erro ao executar a consulta: {str(e)}"}), 500

@app.route('/image_to_audio', methods=['POST'])
def app_process():
    clean_old_temp_files()
    
    if 'image' not in request.files:
        return jsonify({"error": "Nenhuma imagem enviada."}), 400

    image = request.files['image']
    image_path = "./temp/image_temp.jpg"
    ip = request.remote_addr

    with tempfile.NamedTemporaryFile(delete=False,prefix="audio_", suffix=".mp3", dir=TEMP_DIR) as temp_audio_file:
        audio_path = temp_audio_file.name

    image.save(image_path)

    try:
        with open(image_path, "rb") as image_file:
            image_binary = image_file.read()

        try:
            refined_text = image_to_audio(image_path, audio_path)
            insert_log(ip, image_binary, refined_text)
        except ValueError:
            message = "Nenhum texto encontrado na imagem! Tente novamente!"
            generate_default_audio(audio_path, message)
            insert_log(ip, image_binary, message)

    except Exception as e:
        return jsonify({"error": f"Erro ao processar a imagem: {str(e)}"}), 500

    response = send_file(audio_path, as_attachment=True, download_name="output_audio.mp3")

    response.headers["X-Message"] = "Funcionou!"
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))