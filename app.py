"""
Application Flask pour Wispen - Reconnaissance et synthèse vocale
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import io
from datetime import datetime

load_dotenv()

app = Flask(__name__)

# Configuration Azure Speech
SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")

# Configuration Azure Language
LANGUAGE_KEY = os.getenv("AZURE_LANGUAGE_KEY")
LANGUAGE_ENDPOINT = os.getenv("AZURE_LANGUAGE_ENDPOINT")

# Créer le dossier audio s'il n'existe pas
AUDIO_FOLDER = 'audio'
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)


@app.route('/')
def index():
    """Page principale"""
    return render_template('index.html')


@app.route('/api/synthesize', methods=['POST'])
def synthesize():
    """
    API pour la synthèse vocale
    Reçoit du texte et retourne un fichier audio WAV
    """
    try:
        data = request.get_json()
        text = data.get('text', '')

        if not text:
            return jsonify({'error': 'Texte manquant'}), 400

        if not SPEECH_KEY or not SPEECH_REGION:
            return jsonify({'error': 'Configuration Azure manquante'}), 500

        # Configuration Azure Speech
        speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
        speech_config.speech_synthesis_language = "fr-FR"
        speech_config.speech_synthesis_voice_name = "fr-FR-DeniseNeural"

        # Synthèse en mémoire (audio_config=None pour récupérer les données audio brutes)
        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=None
        )

        result = speech_synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            # Retourner l'audio comme fichier
            audio_data = result.audio_data
            return send_file(
                io.BytesIO(audio_data),
                mimetype='audio/wav',
                as_attachment=True,
                download_name='output.wav'
            )
        else:
            cancellation_details = result.cancellation_details
            return jsonify({
                'error': f'Erreur de synthèse: {cancellation_details.error_details}'
            }), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/recognize', methods=['POST'])
def recognize():
    """
    API pour la reconnaissance vocale
    Reçoit un fichier audio et retourne le texte reconnu
    """
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'Fichier audio manquant'}), 400

        audio_file = request.files['audio']

        if not SPEECH_KEY or not SPEECH_REGION:
            return jsonify({'error': 'Configuration Azure manquante'}), 500

        # Générer un nom de fichier avec timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'recording_{timestamp}.wav'
        audio_path = os.path.join(AUDIO_FOLDER, filename)

        # Sauvegarder le fichier dans le dossier audio
        audio_file.save(audio_path)

        # Configuration Azure Speech
        speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
        speech_config.speech_recognition_language = "fr-FR"

        audio_config = speechsdk.audio.AudioConfig(filename=audio_path)
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            audio_config=audio_config
        )

        # Utiliser la reconnaissance continue pour les textes longs
        all_results = []
        done = False

        def handle_recognized(evt):
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                all_results.append(evt.result.text)

        def handle_session_stopped(evt):
            nonlocal done
            done = True

        # Connecter les événements
        speech_recognizer.recognized.connect(handle_recognized)
        speech_recognizer.session_stopped.connect(handle_session_stopped)
        speech_recognizer.canceled.connect(handle_session_stopped)

        # Démarrer la reconnaissance continue
        speech_recognizer.start_continuous_recognition_async()

        # Attendre que la reconnaissance soit terminée (timeout de 60 secondes)
        import time
        timeout = 60
        elapsed = 0
        while not done and elapsed < timeout:
            time.sleep(0.1)
            elapsed += 0.1

        # Arrêter la reconnaissance
        speech_recognizer.stop_continuous_recognition_async()

        if all_results:
            # Combiner tous les résultats
            full_text = ' '.join(all_results)
            return jsonify({
                'text': full_text,
                'filename': filename
            })
        else:
            return jsonify({'error': 'Aucune parole reconnue'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/summarize', methods=['POST'])
def summarize():
    """
    API pour le résumé de texte
    Reçoit un texte et retourne un résumé
    """
    try:
        data = request.get_json()
        text = data.get('text', '').strip()

        if not text:
            return jsonify({'error': 'Texte manquant'}), 400

        # Vérifier la longueur minimale du texte (au moins 3 phrases)
        sentences_count = text.count('.') + text.count('!') + text.count('?')
        if sentences_count < 3:
            return jsonify({'error': 'Le texte doit contenir au moins 3 phrases pour être résumé'}), 400

        if not LANGUAGE_KEY or not LANGUAGE_ENDPOINT:
            return jsonify({'error': 'Configuration Azure Language manquante dans .env'}), 500

        # Créer le client Azure Language
        credential = AzureKeyCredential(LANGUAGE_KEY)
        text_analytics_client = TextAnalyticsClient(
            endpoint=LANGUAGE_ENDPOINT,
            credential=credential
        )

        # Préparer le document
        documents = [text]

        # Utiliser le résumé extractif
        print(f"Tentative de résumé pour {len(text)} caractères, {len(text.split())} mots")
        poller = text_analytics_client.begin_extract_summary(documents, language="fr")
        summary_results = poller.result()

        summary_sentences = []
        for result in summary_results:
            if result.kind == "ExtractiveSummarization":
                print(f"Résumé extractif: {len(result.sentences)} phrases trouvées")
                for sentence in result.sentences:
                    summary_sentences.append(sentence.text)
            elif result.is_error:
                error_msg = f'Azure Error: {result.error.message}'
                print(f"Erreur Azure: {error_msg}")
                return jsonify({'error': error_msg}), 500

        if summary_sentences:
            summary_text = ' '.join(summary_sentences)
            return jsonify({
                'summary': summary_text,
                'original_length': len(text.split()),
                'summary_length': len(summary_text.split())
            })
        else:
            return jsonify({'error': 'Texte trop court ou aucune phrase extraite'}), 400

    except Exception as e:
        print(f"Exception lors du résumé: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'{type(e).__name__}: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
