from flask import Flask, request, jsonify, send_file
import os
from dotenv import load_dotenv
import cv2
import pytesseract
import google.generativeai as genai
import azure.cognitiveservices.speech as speechsdk
import numpy as np


app = Flask(__name__)


load_dotenv()


genai.configure(api_key=os.getenv("GEMINI_KEY"))

subscription_key = os.getenv("AZURE_KEY")
region = os.getenv("AZURE_REGION")
speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=region)
speech_config.speech_synthesis_voice_name = "pt-BR-FranciscaNeural"

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


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

def image_to_audio(image_path, audio_path):
    processed_image = preprocess_image(image_path)

    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(processed_image, config=custom_config)

    if text.strip():
        text = refine_with_gemini(text)
        generate_audio_with_azure(text, audio_path)
    else:
        raise ValueError("Nenhum texto encontrado na imagem.")

@app.route('/')
def home():
    return "Aplicação rodando!"

@app.route('/image_to_audio', methods=['POST'])
def app_process():
    if 'image' not in request.files:
        return jsonify({"error": "Nenhuma imagem enviada."}), 400

    image = request.files['image']
    image_path = "./temp_image.jpg"
    audio_path = "./output_audio.mp3"

    
    image.save(image_path)


    try:
        image_to_audio(image_path, audio_path)
    except Exception as e:
        return jsonify({"error": f"Erro ao processar a imagem: {str(e)}"}), 500
    
    response = send_file(audio_path, as_attachment=True, download_name="output_audio.mp3")

    os.remove(image_path)
    os.remove(audio_path)

    response.headers["X-Message"] = "Funcionou!"
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
