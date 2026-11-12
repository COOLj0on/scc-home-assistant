"""Constants for the Chriselec SCC integration."""

DOMAIN = "scc"

CONF_HOST = "host"
CONF_PATH = "path"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_SENSORS = "sensors"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_HOST = ""
DEFAULT_PATH = "/medius_val.xml"
DEFAULT_SCAN_INTERVAL = 30
MIN_SCAN_INTERVAL = 5
MAX_SCAN_INTERVAL = 3600
REQUEST_TIMEOUT_SECONDS = 10
MAX_RESPONSE_BYTES = 16_384

SENSOR_NAMES = {
    "S1": "S1 - Sonde capteurs solaires",
    "S2": "S2 - Sonde bas de ballon",
    "S3": "S3 - Sonde haut de ballon",
    "S4": "S4 - Sonde départ capteurs solaires",
    "S5": "S5 - Sonde 5",
    "S6": "S6 - Sonde poêle bouilleur",
    "S7": "S7 - Sonde retour capteurs solaires",
    "S8": "S8 - Sonde milieu de ballon",
    "S9": "S9 - Sonde de départ zone 1",
    "S10": "S10 - Sonde extérieur",
    "Str": "Puissance (Str)",
    "R1": "Relais R1",
    "R2": "Relais R2",
    "R3": "Relais R3",
    "R4": "Relais R4",
    "R5": "Relais R5",
    "R6": "Relais R6",
    "R7": "Relais R7",
    "R0": "Relais R0",
    "HE1": "Pompe HE1",
    "HE2": "Pompe HE2",
    "HE3": "Pompe HE3",
    "Q1": "Énergie Q1",
    "Q2": "Énergie Q2",
    "F1S1": "F1S1 - Sonde départ zone 2",
    "F1S2": "F1S2 - Sonde Flex 1.2",
    "F1S3": "F1S3 - Sonde Flex 1.3",
    "F1S4": "F1S4 - Sonde Flex 1.4",
    "F1R1": "Relais F1R1",
    "F1R2": "Relais F1R2",
    "F1R3": "Relais F1R3",
}

SENSOR_KEYS = tuple(SENSOR_NAMES)
TEMPERATURE_SENSOR_KEYS = frozenset(
    {
        *(f"S{index}" for index in range(1, 11)),
        *(f"F1S{index}" for index in range(1, 5)),
    }
)
PERCENTAGE_SENSOR_KEYS = frozenset(
    {
        *(f"R{index}" for index in range(8)),
        *(f"HE{index}" for index in range(1, 4)),
    }
)
