from openslides.core.exceptions import ProjectorException
from openslides.assignments.models import AssignmentPoll
from openslides.assignments.views import AssignmentViewSet
from openslides.motions.models import MotionPoll
from openslides.motions.views import MotionViewSet
from openslides.utils.projector import ProjectorElement, ProjectorRequirement

from .views import KeypadViewSet, SeatViewSet, MotionPollKeypadConnectionViewSet, AssignmentPollKeypadConnectionViewSet


class MotionPollSlide(ProjectorElement):
    """
    Slide definitions for Motion poll model.
    """
    name = 'votecollector/motionpoll'

    def check_data(self):
        pk = self.config_entry.get('id')
        if pk is not None:
            # Detail slide.
            if not MotionPoll.objects.filter(pk=pk).exists():
                raise ProjectorException('MotionPoll does not exist.')

    def get_requirements(self, config_entry):
        pk = config_entry.get('id')
        # Detail slide.
        try:
            motionpoll = MotionPoll.objects.get(pk=pk)
        except Motion.DoesNotExist:
            # Motion does not exist. Just do nothing.
            pass
        else:
            yield ProjectorRequirement(
                view_class=MotionViewSet,
                view_action='retrieve',
                pk=str(motionpoll.motion.pk))
            yield ProjectorRequirement(
                view_class=KeypadViewSet,
                view_action='retrieve')
            yield ProjectorRequirement(
                view_class=SeatViewSet,
                view_action='retrieve')
            yield ProjectorRequirement(
                view_class=MotionPollKeypadConnectionViewSet,
                view_action='retrieve')


class AssignmentPollSlide(ProjectorElement):
    """
    Slide definitions for Assignment poll model.
    """
    name = 'votecollector/assignmentpoll'

    def check_data(self):
        pk = self.config_entry.get('id')
        if pk is not None:
            # Detail slide.
            if not AssignmentPoll.objects.filter(pk=pk).exists():
                raise ProjectorException('AssignmentPoll does not exist.')

    def get_requirements(self, config_entry):
        pk = config_entry.get('id')
        # Detail slide.
        try:
            assignmentpoll = AssignmentPoll.objects.get(pk=pk)
        except Assignment.DoesNotExist:
            # Assignment does not exist. Just do nothing.
            pass
        else:
            yield ProjectorRequirement(
                view_class=AssignmentViewSet,
                view_action='retrieve',
                pk=str(assignmentpoll.assignment.pk))
            yield ProjectorRequirement(
                view_class=KeypadViewSet,
                view_action='retrieve')
            yield ProjectorRequirement(
                view_class=SeatViewSet,
                view_action='retrieve')
            yield ProjectorRequirement(
                view_class=AssignmentPollKeypadConnectionViewSet,
                view_action='retrieve')


class VotingPrompt(ProjectorElement):
    """
    Voting prompt on the projector.
    """
    name = 'voting/prompt'

    def check_data(self):
        if self.config_entry.get('message') is None:
            raise ProjectorException('No message given.')


class VotingIcon(ProjectorElement):
    """
    Voting icon on the projector.
    """
    name = 'voting/icon'
