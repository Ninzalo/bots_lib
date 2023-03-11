from dataclasses import dataclass
from bots.base_config import BaseConfig


@dataclass()
class Message_struct:
    def __init__(
        self,
        user_id: int,
        messenger: BaseConfig.ADDED_MESSENGERS = BaseConfig.ADDED_MESSENGERS,
        text: str | None = None,
        payload: dict | None = None,
        base_config: BaseConfig = BaseConfig,
    ) -> None:
        self.user_id = user_id
        self.text = text
        self.payload = payload
        self._config = base_config
        self.messenger = messenger
