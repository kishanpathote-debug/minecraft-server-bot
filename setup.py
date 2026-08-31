#!/usr/bin/env python3
"""
Minecraft Server Configuration Setup Script
Interactive script to configure your server details
"""

import json
import os
from pathlib import Path

def setup_config():
    """Interactive configuration setup"""
    print("\n" + "="*50)
    print("Minecraft Server Bot - Configuration Setup")
    print("="*50 + "\n")
    
    config = {}
    
    # Server IP
    print("Enter your Minecraft server details:")
    server_ip = input("\n1. Server IP or Domain (e.g., play.example.com or 192.168.1.100): ").strip()
    if not server_ip:
        print("Error: Server IP cannot be empty")
        return False
    config['server_ip'] = server_ip
    
    # Server Port
    while True:
        try:
            server_port = input("2. Server Port (default 25565): ").strip()
            if not server_port:
                config['server_port'] = 25565
                break
            port = int(server_port)
            if 1 <= port <= 65535:
                config['server_port'] = port
                break
            else:
                print("   Error: Port must be between 1 and 65535")
        except ValueError:
            print("   Error: Please enter a valid number")
    
    # Bot Username
    username = input("3. Bot Username (default ServerBot): ").strip()
    config['username'] = username if username else 'ServerBot'
    
    # Check Interval
    while True:
        try:
            interval = input("4. Check Interval in seconds (default 300 = 5 min): ").strip()
            if not interval:
                config['check_interval'] = 300
                break
            interval_int = int(interval)
            if interval_int > 0:
                config['check_interval'] = interval_int
                break
            else:
                print("   Error: Interval must be greater than 0")
        except ValueError:
            print("   Error: Please enter a valid number")
    
    # Reconnect Attempts
    while True:
        try:
            attempts = input("5. Reconnect Attempts before restart (default 5): ").strip()
            if not attempts:
                config['reconnect_attempts'] = 5
                break
            attempts_int = int(attempts)
            if attempts_int > 0:
                config['reconnect_attempts'] = attempts_int
                break
            else:
                print("   Error: Attempts must be greater than 0")
        except ValueError:
            print("   Error: Please enter a valid number")
    
    # Restart Command
    print("\n6. Restart Command (leave empty if not needed)")
    print("   Examples:")
    print("   - systemctl restart minecraft-server")
    print("   - /opt/minecraft/restart.sh")
    print("   - docker restart minecraft-server")
    restart_cmd = input("   Enter command: ").strip()
    config['restart_command'] = restart_cmd if restart_cmd else ""
    
    # Save configuration
    config_file = 'config.json'
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print("\n" + "="*50)
        print(f"✓ Configuration saved to {config_file}")
        print("="*50)
        print("\nServer Configuration:")
        print(f"  Server IP:        {config['server_ip']}")
        print(f"  Server Port:      {config['server_port']}")
        print(f"  Bot Username:     {config['username']}")
        print(f"  Check Interval:   {config['check_interval']} seconds")
        print(f"  Reconnect Tries:  {config['reconnect_attempts']}")
        if config['restart_command']:
            print(f"  Restart Command:  {config['restart_command']}")
        print("\nNext steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Run the bot: python bot.py")
        print("  3. Or run with Docker: docker-compose up -d")
        print()
        return True
    except Exception as e:
        print(f"\nError saving configuration: {e}")
        return False

def load_existing_config():
    """Load and display existing configuration"""
    config_file = 'config.json'
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            print("\n" + "="*50)
            print("Current Configuration")
            print("="*50)
            print(f"  Server IP:        {config.get('server_ip', 'Not set')}")
            print(f"  Server Port:      {config.get('server_port', 'Not set')}")
            print(f"  Bot Username:     {config.get('username', 'Not set')}")
            print(f"  Check Interval:   {config.get('check_interval', 'Not set')} seconds")
            print(f"  Reconnect Tries:  {config.get('reconnect_attempts', 'Not set')}")
            if config.get('restart_command'):
                print(f"  Restart Command:  {config['restart_command']}")
            print("="*50 + "\n")
            return True
        except Exception as e:
            print(f"Error reading configuration: {e}")
            return False
    return False

def main():
    """Main function"""
    # Check if config exists
    if load_existing_config():
        choice = input("Do you want to update the configuration? (yes/no): ").strip().lower()
        if choice not in ['yes', 'y']:
            print("\nConfiguration setup cancelled.")
            return
    
    # Setup new config
    setup_config()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
    except Exception as e:
        print(f"\nError: {e}")
