#!/usr/bin/env python3
"""
Optic One - Wearable Computing Platform
Main entry point for the OpticOS system
"""

import sys
import os
import signal
import argparse
import logging

# Add core module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

from optic_os import OpticOS


def signal_handler(sig, frame):
    """Handle interrupt signals gracefully"""
    global os_instance
    logging.info("Interrupt signal received, shutting down...")
    if os_instance:
        os_instance.stop()
    sys.exit(0)


def main():
    """Main application entry point"""
    
    parser = argparse.ArgumentParser(
        description='Optic One - Wearable Computing Platform',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--simulation',
        action='store_true',
        help='Run in simulation mode without hardware'
    )
    
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run demonstration mode'
    )
    
    parser.add_argument(
        '--voice-control',
        action='store_true',
        help='Start in voice control mode'
    )
    
    args = parser.parse_args()
    
    # Display banner
    print("""
    ╔═══════════════════════════════════════╗
    ║         Optic One v1.0-alpha          ║
    ║    Wearable Computing Platform        ║
    ╚═══════════════════════════════════════╝
    """)
    
    # Configure signal handlers
    global os_instance
    os_instance = None
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize system
        print(f"Loading configuration from {args.config}...")
        os_instance = OpticOS(args.config)
        
        print(f"Initializing modules (simulation mode: {args.simulation})...")
        os_instance.initialize_modules(simulation_mode=args.simulation)
        
        print("Starting system...")
        os_instance.start()
        
        # Run in selected mode
        if args.demo:
            print("\n=== Demo Mode ===\n")
            os_instance.run_demo()
        
        elif args.voice_control:
            print("\n=== Voice Control Mode ===")
            print("Say 'optic' to activate, then issue a command")
            print("Press Ctrl+C to exit\n")
            
            while os_instance.running:
                if os_instance.voice.detect_wake_word('optic', timeout=30):
                    command = os_instance.listen_for_command(duration=5)
                    
                    if command:
                        print(f"Command: {command}")
                        result = os_instance.process_voice_command(command)
                        
                        if result:
                            print(f"Result: {result}")
        
        else:
            # Interactive mode
            print("\n=== Interactive Mode ===")
            print("Available commands:")
            print("  view   - Analyze current view")
            print("  read   - Read visible text")
            print("  trans  - Translate visible text")
            print("  find X - Find object X")
            print("  voice  - Listen for voice command")
            print("  chat   - Chat with AI")
            print("  stats  - System statistics")
            print("  help   - Show this help")
            print("  quit   - Exit\n")
            
            while os_instance.running:
                try:
                    os_instance.process_notifications()
                    
                    cmd = input("optic> ").strip().lower()
                    
                    if not cmd:
                        continue
                    
                    if cmd in ('quit', 'exit'):
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
                            print(f"  RAM: {res['current']['ram_mb']:.0f}MB "
                                  f"({res['current']['ram_percent']:.1f}%)")
                            if res['current']['temperature']:
                                print(f"  Temperature: {res['current']['temperature']:.1f}C")
                            print(f"  Throttled: {res['status']['throttled']}")
                        print(f"  Camera: {stats['camera_active']}")
                        print(f"  Voice: {stats['voice_active']}")
                        print(f"  Notifications: {stats['notifications_queued']}\n")
                    
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
