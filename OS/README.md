# Optic One

Optic One is an advanced open-source wearable computing platform designed to bridge the gap between embedded systems and augmented reality. Unlike consumer-grade smart glasses, Optic One is a standalone ARM-based hardware project that prioritizes transparency, modularity, and low-latency system performance.

Built on top of a stripped-down Raspberry Pi OS Lite distribution, the project aims to provide a functional heads-up display (HUD) capable of real-time data visualization and AI-driven contextual assistance without requiring an external smartphone tether.

## Technical Architecture

### Operating System and Kernel

The software core, OpticOS, is a highly optimized Linux environment. It bypasses the standard X11 or Wayland desktop environments to interact directly with the framebuffer and GPIO pins, ensuring maximum CPU cycles are dedicated to AI processing and display stability.

- **Base Distribution**: Raspberry Pi OS Lite (64-bit)
- **Process Management**: Custom systemd services for automated boot-to-script execution
- **Network Stack**: Optimized SSH over Wi-Fi/Bluetooth for headless development and real-time log monitoring

### Hardware Infrastructure

The hardware is designed for balance, heat dissipation, and optical clarity.

- **Compute Unit**: Raspberry Pi 3 Model B+ or Pi Zero 2W
- **Display Interface**: 0.96" or 1.3" Micro-OLED via SPI/I2C protocols (SSD1306 or SH1106 controllers)
- **Optics**: 45-degree beam splitter prism integrated into a custom-engineered optical engine
- **Power Management**: 5V DC input via regulated Li-Po battery pack

### Software Stack

- **Language**: Python 3.11+ for main logic; C++ for performance-critical display drivers
- **Libraries**: Luma.OLED for display rendering, OpenAI Whisper for voice recognition
- **AI Integration**: Ollama for local LLM inference with optimized models for ARM architecture

## Core Features

- **OLED Display Management**: Optimized rendering pipeline with framebuffer caching
- **Computer Vision**: Real-time scene analysis with local AI models
- **Voice Recognition**: Offline speech-to-text using Whisper (tiny model)
- **Real-Time Translation**: OCR and translation of visible text
- **Resource Management**: Intelligent CPU/RAM throttling and thermal monitoring
- **Notification System**: Priority-based message queue with configurable display duration

## Hardware Requirements

### Minimum Configuration

- Raspberry Pi 3 Model B+ (1GB RAM)
- microSD card (16GB minimum, Class 10)
- 5V 2.5A power supply

### Recommended Components

**Display Module**
- SSD1306 128x64 OLED (I2C interface)
- I2C Address: 0x3C or 0x3D
- Operating Voltage: 3.3V - 5V

**Camera Module**
- Raspberry Pi Camera Module v2 (preferred)
- Alternative: USB webcam (640x480 minimum)

**Audio Input**
- USB microphone
- Alternative: ReSpeaker 2-Mics Pi HAT

**Power Supply (Portable)**
- 10,000mAh USB power bank
- Output: 5V 2.5A minimum (3A recommended)

## Installation

### System Preparation

```bash
# Flash Raspberry Pi OS Lite (64-bit) to SD card
# Enable SSH and configure WiFi in Raspberry Pi Imager advanced options

# Connect via SSH
ssh pi@raspberrypi.local

# Change default password
passwd

# Update system
sudo apt update && sudo apt upgrade -y
```

### Automated Installation

```bash
# Clone repository
git clone https://github.com/username/optic-one.git
cd optic-one

# Make installation script executable
chmod +x install.sh

# Run installation
./install.sh
```

The installation script will:
- Install system dependencies (I2C, audio, video libraries)
- Create Python virtual environment
- Install required Python packages
- Configure I2C interface
- Download and configure Ollama with optimized models
- Set up systemd service for auto-start

### Manual Installation

```bash
# Install system dependencies
sudo apt install -y python3-pip python3-venv python3-dev \
    libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev \
    libopenjp2-7 libtiff5 libatlas-base-dev portaudio19-dev \
    ffmpeg i2c-tools python3-smbus

# Enable I2C
sudo raspi-config
# Interface Options > I2C > Enable

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Download AI models
ollama pull llama3.2:1b
ollama pull llava:7b
```

### Hardware Configuration

**OLED Display (I2C)**

```
Connection Map:
VCC  -> Pin 1 (3.3V) or Pin 2 (5V)
GND  -> Pin 6 (Ground)
SDA  -> Pin 3 (GPIO 2)
SCL  -> Pin 5 (GPIO 3)
```

Verify I2C connection:
```bash
i2cdetect -y 1
# Should display address 0x3C or 0x3D
```

**Camera Module**

For Raspberry Pi Camera Module:
```bash
sudo raspi-config
# Interface Options > Camera > Enable
sudo reboot
```

For USB webcam:
```bash
ls /dev/video*
# Should show /dev/video0
```

**Microphone**

```bash
# List audio devices
arecord -l

# Test recording
arecord -d 5 test.wav
aplay test.wav
```

## Configuration

Edit `config.yaml` to match your hardware setup:

```yaml
hardware:
  display:
    type: "SSD1306"
    width: 128
    height: 64
    i2c_address: 0x3C
    i2c_bus: 1
  
  camera:
    device: "/dev/video0"
    resolution: [640, 480]
    framerate: 15
  
  microphone:
    device: "default"
    sample_rate: 16000

ai:
  ollama:
    base_url: "http://localhost:11434"
    model: "llama3.2:1b"
    timeout: 30
  
  vision:
    model: "llava:7b"
  
  whisper:
    model: "tiny"
    language: "en"

system:
  resources:
    max_cpu_percent: 80
    max_ram_mb: 700
    enable_throttling: true
```

## Usage

### Interactive Mode

```bash
cd optic-one
source venv/bin/activate
python main.py
```

Available commands:
- `view` - Analyze current camera view
- `read` - Read visible text (OCR)
- `trans` - Translate visible text
- `find <object>` - Search for specific object
- `voice` - Listen for voice command
- `chat` - Interact with AI
- `stats` - Display system statistics
- `quit` - Exit application

### Demo Mode

```bash
python main.py --demo
```

Demonstrates all core functionalities in sequence.

### Voice Control Mode

```bash
python main.py --voice-control
```

Voice activation workflow:
1. Say wake word "optic" to activate
2. Issue command (e.g., "what time is it", "describe view", "read text")
3. System processes and responds

### Simulation Mode

```bash
python main.py --simulation
```

Run without physical hardware for development and testing.

### System Service

Enable automatic startup:

```bash
sudo systemctl enable optic-one
sudo systemctl start optic-one

# Check status
sudo systemctl status optic-one

# View logs
sudo journalctl -u optic-one -f
```

## Project Structure

```
optic-one/
├── config.yaml              # System configuration
├── main.py                  # Application entry point
├── install.sh               # Automated installation script
├── requirements.txt         # Python dependencies
│
├── core/
│   ├── optic_os.py         # Main system orchestrator
│   ├── display_mgr.py      # OLED display management
│   ├── camera_mgr.py       # Camera and vision processing
│   ├── voice_recog.py      # Voice recognition engine
│   ├── ollama_client.py    # AI model interface
│   └── resource_mgr.py     # System resource monitoring
│
├── examples/
│   ├── accessibility.py    # Accessibility assistant
│   ├── translator.py       # Real-time translator
│   └── voice_assistant.py  # Voice-controlled assistant
│
└── docs/
    ├── HARDWARE.md         # Hardware assembly guide
    ├── QUICKSTART.md       # Quick start guide
    └── API.md              # API documentation
```

## Performance Optimization

### Raspberry Pi 3 Specific

The system is optimized for resource-constrained environments:

- **CPU Throttling**: Automatic reduction when usage exceeds 80%
- **Memory Management**: 700MB limit with intelligent caching
- **Image Processing**: Reduced resolution (640x480) for faster processing
- **AI Models**: Lightweight variants (1B parameters for text, 7B for vision)
- **Frame Rate**: Limited to 15 FPS to conserve CPU cycles

### Performance Tuning

Disable unused features:
```yaml
features:
  voice_recognition: false
  camera_vision: false
```

Reduce camera resolution:
```yaml
camera:
  resolution: [320, 240]
```

Use smallest Whisper model:
```yaml
whisper:
  model: "tiny"
```

Optional overclocking (use with caution):
```bash
# /boot/config.txt
arm_freq=1350
over_voltage=2
```

## Troubleshooting

### Display Issues

```bash
# Verify I2C connection
sudo i2cdetect -y 1

# Check wiring
# VCC -> 3.3V/5V
# GND -> Ground
# SDA -> GPIO 2
# SCL -> GPIO 3

# Review logs
tail -f /var/log/optic-one.log
```

### Camera Not Detected

```bash
# Raspberry Pi Camera
vcgencmd get_camera

# USB Webcam
ls /dev/video*

# Test capture
raspistill -o test.jpg  # Pi Camera
fswebcam test.jpg       # USB Webcam
```

### Ollama Connection Failed

```bash
# Start Ollama service
ollama serve

# Test API
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:1b",
  "prompt": "Hello"
}'
```

### Insufficient Memory

```bash
# Increase swap space
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set: CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

## Engineering and Manufacturing

### CAD and Mechanical Design

The chassis is modeled using Autodesk Fusion 360, focusing on ergonomics and component housing.

- **Tolerance Management**: 0.2mm precision for press-fit component mounting
- **Material Science**: Structural parts printed in PETG or Carbon-Fiber PLA for thermal resistance and mechanical rigidity
- **Slicing Optimization**: Profile-specific settings in OrcaSlicer to ensure interlayer adhesion and dimensional accuracy

### Bill of Materials

| Component | Specification | Quantity | Est. Cost |
|-----------|--------------|----------|-----------|
| Raspberry Pi 3 B+ | 1GB RAM | 1 | $35 |
| microSD Card | 32GB Class 10 | 1 | $10 |
| OLED Display | SSD1306 128x64 I2C | 1 | $8 |
| Pi Camera v2 | 8MP | 1 | $25 |
| USB Microphone | 16kHz | 1 | $10 |
| Power Bank | 10000mAh | 1 | $20 |
| Jumper Wires | F-F 10cm | 10 | $3 |
| **Total** | | | **~$111** |

## Project Roadmap

### Phase 1: Prototype Foundation (Current)
- Core OpticOS implementation
- SPI/I2C display integration
- Basic text rendering and UI
- Initial 3D frame prototyping

### Phase 2: Intelligence Integration
- Voice-to-text processing pipeline
- Real-time AI response integration
- Power optimization and thermal management
- Advanced notification system

### Phase 3: Computer Vision
- Camera module integration
- Object recognition capabilities
- Heads-up navigation system
- OCR and translation features

### Phase 4: Production Ready
- PCB design for custom hardware
- Injection-molded housing
- Battery management system
- Mobile app companion

## Development Environment

### Prerequisites

- Unix-based system (macOS ARM or Linux recommended)
- Raspberry Pi Imager
- VS Code with Remote-SSH extension
- Python 3.11+

### Contributing

Contributions are welcome. Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/improvement`)
5. Create Pull Request

### Code Style

- Python: Follow PEP 8 guidelines
- Maximum line length: 100 characters
- Use type hints for function signatures
- Document all public methods with docstrings

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Security

- Change default Raspberry Pi password immediately
- Configure firewall for network exposure
- AI processing occurs locally (no cloud dependencies)
- Logs stored in `/var/log/optic-one.log`

## Resources

- [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)
- [Luma.OLED Library](https://luma-oled.readthedocs.io/)
- [Ollama Documentation](https://ollama.com/)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [OpenCV Documentation](https://docs.opencv.org/)

## Support

For issues and questions:
1. Check system logs
2. Run in simulation mode to isolate hardware issues
3. Test each component individually
4. Open an issue on GitHub with detailed information

---

**Project Status**: Alpha (Active Development)  
**Last Updated**: February 2026  
**Maintainer**: [Your Name/Organization]
