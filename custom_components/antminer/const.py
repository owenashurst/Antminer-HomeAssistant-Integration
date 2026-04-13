"""Constants for the Antminer integration."""

DOMAIN = "antminer"

DEFAULT_PORT = 80
DEFAULT_USERNAME = "root"
DEFAULT_PASSWORD = "root"
DEFAULT_SCAN_INTERVAL = 30

# Mapping from the value returned by GET bitmain-work-mode → display name.
# POST uses the key "miner-mode" with an integer value.
# S19k Pro firmware: 0 = Normal, 1 = Sleep, 2 = High Performance.
MINER_MODES: dict[str, str] = {
    "0": "Normal",
    "1": "Sleep",
    "2": "High Performance",
}

MODES_LIST: list[str] = list(MINER_MODES.values())
MODES_BY_NAME: dict[str, str] = {v: k for k, v in MINER_MODES.items()}
