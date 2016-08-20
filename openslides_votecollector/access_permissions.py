from openslides.utils.access_permissions import BaseAccessPermissions


class SeatAccessPermissions(BaseAccessPermissions):
    """
    Access permissions container for Keypad and KeypadViewSet.
    """
    def can_retrieve(self, user):
        """
        Returns True if the user has VoteCollector access.
        """
        return user.has_perm('openslides_votecollector.can_manage_votecollector')

    def get_serializer_class(self, user=None):
        """
        Returns serializer class.
        """
        from .serializers import SeatSerializer

        return SeatSerializer


class KeypadAccessPermissions(BaseAccessPermissions):
    """
    Access permissions container for Keypad and KeypadViewSet.
    """
    def can_retrieve(self, user):
        """
        Returns True if the user has VoteCollector access.
        """
        return user.has_perm('openslides_votecollector.can_manage_votecollector')

    def get_serializer_class(self, user=None):
        """
        Returns serializer class.
        """
        from .serializers import KeypadSerializer

        return KeypadSerializer


class MotionPollKeypadConnectionAccessPermissions(BaseAccessPermissions):
    """
    Access permissions container for MotionPollKeypadConnection and MotionPollKeypadConnectionViewSet.
    """
    def can_retrieve(self, user):
        """
        Returns True if the user has VoteCollector access.
        """
        return user.has_perm('openslides_votecollector.can_manage_votecollector')

    def get_serializer_class(self, user=None):
        """
        Returns serializer class.
        """
        from .serializers import MotionPollKeypadConnectionSerializer

        return MotionPollKeypadConnectionSerializer
