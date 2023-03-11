from dataclasses import dataclass
from bots.base_config import BaseConfig


@dataclass()
class Message_struct:
    user_id: int
    messenger: BaseConfig.ADDED_MESSENGERS = BaseConfig.ADDED_MESSENGERS
    text: str | None = None
    payload: dict | None = None
