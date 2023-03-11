import inspect
from typing import Coroutine
from bots.base_config import BaseConfig
from bots.bot.returns.message import Returns
from bots.bot.struct import Message_struct
from bots.bot.transitions.transitions import Transitions


class Message_handler:
    def __init__(
        self,
        user_stage_getter: Coroutine,
        transitions: Transitions,
        base_config: BaseConfig = BaseConfig,
    ) -> None:
        """
        param user_stage_getter: Should receive 'user_messenger_id' and 'user_messenger'
        """
        self._transitions = transitions
        self._user_stage_getter = user_stage_getter
        self._config = base_config
        if self._config.DEBUG_STATE:
            print(f"Added user stage getter: {user_stage_getter}")
        self._checks()

    async def get(self, message_class: Message_struct) -> Returns:
        user_stage = await self._user_stage_getter(
            message_class.user_id, message_class.messenger
        )
        return_cls = await self._transitions.run(
            user_messenger_id=message_class.user_id,
            user_messenger=message_class.messenger,
            user_stage=user_stage,
            message=message_class,
        )
        return return_cls

    def _checks(self) -> None:
        if not self._transitions._compiled:
            raise RuntimeError(f"Transitions aren't compiled")
        if inspect.getfullargspec(self._user_stage_getter)[0] != [
            "user_messenger_id",
            "user_messenger",
        ]:
            raise RuntimeError(
                "User stage getter don't receive 'user_messenger_id' "
                "and 'user_messenger'"
            )
        if self._config.DEBUG_STATE:
            print(f"Message handler checks passed")
