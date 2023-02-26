from dataclasses import dataclass, field
from typing import Any, List

from bots.bot.struct import Message_struct
from bots.bot.transitions.payloads import Payloads


@dataclass()
class Transition:
    trigger: str | None
    from_stage: str
    to_stage: Any


@dataclass()
class Transitions:
    """
    param payloads: Should be Payloads class
    """

    transitions: List[Transition] = field(default_factory=list)
    payloads: Payloads | None = None
    _compiled: bool = False

    def add_transition(self, trigger: str | None, src: str, dst: Any):
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
                raise ValueError("Multiple 'else' blocks doesn't supported")

            self.transitions.append(new_transition)
        else:
            self.transitions.append(new_transition)

    def compile(self):
        if len(self.transitions) == 0:
            raise RuntimeError(f"Can't compile while no transitions added")
        self._add_none_transition_to_all_stages()
        self.transitions.sort(key=lambda src: src.from_stage)
        self._compiled = True

    async def run(
        self, user_id: str | int, user_stage: str, message: Message_struct
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
        if message.text != None:
            for transition in self._get_transitions_by_stage(stage=user_stage):
                if transition.trigger == message.text:
                    return transition.to_stage(user_id)

            else_transition = await self._get_none_transition_by_stage(
                stage=user_stage
            )
            return else_transition(user_id)
        elif message.payload != None:
            if self.payloads != None:
                output = await self.payloads.run(entry_dict=message.payload)
                if output.get("data") == {}:
                    return (output.get("dst"))(user_id)
                else:
                    return (output.get("dst"))(user_id, output.get("data"))

    def _counter_none(self, src: str) -> int:
        amount = 0
        for transition in self.transitions:
            if transition.trigger == None and transition.from_stage == src:
                amount += 1
        return amount

    def _counter_unique(
        self, trigger: str | dict | None, src: str, dst: Any
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
                    trigger=None, src=stage, dst="error_return"
                )
                added_none_transitions += 1
        return added_none_transitions

    def _check_none_transition_by_stage(self, stage: str) -> bool:
        for transition in self.transitions:
            if transition.trigger == None and transition.from_stage == stage:
                return True
        return False

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
        raise Exception("No transition without a trigger in the transitions")
