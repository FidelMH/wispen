// Variables globales
let mediaRecorder;
let audioChunks = [];
let audioBlob;

// Gestion des onglets
document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    initializeRecognition();
    initializeSynthesis();
});

function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');

            // Désactiver tous les onglets
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Activer l'onglet sélectionné
            button.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
        });
    });
}

// ==================== RECONNAISSANCE VOCALE ====================

function initializeRecognition() {
    const startBtn = document.getElementById('startRecord');
    const stopBtn = document.getElementById('stopRecord');
    const copyBtn = document.getElementById('copyRecognized');
    const copySummaryBtn = document.getElementById('copySummaryRecog');
    const clearBtn = document.getElementById('clearRecognized');
    const fileInput = document.getElementById('audioFileInput');
    const uploadBtn = document.getElementById('uploadAudioBtn');

    startBtn.addEventListener('click', startRecording);
    stopBtn.addEventListener('click', stopRecording);
    copyBtn.addEventListener('click', copyRecognizedText);
    copySummaryBtn.addEventListener('click', copyRecognizedSummary);
    clearBtn.addEventListener('click', clearRecognizedText);

    // Activer le bouton d'upload quand un fichier est sélectionné
    fileInput.addEventListener('change', () => {
        uploadBtn.disabled = !fileInput.files.length;
    });

    uploadBtn.addEventListener('click', uploadAudioFile);
}

async function startRecording() {
    const startBtn = document.getElementById('startRecord');
    const stopBtn = document.getElementById('stopRecord');
    const statusEl = document.getElementById('recordStatus');

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.addEventListener('dataavailable', event => {
            audioChunks.push(event.data);
        });

        mediaRecorder.addEventListener('stop', async () => {
            audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            await sendAudioForRecognition(audioBlob);
        });

        mediaRecorder.start();

        // Mettre à jour l'interface
        startBtn.disabled = true;
        stopBtn.disabled = false;
        statusEl.textContent = 'Enregistrement en cours...';
        statusEl.className = 'status recording';

    } catch (error) {
        console.error('Erreur d\'accès au microphone:', error);
        statusEl.textContent = 'Erreur: Impossible d\'accéder au microphone';
        statusEl.className = 'status';
    }
}

function stopRecording() {
    const startBtn = document.getElementById('startRecord');
    const stopBtn = document.getElementById('stopRecord');
    const statusEl = document.getElementById('recordStatus');

    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();

        // Arrêter tous les tracks audio
        mediaRecorder.stream.getTracks().forEach(track => track.stop());

        // Mettre à jour l'interface
        startBtn.disabled = false;
        stopBtn.disabled = true;
        statusEl.textContent = 'Traitement en cours...';
        statusEl.className = 'status processing';
    }
}

async function sendAudioForRecognition(audioBlob) {
    const statusEl = document.getElementById('recordStatus');
    const textArea = document.getElementById('recognizedText');

    try {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');

        const response = await fetch('/api/recognize', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            textArea.value = data.text;
            statusEl.textContent = 'Reconnaissance réussie';
            statusEl.className = 'status success';

            // Générer automatiquement le résumé
            await generateSummaryForRecognition(data.text);
        } else {
            statusEl.textContent = `Erreur: ${data.error}`;
            statusEl.className = 'status';
        }

    } catch (error) {
        console.error('Erreur lors de la reconnaissance:', error);
        statusEl.textContent = 'Erreur de connexion au serveur';
        statusEl.className = 'status';
    }

    // Réinitialiser le statut après 3 secondes
    setTimeout(() => {
        if (statusEl.className === 'status success' || statusEl.className === 'status') {
            statusEl.textContent = 'Prêt';
            statusEl.className = 'status';
        }
    }, 3000);
}

function copyRecognizedText() {
    const textArea = document.getElementById('recognizedText');
    textArea.select();
    document.execCommand('copy');

    const statusEl = document.getElementById('recordStatus');
    statusEl.textContent = 'Texte copié !';
    statusEl.className = 'status success';

    setTimeout(() => {
        statusEl.textContent = 'Prêt';
        statusEl.className = 'status';
    }, 2000);
}

function copyRecognizedSummary() {
    const summaryArea = document.getElementById('recognizedSummary');
    const statusEl = document.getElementById('recordStatus');

    if (!summaryArea.value) {
        statusEl.textContent = 'Aucun résumé à copier';
        statusEl.className = 'status';
        return;
    }

    summaryArea.select();
    document.execCommand('copy');

    statusEl.textContent = 'Résumé copié !';
    statusEl.className = 'status success';

    setTimeout(() => {
        statusEl.textContent = 'Prêt';
        statusEl.className = 'status';
    }, 2000);
}

function clearRecognizedText() {
    document.getElementById('recognizedText').value = '';
    document.getElementById('recognizedSummary').value = '';
    document.getElementById('recognitionStats').style.display = 'none';
}

async function generateSummaryForRecognition(text) {
    const statusEl = document.getElementById('recordStatus');
    const summaryArea = document.getElementById('recognizedSummary');
    const statsDiv = document.getElementById('recognitionStats');

    if (!text || text.trim().length === 0) {
        return;
    }

    statusEl.textContent = 'Génération du résumé...';
    statusEl.className = 'status processing';
    statsDiv.style.display = 'none';

    try {
        const response = await fetch('/api/summarize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text })
        });

        const data = await response.json();

        if (response.ok) {
            summaryArea.value = data.summary;

            // Afficher les statistiques
            document.getElementById('recogOriginalLength').textContent =
                `Texte original: ${data.original_length} mots`;
            document.getElementById('recogSummaryLength').textContent =
                `Résumé: ${data.summary_length} mots`;
            statsDiv.style.display = 'flex';

            statusEl.textContent = 'Transcription et résumé terminés';
            statusEl.className = 'status success';
        } else {
            summaryArea.value = 'Erreur lors de la génération du résumé';
            statusEl.textContent = 'Reconnaissance réussie, résumé échoué';
            statusEl.className = 'status';
        }
    } catch (error) {
        console.error('Erreur lors du résumé:', error);
        summaryArea.value = 'Impossible de générer le résumé';
    }

    // Réinitialiser le statut après 3 secondes
    setTimeout(() => {
        if (statusEl.className === 'status success' || statusEl.className === 'status') {
            statusEl.textContent = 'Prêt';
            statusEl.className = 'status';
        }
    }, 3000);
}

async function uploadAudioFile() {
    const fileInput = document.getElementById('audioFileInput');
    const uploadBtn = document.getElementById('uploadAudioBtn');
    const statusEl = document.getElementById('recordStatus');
    const textArea = document.getElementById('recognizedText');

    const file = fileInput.files[0];

    if (!file) {
        statusEl.textContent = 'Veuillez sélectionner un fichier';
        statusEl.className = 'status';
        return;
    }

    // Vérifier que c'est un fichier WAV
    if (!file.name.toLowerCase().endsWith('.wav')) {
        statusEl.textContent = 'Erreur: Seuls les fichiers WAV sont acceptés';
        statusEl.className = 'status';
        return;
    }

    uploadBtn.disabled = true;
    statusEl.textContent = 'Traitement en cours...';
    statusEl.className = 'status processing';

    try {
        const formData = new FormData();
        formData.append('audio', file);

        const response = await fetch('/api/recognize', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            textArea.value = data.text;
            statusEl.textContent = 'Reconnaissance réussie';
            statusEl.className = 'status success';

            // Réinitialiser le sélecteur de fichier
            fileInput.value = '';
            uploadBtn.disabled = true;

            // Générer automatiquement le résumé
            await generateSummaryForRecognition(data.text);
        } else {
            statusEl.textContent = `Erreur: ${data.error}`;
            statusEl.className = 'status';
        }

    } catch (error) {
        console.error('Erreur lors de la reconnaissance:', error);
        statusEl.textContent = 'Erreur de connexion au serveur';
        statusEl.className = 'status';
    } finally {
        uploadBtn.disabled = false;

        // Réinitialiser le statut après 3 secondes
        setTimeout(() => {
            if (statusEl.className === 'status success' || statusEl.className === 'status') {
                statusEl.textContent = 'Prêt';
                statusEl.className = 'status';
            }
        }, 3000);
    }
}

// ==================== SYNTHÈSE VOCALE ====================

function initializeSynthesis() {
    const synthesizeBtn = document.getElementById('synthesizeBtn');
    synthesizeBtn.addEventListener('click', synthesizeText);
}

async function synthesizeText() {
    const textArea = document.getElementById('textToSynthesize');
    const statusEl = document.getElementById('synthesisStatus');
    const synthesizeBtn = document.getElementById('synthesizeBtn');

    const text = textArea.value.trim();

    if (!text) {
        statusEl.textContent = 'Veuillez saisir du texte';
        statusEl.className = 'status';
        return;
    }

    // Désactiver le bouton et afficher le statut
    synthesizeBtn.disabled = true;
    statusEl.textContent = 'Génération en cours...';
    statusEl.className = 'status processing';

    try {
        const response = await fetch('/api/synthesize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text })
        });

        if (response.ok) {
            const audioBlob = await response.blob();

            // Télécharger automatiquement le fichier WAV
            const url = URL.createObjectURL(audioBlob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'wispen_output.wav';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            statusEl.textContent = 'Fichier WAV téléchargé avec succès';
            statusEl.className = 'status success';

        } else {
            const data = await response.json();
            statusEl.textContent = `Erreur: ${data.error}`;
            statusEl.className = 'status';
        }

    } catch (error) {
        console.error('Erreur lors de la synthèse:', error);
        statusEl.textContent = 'Erreur de connexion au serveur';
        statusEl.className = 'status';
    } finally {
        synthesizeBtn.disabled = false;

        // Réinitialiser le statut après 3 secondes
        setTimeout(() => {
            if (statusEl.className === 'status success' || statusEl.className === 'status') {
                statusEl.textContent = 'Prêt';
                statusEl.className = 'status';
            }
        }, 3000);
    }
}
