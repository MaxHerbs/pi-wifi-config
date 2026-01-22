import fastapi
from pydantic import BaseModel

from server.routes.wifi import custom_generate_unique_id
from server.utils.subprocess_runner import run_sudo_command


CONFIGURE_ASL_SCRIPT = "/home/rln/configure-asl3.sh"


class ASLConfig(BaseModel):
    node_number: str
    node_password: str
    callsign: str
    login_password: str


class ASLStatus(BaseModel):
    node_number: str | None = None
    callsign: str | None = None


class ASLResult(BaseModel):
    success: bool
    message: str
    error: str | None = None


router = fastapi.APIRouter(
    prefix="/api/asl", generate_unique_id_function=custom_generate_unique_id
)


def configure_asl3(node_number: str, callsign: str, password: str) -> tuple[bool, str]:
    """Run configure-asl3.sh script"""
    result = run_sudo_command(
        [CONFIGURE_ASL_SCRIPT, "-n", node_number, "-c", callsign, "-p", password],
        timeout=60,
    )
    if result.success:
        return True, "ASL3 configured"
    return False, result.stderr or result.stdout


def restart_asterisk() -> tuple[bool, str]:
    """Restart asterisk service"""
    result = run_sudo_command(["systemctl", "restart", "asterisk.service"])
    if result.success:
        return True, "Asterisk restarted"
    return False, result.stderr


def set_allmon3_password(password: str) -> tuple[bool, str]:
    """Set allmon3 password for rln user"""
    result = run_sudo_command(["allmon3-passwd", "--password", password, "rln"])
    if result.success:
        return True, "Allmon3 password set"
    return False, result.stderr


def restart_allmon3() -> tuple[bool, str]:
    """Restart allmon3 service"""
    result = run_sudo_command(["systemctl", "restart", "allmon3"])
    if result.success:
        return True, "Allmon3 restarted"
    return False, result.stderr


def set_rln_user_password(password: str) -> tuple[bool, str]:
    """Set rln user system password using chpasswd"""
    result = run_sudo_command(
        ["chpasswd"],
        input_text=f"rln:{password}\n",
    )
    if result.success:
        return True, "User password set"
    return False, result.stderr


@router.get("")
def get_asl_status() -> ASLStatus:
    """Get current ASL status (passwords not returned)"""
    # We don't have a reliable way to read current config
    # Return empty status - frontend will show empty fields
    return ASLStatus()


@router.post("")
def set_asl(config: ASLConfig) -> ASLResult:
    """Configure ASL: run configure script, restart services, set passwords"""
    errors = []

    # Step 1: Run configure-asl3.sh
    success, msg = configure_asl3(
        config.node_number, config.callsign, config.node_password
    )
    if not success:
        errors.append(f"configure-asl3: {msg}")

    # Step 2: Restart asterisk
    success, msg = restart_asterisk()
    if not success:
        errors.append(f"asterisk restart: {msg}")

    # Step 3: Set allmon3 password
    success, msg = set_allmon3_password(config.login_password)
    if not success:
        errors.append(f"allmon3 password: {msg}")

    # Step 4: Restart allmon3
    success, msg = restart_allmon3()
    if not success:
        errors.append(f"allmon3 restart: {msg}")

    # Step 5: Set rln user password
    success, msg = set_rln_user_password(config.login_password)
    if not success:
        errors.append(f"user password: {msg}")

    if not errors:
        return ASLResult(success=True, message="ASL configured successfully")
    else:
        return ASLResult(
            success=False,
            message="ASL configuration had errors",
            error="; ".join(errors),
        )
