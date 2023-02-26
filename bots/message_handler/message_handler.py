from typing import Coroutine
from bots.bot.returns.message import Returns
from bots.bot.struct import Message_struct
from bots.bot.transitions.transitions import Transitions


class Message_handler:
    def __init__(
        self, user_stage_getter: Coroutine, transitions: Transitions
    ) -> None:
        """
        param user_stage_getter: Should receive 'user_id' and 'messenger'
        """
        self._transitions = transitions
        self._user_stage_getter = user_stage_getter
        self._checks()

    async def get(self, message_class: Message_struct) -> Returns:
        user_stage = await self._user_stage_getter(
            message_class.user_id, message_class.messenger
        )
        user_id = f"{message_class.user_id}{message_class.messenger}"
        return_cls = await self._transitions.run(
            user_id=user_id, user_stage=user_stage, message=message_class
        )
        return return_cls

    def _checks(self) -> None:
        if not self._transitions._compiled:
            raise RuntimeError(f"Transitions aren't compiled")
