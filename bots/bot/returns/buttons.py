from typing import List
from dataclasses import dataclass, field
from bots.base_config.base_config import (
    BUTTONS_COLORS,
    DEBUG_STATE,
    MAX_BUTTONS_IN_ROW,
    MAX_BUTTON_ROWS,
    MAX_BUTTONS_AMOUNT,
)


@dataclass()
class _Button:
    label: str
    color: BUTTONS_COLORS
    new_line_after: bool = False


@dataclass()
class _Inline_button:
    label: str
    color: BUTTONS_COLORS
    payload: dict
    new_line_after: bool = False


@dataclass()
class Buttons:
    """
    Contains a list of buttons for the keyboard
    """

    buttons: List[_Button] = field(default_factory=list)
    _since_new_line = 0
    _rows = 0
    _buttons_amount = 0

    def add_button(self, label: str, color: BUTTONS_COLORS) -> None:
        """
        Adds a new button to a keyboard
        """
        if self._since_new_line >= MAX_BUTTONS_IN_ROW:
            self.add_line()
        self._since_new_line += 1
        self._buttons_amount += 1
        self.buttons.append(_Button(label=label, color=color))
        if DEBUG_STATE:
            print(f"[INFO] Added button: {self.buttons[-1]}")

    def add_line(self) -> None:
        """
        Adds new line after the last created button
        """
        if self._buttons_amount > 0:
            self.buttons[-1].new_line_after = True
            self._since_new_line = 0
            self._rows += 1
            if DEBUG_STATE:
                print(f"[INFO] Added line after: {self.buttons[-1]}")
        else:
            raise ValueError(f"[ERROR] Can't add new line, no buttons in list")

    def remove_last_button(self) -> None:
        """
        Removes the last button
        """
        if self._buttons_amount > 0:
            if DEBUG_STATE:
                print(f"[INFO] Last button: {self.buttons[-1]} removed")
            self.buttons.pop(-1)
            if self._since_new_line > 0:
                self._since_new_line -= 1
        else:
            raise ValueError(
                f"[ERROR] Can't remove last button, no buttons in list"
            )

    def confirm(self) -> List[_Button]:
        """
        Returns buttons from the current class
        Raises the errors
        Fixing the wrong lining
        """
        if self._buttons_amount > MAX_BUTTONS_AMOUNT:
            raise ValueError(
                f"[ERROR] Too much buttons: {self._buttons_amount}"
            )
        if self._rows > MAX_BUTTON_ROWS:
            raise ValueError(f"[ERROR] Too much rows: {self._rows}")
        if self._buttons_amount > 0:
            if self.buttons[-1].new_line_after == True:
                self.buttons[-1].new_line_after = False
        return self.buttons


@dataclass()
class Inline_buttons:
    """
    Contains a list of buttons for the keyboard
    """

    buttons: List[_Inline_button] = field(default_factory=list)
    _since_new_line = 0
    _rows = 0
    _buttons_amount = 0

    def add_button(
        self, label: str, color: BUTTONS_COLORS, payload: dict
    ) -> None:
        """
        Adds a new button to a keyboard
        """
        if self._since_new_line >= MAX_BUTTONS_IN_ROW:
            self.add_line()
        self._since_new_line += 1
        self._buttons_amount += 1
        self.buttons.append(
            _Inline_button(label=label, color=color, payload=payload)
        )
        if DEBUG_STATE:
            print(f"[INFO] Added button: {self.buttons[-1]}")

    def add_line(self) -> None:
        """
        Adds new line after the last created button
        """
        if self._buttons_amount > 0:
            self.buttons[-1].new_line_after = True
            self._since_new_line = 0
            self._rows += 1
            if DEBUG_STATE:
                print(f"[INFO] Added line after: {self.buttons[-1]}")
        else:
            raise ValueError(f"[ERROR] Can't add new line, no buttons in list")

    def remove_last_button(self) -> None:
        """
        Removes the last button
        """
        if self._buttons_amount > 0:
            if DEBUG_STATE:
                print(f"[INFO] Last button: {self.buttons[-1]} removed")
            self.buttons.pop(-1)
            if self._since_new_line > 0:
                self._since_new_line -= 1
        else:
            raise ValueError(
                f"[ERROR] Can't remove last button, no buttons in list"
            )

    def confirm(self) -> List[_Inline_button]:
        """
        Returns buttons from the current class
        Raises the errors
        Fixing the wrong lining
        """
        if self._buttons_amount > MAX_BUTTONS_AMOUNT:
            raise ValueError(
                f"[ERROR] Too much buttons: {self._buttons_amount}"
            )
        if self._rows > MAX_BUTTON_ROWS:
            raise ValueError(f"[ERROR] Too much rows: {self._rows}")
        if self._buttons_amount > 0:
            if self.buttons[-1].new_line_after == True:
                self.buttons[-1].new_line_after = False
        return self.buttons
