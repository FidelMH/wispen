# Wispen

Un projet de reconnaissance et synthèse vocale utilisant Azure AI Speech.

## Configuration

### 1. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 2. Configurer les services Azure

#### Azure Speech Service

1. Créez un service Azure Speech dans le portail Azure
2. Récupérez votre clé API et votre région

#### Azure Language Service

1. Créez un service Azure Language dans le portail Azure
2. Récupérez votre clé API et votre endpoint

#### Fichier .env

3. Copiez le fichier `.env.example` vers `.env`
4. Remplissez vos identifiants Azure:

```env
AZURE_SPEECH_KEY=votre_cle_azure
AZURE_SPEECH_REGION=votre_region (ex: westeurope, francecentral)

AZURE_LANGUAGE_KEY=votre_cle_language
AZURE_LANGUAGE_ENDPOINT=votre_endpoint_language (ex: https://votre-resource.cognitiveservices.azure.com/)
```

## Utilisation

### Interface Web (Recommandé)

Lancez l'application web:

```bash
python app.py
```

Puis ouvrez votre navigateur à l'adresse: http://localhost:5000

L'interface propose deux onglets:
1. **Reconnaissance vocale** - Enregistrez depuis le microphone OU uploadez un fichier WAV. Le texte est transcrit puis un résumé est automatiquement généré
2. **Synthèse vocale** - Générez des fichiers WAV à partir de texte

### Générer des fichiers audio de test

Pour tester la reconnaissance vocale sans micro, générez des fichiers WAV de test:

```bash
python generate_test_audio.py
```

Ce script génère 5 fichiers WAV dans le dossier `test_audio/` utilisables pour démonstration.
Chaque fichier contient un texte d'environ 100 mots sur différents thèmes (IA, environnement, technologie, éducation, santé).
Ces fichiers sont créés avec Azure TTS et sont garantis compatibles avec Azure Speech Recognition.

**Avantages:**
- Pas besoin de microphone fonctionnel
- Fichiers WAV parfaitement compatibles avec Azure Speech
- Reproductible pour les démonstrations
- Aucune dépendance externe (pas besoin de FFmpeg)

**Utilisation des fichiers de test:**
Une fois générés, vous pouvez les utiliser dans l'interface web:
1. Lancez l'application web avec `python app.py`
2. Dans l'onglet "Reconnaissance Vocale", cliquez sur "Choisir un fichier WAV"
3. Sélectionnez un des fichiers de test_audio/
4. Cliquez sur "Transcrire le fichier"

## Fonctionnalités

### Reconnaissance vocale
- Reconnaissance en français (fr-FR)
- Support microphone et fichiers audio
- Reconnaissance continue pour textes longs (jusqu'à 60 secondes)
- Gestion complète de tout le contenu audio (pas de limite de phrases)
- **Résumé automatique** du texte transcrit avec Azure AI Language
- Statistiques de compression (nombre de mots original vs résumé)
- Gestion des erreurs et des événements

### Synthèse vocale
- Synthèse en français avec voix neurale (fr-FR-DeniseNeural)
- Export au format WAV
- Qualité audio optimale

## Formats audio supportés

Pour la reconnaissance depuis fichier, utilisez des fichiers WAV avec:
- Format: PCM
- Fréquence d'échantillonnage: 16 kHz ou 8 kHz
- Canaux: Mono
- Bits par échantillon: 16 bits

