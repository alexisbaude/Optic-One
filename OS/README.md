# Smart Glasses OS

Système d'exploitation personnalisé pour lunettes intelligentes basé sur Raspberry Pi 3 avec IA locale (Ollama).

## 🎯 Fonctionnalités

- ✅ **Affichage OLED** - Interface visuelle optimisée
- ✅ **Vision par caméra** - Analyse de scène avec IA
- ✅ **Reconnaissance vocale** - Commandes et transcription (Whisper)
- ✅ **Traduction temps réel** - Texte visible traduit instantanément
- ✅ **IA locale** - Ollama avec modèles légers pour Pi 3
- ✅ **Notifications** - Système de queue intelligent
- ✅ **Gestion des ressources** - Monitoring et throttling automatique

## 🛠️ Matériel Recommandé

### Minimum
- Raspberry Pi 3 (1GB RAM)
- Carte SD 16GB minimum (32GB recommandé)
- Alimentation 5V 2.5A

### Recommandé pour Smart Glasses
- **Écran OLED**: SSD1306 128x64 I2C (~10€)
  - Connexions: VCC, GND, SDA (GPIO 2), SCL (GPIO 3)
  - Adresse I2C: 0x3C ou 0x3D
  
- **Caméra**: 
  - Raspberry Pi Camera Module v2 (meilleure qualité)
  - OU USB Webcam compatible

- **Microphone**: USB ou HAT compatible
  - Exemple: ReSpeaker 2-Mics Pi HAT

### Alternative : Écran OLED
- **SSD1351** 128x128 RGB couleur (meilleure lisibilité)
- **SH1106** 128x64 (compatible avec SSD1306)

## 📦 Installation

### 1. Préparation du Raspberry Pi

```bash
# Téléchargez et flashez Raspberry Pi OS Lite sur SD
# https://www.raspberrypi.com/software/

# Première connexion
ssh pi@raspberrypi.local
# Mot de passe par défaut: raspberry

# Changez le mot de passe
passwd

# Configurez le hostname
sudo raspi-config
# System Options > Hostname > smart-glasses
```

### 2. Installation du système

```bash
# Clonez ou copiez les fichiers
mkdir ~/smart_glasses_os
cd ~/smart_glasses_os

# Copiez tous les fichiers du projet ici

# Rendez le script d'installation exécutable
chmod +x install.sh

# Lancez l'installation
./install.sh
```

Le script va installer :
- Dépendances système (I2C, audio, vidéo)
- Python packages (OpenCV, Whisper, Luma, etc.)
- Ollama (optionnel)
- Modèles IA (llama3.2:1b, llava:7b)

### 3. Configuration matérielle

#### Écran OLED I2C

```bash
# Activez I2C (si pas fait par install.sh)
sudo raspi-config
# Interface Options > I2C > Enable

# Redémarrez
sudo reboot

# Détectez l'adresse de l'écran
i2cdetect -y 1

# Devrait afficher quelque chose comme:
#      0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
# 00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
# ...
# 30: -- -- -- -- -- -- -- -- -- -- -- -- 3c -- -- --
```

#### Caméra

```bash
# Pour Raspberry Pi Camera Module
sudo raspi-config
# Interface Options > Camera > Enable

# Pour USB webcam
ls /dev/video*
# Devrait afficher /dev/video0
```

#### Microphone

```bash
# Listez les devices audio
arecord -l

# Testez l'enregistrement
arecord -d 5 test.wav
aplay test.wav
```

### 4. Configuration

Éditez `config.yaml` selon votre matériel :

```yaml
hardware:
  display:
    type: "SSD1306"        # Votre modèle d'écran
    i2c_address: 0x3C      # Adresse détectée avec i2cdetect
    width: 128
    height: 64
  
  camera:
    device: "/dev/video0"  # Ou 0 pour Pi Camera
    resolution: [640, 480]
    framerate: 15
  
  microphone:
    device: "default"      # Ou nom du device

ai:
  ollama:
    model: "llama3.2:1b"   # Modèle léger pour Pi 3
  
  vision:
    model: "llava:7b"      # Pour analyse d'images
  
  whisper:
    model: "tiny"          # tiny, base, small (tiny = plus rapide)
```

## 🚀 Utilisation

### Mode interactif

```bash
cd ~/smart_glasses_os
source venv/bin/activate
python main.py
```

Commandes disponibles :
- `view` - Analyser la vue actuelle
- `read` - Lire le texte visible
- `trans` - Traduire le texte visible
- `find X` - Chercher un objet X
- `voice` - Commande vocale
- `chat` - Discuter avec l'IA
- `stats` - Statistiques système
- `quit` - Quitter

### Mode démo

```bash
python main.py --demo
```

Démontre toutes les fonctionnalités.

### Mode contrôle vocal

```bash
python main.py --voice-control
```

Dites "lunettes" pour activer, puis :
- "Quelle heure ?"
- "Que vois-tu ?"
- "Lis le texte"
- "Traduis"
- "Cherche [objet]"
- "Aide"

### Mode simulation (sans hardware)

```bash
python main.py --simulation
```

Parfait pour tester sans écran/caméra/micro.

### Démarrage automatique

```bash
# Active le service
sudo systemctl enable smart-glasses
sudo systemctl start smart-glasses

# Vérifier le statut
sudo systemctl status smart-glasses

# Logs
sudo journalctl -u smart-glasses -f
```

## 📁 Structure du projet

```
smart_glasses_os/
├── config.yaml              # Configuration
├── main.py                  # Point d'entrée
├── install.sh               # Script d'installation
│
├── smart_glasses_os.py      # Service principal
├── display_manager.py       # Gestion OLED
├── camera_manager.py        # Vision par caméra
├── voice_recognizer.py      # Reconnaissance vocale
├── ollama_client.py         # Client API Ollama
├── resource_manager.py      # Monitoring ressources
│
└── requirements.txt         # Dépendances Python
```

## 🔧 Optimisation pour Pi 3

Le système est optimisé pour les ressources limitées :

- **CPU** : Throttling automatique si > 80%
- **RAM** : Limite à 700MB, cache intelligent
- **Résolution** : Images réduites (640x480)
- **Modèles IA** : Versions légères (1B params)
- **Framerate** : Limité à 15 FPS

### Conseils de performance

1. **Désactivez les fonctionnalités non utilisées**
   ```yaml
   features:
     voice_recognition: false  # Si pas de micro
     camera_vision: false      # Si pas de caméra
   ```

2. **Réduisez la résolution**
   ```yaml
   camera:
     resolution: [320, 240]    # Plus rapide
   ```

3. **Modèle Whisper plus petit**
   ```yaml
   whisper:
     model: "tiny"  # Le plus rapide
   ```

4. **Overclocking modéré** (optionnel)
   ```bash
   # /boot/config.txt
   arm_freq=1350
   over_voltage=2
   ```

## 🐛 Dépannage

### L'écran ne s'affiche pas

```bash
# Vérifiez I2C
sudo i2cdetect -y 1

# Testez les connexions
# VCC → 3.3V ou 5V
# GND → GND
# SDA → GPIO 2 (Pin 3)
# SCL → GPIO 3 (Pin 5)

# Logs
tail -f /var/log/smart_glasses.log
```

### La caméra ne fonctionne pas

```bash
# Vérifiez la détection
vcgencmd get_camera  # Pi Camera
ls /dev/video*       # USB Webcam

# Testez avec
raspistill -o test.jpg  # Pi Camera
fswebcam test.jpg       # USB Webcam
```

### Ollama ne répond pas

```bash
# Démarrez Ollama
ollama serve

# Testez
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:1b",
  "prompt": "Hello"
}'
```

### Pas assez de RAM

```bash
# Augmentez le swap
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# Ou désactivez des fonctionnalités
```

## 📝 Exemples d'utilisation

### 1. Lecture de panneaux

```python
os_instance.read_text_in_view()
# Affiche: "SORTIE DE SECOURS"
```

### 2. Traduction en temps réel

```python
os_instance.translate_view(target_lang='en')
# "SORTIE DE SECOURS" → "EMERGENCY EXIT"
```

### 3. Recherche d'objets

```python
os_instance.find_object_by_name("clés")
# "Oui, il y a des clés sur la table à droite"
```

### 4. Assistant de navigation

```python
os_instance.camera.get_navigation_hints()
# "Couloir droit devant, porte à gauche dans 3 mètres"
```

## 🔐 Sécurité

- Changez le mot de passe par défaut
- Configurez le firewall si connexion réseau
- Données IA traitées localement (pas de cloud)
- Logs en `/var/log/smart_glasses.log`

## 📄 Licence

Ce projet est fourni à des fins éducatives.

## 🤝 Contribution

Améliorations bienvenues :
- Support d'autres écrans (e-ink, TFT)
- Nouveaux modèles IA
- Optimisations performances
- Nouvelles fonctionnalités

## 📞 Support

Pour questions ou problèmes :
1. Vérifiez les logs
2. Mode simulation pour isoler le problème
3. Testez chaque composant séparément

## 🎓 Ressources

- [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)
- [Luma.OLED](https://luma-oled.readthedocs.io/)
- [Ollama](https://ollama.com/)
- [Whisper](https://github.com/openai/whisper)
- [OpenCV](https://docs.opencv.org/)

---

**Bon développement ! 🤓👓**
