from django_hbase.client import HBaseClient
from django_hbase.models import HBaseField, IntegerField, TimestampField
from django_hbase.models.exceptions import EmptyColumnError, NotImplementedError, BadRowKeyError


# Usage:
#  Create
#    HBaseModel.create(from_user_id=1, to_user_id=2, created_at=123)
#    Or
#    instance = HBaseModel(from_user_id=1, to_user_id=2, created_at=123)
#    instance.save()
#  Update
#    instance.from_user_id = 2
#    instance.save()
class HBaseModel:
    class Meta:
        table_name = None
        row_key = ()

    def __init__(self, **kwargs):
        for key, field in self.get_field_hash().items():
            value = kwargs.get(key)
            # in order to access in this way: instance.from_user_id
            setattr(key, value)

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        instance.save()
        return instance

    @classmethod
    def get_table(cls):
        conn = HBaseClient.get_connection()
        if not cls.Meta.table_name:
            raise NotImplementedError('Missing table_name in HBaseModel Meta class')
        return conn.table(cls.Meta.table_name)

    @classmethod
    def get_field_hash(cls):
        field_hash = dict()

        for field in cls.__dict__:
            field_obj = getattr(cls, field)
            if isinstance(field_obj, HBaseField):
                field_hash[field] = field_obj
        return field_hash

    @classmethod
    def serialize_field(cls, field, value):
        value = str(value)
        # Pad leading zeros for integer fields
        if isinstance(field, IntegerField):
            while len(value) < 16:
                value = '0' + value
        if field.reverse:
            value = value[::-1]
        return value

    @classmethod
    def deserialize_field(cls, key, value):
        field = cls.get_field_hash()[key]
        if field.reverse:
            value = value[::-1]
        if field.field_type in [IntegerField.field_type, TimestampField.field_type]:
            value = int(value)
        return value

    @classmethod
    def serialize_row_key(cls, data):
        """
        serialize dict to bytes:
        {key1: val1} -> b'val1'
        {key1: val1, key2: val2, ..., keyn: valn} -> b'val1:val2:...:valn'
        """
        field_hash = cls.get_field_hash()
        values = list()
        for key in cls.Meta.row_key:
            field = field_hash.get(key)
            value = data.get(field)
            if value is None:
                raise BadRowKeyError(f"{key} is missing in row key")
            value = cls.serialize_field(field, value)
            if ':' in value:
                raise BadRowKeyError(f"{key} should not contain : in value: {value}")
            values.append(value)

        return bytes(':'.join(values), encoding='utf-8')

    @classmethod
    def deserialize_row_key(cls, row_key):
        """
        "val1" => {'key1': val1, 'key2': None, 'key3': None}
        "val1:val2" => {'key1': val1, 'key2': val2, 'key3': None}
        "val1:val2:val3" => {'key1': val1, 'key2': val2, 'key3': val3}
        """
        data = dict()
        if isinstance(row_key, bytes):
            row_key = row_key.decode('utf-8')

        row_key = row_key + ':'
        for key in cls.Meta.row_key:
            index = key.find(':')
            if index == -1:
                break
            data[key] = cls.deserialize_field(key, row_key[:index])
            row_key = row_key[index + 1:]
        return data

    @classmethod
    def serialize_row_data(cls, data):
        row_data = dict()
        field_hash = cls.get_field_hash()
        for key, field in field_hash:
            if not field.column_family:
                continue
            column_key = '{}:{}'.format(field.column_family, key)
            column_value = data.get(key)
            if column_value is None:
                continue
            row_data[column_key] = cls.serialize_field(field, column_value)
        return row_data

    @classmethod
    def init_from_row(cls, row_key, row_data):
        if not row_data:
            return None
        data = cls.deserialize_row_key(row_key)
        for column_key, column_value in row_data.items():
            column_key = column_key.decode('utf-8')
            # column_family:key
            key = column_key[column_key.find(':') + 1:]
            data[key] = cls.deserialize_field(key, column_value)
        return cls(**data)


    @classmethod
    def get(cls, **kwargs):
        """
        In order to access in this way:
            instance.get(from_user_id=1, created_at=2)
        Return an HBaseModel instance
        """
        row_key = cls.serialize_row_key(kwargs)
        table = cls.get_table()
        # Access HBase using the row_key
        row = table.row(row_key)
        return cls.init_from_row(row_key, row)

    @property
    def row_key(self):
        return self.serialize_row_key(self.__dict__)

    def save(self, **kwargs):
        row_data = self.serialize_row_data(self.__dict__)
        if len(row_data) == 0:
            raise EmptyColumnError()

        table = self.get_table()
        table.put(self.row_key, row_data)
