"""
Script pour générer des fichiers audio de test pour Wispen
Ces fichiers sont générés avec Azure TTS et sont garantis compatibles avec Azure Speech Recognition
"""

import azure.cognitiveservices.speech as speechsdk
import os
from dotenv import load_dotenv

load_dotenv()

SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")

# Créer le dossier de test s'il n'existe pas
TEST_FOLDER = 'test_audio'
if not os.path.exists(TEST_FOLDER):
    os.makedirs(TEST_FOLDER)

# Phrases de test à générer (environ 100 mots chacune)
test_phrases = [
    ("test_intelligence_artificielle.wav",
     "L'intelligence artificielle transforme notre monde de manière profonde et continue. "
     "Elle permet aux machines d'apprendre, de raisonner et de prendre des décisions complexes. "
     "Les applications sont nombreuses dans tous les domaines de notre vie quotidienne. "
     "De la reconnaissance vocale à la conduite autonome, en passant par les assistants virtuels et les systèmes de recommandation, "
     "l'IA est partout autour de nous. Les entreprises investissent massivement dans cette technologie prometteuse. "
     "Les chercheurs développent constamment de nouveaux algorithmes et modèles plus performants. "
     "Cependant, il est essentiel de réfléchir aux implications éthiques de ces avancées technologiques."),

    ("test_environnement.wav",
     "La protection de l'environnement est devenue une priorité mondiale absolue. "
     "Le changement climatique menace notre planète et toutes les espèces vivantes qui l'habitent. "
     "Les émissions de gaz à effet de serre continuent d'augmenter dangereusement. "
     "Les températures moyennes s'élèvent progressivement année après année. "
     "Les glaciers fondent à une vitesse alarmante dans toutes les régions du monde. "
     "Les océans deviennent plus acides et menacent la biodiversité marine. "
     "Il est urgent d'adopter des énergies renouvelables et des modes de vie durables. "
     "Chacun peut contribuer à préserver notre belle planète pour les générations futures."),

    ("test_technologie.wav",
     "Les technologies numériques évoluent à une vitesse impressionnante et révolutionnent nos sociétés. "
     "Internet a complètement transformé notre façon de communiquer et d'accéder à l'information. "
     "Les smartphones sont devenus des outils indispensables dans notre quotidien moderne. "
     "Les réseaux sociaux connectent des milliards de personnes à travers le monde entier. "
     "Le cloud computing permet de stocker et traiter des quantités massives de données. "
     "La réalité virtuelle et augmentée offrent des expériences immersives totalement nouvelles. "
     "L'Internet des objets connecte nos appareils et automatise nos maisons intelligentes. "
     "Ces innovations technologiques créent de nouvelles opportunités mais aussi de nouveaux défis."),

    ("test_education.wav",
     "L'éducation est la clé du développement personnel et professionnel de chaque individu. "
     "Elle ouvre les portes de la connaissance et développe l'esprit critique des apprenants. "
     "Les méthodes pédagogiques évoluent avec l'intégration des outils numériques modernes. "
     "L'apprentissage en ligne permet d'accéder aux cours depuis n'importe quel endroit. "
     "Les plateformes éducatives proposent des contenus variés et adaptés à tous les niveaux. "
     "Les enseignants utilisent des technologies innovantes pour rendre leurs cours plus interactifs. "
     "La formation continue devient essentielle dans un monde en constante mutation. "
     "Investir dans l'éducation, c'est investir dans l'avenir de notre société tout entière."),

    ("test_sante.wav",
     "La santé est notre bien le plus précieux et mérite toute notre attention quotidienne. "
     "Une alimentation équilibrée et variée est essentielle pour maintenir notre forme physique. "
     "L'activité physique régulière renforce notre système immunitaire et notre bien-être général. "
     "Le sommeil de qualité permet à notre corps de se régénérer et se réparer. "
     "La gestion du stress est cruciale pour préserver notre santé mentale et émotionnelle. "
     "Les avancées médicales permettent de traiter de nombreuses maladies autrefois incurables. "
     "La prévention reste le meilleur moyen d'éviter de nombreux problèmes de santé. "
     "Prendre soin de soi aujourd'hui, c'est s'assurer un avenir en meilleure santé."),
]


def generate_test_files():
    """Génère les fichiers audio de test"""

    if not SPEECH_KEY or not SPEECH_REGION:
        print("Erreur: AZURE_SPEECH_KEY et AZURE_SPEECH_REGION doivent être définis dans .env")
        return False

    print("Génération des fichiers audio de test...")
    print(f"Dossier de destination: {TEST_FOLDER}/\n")

    # Configuration Azure Speech
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    speech_config.speech_synthesis_language = "fr-FR"
    speech_config.speech_synthesis_voice_name = "fr-FR-DeniseNeural"

    success_count = 0

    for filename, text in test_phrases:
        output_path = os.path.join(TEST_FOLDER, filename)

        # Configuration audio (fichier)
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)

        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config
        )

        print(f"Génération de '{filename}'...")
        print(f"  Texte: \"{text}\"")

        result = speech_synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"  [OK] Succes\n")
            success_count += 1
        else:
            print(f"  [ERREUR] Echec: {result.cancellation_details.error_details}\n")

    print(f"\n{'='*60}")
    print(f"Résumé: {success_count}/{len(test_phrases)} fichiers générés avec succès")
    print(f"{'='*60}")

    if success_count > 0:
        print(f"\nLes fichiers ont été générés dans le dossier '{TEST_FOLDER}/'")
        print("Vous pouvez maintenant les utiliser pour tester la reconnaissance vocale.")

    return success_count == len(test_phrases)


if __name__ == "__main__":
    print("="*60)
    print("Générateur de fichiers audio de test pour Wispen")
    print("="*60)
    print()

    success = generate_test_files()

    if success:
        print("\n[OK] Tous les fichiers ont ete generes avec succes !")
    else:
        print("\n[ATTENTION] Certains fichiers n'ont pas pu etre generes.")
        print("Verifiez votre configuration Azure dans le fichier .env")
