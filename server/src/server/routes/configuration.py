import fastapi
from pydantic import BaseModel

from server.routes.wifi import (
    custom_generate_unique_id,
    WiFiConfig,
    WiFiStatus,
    get_current_wifi_status,
    set_regulatory_country,
    connect_to_wifi,
)
from server.routes.favourites import (
    FavouritesConfig,
    read_favourites_file,
    write_favourites_file,
    restart_display_service,
)
from server.routes.asl import (
    ASLConfig,
    ASLStatus,
    configure_asl3,
    restart_asterisk,
    set_allmon3_password,
    restart_allmon3,
    set_rln_user_password,
)


router = fastapi.APIRouter(
    prefix="/api/configuration", generate_unique_id_function=custom_generate_unique_id
)


# Request/Response models for unified endpoint


class SectionResult(BaseModel):
    success: bool
    message: str
    error: str | None = None


class ConfigurationResponse(BaseModel):
    favourites: FavouritesConfig
    wifi: WiFiStatus
    asl: ASLStatus


class ConfigurationRequest(BaseModel):
    update_favourites: bool = False
    update_wifi: bool = False
    update_asl: bool = False
    favourites: FavouritesConfig | None = None
    wifi: WiFiConfig | None = None
    asl: ASLConfig | None = None


class ConfigurationUpdateResponse(BaseModel):
    success: bool
    results: dict[str, SectionResult]


@router.get("")
def get_configuration() -> ConfigurationResponse:
    """Get current configuration (passwords returned as empty)"""
    return ConfigurationResponse(
        favourites=read_favourites_file(),
        wifi=get_current_wifi_status(),
        asl=ASLStatus(),  # No way to read current ASL config
    )


@router.post("")
def update_configuration(request: ConfigurationRequest) -> ConfigurationUpdateResponse:
    """Update selected configuration sections"""
    results: dict[str, SectionResult] = {}
    overall_success = True

    # Update favourites if requested
    if request.update_favourites:
        if request.favourites is None:
            results["favourites"] = SectionResult(
                success=False, message="No favourites data provided"
            )
            overall_success = False
        else:
            try:
                write_favourites_file(request.favourites)
                restart_result = restart_display_service()
                if restart_result.success:
                    results["favourites"] = SectionResult(
                        success=True, message="Updated and display service restarted"
                    )
                else:
                    results["favourites"] = SectionResult(
                        success=False,
                        message="File saved but service restart failed",
                        error=restart_result.stderr,
                    )
                    overall_success = False
            except Exception as e:
                results["favourites"] = SectionResult(
                    success=False, message="Failed", error=str(e)
                )
                overall_success = False

    # Update WiFi if requested
    if request.update_wifi:
        if request.wifi is None:
            results["wifi"] = SectionResult(
                success=False, message="No WiFi data provided"
            )
            overall_success = False
        else:
            errors = []

            # Set country code
            country_success, country_msg = set_regulatory_country(request.wifi.country)
            if not country_success:
                errors.append(f"Country: {country_msg}")

            # Connect to WiFi
            wifi_success, wifi_msg = connect_to_wifi(
                request.wifi.ssid, request.wifi.password
            )
            if not wifi_success:
                errors.append(f"Connection: {wifi_msg}")

            if wifi_success:
                results["wifi"] = SectionResult(
                    success=True, message=f"Connected to {request.wifi.ssid}"
                )
            else:
                results["wifi"] = SectionResult(
                    success=False, message="Failed", error="; ".join(errors)
                )
                overall_success = False

    # Update ASL if requested
    if request.update_asl:
        if request.asl is None:
            results["asl"] = SectionResult(
                success=False, message="No ASL data provided"
            )
            overall_success = False
        else:
            errors = []

            # Step 1: Run configure-asl3.sh
            success, msg = configure_asl3(
                request.asl.node_number,
                request.asl.callsign,
                request.asl.node_password,
            )
            if not success:
                errors.append(f"configure-asl3: {msg}")

            # Step 2: Restart asterisk
            success, msg = restart_asterisk()
            if not success:
                errors.append(f"asterisk: {msg}")

            # Step 3: Set allmon3 password
            success, msg = set_allmon3_password(request.asl.login_password)
            if not success:
                errors.append(f"allmon3 password: {msg}")

            # Step 4: Restart allmon3
            success, msg = restart_allmon3()
            if not success:
                errors.append(f"allmon3: {msg}")

            # Step 5: Set rln user password
            success, msg = set_rln_user_password(request.asl.login_password)
            if not success:
                errors.append(f"user password: {msg}")

            if not errors:
                results["asl"] = SectionResult(
                    success=True, message="ASL configured successfully"
                )
            else:
                results["asl"] = SectionResult(
                    success=False,
                    message="ASL configuration had errors",
                    error="; ".join(errors),
                )
                overall_success = False

    return ConfigurationUpdateResponse(success=overall_success, results=results)
