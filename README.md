# Tuya Device Migration Tool for Home Assistant

A robust Python-based utility designed to automate the migration of Tuya device configurations in Home Assistant. This tool handles the complete migration process including device scanning, configuration backup, migration, and automatic system reboot via MQTT.

## Features

- **Automated Device Discovery**: Utilizes `tinytuya` to scan and identify Tuya devices on your network
- **Safe Configuration Management**:
  - Automatic backup of Home Assistant's core configuration
  - Local configuration snapshot creation
  - Secure restoration of migrated configurations
- **MQTT Integration**:
  - Automatic Home Assistant reboot triggering post-migration
  - Configurable MQTT broker settings
- **Robust Error Handling**:
  - Comprehensive logging system
  - Detailed error reporting
  - Fail-safe backup mechanisms
- **Environment-based Configuration**:
  - Flexible configuration through environment variables
  - Secure handling of sensitive information

## Prerequisites

- Python 3.x
- Home Assistant installation with Tuya devices
- MQTT broker (for automatic reboot functionality)
- Network access to Tuya devices
- Required Python packages:
  - `paho-mqtt>=1.6.1`
  - `python-dotenv>=1.0.0`
  - `tinytuya>=1.13.0`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Nasawa/update_tuya_ips.git
   cd tuya-migration-tool
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   ```

4. Edit the `.env` file with your specific configuration

## Configuration

Configure the following environment variables in your `.env` file:

### File Paths
- `CORE_CONFIG_FILE`: Path to Home Assistant's core.config_entries file
- `BACKUP_FILE`: Location for configuration backup
- `LOCAL_CORE_CONFIG_FILE`: Local working copy path
- `SNAPSHOT_FILE`: Path for configuration snapshot

### MQTT Settings
- `MQTT_BROKER`: MQTT broker hostname/IP
- `MQTT_PORT`: Broker port (default: 1883)
- `MQTT_USERNAME`: MQTT authentication username
- `MQTT_PASSWORD`: MQTT authentication password
- `MQTT_TOPIC`: Topic for reboot commands

### Logging Configuration
- `LOG_FILE`: Log file path
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `LOG_FORMAT`: Log message format

## Usage

1. Set up your environment variables as described above

2. Run the migration tool:
   ```bash
   python full_migrate.py
   ```

The tool will:
1. Scan for Tuya devices on your network
2. Back up your current Home Assistant configuration
3. Create a local copy of the configuration
4. Run the migration process
5. Restore the updated configuration
6. Trigger a Home Assistant reboot via MQTT

### Expected Output

```
Running tinytuya scan...
Backing up core.config_entries...
Copying core.config_entries to local directory...
Running migrate.py...
Copying updated core.config_entries back to original location...
Process completed successfully!
Publishing MQTT reboot message...
```

### Error Handling

The tool includes comprehensive error handling and will:
- Create backups before any modifications
- Log all operations with timestamps
- Provide detailed error messages if issues occur
- Exit safely if critical errors are encountered

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Open a Pull Request

### Reporting Issues

When reporting issues, please include:
- Detailed description of the problem
- Relevant log outputs
- Your environment configuration (excluding sensitive data)
- Steps to reproduce the issue

### Pull Request Process

1. Ensure your code follows the existing style
2. Update documentation as needed
3. Add or update tests as appropriate
4. Verify all tests pass
5. Update the README.md if needed
