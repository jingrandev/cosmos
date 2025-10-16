# ruff: noqa: E501
import json
import random
from typing import Any

from apps.restaurant.constants import OrderState
from apps.restaurant.roles.analyze import AnalyzeDialogRole
from apps.restaurant.roles.base import DialogMessage
from apps.restaurant.roles.base import RestaurantRole
from apps.restaurant.roles.customer import CustomerRole
from apps.restaurant.roles.waiter import WaiterRole
from apps.restaurant.serializers.output_validate import AnalyzeResultSerializer
from apps.restaurant.serializers.output_validate import StringOutputSerializer

from ..models import Dish
from ..models.dialog_session import DialogSession

state_registry: dict[OrderState, type["BaseState"]] = {}


class BaseState:
    state: OrderState

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        state_registry[cls.state] = cls

    def __init__(self, session: DialogSession, role: RestaurantRole = None) -> None:
        self.role = role
        self.session = session
        self.output: Any | None = None

    def validate_output(self, text: str, silent: bool = True) -> tuple[Any, bool]:
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(
            data={"value": text}, context=self.get_serializer_context()
        )
        ok = serializer.is_valid(raise_exception=not silent)
        if ok:
            return serializer.validated_data.get("value", text), True
        return text, False

    def get_serializer_class(self):
        return StringOutputSerializer

    def get_serializer_context(self) -> dict:
        return {
            "forbid_newline": True,
            "forbid_wrapped_quotes": True,
        }

    def system_prompt(self) -> str:
        return ""

    def generate(
        self,
        *,
        temperature: float | None = None,
        model: str | None = None,
    ) -> tuple[str, bool]:
        dialog_context: list[DialogMessage] | None = self.session.messages or []
        messages = self.role.build_messages(
            self.system_prompt(),
            extra_messages=[self.role.developer("Start your chat.")],
            dialog_context=dialog_context,
        )
        text = self.role.chat(
            messages=messages,
            temperature=temperature,
            model=model,
        )
        validated_text, ok = self.validate_output(text)
        self.output = validated_text
        return validated_text, ok

    def persist_state(self, previous_state: OrderState) -> None:
        pass


class GreetingState(BaseState):
    state: str = OrderState.GREETING

    def __init__(self, session: DialogSession, role: RestaurantRole = None) -> None:
        super().__init__(session, role or WaiterRole())

    def system_prompt(self) -> str:
        return f"""
        # Role
        {self.role.persona_messages}

        # Task
        **Greeting new customers**:
        1. Start with a unique welcome phrase.
        2. After welcoming, ask the customer how their day has been.
        3. 3-4 sentences total, with natural flow between welcome and question.

        # Strict Rules
        1. Use only English.
        2. Include ONLY conversation content (no extra explanations, labels, or metadata).
        3. Format as a single line with no line breaks.
        4. Do NOT enclose the response in quotation marks.
        """

    def get_serializer_context(self) -> dict:
        return {
            "forbid_newline": True,
            "forbid_wrapped_quotes": True,
            "require_question_mark": True,
        }

    def persist_state(self, previous_state: OrderState) -> None:
        messages = list(self.session.messages or [])
        messages.append({"role": "waiter", "content": self.output or ""})
        DialogSession.objects.select_for_update().filter(
            id=self.session.id, state=previous_state
        ).update(
            messages=messages,
            state=self.state,
        )


class ReplyGreetingState(BaseState):
    state: str = OrderState.DAY_REPLY

    def __init__(self, session: DialogSession, role: RestaurantRole = None) -> None:
        super().__init__(session, role or CustomerRole())

    def system_prompt(self) -> str:
        day_status_choices = [
            "You are having a wonderful/great/lovely day.",
            "You are having a tough/rough/bad/exhausted day—something minor went wrong",
            "You are having an average/uneventful day—nothing particularly good or bad happened.",
        ]
        weights = [0.4, 0.3, 0.3]
        customer_day_status = random.choices(day_status_choices, weights=weights)[0]
        return f"""
        # Role
        {self.role.persona_messages}

        # Task
        **Respond to waiter's Greeting**:
        1. {customer_day_status}
        2. Briefly and politely describe your day in 4-5 sentences.
        3. Keep the response in one line with no line breaks.
        4. Do NOT ask any questions.

        # Strict Rules
        1. Use only English.
        2. Include only conversation content (no explanations).
        3. Do NOT use quotation marks.
        4. THIS RULE TAKES PRECEDENCE OVER ALL OTHERS: No questions of any kind in the response.
        """

    def get_serializer_context(self) -> dict:
        return {
            "forbid_newline": True,
            "forbid_wrapped_quotes": True,
            "forbid_question_mark": True,
        }

    def persist_state(self, previous_state: OrderState) -> None:
        messages = list(self.session.messages or [])
        messages.append({"role": "customer", "content": self.output or ""})
        DialogSession.objects.select_for_update().filter(
            id=self.session.id, state=previous_state
        ).update(
            messages=messages,
            state=self.state,
        )


class AskFavoritesState(BaseState):
    state: str = OrderState.ASK_FAVORITES

    def __init__(self, session: DialogSession, role: RestaurantRole = None) -> None:
        super().__init__(session, role or WaiterRole())

    def system_prompt(self) -> str:
        return f"""
        # Role
        {self.role.persona_messages}

        # Task
        **Ask about the customer's top 3 favorite foods**:
        1. Reference the customer's previous response about their day when relevant to keep the conversation natural.
        2. Clearly ask for their top 3 favorite foods.
        3. Add a brief, positive note to encourage them.
        4. 3-5 sentences total, with a smooth and friendly flow.

        # Strict Rules
        1. Use only English.
        2. Include ONLY conversation content (no extra explanations).
        3. Format as a single line with no line breaks.
        4. Do NOT enclose the response in quotation marks.
        5. Explicitly request "top 3" foods.
        """

    def get_serializer_context(self) -> dict:
        return {
            "forbid_newline": True,
            "forbid_wrapped_quotes": True,
            # "require_question_mark": True,
        }

    def persist_state(self, previous_state: OrderState) -> None:
        messages = list(self.session.messages or [])
        messages.append({"role": "waiter", "content": self.output or ""})
        DialogSession.objects.select_for_update().filter(
            id=self.session.id, state=previous_state
        ).update(
            messages=messages,
            state=self.state,
        )


class AnswerFavoritesState(BaseState):
    state: str = OrderState.FAVORITES_REPLY

    def __init__(self, session: DialogSession, role: RestaurantRole = None) -> None:
        super().__init__(session, role or CustomerRole())

    def system_prompt(self) -> str:
        return f"""
        # Role
        {self.role.persona_messages}

        # Task
        **Share your top 3 favorite foods**:
        1. Randomly select 3 distinct foods from a diverse range (e.g., Italian, Asian, American, vegetarian options—avoid repeating the same cuisine type).
        2. For each food, add a brief, unique reason why you like it (e.g., "sushi because it's fresh and light" or "pasta because of the rich sauces").
        3. Present them in a natural, conversational flow (not numbered lists), in 3-4 sentences total.
        4. Ensure the combination of foods is different from typical responses (avoid overused trios like "pizza, burgers, fries").

        # Strict Rules
        1. Use only English.
        2. Include ONLY conversation content (no explanations or labels).
        3. Format as a single line with no line breaks.
        4. Do NOT enclose in quotation marks.
        5. Never list fewer or more than 3 foods—exactly 3 must be mentioned.
        6. Do NOT ask any questions.
        """

    def get_serializer_context(self) -> dict:
        return {
            "forbid_newline": True,
            "validate_quotation": True,
            "forbid_question_mark": True,
        }

    def persist_state(self, previous_state: OrderState) -> None:
        messages = list(self.session.messages or [])
        messages.append({"role": "customer", "content": self.output or ""})
        DialogSession.objects.select_for_update().filter(
            id=self.session.id, state=previous_state
        ).update(
            messages=messages,
            customer_favorite_text=(self.output or ""),
            state=self.state,
        )


class AskOrderState(BaseState):
    state: str = OrderState.ASK_ORDER

    def __init__(self, session: DialogSession, role: RestaurantRole = None) -> None:
        super().__init__(session, role or WaiterRole())

    def system_prompt(self) -> str:
        return f"""
        # Role
        {self.role.persona_messages}

        # Task
        **Ask the customer what they'd like to order today**:
        1. Invite them to order, using an open and helpful tone (e.g., "feel free to choose from our menu" or "we can prepare something special based on your favorites").
        2. 2-3 sentences, flowing smoothly from their food preferences.

        # Strict Rules
        1. Use only English.
        2. Include ONLY conversation content (no extra explanations).
        3. Format as a single line with no line breaks.
        4. Do NOT enclose in quotation marks.
        """

    def get_serializer_context(self) -> dict:
        return {
            "forbid_newline": True,
            "validate_quotation": True,
            # "require_question_mark": True,
        }

    def persist_state(self, previous_state: OrderState) -> None:
        messages = list(self.session.messages or [])
        messages.append({"role": "waiter", "content": self.output or ""})
        DialogSession.objects.select_for_update().filter(
            id=self.session.id, state=previous_state
        ).update(
            messages=messages,
            state=self.state,
        )


class ReplyOrderState(BaseState):
    state: str = OrderState.ORDER_REPLY

    def __init__(self, session: DialogSession, role: RestaurantRole = None) -> None:
        super().__init__(session, role or CustomerRole())

    def system_prompt(self) -> str:
        dishes = (
            Dish.objects.all()
            .only("name", "description")
            .values_list("name", "description")
            .order_by("id")
        )
        menu = "\n".join([f"- {name}: {description}" for name, description in dishes])

        return f"""
        # Role
        {self.role.persona_messages}

        # Task
        **Respond with your order**:
        1. Choose 1-2 specific dishes in the restaurant menu.
        2. dish should be in the restaurant menu
        3. Do not order same type of dishes (e.g. Grilled Tofu Salad and Fresh Fruit Salad are both salad)
        4. Briefly explain why you chose these dishes.
        5. Keep the response natural and conversational: 4-6 sentences, flowing from the waiter's question.

        # Restaurant Menu
        {menu}

        # Strict Rules
        1. Use only English.
        2. Include ONLY conversation content (no explanations or labels).
        3. Format as a single line with no line breaks.
        4. Do NOT enclose in quotation marks.
        5. Ensure the order connects logically to your previously mentioned favorite foods.
        """

    def get_serializer_context(self) -> dict:
        return {
            "forbid_newline": True,
            "validate_quotation": True,
            "forbid_question_mark": True,
        }

    def persist_state(self, previous_state: OrderState) -> None:
        messages = list(self.session.messages or [])
        messages.append({"role": "customer", "content": self.output or ""})
        DialogSession.objects.select_for_update().filter(
            id=self.session.id, state=previous_state
        ).update(
            messages=messages,
            customer_order_text=(self.output or ""),
            state=self.state,
        )


class AnalyzeState(BaseState):
    state: str = OrderState.ANALYZE

    def __init__(self, session: DialogSession, role: RestaurantRole = None) -> None:
        super().__init__(session, role or AnalyzeDialogRole())

    def system_prompt(self) -> str:
        dishes = Dish.objects.all().values("name", "ingredients").order_by("id")
        menu = "\n".join(
            [f"- {dish['name']}: {dish['ingredients']}" for dish in dishes]
        )
        return f"""
        # Role
        You are an assistant specialized in detecting a customer's dietary preference from conversation.

        # Task
        Determine the customer's dietary preference using ONLY the customer's messages (lines starting with "Customer:") and the restaurant menu and its ingredients.

        # Definitions (use these strictly)
        - vegan: excludes all animal products: meat, poultry, fish, seafood, dairy, eggs, honey, gelatin.
        - vegetarian: excludes meat, poultry, fish, seafood; may include dairy and/or eggs and/or honey.
        - non-vegetarian: includes any meat, poultry, fish, or seafood.
        - unknown: insufficient or conflicting evidences.

        # Strict Rules
        1. Extract "favorite_dishes":
            a. Locate the line starting with "Customer's Favorite:".
            b. Read the entire line, find all phrases that refer to specific foods/dishes (e.g., "Thai green curry", "eggplant parmesan", "sushi").
            c. List these phrases as strings in "favorite_dishes" (do not abbreviate, e.g., write "Thai green curry" not "curry").
        2. Extract "ordered_dishes":
            a. Locate the line starting with "Customer's Order:".
            b. Extract dishes that are EXACTLY in the restaurant menu (e.g., "Roasted Seasonal Veggies" is in the menu, so include it).
        3. Check Customer's favorite dishes according to their description and how the dishes are categorized. Cross-check ordered_dishes with the provided menu and its ingredients.
            The preference detection steps is as follows:
            a. First check non-vegetarian (highest priority).
            b. If non-vegetarian is not detected, check vegetarian.
            c. If vegetarian is detected, check vegan.
            d. otherwise, check unknown:
                - If favorite_dishes and ordered_dishes contains all kinds of foods and you cannot tell the customer's dietary preference → "non-vegetarian".
                - If favorite_dishes is empty AND ordered_dishes is empty → "unknown".
                - If evidence conflicts (e.g., says "vegan" but orders dairy) → "unknown".
        4. Response must be a valid JSON object with exactly these keys:
            - "dietary_preference": one of ["vegetarian", "vegan", "non-vegetarian", "unknown"]
            - "confidence_percent": integer 0-100. 100 if Step 1/2 has clear evidence (meat/ingredient match), else 0-90 depends on the evidences
            - "evidence": brief clues you used to determine the customer's dietary preference (e.g., mentions of cheese or fish).
                a. If the result is non-vegetarian, the evidence should include the meat clue (e.g. Roast Duck -> non-vegetarian).
                b. If the result is vegetarian, the evidence should include the non-vegan clue (e.g. Vegetable Omelette -> not vegan).
                c. If the result is unknown, the evidence should include the conflict clue (e.g. Roast Duck + vegan statements -> unknown).
            - "ordered_dishes": list that step 2 extracted
            - "favorite_dishes": list that step 1 extracted
        5. JSON must be minified (no line breaks, extra spaces). Do not include any content outside the JSON object.

        # Restaurant Menu (format: - name: ingredients list)
        {menu}
        """

    def generate(
        self,
        *,
        temperature: float | None = 0,
        model: str | None = None,
    ) -> tuple[dict, bool]:
        messages = self.role.build_messages(
            self.system_prompt(),
            extra_messages=[
                self.role.developer(f"""
                Customer's Favorite: {self.session.customer_favorite_text}
                Customer's Order: {self.session.customer_order_text}
                """)
            ],
        )
        text = self.role.chat(
            messages=messages,
            temperature=temperature,
            model=model,
            response_format="json",
        )
        validated, ok = self.validate_output(text)
        self.output = validated
        return validated, ok

    def validate_output(self, text: str, silent: bool = True) -> tuple[dict, bool]:
        try:
            data = json.loads(text)
        except Exception as e:
            if not silent:
                raise e
            return {}, False
        serializer = self.get_serializer_class()(data=data)
        ok = serializer.is_valid(raise_exception=not silent)
        if ok:
            return {**serializer.validated_data}, True
        return {}, False

    def get_serializer_class(self):
        return AnalyzeResultSerializer

    def persist_state(self, previous_state: OrderState) -> None:
        result = self.output if isinstance(self.output, dict) else {}
        DialogSession.objects.select_for_update().filter(
            id=self.session.id, state=previous_state
        ).update(
            analysis_result=result,
            state=self.state,
        )
