import inspect
from emoji import replace_emoji
from dataclasses import dataclass, field
from typing import Coroutine, List
from bots.base_config import BaseConfig

from bots.bot.struct import Message_struct
from bots.bot.transitions.payloads import Payloads


@dataclass()
class Transition:
    trigger: str | None
    from_stage: str
    to_stage: Coroutine


@dataclass()
class Transitions:
    """
    FSM (finite state machine). Add transitions and compile before using

    param transitions: Added transitions
    param error_return: Coroutine with 'user_messenger_id'
    and 'user_messenger' args
    param payloads: Should be Payloads class
    """

    transitions: List[Transition] = field(default_factory=list)
    error_return: Coroutine | None = None
    payloads: Payloads | None = None
    config: BaseConfig = BaseConfig
    _compiled: bool = False

    def __post_init__(self):
        if self.config.DEBUG_STATE:
            if self.payloads == None:
                print(f"Payloads aren't added")

    def add_transition(
        self, trigger: str | None, src: str, dst: Coroutine
    ) -> None:
        new_transition = Transition(
            trigger=trigger, from_stage=src, to_stage=dst
        )
        if self._compiled:
            raise ValueError(
                "Transitions already compiled. "
                "Please, compile after adding all of the transitions"
            )
        if new_transition in self.transitions:
            raise ValueError("Transition already exists")

        if self._counter_unique(trigger=trigger, src=src, dst=dst) > 0:
            raise ValueError("Transition already realized by other trigger")

        if new_transition.trigger == None:
            if self._counter_none(src=src) > 0:
                raise ValueError("Multiple 'else' blocks aren't supported")
            self.transitions.append(new_transition)
        else:
            self.transitions.append(new_transition)
        if self.config.DEBUG_STATE:
            print(f"Added transition: {new_transition}")

    def add_error_return(self, error_func: Coroutine) -> None:
        self.error_return = error_func
        if self.config.DEBUG_STATE:
            print(f"Added error return: {error_func}")

    def compile(self) -> None:
        self._add_none_transition_to_all_stages()
        self._checks()
        self.transitions.sort(key=lambda src: src.from_stage)
        self._compiled = True
        if self.config.DEBUG_STATE:
            print(f"Transitions compiled successfully")

    async def run(
        self,
        user_messenger_id: int,
        user_messenger: BaseConfig.ADDED_MESSENGERS,
        user_stage: str,
        message: Message_struct,
    ):
        """
        Returns answer from transition
        param message: Should have .text/.payload
        """
        if not self._compiled:
            raise ValueError(
                "Transitions not compiled. "
                f"\nEnsure to compile transitions to run"
            )
        message.text = replace_emoji(message.text, replace="")
        if message.text != None:
            stage_transitions = await self._get_transitions_by_stage(
                stage=user_stage
            )
            for transition in stage_transitions:
                if transition.trigger == message.text.lower():
                    answer = await transition.to_stage(
                        user_messenger_id, user_messenger
                    )
                    return answer
            else_transition = await self._get_none_transition_by_stage(
                stage=user_stage
            )
            answer = await else_transition.to_stage(
                user_messenger_id, user_messenger
            )
            return answer
        elif message.payload != None:
            if self.payloads != None:
                output = await self.payloads.run(entry_dict=message.payload)
                if output.get("data") == {}:
                    return (output.get("dst"))(
                        user_messenger_id, user_messenger
                    )
                else:
                    return (output.get("dst"))(
                        user_messenger_id, user_messenger, output.get("data")
                    )

    def _counter_none(self, src: str) -> int:
        amount = 0
        for transition in self.transitions:
            if transition.trigger == None and transition.from_stage == src:
                amount += 1
        return amount

    def _counter_unique(
        self, trigger: str | dict | None, src: str, dst: Coroutine
    ) -> int:
        amount = 0
        for transition in self.transitions:
            if transition.from_stage == src and transition.to_stage == dst:
                if trigger is not None:
                    if transition.trigger is None:
                        amount += 1
                else:
                    if transition.trigger is not None:
                        amount += 1
        return amount

    def _get_all_source_stages(self) -> List[Transition]:
        return list(
            set([transition.from_stage for transition in self.transitions])
        )

    def _add_none_transition_to_all_stages(self) -> int:
        added_none_transitions = 0
        for stage in self._get_all_source_stages():
            if not self._check_none_transition_by_stage(stage=stage):
                self.add_transition(
                    trigger=None, src=stage, dst=self.error_return
                )
                added_none_transitions += 1
        return added_none_transitions

    def _check_none_transition_by_stage(self, stage: str) -> bool:
        for transition in self.transitions:
            if transition.trigger == None and transition.from_stage == stage:
                return True
        return False

    def _checks(self) -> None:
        if self.error_return == None:
            raise RuntimeError("Error return wasn't added")
        if len(self.transitions) == 0:
            raise RuntimeError(f"Can't compile while no transitions added")
        for transition in self.transitions:
            self._transition_args_check(func=transition.to_stage)
        self._transition_args_check(func=self.error_return)
        if self.payloads != None:
            if not self.payloads._compiled:
                raise RuntimeError(f"Payloads aren't compiled")

    def _transition_args_check(self, func: Coroutine) -> None:
        if inspect.getfullargspec(func)[0] != [
            "user_messenger_id",
            "user_messenger",
        ]:
            error_str = (
                f"Transition dst should have 'user_messenger_id' "
                f"and 'user_messenger' args:\n{func}"
            )
            raise ValueError(error_str)

    async def _get_transitions_by_stage(self, stage: str) -> List[Transition]:
        return [
            transition
            for transition in self.transitions
            if transition.from_stage == stage
        ]

    async def _get_none_transition_by_stage(self, stage: str) -> Transition:
        for transition in self.transitions:
            if transition.trigger == None and transition.from_stage == stage:
                return transition
        return self.error_return
