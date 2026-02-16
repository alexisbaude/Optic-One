# 🚀 Guide de Démarrage Rapide

## Installation Express (30 minutes)

### 1. Flasher Raspberry Pi OS (10 min)

1. Téléchargez [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Choisissez **Raspberry Pi OS Lite (64-bit)**
3. Configurez WiFi et SSH dans les options avancées
4. Flashez sur carte SD (16GB min)
5. Insérez et démarrez le Pi

### 2. Connexion SSH (2 min)

```bash
# Depuis votre ordinateur
ssh pi@raspberrypi.local

# Mot de passe par défaut: raspberry
# CHANGEZ-LE immédiatement!
passwd
```

### 3. Installation automatique (15 min)

```bash
# Créez le dossier
mkdir ~/smart_glasses_os
cd ~/smart_glasses_os

# Copiez les fichiers du projet ici (via scp, git, ou USB)

# Lancez l'installation
chmod +x install.sh
./install.sh

# Suivez les prompts:
# - Installer Whisper? Oui (pour voix)
# - Installer Ollama? Oui (pour IA)
# - Télécharger modèle vision? Oui (pour caméra)
```

### 4. Premier test (3 min)

```bash
# Redémarrez pour activer I2C
sudo reboot

# Reconnectez-vous
ssh pi@raspberrypi.local

# Activez l'environnement virtuel
cd ~/smart_glasses_os
source venv/bin/activate

# Lancez en mode simulation (sans hardware)
python main.py --simulation --demo

# Vous devriez voir la démo s'exécuter dans les logs
```

## 🔌 Connexion du matériel

### Écran OLED SSD1306 (I2C)

```
OLED Pin → Raspberry Pi
-----------------------
VCC      → Pin 1 (3.3V) ou Pin 2 (5V)
GND      → Pin 6 (GND)
SDA      → Pin 3 (GPIO 2)
SCL      → Pin 5 (GPIO 3)
```

**Vérification :**
```bash
i2cdetect -y 1
# Devrait afficher 3c ou 3d
```

### Caméra Raspberry Pi

1. Connectez le ruban à la prise CSI (entre HDMI et USB)
2. Activez :
```bash
sudo raspi-config
# Interface Options > Camera > Enable
sudo reboot
```

### Microphone USB

Branchez simplement sur port USB.

**Vérification :**
```bash
arecord -l
# Devrait lister votre micro
```

## ⚙️ Configuration minimale

Éditez `config.yaml` :

```yaml
hardware:
  display:
    i2c_address: 0x3C  # Changez si nécessaire (3d)
  
  camera:
    device: "/dev/video0"  # Ou 0 pour Pi Camera
  
  microphone:
    device: "default"

ai:
  ollama:
    model: "llama3.2:1b"  # Modèle le plus léger
  
  whisper:
    model: "tiny"  # Le plus rapide
```

## 🎮 Premiers tests

### Test 1: Affichage

```bash
python main.py --demo
```

Vous devriez voir :
- Texte de bienvenue
- Notification
- Barre de progression

### Test 2: Caméra (si connectée)

```bash
python main.py
# À l'invite:
glasses> view
```

L'IA décrit ce que voit la caméra.

### Test 3: Reconnaissance vocale

```bash
python main.py --voice-control

# Dites "lunettes" puis une commande:
# - "Quelle heure ?"
# - "Que vois-tu ?"
```

### Test 4: Mode interactif complet

```bash
python main.py

# Essayez:
glasses> stats     # État du système
glasses> view      # Analyse de vue
glasses> read      # Lecture de texte
glasses> trans     # Traduction
glasses> chat      # Discussion IA
```

## 🐛 Problèmes courants

### "Cannot connect to Ollama"

```bash
# Démarrez Ollama
ollama serve &

# Vérifiez qu'il tourne
curl http://localhost:11434
```

### "Display not found"

```bash
# Vérifiez I2C
sudo i2cdetect -y 1

# Si vide, vérifiez les câbles et:
sudo raspi-config
# Interface Options > I2C > Enable
sudo reboot
```

### "Camera not detected"

```bash
# Pour Pi Camera:
vcgencmd get_camera

# Pour USB:
ls /dev/video*
```

### Système lent / crashes

```bash
# Augmentez le swap
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

## 📱 Utilisations pratiques

### 1. Lecteur de panneaux pour malvoyants

```python
# Mode lecture continue
python main.py --voice-control

# Dites "lunettes" puis "lis le texte"
# L'affichage montre le texte détecté
```

### 2. Traducteur temps réel

```python
# En voyage
glasses> trans

# Le texte visible est traduit en français
```

### 3. Assistant de navigation

```python
glasses> view

# "Couloir droit devant, escalier à gauche"
```

### 4. Reconnaissance d'objets

```python
glasses> find clés

# "Oui, vos clés sont sur la table"
```

## 🔧 Personnalisation rapide

### Changer la langue de traduction

```yaml
# config.yaml
features:
  translation:
    target_lang: "en"  # ou es, de, it, etc.
```

### Augmenter la qualité (si Pi4/5)

```yaml
hardware:
  camera:
    resolution: [1280, 720]
    framerate: 30

ai:
  ollama:
    model: "llama3.2:3b"  # Plus intelligent mais plus lent
    max_tokens: 512
```

### Économiser les ressources

```yaml
features:
  voice_recognition: false  # Si pas de micro
  camera_vision: false      # Si pas de caméra

system:
  resources:
    max_cpu_percent: 70     # Plus conservateur
    max_ram_mb: 500
```

## 🎯 Prochaines étapes

1. **Testez toutes les fonctionnalités** avec votre matériel
2. **Créez des scripts personnalisés** (voir `examples/`)
3. **Configurez le démarrage automatique**
   ```bash
   sudo systemctl enable smart-glasses
   ```
4. **Optimisez** selon vos besoins spécifiques
5. **Partagez vos améliorations !**

## 📚 Ressources

- [README complet](README.md) - Documentation détaillée
- [Exemples de scripts](examples/) - Cas d'usage
- [Configuration avancée](config.yaml) - Toutes les options

---

**Besoin d'aide ?** Consultez la section Dépannage du README.md
