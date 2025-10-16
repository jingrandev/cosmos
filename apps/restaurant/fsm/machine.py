from typing import Any

from transitions import Machine
from transitions import MachineError

from apps.restaurant.models.dialog_session import DialogSession

OrderState = DialogSession.CustomerOrderState


class DialogStateMachine:
    """State machine for managing waiter-customer dialog steps.

    This machine mirrors `DialogSession.CustomerOrderState` and persists
    transitions back to the `DialogSession` model. It also provides helpers
    to append messages and store analysis results.
    """

    def __init__(self, session: DialogSession) -> None:
        """Initialize the machine with an existing DialogSession instance."""
        self.session = session
        self.state = session.state

        states = [s.value for s in OrderState]

        transitions = [
            {
                "trigger": "start_greeting",
                "source": OrderState.INIT.value,
                "dest": OrderState.GREETING.value,
                "after": "persist_state",
            },
            {
                "trigger": "receive_day_reply",
                "source": OrderState.GREETING.value,
                "dest": OrderState.DAY_REPLY.value,
                "after": "persist_state",
            },
            {
                "trigger": "proceed_to_ask_favorites",
                "source": OrderState.DAY_REPLY.value,
                "dest": OrderState.ASK_FAVORITES.value,
                "after": "persist_state",
            },
            {
                "trigger": "receive_favorites_reply",
                "source": OrderState.ASK_FAVORITES.value,
                "dest": OrderState.FAVORITES_REPLY.value,
                "after": "persist_state",
            },
            {
                "trigger": "proceed_to_ask_order",
                "source": OrderState.FAVORITES_REPLY.value,
                "dest": OrderState.ASK_ORDER.value,
                "after": "persist_state",
            },
            {
                "trigger": "receive_order_reply",
                "source": OrderState.ASK_ORDER.value,
                "dest": OrderState.ORDER_REPLY.value,
                "after": "persist_state",
            },
            {
                "trigger": "run_analysis",
                "source": OrderState.ORDER_REPLY.value,
                "dest": OrderState.ANALYZE.value,
                "after": "persist_state",
            },
            {
                "trigger": "finish",
                "source": OrderState.ANALYZE.value,
                "dest": OrderState.COMPLETE.value,
                "after": "persist_state",
            },
        ]

        self._machine = Machine(
            model=self,
            states=states,
            transitions=transitions,
            initial=self.state,
            auto_transitions=False,
            ignore_invalid_triggers=False,
            send_event=False,
        )

    def persist_state(self) -> None:
        """Persist current machine state to the session."""
        if self.session.state != self.state:
            self.session.state = self.state
            self.session.save(update_fields=["state"])

    def add_message(
        self,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
        save: bool = True,
    ) -> None:
        """Append a message to the session's message list and optionally save."""
        payload: dict[str, Any] = {"role": role, "content": content}
        if metadata:
            payload["meta"] = metadata
        messages: list[dict[str, Any]] = list(self.session.messages or [])
        messages.append(payload)
        self.session.messages = messages
        if save:
            self.session.save(update_fields=["messages"])

    def set_analysis_result(self, result: dict[str, Any], save: bool = True) -> None:
        """Store analysis result to the session."""
        self.session.analysis_result = result or {}
        if save:
            self.session.save(update_fields=["analysis_result"])

    @property
    def current_state(self) -> str:
        """Return current state string."""
        return self.state

    @staticmethod
    def from_session(session: DialogSession) -> "DialogStateMachine":
        """Factory to create a state machine from a DialogSession instance."""
        return DialogStateMachine(session=session)

    def safe_trigger(self, trigger_name: str) -> bool:
        """Trigger transition by name with safety checks.

        Returns True if transition succeeded; otherwise returns False when
        transition is invalid for the current state.
        """
        try:
            trigger = getattr(self, trigger_name)
        except AttributeError:
            return False
        try:
            trigger()
            return True
        except MachineError:
            return False
