# Avalon Miner – Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Home Assistant custom integration for **Canaan Avalon** cryptocurrency miners (Nano 3S, Q and compatible models).

Communicates directly with the miner via **TCP socket on port 4028** (cgminer API) – no cloud, no extra dependencies.

## Features

- Real-time monitoring of hashrate, temperature, fan speed, power consumption
- Control fan speed, work mode (Eco / Standard / Super), and target temperature
- Pool connectivity status and active pool info
- Reboot and filter-clean-reset buttons
- Automatic device discovery via DNA serial number

## Installation

### HACS (recommended)

1. Open **HACS** in Home Assistant
2. Go to **Integrations** → three-dot menu → **Custom repositories**
3. Add the repository URL, category **Integration**
4. Search for "Avalon Miner" and install
5. Restart Home Assistant

### Manual

Copy the `custom_components/avalon_miner` folder into your Home Assistant `config/custom_components/` directory and restart.

## Configuration

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for **Avalon Miner**
3. Enter the miner's IP address, port (default 4028), and polling interval (default 30 s)
4. The integration auto-detects model and serial number

## Entities

| Platform | Entities | Description |
|----------|----------|-------------|
| Binary Sensor | 2 | Miner running, Pool connected |
| Sensor | 27 | Hashrate (6), Temperature (6), Fan (5), Power/Mining (6), Status (4) |
| Number | 2 | Fan Speed (0 = Auto, 25-100%), Target Temperature (50-90 °C) |
| Select | 1 | Work Mode (Eco / Standard / Super) |
| Button | 2 | Reboot, Reset Filter Clean |

## Supported Devices

- Canaan Avalon Nano 3S
- Canaan Avalon Q
- Other Avalon miners with cgminer API on port 4028

## License

Apache-2.0
