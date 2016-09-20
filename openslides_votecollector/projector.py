from openslides.core.exceptions import ProjectorException
from openslides.assignments.models import AssignmentPoll
from openslides.motions.models import MotionPoll
from openslides.utils.projector import ProjectorElement

from .models import Keypad, Seat, MotionPollKeypadConnection, AssignmentPollKeypadConnection


class MotionPollSlide(ProjectorElement):
    """
    Slide definitions for Motion poll model.
    """
    name = 'votecollector/motionpoll'

    def check_data(self):
        if not MotionPoll.objects.filter(pk=self.config_entry.get('id')).exists():
            raise ProjectorException('MotionPoll does not exist.')

    def get_requirements(self, config_entry):
        try:
            motionpoll = MotionPoll.objects.get(pk=config_entry.get('id'))
        except MotionPoll.DoesNotExist:
            # MotionPoll does not exist. Just do nothing.
            pass
        else:
            yield motionpoll.motion
            yield motionpoll.motion.agenda_item
            yield from Seat.objects.all()
            keypads = Keypad.objects.all()
            yield from keypads
            for keypad in keypads:
                # Yield user of each keypad
                if keypad.user is not None:
                    yield keypad.user
            yield from MotionPollKeypadConnection.objects.all()


class AssignmentPollSlide(ProjectorElement):
    """
    Slide definitions for Assignment poll model.
    """
    name = 'votecollector/assignmentpoll'

    def check_data(self):
        if not AssignmentPoll.objects.filter(pk=self.config_entry.get('id')).exists():
            raise ProjectorException('AssignmentPoll does not exist.')

    def get_requirements(self, config_entry):
        try:
            assignmentpoll = AssignmentPoll.objects.get(pk=config_entry.get('id'))
        except AssignmentPoll.DoesNotExist:
            # AssignmentPoll does not exist. Just do nothing.
            pass
        else:
            assignment = assignmentpoll.assignment
            yield assignment
            yield assignment.agenda_item
            for option in assignmentpoll.options.all():
                yield option.candidate
            yield from Seat.objects.all()
            keypads = Keypad.objects.all()
            yield from keypads
            for keypad in keypads:
                # Yield user of each keypad
                if keypad.user is not None:
                    yield keypad.user
            yield from AssignmentPollKeypadConnection.objects.all()

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
