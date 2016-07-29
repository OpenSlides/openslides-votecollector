from openslides.utils.rest_api import ModelSerializer, RelatedField

from .models import Keypad, Seat


class KeypadSerializer(ModelSerializer):
    """
    Serializer for openslides_votecollector.models.Keypad object.
    """
    class Meta:
        model = Keypad
        fields = (
            'id',
            'user',
            'keypad_id',
            'seat',
            'battery_level',
            'in_range',
        )


class SeatSerializer(ModelSerializer):
    """
    Serializer for openslides_votecollector.model.Seat object.
    """
    class Meta:
        model = Seat
        fields = (
            'id',
            'number',
            'seating_plan_x_axis',
            'seating_plan_y_axis',
        )
