from typing import Literal


class BaseConfig:
    ADDED_MESSENGERS = Literal["vk", "tg"]
    BUTTONS_COLORS = Literal["primary", "secondary", "positive", "negative"]
    DEBUG_STATE: bool = True
    MAX_BUTTONS_IN_ROW = 4
    MAX_BUTTON_ROWS = 9
    MAX_BUTTONS_AMOUNT = 10
