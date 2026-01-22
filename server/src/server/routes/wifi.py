import fastapi
from fastapi.routing import APIRoute
from pydantic import BaseModel

from server.utils.subprocess_runner import run_sudo_command


def custom_generate_unique_id(route: APIRoute) -> str:
    tag = route.tags[0] if route.tags else "default"
    safe_name = "".join(c if c.isalnum() else "_" for c in route.name)
    method = sorted(route.methods)[0].lower() if route.methods else "get"
    return f"{tag}_{safe_name}_{method}"


router = fastapi.APIRouter(
    prefix="/api/wifi", generate_unique_id_function=custom_generate_unique_id
)


class WiFiConfig(BaseModel):
    ssid: str
    password: str
    country: str


class WiFiStatus(BaseModel):
    connected: bool
    ssid: str | None = None
    country: str | None = None


class WiFiResult(BaseModel):
    success: bool
    message: str
    error: str | None = None


class ErrorResponse(BaseModel):
    detail: str


def get_current_wifi_status() -> WiFiStatus:
    """Get current WiFi connection status using nmcli"""
    result = run_sudo_command(["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"])

    ssid = None
    if result.success:
        for line in result.stdout.strip().split("\n"):
            if line.startswith("yes:"):
                ssid = line.split(":", 1)[1]
                break

    # Get current regulatory country
    country = None
    reg_result = run_sudo_command(["iw", "reg", "get"])
    if reg_result.success:
        for line in reg_result.stdout.split("\n"):
            if "country" in line.lower():
                parts = line.split()
                if len(parts) >= 2:
                    country = parts[1].rstrip(":")
                    break

    return WiFiStatus(connected=ssid is not None, ssid=ssid, country=country)


def set_regulatory_country(country: str) -> tuple[bool, str]:
    """Set WiFi regulatory country code"""
    result = run_sudo_command(["iw", "reg", "set", country.upper()])
    if result.success:
        return True, f"Country set to {country.upper()}"
    return False, result.stderr


def connect_to_wifi(ssid: str, password: str) -> tuple[bool, str]:
    """Connect to WiFi network using nmcli"""
    result = run_sudo_command(
        ["nmcli", "dev", "wifi", "connect", ssid, "password", password],
        timeout=60,
    )
    if result.success:
        return True, f"Connected to {ssid}"
    return False, result.stderr


@router.get("")
def get_wifi_status() -> WiFiStatus:
    """Get current WiFi connection status"""
    return get_current_wifi_status()


@router.post("")
def set_wifi(config: WiFiConfig) -> WiFiResult:
    """Configure WiFi: set country code and connect to network"""
    errors = []

    # Set regulatory country first
    country_success, country_msg = set_regulatory_country(config.country)
    if not country_success:
        errors.append(f"Country code: {country_msg}")

    # Connect to WiFi
    wifi_success, wifi_msg = connect_to_wifi(config.ssid, config.password)
    if not wifi_success:
        errors.append(f"WiFi connection: {wifi_msg}")

    if wifi_success:
        return WiFiResult(
            success=True,
            message=f"Connected to {config.ssid}",
        )
    else:
        return WiFiResult(
            success=False,
            message="Failed to connect",
            error="; ".join(errors),
        )
