from pathlib import Path
from typing import List
import fastapi
from pydantic import BaseModel

from server.routes.wifi import custom_generate_unique_id
from server.utils.subprocess_runner import run_sudo_command, CommandResult


FAVOURITES_PATH = Path("/home/rln/favourites.txt")
DISPLAY_SERVICE = "rlnz2-display.service"

# Default favourites from spec
DEFAULT_FAVOURITES = [
    {"name": "Hubnet", "node_number": "41223"},
    {"name": "Freestar", "node_number": "63061"},
    {"name": "EC Reflector", "node_number": "27339"},
    {"name": "Win System", "node_number": "2560"},
    {"name": "DoDropin", "node_number": "3546"},
    {"name": "Parrot", "node_number": "40894"},
]


class FavouriteItem(BaseModel):
    name: str
    node_number: str


class FavouritesConfig(BaseModel):
    items: List[FavouriteItem]


class FavouritesResult(BaseModel):
    success: bool
    message: str
    error: str | None = None


router = fastapi.APIRouter(
    prefix="/api/favourites", generate_unique_id_function=custom_generate_unique_id
)


def read_node_number_from_file() -> str | None:
    """Read the node number from the first line of the favourites file"""
    if not FAVOURITES_PATH.exists():
        return None
    with open(FAVOURITES_PATH) as f:
        first_line = f.readline().strip()
        # First line should be just a node number (digits only)
        if first_line and first_line.isdigit():
            return first_line
    return None


DEFAULT_NODE_NUMBER = "99999"


def write_favourites_file(config: FavouritesConfig, node_number: str | None = None) -> None:
    """Write favourites to file with node number as first line, then name,node_number per line.
    If node_number not provided, reads existing one from file or defaults to 99999."""
    if node_number is None:
        node_number = read_node_number_from_file()
    if node_number is None:
        node_number = DEFAULT_NODE_NUMBER

    with open(FAVOURITES_PATH, "w") as f:
        f.write(f"{node_number}\n")
        for item in config.items:
            f.write(f"{item.name},{item.node_number}\n")


def read_favourites_file() -> FavouritesConfig:
    """Read favourites from file. First line is node number (skipped), rest are name,node_number"""
    if not FAVOURITES_PATH.exists():
        return FavouritesConfig(items=[FavouriteItem(**f) for f in DEFAULT_FAVOURITES])

    items: List[FavouriteItem] = []
    with open(FAVOURITES_PATH) as f:
        lines = f.readlines()
        # Skip first line if it's a node number (digits only)
        start_idx = 0
        if lines and lines[0].strip().isdigit():
            start_idx = 1

        for line in lines[start_idx:]:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) == 2:
                items.append(FavouriteItem(name=parts[0], node_number=parts[1]))

    # Pad with defaults if fewer than 6
    while len(items) < 6:
        idx = len(items)
        if idx < len(DEFAULT_FAVOURITES):
            items.append(FavouriteItem(**DEFAULT_FAVOURITES[idx]))
        else:
            items.append(FavouriteItem(name="", node_number=""))

    return FavouritesConfig(items=items[:6])  # Max 6 items


def write_node_number_to_favourites_file(node_number: str) -> None:
    """Update only the node number in the favourites file, preserving existing favourites"""
    existing_config = read_favourites_file()
    write_favourites_file(existing_config, node_number)


def restart_display_service() -> CommandResult:
    """Restart the display service"""
    return run_sudo_command(["systemctl", "restart", DISPLAY_SERVICE])


@router.get("")
def get_favourites() -> FavouritesConfig:
    """Get current favourites configuration"""
    return read_favourites_file()


@router.post("")
def set_favourites(config: FavouritesConfig) -> FavouritesResult:
    """Save favourites and restart display service"""
    try:
        write_favourites_file(config)
        result = restart_display_service()

        if result.success:
            return FavouritesResult(
                success=True, message="Updated and display service restarted"
            )
        else:
            return FavouritesResult(
                success=False,
                message="File saved but service restart failed",
                error=result.stderr,
            )
    except Exception as e:
        return FavouritesResult(success=False, message="Failed to save", error=str(e))
