from dataclasses import dataclass
from bots.base_config.base_config import ADDED_MESSENGERS


@dataclass()
class Message_struct:
    user_id: int
    messenger: ADDED_MESSENGERS
    text: str | None = None
    payload: dict | None = None
