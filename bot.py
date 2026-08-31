#!/usr/bin/env python3
"""
Minecraft Server 24/7 Bot
Actually joins and stays connected to your Minecraft server
"""

import json
import time
import logging
import threading
from datetime import datetime
from mcstatus import JavaServer
from minecraft.utility import authentication
from minecraft.networking.connection import Connection
from minecraft.networking.packets import Packet, clientbound, serverbound
from minecraft.networking.packets.login import LoginSetResponsePacket
from minecraft.authentication import AuthenticationException
import socket

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
        self.check_interval = self.config.get('check_interval', 300)
        self.is_running = False
        self.connection = None
        self.connection_thread = None
        
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            logger.info(f"✓ Configuration loaded from {config_file}")
            return config
        except FileNotFoundError:
            logger.error(f"✗ Configuration file {config_file} not found")
            raise
        except json.JSONDecodeError:
            logger.error(f"✗ Invalid JSON in {config_file}")
            raise
    
    def check_server_online(self):
        """Check if server is online using mcstatus"""
        try:
            logger.info(f"🔍 Checking server status {self.server_ip}:{self.server_port}...")
            server = JavaServer.lookup(f"{self.server_ip}:{self.server_port}")
            status = server.status()
            logger.info(f"✓ Server is ONLINE - Players: {status.players.online}/{status.players.max}")
            return True
        except Exception as e:
            logger.warning(f"✗ Server offline or unreachable: {e}")
            return False
    
    def connect_to_server(self):
        """Connect to Minecraft server as a player"""
        try:
            logger.info(f"🎮 Attempting to connect as '{self.username}' to {self.server_ip}:{self.server_port}...")
            
            # Create connection
            self.connection = Connection(
                self.server_ip,
                self.server_port,
                username=self.username
            )
            
            # Connect
            self.connection.connect()
            logger.info(f"✓ Successfully joined server as {self.username}!")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to connect to server: {e}")
            self.connection = None
            return False
    
    def keep_connection_alive(self):
        """Keep connection alive by responding to keep-alive packets"""
        try:
            while self.is_running and self.connection and self.connection.connected:
                try:
                    # Read and respond to packets
                    packet = self.connection.read_packet()
                    if packet:
                        logger.debug(f"Received packet: {type(packet).__name__}")
                    time.sleep(0.1)
                except Exception as e:
                    logger.debug(f"Packet read error: {e}")
                    break
        except Exception as e:
            logger.error(f"Connection keep-alive error: {e}")
    
    def run(self):
        """Main bot loop"""
        self.is_running = True
        logger.info("="*70)
        logger.info("🎮 MINECRAFT SERVER BOT STARTED")
        logger.info("="*70)
        logger.info(f"Server: {self.server_ip}:{self.server_port}")
        logger.info(f"Bot Username: {self.username}")
        logger.info(f"Check Interval: {self.check_interval} seconds")
        logger.info("="*70)
        
        start_time = datetime.now()
        connection_attempts = 0
        
        while self.is_running:
            try:
                connection_attempts += 1
                uptime = datetime.now() - start_time
                logger.info(f"\n[Attempt #{connection_attempts}] Uptime: {uptime}")
                
                # Check if server is online
                if self.check_server_online():
                    # Try to connect
                    if self.connect_to_server():
                        logger.info("✓ Bot is now connected and will keep server alive")
                        
                        # Keep connection alive
                        self.keep_connection_alive()
                        
                        logger.warning("⚠ Connection lost. Attempting to reconnect...")
                        connection_attempts = 0
                    else:
                        logger.warning(f"⚠ Connection failed. Retrying in {self.check_interval} seconds...")
                else:
                    logger.warning(f"⚠ Server is offline. Retrying in {self.check_interval} seconds...")
                
                # Wait before next attempt
                logger.info(f"⏰ Next connection attempt in {self.check_interval} seconds...")
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("\n⏹ Bot stopped by user")
                self.is_running = False
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(self.check_interval)
        
        # Cleanup
        if self.connection and self.connection.connected:
            logger.info("Disconnecting...")
            self.connection.disconnect()
    
    def stop(self):
        """Stop the bot"""
        self.is_running = False
        if self.connection and self.connection.connected:
            self.connection.disconnect()
        logger.info("Bot stopped.")


if __name__ == '__main__':
    try:
        logger.info("Initializing Minecraft Server Bot...")
        bot = MinecraftServerBot('config.json')
        bot.run()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        exit(1)
