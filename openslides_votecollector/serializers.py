from openslides.utils.rest_api import ModelSerializer, RelatedField

from .models import AssignmentPollKeypadConnection, Keypad, MotionPollKeypadConnection, Seat, VoteCollector


class VoteCollectorSerializer(ModelSerializer):
    """
    Serializer for openslides_votecollector.models.VoteCollector object.
    """
    class Meta:
        model = VoteCollector
        fields = (
            'id',
            'device_status',
            'voting_mode',
            'voting_target',
            'voting_duration',
            'voters_count',
            'votes_received',
            'is_voting',
        )


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


class MotionPollKeypadConnectionSerializer(ModelSerializer):
    """
    Serializer for openslides_votecollector.model.MotionPollKeypadConnection object.
    """
    class Meta:
        model = MotionPollKeypadConnection
        fields = (
            'id',
            'poll',
            'keypad',
            'value',
            'serial_number',
        )


class AssignmentPollKeypadConnectionSerializer(ModelSerializer):
    """
    Serializer for openslides_votecollector.model.AssignmentPollKeypadConnection object.
    """
    class Meta:
        model = AssignmentPollKeypadConnection
        fields = (
            'id',
            'poll',
            'keypad',
            'candidate',
            'value',
            'serial_number',
        )
