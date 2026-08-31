#!/usr/bin/env python3
"""
Minecraft Server 24/7 Bot
Keeps your Minecraft server online by maintaining an active connection
"""

import json
import time
import logging
import subprocess
import os
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MinecraftServerBot:
    def __init__(self, config_file='config.json'):
        """Initialize the bot with configuration"""
        self.config = self.load_config(config_file)
        self.server_ip = self.config.get('server_ip')
        self.server_port = self.config.get('server_port', 25565)
        self.username = self.config.get('username', 'ServerBot')
        self.check_interval = self.config.get('check_interval', 300)  # 5 minutes
        self.reconnect_attempts = self.config.get('reconnect_attempts', 5)
        self.is_running = False
        self.connection_failures = 0
        
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {config_file}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file {config_file} not found")
            raise
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in {config_file}")
            raise
    
    def check_server_status(self):
        """Check if server is responding using socket connection"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.server_ip, self.server_port))
            sock.close()
            
            if result == 0:
                logger.info(f"✓ Server is ONLINE - {self.server_ip}:{self.server_port}")
                self.connection_failures = 0
                return True
            else:
                self.connection_failures += 1
                logger.warning(f"✗ Server is OFFLINE - Connection attempt {self.connection_failures}/{self.reconnect_attempts}")
                return False
        except Exception as e:
            self.connection_failures += 1
            logger.error(f"Error checking server status: {e} (Attempt {self.connection_failures}/{self.reconnect_attempts})")
            return False
    
    def send_keepalive(self):
        """Send keepalive packet to server"""
        try:
            logger.info(f"🔄 Sending keepalive to {self.server_ip}:{self.server_port}...")
            if self.check_server_status():
                logger.info("✓ Server is online and responsive")
                return True
            else:
                logger.warning("✗ Server is not responding")
                return False
        except Exception as e:
            logger.error(f"Error sending keepalive: {e}")
            return False
    
    def restart_server_if_needed(self):
        """Attempt to restart server if it's down"""
        if self.connection_failures >= self.reconnect_attempts:
            logger.critical(f"🚨 Server DOWN after {self.reconnect_attempts} failed attempts!")
            restart_cmd = self.config.get('restart_command')
            if restart_cmd:
                try:
                    logger.info(f"Executing restart command: {restart_cmd}")
                    subprocess.run(restart_cmd, shell=True, check=True)
                    logger.info("✓ Server restart command executed")
                    self.connection_failures = 0
                    time.sleep(15)  # Wait for server to start
                    return True
                except subprocess.CalledProcessError as e:
                    logger.error(f"✗ Failed to restart server: {e}")
                    return False
            else:
                logger.warning("No restart command configured. Please restart server manually.")
                return False
        return True
    
    def run(self):
        """Main bot loop"""
        self.is_running = True
        logger.info("="*60)
        logger.info("🎮 MINECRAFT SERVER BOT STARTED")
        logger.info("="*60)
        logger.info(f"Server: {self.server_ip}:{self.server_port}")
        logger.info(f"Bot Username: {self.username}")
        logger.info(f"Check Interval: {self.check_interval} seconds")
        logger.info(f"Reconnect Attempts: {self.reconnect_attempts}")
        logger.info("="*60)
        
        start_time = datetime.now()
        check_count = 0
        
        while self.is_running:
            try:
                check_count += 1
                uptime = datetime.now() - start_time
                logger.info(f"\n[Check #{check_count}] Uptime: {uptime}")
                
                # Check server status
                if not self.send_keepalive():
                    # Check if we need to restart
                    self.restart_server_if_needed()
                
                logger.info(f"⏰ Next check in {self.check_interval} seconds...")
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("\n⛔ Bot stopped by user")
                self.is_running = False
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                time.sleep(self.check_interval)
    
    def stop(self):
        """Stop the bot"""
        self.is_running = False
        logger.info("Bot stopping...")


if __name__ == '__main__':
    try:
        logger.info("Initializing Minecraft Server Bot...")
        bot = MinecraftServerBot('config.json')
        bot.run()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        exit(1)
