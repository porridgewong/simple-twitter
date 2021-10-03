from django.core import serializers
from util.json_encoder import JSONEncoder


class DjangoModelSerializer(object):

    @classmethod
    def serialize(cls, instance):
        return serializers.serialize('json', [instance], cls=JSONEncoder)

    @classmethod
    def deserialize(cls, serialized_data):
        return list(serializers.deserialize('json', serialized_data))[0].object

