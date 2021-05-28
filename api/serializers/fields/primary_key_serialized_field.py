from rest_framework import serializers


class PrimaryKeySerializedField(serializers.PrimaryKeyRelatedField):
    """
    Custom field subclassing PrimaryKeyRelated
    On writes, this allows us to specify the primary key for a resource
    On reads, this will serialize the associated resource, nesting it
    within the outer json
    """

    def __init__(self, **kwargs):
        self.serializer = kwargs.pop('serializer')
        self.many = kwargs.get('many')
        super().__init__(**kwargs)

    def to_representation(self, value):
        if self.pk_field is not None:
            return self.pk_field.to_representation(value.pk)

        if self.many:
            return self.serializer(value, many=self.many).data

        else:
            instance = self.queryset.get(pk=value.pk)
            return self.serializer(instance).data
