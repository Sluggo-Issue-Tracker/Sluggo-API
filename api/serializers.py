"""
A REST API needs to provide a way of serializing and deserializing the models created into representations such as json. We can do this by declaring serializers that work very similar to Django's forms. Create a file in the app directory named serializers.py and create your classes.
"""


# REST TUTORIAL BELOW HERE #


from rest_framework import serializers
from .models import Snippet, LANGUAGE_CHOICES, STYLE_CHOICES


class SnippetSerializerClass(serializers.Serializer):
    """
The first part of the serializer class defines the fields that get serialized/deserialized. The create() and update() methods define how fully fledged instances are created or modified when calling serializer.save()

A serializer class is very similar to a Django Form class, and includes similar validation flags on the various fields, such as required, max_length and default.

This class works but a better way is using the model serializer.
    """

    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=False, allow_blank=True, max_length=100)
    code = serializers.CharField(style={"base_template": "textarea.html"})
    linenos = serializers.BooleanField(required=False)
    language = serializers.ChoiceField(choices=LANGUAGE_CHOICES, default="python")
    style = serializers.ChoiceField(choices=STYLE_CHOICES, default="friendly")

    def create(self, validated_data):
        """
        Created and returns a new `Snipppet` instance given properly validated data.
        """
        return Snippet.objects.create(**validated_data)

    def update(self, instance, validated):
        """
        Updates and returns an existing `Snippet` instance, given validated data.
        """
        instance.title = validated_data.get("title", instance.title)
        instance.code = validated_data.get("code", instance.code)
        instance.linenos = validated_data.get("linenos", instance.linenos)
        instance.language = validated_data.get("language", instance.language)
        instance.style = validated_data.get("style", instance.style)
        instance.save()
        return instance


class SnippetSerializer(serializers.ModelSerializer):
    """
    Serializer Class for Snippets that takes use of a Model similar to how forms in django take use of Model base classes. This will automatically do everything that exists above. You can see that by running this code in the shell:

    `from api.serializers import SnippetSerializer`

    `serializer = SnippetSerializer()`

    `print(repr(serializer))`
    """

    class Meta:
        model = Snippet
        fields = ["id", "title", "code", "linenos", "language", "style"]

