"""Constants for the Provident Energy integration."""

DOMAIN = "provident_energy"

# Configuration
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

# Default values
DEFAULT_NAME = "Provident Energy"
DEFAULT_SCAN_INTERVAL = 3600  # 1 hour

# API endpoints
API_BASE_URL = "https://provident.meterconnex.com"
API_LOGIN_ENDPOINT = "/login/LoginService.aspx/ProcessLogin"
API_GET_UTILITIES_ENDPOINT = "/secure/Dashboard/Default.aspx/GetUtilities"
API_UPDATE_CARD_ENDPOINT = "/secure/Dashboard/Default.aspx/UpdateCard"
API_GET_CHART_DATA_ENDPOINT = "/secure/Dashboard/Default.aspx/GetChartData"
API_ROOT_NODES_ENDPOINT = "/api/internal/metertree/rootnodes"
API_QUICKGRAPHS_ENDPOINT = "/api/internal/graphs/quickgraphs"

API_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0"

# Data keys
DATA_ELECTRICITY = "electricity"
DATA_GAS = "gas"
DATA_WATER = "water"
DATA_COLD_WATER = "cold_water"

# Utility types
UTILITY_ELECTRICITY = "Electricity"
UTILITY_COLD_WATER = "Cold Water"
UTILITY_HOT_WATER = "Hot Water"
UTILITY_COOLING = "Cooling"
UTILITY_HEATING = "Heating"

# Units of measurement
ENERGY_KILOWATT_HOUR = "kWh"
VOLUME_CUBIC_METERS = "m³"

UTILITY_UNITS = {
    UTILITY_ELECTRICITY: ENERGY_KILOWATT_HOUR,
    UTILITY_COLD_WATER: VOLUME_CUBIC_METERS,
    UTILITY_HOT_WATER: VOLUME_CUBIC_METERS,
    UTILITY_COOLING: ENERGY_KILOWATT_HOUR,
    UTILITY_HEATING: ENERGY_KILOWATT_HOUR
}
