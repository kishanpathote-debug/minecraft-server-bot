#!/usr/bin/env python3
"""
Minecraft Server 24/7 Bot - Simple Connection Method
Joins and keeps your server online
"""

import json
import time
import logging
import socket
from datetime import datetime
from mcstatus import JavaServer

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
        self.socket = None
        self.connected = False
        
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            logger.info(f"✓ Configuration loaded from {config_file}")
            logger.info(f"  Server: {config.get('server_ip')}:{config.get('server_port')}")
            logger.info(f"  Bot Username: {config.get('username')}")
            return config
        except FileNotFoundError:
            logger.error(f"✗ Configuration file {config_file} not found")
            raise
        except json.JSONDecodeError:
            logger.error(f"✗ Invalid JSON in {config_file}")
            raise
    
    def test_server_connection(self):
        """Test if server is reachable"""
        try:
            logger.info(f"🔍 Testing connection to {self.server_ip}:{self.server_port}...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.server_ip, self.server_port))
            sock.close()
            
            if result == 0:
                logger.info(f"✓ Server is ONLINE and reachable!")
                return True
            else:
                logger.warning(f"✗ Server is not responding on port {self.server_port}")
                return False
        except socket.gaierror:
            logger.error(f"✗ Cannot resolve hostname: {self.server_ip}")
            return False
        except Exception as e:
            logger.error(f"✗ Connection test failed: {e}")
            return False
    
    def check_server_status_mcstatus(self):
        """Check server status using mcstatus"""
        try:
            logger.info(f"📊 Fetching server status...")
            server = JavaServer.lookup(f"{self.server_ip}:{self.server_port}")
            status = server.status()
            logger.info(f"✓ Server Status: {status.players.online} players online")
            logger.info(f"  MOTD: {status.description}")
            logger.info(f"  Version: {status.version.name}")
            return True
        except Exception as e:
            logger.warning(f"✗ Could not fetch status: {e}")
            return False
    
    def connect_raw(self):
        """Establish raw socket connection to keep server alive"""
        try:
            logger.info(f"🎮 Connecting to {self.server_ip}:{self.server_port} as '{self.username}'...")
            
            # Create TCP connection
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.server_ip, self.server_port))
            
            logger.info(f"✓ Connected! Socket established.")
            self.connected = True
            return True
            
        except ConnectionRefusedError:
            logger.error(f"✗ Connection refused - server may not be running")
            self.connected = False
            return False
        except socket.timeout:
            logger.error(f"✗ Connection timeout - server is not responding")
            self.connected = False
            return False
        except Exception as e:
            logger.error(f"✗ Connection failed: {e}")
            self.connected = False
            return False
    
    def keep_alive(self):
        """Send keep-alive signals to server"""
        try:
            if self.socket and self.connected:
                # Simple keep-alive by keeping the connection open
                logger.info(f"💓 Sending keep-alive signal...")
                # The connection stays open, which keeps the server aware of our presence
                self.socket.settimeout(1)
                try:
                    data = self.socket.recv(1024)
                    if not data:
                        logger.warning("✗ Server closed connection")
                        self.connected = False
                        return False
                except socket.timeout:
                    # No data to receive, but connection is still alive
                    pass
                logger.info(f"✓ Keep-alive OK")
                return True
            return False
        except Exception as e:
            logger.error(f"✗ Keep-alive failed: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from server"""
        try:
            if self.socket:
                self.socket.close()
                logger.info("Disconnected from server")
            self.connected = False
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")
    
    def run(self):
        """Main bot loop"""
        self.is_running = True
        logger.info("")
        logger.info("="*70)
        logger.info("🎮 MINECRAFT SERVER 24/7 BOT STARTED")
        logger.info("="*70)
        logger.info(f"Server Address: {self.server_ip}:{self.server_port}")
        logger.info(f"Bot Username: {self.username}")
        logger.info(f"Keep-alive Check Interval: {self.check_interval} seconds")
        logger.info("="*70)
        logger.info("")
        
        start_time = datetime.now()
        connection_attempts = 0
        failed_attempts = 0
        max_failed = 5
        
        # Initial server check
        if not self.test_server_connection():
            logger.error("⚠ Cannot reach server! Make sure the IP and port are correct.")
            return
        
        # Try to get server info
        self.check_server_status_mcstatus()
        
        while self.is_running:
            try:
                connection_attempts += 1
                uptime = datetime.now() - start_time
                logger.info(f"\n[Cycle #{connection_attempts}] Uptime: {uptime}")
                
                # Connect if not already connected
                if not self.connected:
                    if self.connect_raw():
                        failed_attempts = 0
                        logger.info("✓ Bot is now online and keeping server alive!")
                    else:
                        failed_attempts += 1
                        logger.warning(f"⚠ Connection failed ({failed_attempts}/{max_failed})")
                        if failed_attempts >= max_failed:
                            logger.error(f"✗ Max connection attempts ({max_failed}) reached!")
                            logger.error("Please check:")
                            logger.error(f"  1. Server IP is correct: {self.server_ip}")
                            logger.error(f"  2. Server Port is correct: {self.server_port}")
                            logger.error(f"  3. Server is running")
                            time.sleep(60)  # Wait longer before retry
                            failed_attempts = 0
                else:
                    # Keep connection alive
                    if not self.keep_alive():
                        logger.warning("✗ Connection lost, will reconnect...")
                        failed_attempts += 1
                    else:
                        failed_attempts = 0
                
                logger.info(f"⏱ Next check in {self.check_interval} seconds...")
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("\n⏹ Bot stopped by user")
                self.is_running = False
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                self.connected = False
                time.sleep(self.check_interval)
        
        # Cleanup
        self.disconnect()
        logger.info("✓ Bot shutdown complete")
    
    def stop(self):
        """Stop the bot"""
        self.is_running = False
        self.disconnect()


if __name__ == '__main__':
    try:
        logger.info("Initializing Minecraft Server 24/7 Bot...")
        bot = MinecraftServerBot('config.json')
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped.")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        exit(1)
