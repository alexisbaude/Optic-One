#!/usr/bin/env python3
"""
Point d'entrée principal pour Smart Glasses OS
"""

import sys
import os

# Ajoute le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import des modules (en fusionnant les parties)
import logging

# Fusionne les modules divisés
def merge_module_files(base_name):
    """Fusionne les fichiers _pt2 avec les fichiers de base"""
    base_file = f"{base_name}.py"
    pt2_file = f"{base_name}_pt2.py"
    
    if os.path.exists(base_file) and os.path.exists(pt2_file):
        with open(base_file, 'r') as f:
            base_content = f.read()
        
        with open(pt2_file, 'r') as f:
            pt2_content = f.read()
        
        # Combine les contenus
        merged_content = base_content.rstrip() + '\n' + pt2_content
        
        # Écrit le fichier fusionné
        with open(base_file, 'w') as f:
            f.write(merged_content)
        
        # Supprime le fichier pt2
        os.remove(pt2_file)
        
        logging.info(f"Merged {base_name}")

# Fusionne tous les modules au premier démarrage
modules_to_merge = [
    'display_manager',
    'ollama_client',
    'camera_manager',
    'voice_recognizer',
    'smart_glasses_os'
]

for module in modules_to_merge:
    try:
        merge_module_files(module)
    except Exception as e:
        logging.debug(f"Module {module} merge: {e}")

# Import du système principal
from smart_glasses_os import SmartGlassesOS, signal_handler
import signal
import argparse


def main():
    """Fonction principale"""
    
    # Parse les arguments
    parser = argparse.ArgumentParser(description='Smart Glasses OS')
    parser.add_argument('--config', type=str, default='config.yaml',
                       help='Path to config file')
    parser.add_argument('--simulation', action='store_true',
                       help='Run in simulation mode (no hardware required)')
    parser.add_argument('--demo', action='store_true',
                       help='Run demo mode')
    parser.add_argument('--voice-control', action='store_true',
                       help='Start in voice control mode')
    
    args = parser.parse_args()
    
    # Bannière
    print("""
    ╔═══════════════════════════════════════╗
    ║      Smart Glasses OS v1.0           ║
    ║   Powered by Ollama + Raspberry Pi   ║
    ╚═══════════════════════════════════════╝
    """)
    
    # Configure les signal handlers
    global os_instance
    os_instance = None
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Crée l'instance
        print(f"Loading configuration from {args.config}...")
        os_instance = SmartGlassesOS(args.config)
        
        # Initialise
        print(f"Initializing modules (simulation={args.simulation})...")
        os_instance.initialize_modules(simulation_mode=args.simulation)
        
        # Démarre
        print("Starting system...")
        os_instance.start()
        
        # Mode démo
        if args.demo:
            print("\n=== Running Demo Mode ===\n")
            os_instance.run_demo()
        
        # Mode contrôle vocal
        elif args.voice_control:
            print("\n=== Voice Control Mode ===")
            print("Say 'lunettes' to activate, then give a command.")
            print("Press Ctrl+C to exit.\n")
            
            while os_instance.running:
                # Attend le mot d'activation
                if os_instance.voice.detect_wake_word('lunettes', timeout=30):
                    # Écoute la commande
                    command = os_instance.listen_for_command(duration=5)
                    
                    if command:
                        print(f"Command: {command}")
                        
                        # Traite la commande
                        result = os_instance.process_voice_command(command)
                        
                        if result:
                            print(f"Result: {result}")
        
        # Mode interactif standard
        else:
            print("\n=== Interactive Mode ===")
            print("Available commands:")
            print("  view   - Analyze current view")
            print("  read   - Read text in view")
            print("  trans  - Translate text in view")
            print("  find X - Find object X")
            print("  voice  - Listen for voice command")
            print("  chat   - Chat with AI")
            print("  stats  - System statistics")
            print("  help   - Show this help")
            print("  quit   - Exit")
            print()
            
            while os_instance.running:
                try:
                    # Traite les notifications en arrière-plan
                    os_instance.process_notifications()
                    
                    # Commande utilisateur
                    cmd = input("glasses> ").strip().lower()
                    
                    if not cmd:
                        continue
                    
                    if cmd == 'quit' or cmd == 'exit':
                        break
                    
                    elif cmd == 'help':
                        print("Commands: view, read, trans, find X, voice, chat, stats, quit")
                    
                    elif cmd == 'view':
                        result = os_instance.analyze_current_view()
                        if result:
                            print(f"\n{result}\n")
                    
                    elif cmd == 'read':
                        result = os_instance.read_text_in_view()
                        if result:
                            print(f"\nText: {result}\n")
                    
                    elif cmd == 'trans':
                        result = os_instance.translate_view()
                        if result:
                            print(f"\nTranslation: {result}\n")
                    
                    elif cmd.startswith('find '):
                        obj = cmd[5:].strip()
                        result = os_instance.find_object_by_name(obj)
                        if result:
                            print(f"\n{result}\n")
                    
                    elif cmd == 'voice':
                        result = os_instance.listen_for_command()
                        if result:
                            print(f"\nCommand: {result}")
                            response = os_instance.process_voice_command(result)
                            if response:
                                print(f"Response: {response}\n")
                    
                    elif cmd == 'chat':
                        msg = input("You: ")
                        response = os_instance.chat_with_ai(msg)
                        if response:
                            print(f"AI: {response}\n")
                    
                    elif cmd == 'stats':
                        stats = os_instance.get_system_status()
                        print("\nSystem Status:")
                        print(f"  Running: {stats['running']}")
                        if stats['resources']:
                            res = stats['resources']
                            print(f"  CPU: {res['current']['cpu_percent']:.1f}%")
                            print(f"  RAM: {res['current']['ram_mb']:.0f}MB ({res['current']['ram_percent']:.1f}%)")
                            if res['current']['temperature']:
                                print(f"  Temp: {res['current']['temperature']:.1f}°C")
                            print(f"  Throttled: {res['status']['throttled']}")
                        print(f"  Camera: {stats['camera_active']}")
                        print(f"  Voice: {stats['voice_active']}")
                        print(f"  Notifications: {stats['notifications_queued']}")
                        print()
                    
                    else:
                        print(f"Unknown command: {cmd}")
                        print("Type 'help' for available commands")
                
                except KeyboardInterrupt:
                    print("\nInterrupted")
                    break
                except Exception as e:
                    print(f"Error: {e}")
                    logging.exception("Command error")
    
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Fatal error: {e}")
        logging.exception("Fatal error")
        return 1
    finally:
        if os_instance:
            os_instance.stop()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
