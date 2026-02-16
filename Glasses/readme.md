# 🕶️ Optic One - Deep Technical Specifications

## 1. System Overview
Optic One is an Augmented Reality (AR) wearable powered by a Raspberry Pi 3 Model B. The architecture follows a "Split-Processing" design: a lightweight head-mounted peripheral connected via a high-density wire harness to a pocket-sized compute unit.

---

## 2. Detailed Hardware Components & Wiring (GPIO Map)

To ensure the system remains compact, we use the Raspberry Pi's 40-pin GPIO header. Below is the precise mapping for the sensors and actuators.

### A. Visual Output (HUD)
* **Component:** 0.96" SSD1306 OLED Display (128x64 pixels).
* **Interface:** I2C Protocol.
* **Wiring:**
    * **VCC** -> 3.3V (Pin 1)
    * **GND** -> Ground (Pin 9)
    * **SDA** -> GPIO 2 (Pin 3)
    * **SCL** -> GPIO 3 (Pin 5)

### B. Computer Vision (The Eye)
* **Component:** Raspberry Pi Camera Module V2 (Green PCB).
* **Interface:** CSI (Camera Serial Interface).
* **Connection:** 15-pin FFC (Flexible Flat Cable) plugged into the dedicated CSI port between the Audio and HDMI jacks.
* **Role:** Real-time image capture for AI object recognition and OCR (Optical Character Recognition).

### C. Audio Intelligence (Ear & Mouth)
* **Microphone:** MEMS SPH0645 (I2S Digital Mic).
    * **Wiring:**
        * **SEL** -> GND
        * **LRCL** -> GPIO 19 (Pin 35)
        * **BCLK** -> GPIO 18 (Pin 12)
        * **DOUT** -> GPIO 20 (Pin 38)
* **Speaker:** 8 Ohm 1W Miniature Driver.
    * **Connection:** Connected via a MAX98357A I2S Amplifier to maintain a fully digital audio path for better noise isolation.

### D. Navigation & Inertial Unit (IMU)
* **Component:** MPU6050 (6-Axis Gyroscope + Accelerometer).
* **Interface:** I2C (Shared with OLED).
* **Wiring:**
    * **VCC** -> 3.3V
    * **GND** -> Ground
    * **SDA** -> GPIO 2 (Parallel with OLED)
    * **SCL** -> GPIO 3 (Parallel with OLED)
* **Logic:** Detects "Nod" (Yes) and "Shake" (No) gestures for hands-free menu navigation.

---

## 3. Navigation Logic & User Interface (UI)

The "Optic-OS" uses a minimalist circular menu system to compensate for the small screen size.

1.  **Idle State:** Displays time and system temperature.
2.  **Gesture Trigger:** A sharp tilt of the head to the right opens the "App Drawer".
3.  **Selection:** * **Nod (Pitch axis):** Confirms the highlighted app (Camera, Notes, Settings).
    * **Shake (Yaw axis):** Exits the current app or goes back to the home screen.
4.  **Voice Override:** At any time, the user can say "Optic, Terminal" to open a remote SSH session on the HUD.

---

## 4. Integration & Cable Management

The link between the Pi 3 and the glasses is a custom **12-core shielded cable** (30 AWG). This cable is routed through a 3D-printed strain relief clip on the right temple of the frame. 

* **Shielding:** To prevent EMI (Electromagnetic Interference) from the CSI camera cable affecting the I2C bus of the OLED.
* **Power Management:** The system is powered by a 5V 3A Li-Po Power Bank via the Micro-USB port of the Pi.

---

## 5. Engineering Goals for V2
* Transition from Raspberry Pi 3 to **Compute Module 4 (CM4)** for a custom carrier board.
* Implementation of **Tailscale** for secure remote access from an iPhone/Mac without port forwarding.
* Design of a custom **Monocle Housing** using Fusion 360 to improve the optical clarity of the beam splitter.

---
**Lead Developer:** Alexis
**Date:** February 2026
**Project Status:** Alpha / Hardware Integration Phase