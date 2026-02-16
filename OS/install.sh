#!/bin/bash
# Optic One Installation Script
# Optimized for Raspberry Pi 3 Model B+

set -e

echo "========================================="
echo "Optic One - Installation Script"
echo "========================================="
echo ""

# Verify Raspberry Pi OS
if [ ! -f /etc/rpi-issue ]; then
    echo "WARNING: This does not appear to be Raspberry Pi OS"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Step 1/9: Updating system packages..."
sudo apt update
sudo apt upgrade -y

echo ""
echo "Step 2/9: Installing system dependencies..."
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

echo ""
echo "Step 3/9: Configuring I2C interface..."
if ! grep -q "^i2c-dev" /etc/modules; then
    echo "i2c-dev" | sudo tee -a /etc/modules
fi

if ! grep -q "^dtparam=i2c_arm=on" /boot/config.txt; then
    echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt
fi

sudo usermod -a -G i2c $USER

echo ""
echo "Step 4/9: Creating Python virtual environment..."
cd ~/optic-one
python3 -m venv venv
source venv/bin/activate

echo ""
echo "Step 5/9: Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Step 6/9: Installing Whisper (voice recognition)..."
echo "NOTE: Whisper models can be resource-intensive on Pi 3"
echo "      The 'tiny' model is recommended (configured in config.yaml)"
read -p "Install Whisper? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pip install openai-whisper
else
    echo "Skipping Whisper - voice recognition will run in simulation mode"
fi

echo ""
echo "Step 7/9: Installing Ollama..."
echo "Ollama provides local AI inference capabilities"
echo ""
echo "  curl -fsSL https://ollama.com/install.sh | sh"
echo ""
read -p "Install Ollama now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    curl -fsSL https://ollama.com/install.sh | sh
    
    echo ""
    echo "Downloading Llama 3.2 (1B) model..."
    ollama pull llama3.2:1b
    
    echo ""
    echo "Downloading LLaVA (7B) vision model..."
    read -p "Download vision model? (recommended, ~4GB) (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ollama pull llava:7b
    fi
fi

echo ""
echo "Step 8/9: Configuring systemd service..."
cat > optic-one.service << EOF
[Unit]
Description=Optic One Wearable Computing Platform
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/optic-one
Environment="PATH=/home/$USER/optic-one/venv/bin"
ExecStart=/home/$USER/optic-one/venv/bin/python main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo mv optic-one.service /etc/systemd/system/
sudo systemctl daemon-reload

echo ""
echo "Step 9/9: Verifying configuration..."
echo "Detecting I2C devices:"
i2cdetect -y 1

echo ""
echo "========================================="
echo "Installation Complete"
echo "========================================="
echo ""
echo "Next Steps:"
echo ""
echo "1. Reboot to activate I2C:"
echo "   sudo reboot"
echo ""
echo "2. After reboot, start Ollama:"
echo "   ollama serve &"
echo ""
echo "3. Test the system:"
echo "   cd ~/optic-one"
echo "   source venv/bin/activate"
echo "   python main.py --demo"
echo ""
echo "4. Enable auto-start (optional):"
echo "   sudo systemctl enable optic-one"
echo "   sudo systemctl start optic-one"
echo ""
echo "Configuration:"
echo "  Edit config.yaml to match your hardware"
echo "  I2C addresses: Use 'i2cdetect -y 1' to find OLED address"
echo "  Common addresses: 0x3C or 0x3D"
echo ""
