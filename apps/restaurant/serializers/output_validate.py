from rest_framework import serializers

from apps.restaurant.models import CustomerProfile


class StringOutputSerializer(serializers.Serializer):
    value = serializers.CharField()

    def validate_value(self, value):
        if not value:
            raise serializers.ValidationError("text is empty")
        context = self.context
        forbid_wrapped_quotes = context.get(
            "forbid_wrapped_quotes", context.get("validate_quotation", False)
        )
        if (
            forbid_wrapped_quotes
            and value.strip().startswith('"')
            and value.strip().endswith('"')
        ):
            raise serializers.ValidationError("text should not be quoted")
        forbid_newline = context.get("forbid_newline", False)
        if forbid_newline and "\n" in value:
            raise serializers.ValidationError("text should be single line")
        require_question_mark = context.get("require_question_mark", False)
        if require_question_mark and "?" not in value:
            raise serializers.ValidationError("text should contain a question mark")
        forbid_question_mark = context.get("forbid_question_mark", False)
        if forbid_question_mark and "?" in value:
            raise serializers.ValidationError("text should not contain question marks")
        require_contains = context.get("require_contains") or []
        if require_contains:
            lower_value = value.lower()
            for phrase in require_contains:
                if phrase.lower() not in lower_value:
                    raise serializers.ValidationError(
                        f"text should contain phrase: {phrase}"
                    )
        return value


class AnalyzeResultSerializer(serializers.Serializer):
    dietary_preference = serializers.ChoiceField(
        choices=CustomerProfile.DietaryPreference.choices
    )
    confidence_percent = serializers.IntegerField(min_value=0, max_value=100)
    evidence = serializers.CharField(allow_blank=True)
    ordered_dishes = serializers.ListField(
        child=serializers.CharField(), allow_empty=True
    )
    favorite_dishes = serializers.ListField(
        child=serializers.CharField(), allow_empty=True
    )
