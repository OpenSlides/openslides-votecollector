from openslides.utils.access_permissions import BaseAccessPermissions
from openslides.utils.auth import has_perm


class VoteCollectorAccessPermissions(BaseAccessPermissions):
    """
    Access permissions container for VoteCollector.
    """
    def check_permissions(self, user):
        """
        Returns True if the user has VoteCollector access.
        """
        return has_perm(user, 'openslides_votecollector.can_manage')

    def get_serializer_class(self, user=None):
        """
        Returns serializer class.
        """
        from .serializers import VoteCollectorSerializer

        return VoteCollectorSerializer


class SeatAccessPermissions(BaseAccessPermissions):
    """
    Access permissions container for Seat and SeatViewSet.
    """
    def check_permissions(self, user):
        """
        Returns True if the user has VoteCollector access.
        """
        return has_perm(user, 'openslides_votecollector.can_manage')

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
    def check_permissions(self, user):
        """
        Returns True if the user has VoteCollector access.
        """
        return has_perm(user, 'openslides_votecollector.can_manage')

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
    def check_permissions(self, user):
        """
        Returns True if the user has VoteCollector access.
        """
        return has_perm(user, 'openslides_votecollector.can_manage')

    def get_serializer_class(self, user=None):
        """
        Returns serializer class.
        """
        from .serializers import MotionPollKeypadConnectionSerializer

        return MotionPollKeypadConnectionSerializer


class AssignmentPollKeypadConnectionAccessPermissions(BaseAccessPermissions):
    """
    Access permissions container for AssignmentPollKeypadConnection and AssignmentPollKeypadConnectionViewSet.
    """
    def check_permissions(self, user):
        """
        Returns True if the user has VoteCollector access.
        """
        return has_perm(user, 'openslides_votecollector.can_manage')

    def get_serializer_class(self, user=None):
        """
        Returns serializer class.
        """
        from .serializers import AssignmentPollKeypadConnectionSerializer

        return AssignmentPollKeypadConnectionSerializer
