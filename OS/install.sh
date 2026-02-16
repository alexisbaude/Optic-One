#!/bin/bash
# Script d'installation pour Smart Glasses OS
# Optimisé pour Raspberry Pi 3

echo "=== Smart Glasses OS - Installation ==="
echo ""

# Vérifie qu'on est sur Raspberry Pi OS
if [ ! -f /etc/rpi-issue ]; then
    echo "⚠️  Warning: This doesn't appear to be Raspberry Pi OS"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "1. Mise à jour du système..."
sudo apt update
sudo apt upgrade -y

echo ""
echo "2. Installation des dépendances système..."
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7 \
    libtiff5 \
    libatlas-base-dev \
    portaudio19-dev \
    ffmpeg \
    i2c-tools \
    python3-smbus

# Active I2C pour l'écran OLED
echo ""
echo "3. Configuration I2C..."
if ! grep -q "^i2c-dev" /etc/modules; then
    echo "i2c-dev" | sudo tee -a /etc/modules
fi

# Active I2C dans config.txt
if ! grep -q "^dtparam=i2c_arm=on" /boot/config.txt; then
    echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt
fi

# Donne les permissions I2C à l'utilisateur
sudo usermod -a -G i2c $USER

echo ""
echo "4. Création de l'environnement virtuel Python..."
cd ~/smart_glasses_os
python3 -m venv venv
source venv/bin/activate

echo ""
echo "5. Installation des packages Python..."

# PIL/Pillow pour les images
pip install --upgrade pip
pip install Pillow

# Luma.OLED pour l'écran
pip install luma.oled

# OpenCV pour la caméra (version optimisée pour Pi)
pip install opencv-python-headless

# PyAudio pour le microphone
pip install pyaudio

# Requests pour l'API
pip install requests

# PyYAML pour la config
pip install pyyaml

# PSUtil pour monitoring
pip install psutil

echo ""
echo "6. Installation de Whisper (pour reconnaissance vocale)..."
echo "⚠️  Note: Whisper peut être lourd pour Pi 3."
echo "   Modèle 'tiny' recommandé (défini dans config.yaml)"
read -p "Installer Whisper? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pip install openai-whisper
else
    echo "Skipping Whisper - voice recognition will be in simulation mode"
fi

echo ""
echo "7. Installation d'Ollama..."
echo "Ollama doit être installé séparément:"
echo ""
echo "  curl -fsSL https://ollama.com/install.sh | sh"
echo ""
read -p "Installer Ollama maintenant? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    curl -fsSL https://ollama.com/install.sh | sh
    
    echo ""
    echo "Téléchargement du modèle Llama 3.2 (1B)..."
    ollama pull llama3.2:1b
    
    echo ""
    echo "Téléchargement du modèle vision LLaVA (7B)..."
    read -p "Télécharger aussi le modèle vision? (recommandé, ~4GB) (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ollama pull llava:7b
    fi
fi

echo ""
echo "8. Configuration du service systemd..."
cat > smart-glasses.service << EOF
[Unit]
Description=Smart Glasses OS
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/smart_glasses_os
Environment="PATH=/home/$USER/smart_glasses_os/venv/bin"
ExecStart=/home/$USER/smart_glasses_os/venv/bin/python main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo mv smart-glasses.service /etc/systemd/system/
sudo systemctl daemon-reload

echo ""
echo "9. Vérification de la configuration..."

# Test I2C
echo "Détection des périphériques I2C:"
i2cdetect -y 1

echo ""
echo "=== Installation terminée! ==="
echo ""
echo "Prochaines étapes:"
echo ""
echo "1. Redémarrer le Pi pour activer I2C:"
echo "   sudo reboot"
echo ""
echo "2. Après le redémarrage, démarrer Ollama:"
echo "   ollama serve &"
echo ""
echo "3. Tester le système:"
echo "   cd ~/smart_glasses_os"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "4. Activer le démarrage automatique (optionnel):"
echo "   sudo systemctl enable smart-glasses"
echo "   sudo systemctl start smart-glasses"
echo ""
echo "Configuration de votre écran OLED:"
echo "  - Éditez config.yaml pour configurer l'adresse I2C"
echo "  - Adresse commune: 0x3C ou 0x3D"
echo "  - Détectez avec: i2cdetect -y 1"
echo ""
