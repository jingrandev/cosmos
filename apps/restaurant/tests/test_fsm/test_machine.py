# ruff: noqa: E501
from unittest.mock import patch

from django.test import TestCase

from apps.restaurant.fsm.machine import DialogStateMachine
from apps.restaurant.models.dialog_session import DialogSession
from apps.restaurant.roles.base import RestaurantRole
from core.auth.utils.factories import UserFactory


class TestDialogStateMachine(TestCase):
    def test_machine_greeting(self):
        mock_output = "Welcome to Cosmos! How are you?"

        with patch.object(
            RestaurantRole, "chat", return_value=mock_output
        ) as mock_chat:
            session = DialogSession.objects.create(customer_id=0)
            machine = DialogStateMachine.from_session(session)

            assert machine.safe_trigger("start_greeting")

            session.refresh_from_db()
            assert session.state == DialogSession.CustomerOrderState.GREETING
            assert len(session.messages) == 1
            assert session.messages[0]["role"] == "waiter"
            assert session.messages[0]["content"] == mock_output
            mock_chat.assert_called_once()

    def test_machine_day_reply(self):
        outputs = [
            "Welcome to Cosmos! How has your day been?",
            "I'm doing well today and enjoyed some time reading in the afternoon.",
        ]

        with patch.object(RestaurantRole, "chat", side_effect=outputs) as mock_chat:
            session = DialogSession.objects.create(customer_id=0)
            machine = DialogStateMachine.from_session(session)

            assert machine.safe_trigger("start_greeting")
            assert machine.safe_trigger("receive_day_reply")

            session.refresh_from_db()
            assert session.state == DialogSession.CustomerOrderState.DAY_REPLY
            assert len(session.messages) == 2
            assert [m["role"] for m in session.messages] == ["waiter", "customer"]
            assert session.messages[1]["content"] == outputs[1]
            assert mock_chat.call_count == 2

    def test_machine_ask_favorites(self):
        outputs = [
            "Welcome to Cosmos! How has your day been?",
            "I'm doing well today and enjoyed some time reading in the afternoon.",
            "Could you share your top 3 favorite foods?",
        ]

        with patch.object(RestaurantRole, "chat", side_effect=outputs) as mock_chat:
            session = DialogSession.objects.create(customer_id=0)
            machine = DialogStateMachine.from_session(session)

            assert machine.safe_trigger("start_greeting")
            assert machine.safe_trigger("receive_day_reply")
            assert machine.safe_trigger("proceed_to_ask_favorites")

            session.refresh_from_db()
            assert session.state == DialogSession.CustomerOrderState.ASK_FAVORITES
            assert len(session.messages) == 3
            assert [m["role"] for m in session.messages] == [
                "waiter",
                "customer",
                "waiter",
            ]
            assert session.messages[2]["content"] == outputs[2]
            assert mock_chat.call_count == 3

    def test_machine_favorites_reply(self):
        outputs = [
            "Welcome to Cosmos! How has your day been?",
            "I'm doing well today and enjoyed some time reading in the afternoon.",
            "Could you share your top 3 favorite foods?",
            "I love sushi for freshness, pasta for rich sauces, and falafel because it's hearty.",
        ]

        with patch.object(RestaurantRole, "chat", side_effect=outputs) as mock_chat:
            session = DialogSession.objects.create(customer_id=0)
            machine = DialogStateMachine.from_session(session)

            assert machine.safe_trigger("start_greeting")
            assert machine.safe_trigger("receive_day_reply")
            assert machine.safe_trigger("proceed_to_ask_favorites")
            assert machine.safe_trigger("receive_favorites_reply")

            session.refresh_from_db()
            assert session.state == DialogSession.CustomerOrderState.FAVORITES_REPLY
            assert len(session.messages) == 4
            assert [m["role"] for m in session.messages] == [
                "waiter",
                "customer",
                "waiter",
                "customer",
            ]
            assert session.messages[3]["content"] == outputs[3]
            assert session.customer_favorite_text == outputs[3]
            assert mock_chat.call_count == 4

    def test_machine_ask_order(self):
        outputs = [
            "Welcome to Cosmos! How has your day been?",
            "I'm doing well today and enjoyed some time reading in the afternoon.",
            "Could you share your top 3 favorite foods?",
            "I love sushi for freshness, pasta for rich sauces, and falafel because it's hearty.",
            "What would you like to order today from our menu?",
        ]

        with patch.object(RestaurantRole, "chat", side_effect=outputs) as mock_chat:
            session = DialogSession.objects.create(customer_id=0)
            machine = DialogStateMachine.from_session(session)

            assert machine.safe_trigger("start_greeting")
            assert machine.safe_trigger("receive_day_reply")
            assert machine.safe_trigger("proceed_to_ask_favorites")
            assert machine.safe_trigger("receive_favorites_reply")
            assert machine.safe_trigger("proceed_to_ask_order")

            session.refresh_from_db()
            assert session.state == DialogSession.CustomerOrderState.ASK_ORDER
            assert len(session.messages) == 5
            assert [m["role"] for m in session.messages] == [
                "waiter",
                "customer",
                "waiter",
                "customer",
                "waiter",
            ]
            assert session.messages[4]["content"] == outputs[4]
            assert session.customer_favorite_text == outputs[3]
            assert mock_chat.call_count == 5

    def test_machine_order_reply(self):
        outputs = [
            "Welcome to Cosmos! How has your day been?",
            "I'm doing well today and enjoyed some time reading in the afternoon.",
            "Could you share your top 3 favorite foods?",
            "I love sushi for freshness, pasta for rich sauces, and falafel because it's hearty.",
            "What would you like to order today from our menu?",
            "I'll have Roasted Seasonal Veggies and Mushroom Risotto because they sound delicious.",
        ]

        with patch.object(RestaurantRole, "chat", side_effect=outputs) as mock_chat:
            session = DialogSession.objects.create(customer_id=0)
            machine = DialogStateMachine.from_session(session)

            assert machine.safe_trigger("start_greeting")
            assert machine.safe_trigger("receive_day_reply")
            assert machine.safe_trigger("proceed_to_ask_favorites")
            assert machine.safe_trigger("receive_favorites_reply")
            assert machine.safe_trigger("proceed_to_ask_order")
            assert machine.safe_trigger("receive_order_reply")

            session.refresh_from_db()
            assert session.state == DialogSession.CustomerOrderState.ORDER_REPLY
            assert len(session.messages) == 6
            assert [m["role"] for m in session.messages] == [
                "waiter",
                "customer",
                "waiter",
                "customer",
                "waiter",
                "customer",
            ]
            assert session.messages[5]["content"] == outputs[5]
            assert session.customer_favorite_text == outputs[3]
            assert session.customer_order_text == outputs[5]
            assert mock_chat.call_count == 6

    def test_machine_analyze(self):
        outputs = [
            "Welcome to Cosmos! How has your day been?",
            "I'm doing well today and enjoyed some time reading in the afternoon.",
            "Could you share your top 3 favorite foods?",
            "I love sushi for freshness, pasta for rich sauces, and falafel because it's hearty.",
            "What would you like to order today from our menu?",
            "I'll have Roasted Seasonal Veggies and Mushroom Risotto because they sound delicious.",
            '{"dietary_preference":"vegetarian","confidence_percent":80,"evidence":"mentions of veggies and no meat","ordered_dishes":["Roasted Seasonal Veggies","Mushroom Risotto"],"favorite_dishes":["sushi","pasta","falafel"]}',
        ]

        with patch.object(RestaurantRole, "chat", side_effect=outputs) as mock_chat:
            user = UserFactory()
            session = DialogSession.objects.create(customer_id=user.customer.id)
            machine = DialogStateMachine.from_session(session)

            assert machine.safe_trigger("start_greeting")
            assert machine.safe_trigger("receive_day_reply")
            assert machine.safe_trigger("proceed_to_ask_favorites")
            assert machine.safe_trigger("receive_favorites_reply")
            assert machine.safe_trigger("proceed_to_ask_order")
            assert machine.safe_trigger("receive_order_reply")
            assert machine.safe_trigger("run_analysis")

            session.refresh_from_db()
            assert session.state == DialogSession.CustomerOrderState.ANALYZE
            assert isinstance(session.analysis_result, dict)
            assert session.analysis_result.get("dietary_preference") in {
                "vegetarian",
                "vegan",
                "non-vegetarian",
                "unknown",
            }
            assert mock_chat.call_count == 7
