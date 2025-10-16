from django.db import transaction
from loguru import logger
from transitions import Machine
from transitions import MachineError

from apps.restaurant.models.dialog_session import DialogSession

from .states import state_registry

OrderState = DialogSession.CustomerOrderState


class DialogStateMachine:
    states = list(OrderState)

    def __init__(self, session: DialogSession) -> None:
        self.session = session
        self.previous_state = None
        self.state = session.state
        self.state_index = self.states.index(self.state)

        transitions = [
            {
                "trigger": "start_greeting",
                "source": OrderState.INIT,
                "dest": OrderState.GREETING,
            },
            {
                "trigger": "receive_day_reply",
                "source": OrderState.GREETING,
                "dest": OrderState.DAY_REPLY,
            },
            {
                "trigger": "proceed_to_ask_favorites",
                "source": OrderState.DAY_REPLY,
                "dest": OrderState.ASK_FAVORITES,
            },
            {
                "trigger": "receive_favorites_reply",
                "source": OrderState.ASK_FAVORITES,
                "dest": OrderState.FAVORITES_REPLY,
            },
            {
                "trigger": "proceed_to_ask_order",
                "source": OrderState.FAVORITES_REPLY,
                "dest": OrderState.ASK_ORDER,
            },
            {
                "trigger": "receive_order_reply",
                "source": OrderState.ASK_ORDER,
                "dest": OrderState.ORDER_REPLY,
            },
            {
                "trigger": "run_analysis",
                "source": OrderState.ORDER_REPLY,
                "dest": OrderState.ANALYZE,
            },
        ]

        self.machine = Machine(
            model=self,
            states=self.states,
            transitions=transitions,
            initial=self.state,
            ignore_invalid_triggers=False,
            before_state_change=self.on_enter_states,
            after_state_change=self.after_states_changed,
        )

    def on_enter_states(self):
        self.previous_state = self.state

    def after_states_changed(self):
        state_class = state_registry[self.state]
        with transaction.atomic():
            session = DialogSession.objects.filter(id=self.session.id).first()
            if not session:
                raise RuntimeError("Session not found")
            state = state_class(session)
            output, ok = state.generate()
            if not ok:
                logger.error(
                    f"Failed to generate text with "
                    f"{self.state=} {self.session.id=} {output=}"
                )
                raise RuntimeError("Failed to generate text")
            state.persist_state(self.previous_state)

    @property
    def current_state(self) -> str:
        return self.state

    @staticmethod
    def from_session(session: DialogSession) -> "DialogStateMachine":
        return DialogStateMachine(session=session)

    def safe_trigger(self, trigger_name: str) -> bool:
        try:
            trigger = getattr(self, trigger_name)
        except AttributeError:
            return False
        try:
            trigger()
            return True
        except MachineError:
            return False
