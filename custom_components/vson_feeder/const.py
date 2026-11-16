"""Constants for the VSON Fish Feeder integration."""

DOMAIN = "vson_feeder"
CONF_MAC = "mac"
DEFAULT_NAME = "智能喂鱼器"
DEFAULT_SCAN_INTERVAL = 30  # seconds

API_BASE_URL = "https://apis.myvsoncloud.com:16082"

# Endpoints for WP8615 (dual hopper)
ENDPOINT_QUERY_BLY_HOMEPAGE = "/vc-air-ws-1.0.2/api/air/queryBlywHomepage"
ENDPOINT_UPDATE_BLY_FEED = "/vc-air-ws-1.0.2/api/air/updateBlywFeed"
ENDPOINT_UPDATE_BLY_RESET = "/vc-air-ws-1.0.2/api/air/updateBlywReset"

# Endpoints for WP8621 / WP8621N (with pump & single feed)
ENDPOINT_QUERY_BLE_HOMEPAGE = "/vc-air-ws-1.0.2/api/air/queryBleyHomepage"
ENDPOINT_UPDATE_BLE_FEED = "/vc-air-ws-1.0.2/api/air/updateBleyFeed"
ENDPOINT_UPDATE_BLE_RESET = "/vc-air-ws-1.0.2/api/air/updateBleyReset"
ENDPOINT_UPDATE_BLE_PUMP = "/vc-air-ws-1.0.2/api/air/updateBleyPump"

DEFAULT_HEADERS = {
    "bh": "JmnuSXWflZY=",
    "md": "WP2810",
    "pid": "cup033",
    "ost": "2",
    "apt": "108",
    "apv": "2.2.0",
    "cm": "1",
    "mac": "S+T1TP5Nrak=",
    "uuid": "ScqUePab+h0=",
    "language": "zh-CN",
    "timeZone": "Asia/Shanghai",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; Build/SQ3A.220705.004)",
}
