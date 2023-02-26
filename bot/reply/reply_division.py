from dataclasses import dataclass, field
from typing import List, Any
from bot.returns.message import Return
from base_config import ADDED_MESSENGERS


@dataclass()
class _Messenger:
    trigger: ADDED_MESSENGERS
    reply_func: Any


@dataclass()
class Messengers_division:
    _messengers_to_answer: List[_Messenger] = field(default_factory=list)
    _compiled: bool = False

    def register_messenger(
        self, trigger: ADDED_MESSENGERS, reply_func: Any
    ) -> None:
        if self._compiled:
            error_str = (
                f"Messengers already compiled"
                f"\nEnsure to add messengers before compiling"
            )
            raise ValueError(error_str)
        new_messenger_to_reply = _Messenger(
            trigger=trigger, reply_func=reply_func
        )
        if new_messenger_to_reply in self._messengers_to_answer:
            error_str = f"Messenger already registered"
            raise ValueError(error_str)
        if reply_func in [
            func.reply_func for func in self._messengers_to_answer
        ]:
            error_str = f"Same reply func already used"
            raise ValueError(error_str)
        self._messengers_to_answer.append(new_messenger_to_reply)

    def compile(self) -> None:
        if self._compiled:
            raise ValueError(f"Messengers already compiled")
        if not self._compiled:
            self._compiled = True

    async def get_func(
        self, messenger: ADDED_MESSENGERS, return_cls: Return
    ) -> None:
        if self._compiled:
            for existing_messenger in self._messengers_to_answer:
                if existing_messenger.trigger == messenger:
                    await existing_messenger.reply_func(return_cls)
                    return
            error_str = (
                f"[ERROR] Needed messenger '{messenger}' wasn't registered"
            )
            print(error_str)
