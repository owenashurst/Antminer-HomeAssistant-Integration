# Antminer Home Assistant Integration

A Home Assistant integration for **Bitmain Antminer** miners (tested on S19k Pro). Install via HACS by adding this as a custom repository.

## Features

- **Real-time statistics** – 5-second hashrate, 30-minute average hashrate, overall average hashrate, ideal hashrate, miner uptime, hardware errors, and best share
- **Mode control** – Switch between Normal (120 TH/s), Sleep (idle), and High Performance (140 TH/s) modes
- **Fan control** – Toggle between automatic and manual fan speed, with a slider for the PWM percentage

## Installation via HACS

1. Open HACS in your Home Assistant instance
2. Go to **Integrations**
3. Click the three-dot menu → **Custom repositories**
4. Paste this repository URL and select category **Integration**
5. Click **Add** → search for **Antminer** → **Download**
6. Restart Home Assistant

## Manual Installation

1. Copy the `custom_components/antminer` folder into your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

Navigate to **Settings → Devices & Services → Add Integration → Antminer S19k Pro**.

| Field | Default | Description |
|-------|---------|-------------|
| IP Address / Hostname | – | Your miner's IP, e.g. `192.168.0.223` |
| Port | `80` | HTTP port |
| Username | `root` | CGI auth username |
| Password | `root` | CGI auth password |

## Entities

### Sensors

| Entity | Unit | Description |
|--------|------|-------------|
| Hashrate (5s) | TH/s | Real-time 5-second hashrate |
| Hashrate (30m avg) | TH/s | 30-minute rolling average |
| Hashrate (average) | TH/s | Overall session average |
| Ideal Hashrate | TH/s | Theoretical maximum hashrate |
| Running Time | s | Miner uptime |
| HW Errors | – | Cumulative hardware error count |
| Best Share | – | Highest share difficulty submitted |
| Miner Type | – | Detected model string |

### Controls

| Entity | Description |
|--------|-------------|
| Mining Mode | Select between **Normal**, **Sleep**, and **High Performance** |
| Fan Speed | PWM percentage (0–100). Setting this also enables manual fan control. |
| Manual Fan Control | Switch: ON = manual PWM, OFF = miner auto-controls fans |

## Notes

- Settings (mode, fan speed) are applied immediately when changed in Home Assistant.
- Data is polled every 30 seconds.
- Pool rejection rate is not exposed by the Antminer CGI API and is therefore not available.
- Miner mode values: `0` = Normal, `1` = Sleep, `2` = High Performance. Adjust `const.py → MINER_MODES` if your firmware uses different values.
