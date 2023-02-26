from dataclasses import dataclass, field
from typing import List
from .buttons import Buttons, Inline_buttons
from base_config.base_config import ADDED_MESSENGERS


@dataclass()
class Return:
    user_id: int
    user_messenger: ADDED_MESSENGERS
    text: str
    keyboard: Buttons | None = None
    inline_keyboard: Inline_buttons | None = None


@dataclass()
class Returns:
    returns: List[Return] = field(default_factory=list)

    async def add_return(
        self,
        user_id: int,
        user_messenger: ADDED_MESSENGERS,
        text: str,
        keyboard: Buttons | None = None,
        inline_keyboard: Inline_buttons | None = None,
    ):
        new_return = Return(
            user_id=user_id,
            user_messenger=user_messenger,
            text=text,
            keyboard=keyboard,
            inline_keyboard=inline_keyboard,
        )
        if new_return not in self.returns:
            self.returns.append(new_return)
