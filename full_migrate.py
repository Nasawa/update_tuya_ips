"""
Tuya Device Local Control Migration Script

This script automates the migration of Tuya devices from cloud to local control in Home Assistant.
It performs the following main operations:
1. Scans for Tuya devices using tinytuya
2. Backs up Home Assistant configuration
3. Updates device configurations for local control
4. Triggers Home Assistant reboot via MQTT

Dependencies:
- paho-mqtt>=1.6.1: MQTT client for Home Assistant communication
- python-dotenv>=1.0.0: Environment variable management
- tinytuya>=1.13.0: Tuya device management and scanning

Environment Variables Required:
File Paths:
- CORE_CONFIG_FILE: Path to Home Assistant core.config_entries file
- BACKUP_FILE: Backup location for core.config_entries file
- LOCAL_CORE_CONFIG_FILE: Local copy of core.config_entries file
- SNAPSHOT_FILE: Path to store configuration snapshot
- LOG_FILE: Path to log file

MQTT Configuration:
- MQTT_BROKER: MQTT broker hostname/IP
- MQTT_PORT: MQTT broker port
- MQTT_USERNAME: MQTT authentication username
- MQTT_PASSWORD: MQTT authentication password
- MQTT_TOPIC: MQTT topic for reboot commands

Logging Configuration:
- LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- LOG_FORMAT: Format string for log messages

Usage:
1. Set up environment variables in .env file
2. Install required dependencies: pip install -r requirements.txt
3. Run the script: python full_migrate.py

Note: This script requires appropriate permissions to read/write Home Assistant
configuration files and communicate with the MQTT broker.
"""

import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

import paho.mqtt.client as mqtt

try:
    from dotenv import load_dotenv
except ImportError:
    raise ImportError("python-dotenv is required. Please install it using 'pip install python-dotenv'")

# Load environment variables
if not load_dotenv():
    raise RuntimeError("Failed to load .env file")

def get_env_var(var_name: str) -> str:
    """
    Retrieve and validate required environment variables.

    Args:
        var_name (str): Name of the environment variable to retrieve

    Returns:
        str: Value of the environment variable with normalized paths

    Raises:
        ValueError: If the environment variable is not set or is empty
    """
    value: Optional[str] = os.getenv(var_name)
    if value is None:
        raise ValueError(f"Required environment variable '{var_name}' is not set")
    
    # Normalize path-like environment variables
    if any(key in var_name.lower() for key in ['path', 'file', 'dir']):
        # Convert Windows backslashes to forward slashes and normalize path
        value = os.path.normpath(value.replace('\\', '/'))
    
    return value

# Configure logging with explicit UTF-8 encoding
logging.basicConfig(
    filename=get_env_var('LOG_FILE'),
    level=getattr(logging, get_env_var('LOG_LEVEL')),
    format=get_env_var('LOG_FORMAT'),
    encoding='utf-8'
)

# Define paths
TINYTUYA_COMMAND = "tinytuya scan"
SNAPSHOT_FILE = get_env_var('SNAPSHOT_FILE')
CORE_CONFIG_FILE = get_env_var('CORE_CONFIG_FILE')
BACKUP_FILE = get_env_var('BACKUP_FILE')
LOCAL_CORE_CONFIG_FILE = get_env_var('LOCAL_CORE_CONFIG_FILE')

# MQTT configuration
MQTT_BROKER = get_env_var('MQTT_BROKER')
MQTT_PORT = int(get_env_var('MQTT_PORT'))
MQTT_USERNAME = get_env_var('MQTT_USERNAME')
MQTT_PASSWORD = get_env_var('MQTT_PASSWORD')
MQTT_TOPIC = get_env_var('MQTT_TOPIC')

def log(message: str, level: str = 'info') -> None:
    """
    Log messages to both console and log file.

    Args:
        message (str): Message to be logged
        level (str, optional): Log level ('info' or 'error'). Defaults to 'info'.

    Note:
        Messages are always printed to console regardless of log level.
        For file logging, messages are logged at the specified level.
    """
    print(message)
    if level == 'info':
        logging.info(message)
    elif level == 'error':
        logging.error(message)

# TODO: Add retry mechanism for tinytuya scan in case of temporary network issues
# TODO: Add validation of scan results before proceeding

# Step 1: Run tinytuya scan to discover local Tuya devices
try:
    log("Running tinytuya scan...")
    # Use shell=True to handle command with arguments, capture both stdout/stderr for logging
    result = subprocess.run(TINYTUYA_COMMAND, shell=True, check=True, capture_output=True, text=True)
    
    # Log all output to maintain complete audit trail
    if result.stdout:
        log(result.stdout)
    if result.stderr:  # stderr may contain important warnings even on success
        log(result.stderr)
    log("tinytuya scan completed successfully.")
except subprocess.CalledProcessError as e:
    # Comprehensive error logging for debugging
    log(f"Error running tinytuya scan: {e}", 'error')
    if e.output:
        log(e.output, 'error')
    if e.stderr:
        log(e.stderr, 'error')
    exit(1)  # Exit on scan failure as continuing would be pointless

# TODO: Add backup file rotation to keep multiple versions
# TODO: Add backup verification step to ensure backup integrity

# Step 2: Backup core.config_entries before modifications
try:
    log("Backing up core.config_entries...")
    with open(CORE_CONFIG_FILE, 'r', encoding='utf-8') as src, \
         open(BACKUP_FILE, 'w', encoding='utf-8') as dst:
        dst.write(src.read())
    log(f"Backup created at {BACKUP_FILE}.")
except Exception as e:
    log(f"Error creating backup: {e}", 'error')
    exit(1)  # Exit if backup fails to prevent potential data loss

# Step 3: Copy core.config_entries to local working directory
try:
    log("Copying core.config_entries to local directory for processing...")
    with open(CORE_CONFIG_FILE, 'r', encoding='utf-8') as src, \
         open(LOCAL_CORE_CONFIG_FILE, 'w', encoding='utf-8') as dst:
        dst.write(src.read())
    log(f"File copied to {LOCAL_CORE_CONFIG_FILE}.")
except Exception as e:
    log(f"Error copying file: {e}", 'error')
    exit(1)  # Exit if local copy fails as we can't proceed with migration

# Step 4: Run migrate.py
try:
    log("Running migrate.py...")
    # Capture output from migrate.py
    result = subprocess.run(["python", "migrate.py"], check=True, capture_output=True, text=True)
    if result.stdout:
        log(result.stdout)
    if result.stderr:
        log(result.stderr)
    log("migrate.py completed successfully.")
except subprocess.CalledProcessError as e:
    log(f"Error running migrate.py: {e}", 'error')
    if e.output:
        log(e.output, 'error')
    if e.stderr:
        log(e.stderr, 'error')
    exit(1)

# Step 5: Copy updated core.config_entries back
try:
    log("Copying updated core.config_entries back to original location...")
    with open(LOCAL_CORE_CONFIG_FILE, 'r', encoding='utf-8') as src, \
         open(CORE_CONFIG_FILE, 'w', encoding='utf-8') as dst:
        dst.write(src.read())
    log("File restored successfully.")
except Exception as e:
    log(f"Error restoring updated file: {e}", 'error')
    exit(1)

log("Process completed successfully!")

# TODO: Add MQTT connection retry logic
# TODO: Add confirmation of reboot command receipt
# TODO: Add timeout handling for MQTT operations

# Publish MQTT message to request a Home Assistant reboot
try:
    log("Publishing MQTT reboot message...")
    client = mqtt.Client()
    
    # Configure authentication if credentials are provided
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    
    # Connect with 60 second keepalive, publish message, then cleanup
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.publish(MQTT_TOPIC, "reboot")
    client.disconnect()
    log(f"MQTT reboot message published to topic '{MQTT_TOPIC}'.")
except Exception as e:
    # Non-fatal error as the migration has already completed
    log(f"Error publishing MQTT message: {e}", 'error')

