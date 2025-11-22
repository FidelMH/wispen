# Wispen

Un projet de reconnaissance et synthèse vocale utilisant Azure AI Speech.

## Configuration

### 1. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 2. Configurer les services Azure

> ⚠️ **IMPORTANT - Sécurité des clés API**
>
> **ATTENTION :** Ne JAMAIS commiter vos vraies clés API dans le repository Git !
> - Le fichier `.env` doit rester **LOCAL** et ne jamais être partagé
> - Utilisez uniquement le fichier `.env.example` comme template
> - Vérifiez que `.env` est bien présent dans `.gitignore`
> - Si vos clés ont été exposées publiquement, **régénérez-les immédiatement** dans le portail Azure

#### Azure Speech Service

1. Créez un service Azure Speech dans le portail Azure
2. Récupérez votre clé API et votre région

#### Azure Language Service

1. Créez un service Azure Language dans le portail Azure
2. Récupérez votre clé API et votre endpoint

#### Fichier .env

3. **Créez votre fichier de configuration local :**
   ```bash
   cp .env.example .env
   ```

4. **Remplissez vos PROPRES identifiants Azure dans le fichier `.env` :**

   ```env
   AZURE_SPEECH_KEY=votre_cle_azure_personnelle
   AZURE_SPEECH_REGION=votre_region (ex: westeurope, francecentral)

   AZURE_LANGUAGE_KEY=votre_cle_language_personnelle
   AZURE_LANGUAGE_ENDPOINT=votre_endpoint_language (ex: https://votre-resource.cognitiveservices.azure.com/)
   ```

   > 📝 **Note :** Les valeurs dans `.env.example` sont uniquement des exemples de format.
   > Vous devez les remplacer par vos propres clés obtenues depuis le portail Azure.

## Utilisation

### Interface Web (Recommandé)

Lancez l'application web:

```bash
python app.py
```

Puis ouvrez votre navigateur à l'adresse: http://localhost:5000

L'interface propose deux onglets:
1. **Reconnaissance vocale** - Enregistrez depuis le microphone, uploadez un fichier WAV ou utilisez un fichier de test. Le texte est transcrit puis un résumé est automatiquement généré
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
Une fois générés, vous pouvez les utiliser dans l'interface web de deux façons:

**Option 1 - Accès direct depuis l'interface (Recommandé):**
1. Lancez l'application web avec `python app.py`
2. Dans l'onglet "Reconnaissance Vocale", trouvez la section "Fichiers de test disponibles"
3. Sélectionnez un fichier dans la liste déroulante (Intelligence Artificielle, Environnement, Technologie, Éducation, ou Santé)
4. Les informations du fichier (thème et taille) s'affichent automatiquement
5. Cliquez sur "Transcrire le fichier de test"
6. La transcription et le résumé s'affichent automatiquement

**Option 2 - Upload manuel:**
1. Dans l'onglet "Reconnaissance Vocale", cliquez sur "Choisir un fichier WAV"
2. Naviguez vers le dossier test_audio/ et sélectionnez un fichier
3. Cliquez sur "Transcrire le fichier"

## Fonctionnalités

### Reconnaissance vocale
- Reconnaissance en français (fr-FR)
- Support microphone et fichiers audio
- **Accès direct aux fichiers de test** depuis l'interface (liste déroulante avec informations)
- Reconnaissance continue pour textes longs (jusqu'à 60 secondes)
- Gestion complète de tout le contenu audio (pas de limite de phrases)
- **Résumé automatique** du texte transcrit avec Azure AI Language
- Statistiques de compression (nombre de mots original vs résumé)
- Gestion des erreurs et des événements

### Synthèse vocale
- Synthèse en français avec voix neurale (fr-FR-DeniseNeural)
- Export au format WAV
- Qualité audio optimale

## 🔒 Bonnes pratiques de sécurité

### Protection des clés API

- ✅ **TOUJOURS** utiliser des variables d'environnement (fichier `.env`)
- ✅ **VÉRIFIER** que `.env` est dans `.gitignore` avant chaque commit
- ✅ **NE JAMAIS** hardcoder les clés directement dans le code
- ✅ **UTILISER** des clés différentes pour les environnements de développement et production
- ✅ **RÉGÉNÉRER** immédiatement vos clés si elles ont été exposées publiquement

### Rotation des clés

Si vous suspectez qu'une clé a été compromise :
1. Connectez-vous au [portail Azure](https://portal.azure.com)
2. Accédez à votre ressource Azure Speech / Language
3. Dans "Clés et point de terminaison", cliquez sur "Régénérer la clé"
4. Mettez à jour votre fichier `.env` local avec la nouvelle clé

### Vérification de sécurité

Avant de commiter du code, vérifiez toujours :
```bash
# Vérifier que .env n'est pas tracé par Git
git status

# Le fichier .env ne doit PAS apparaître dans la liste
# S'il apparaît, ajoutez-le immédiatement à .gitignore
```

## Formats audio supportés

Pour la reconnaissance depuis fichier, utilisez des fichiers WAV avec:
- Format: PCM
- Fréquence d'échantillonnage: 16 kHz ou 8 kHz
- Canaux: Mono
- Bits par échantillon: 16 bits

