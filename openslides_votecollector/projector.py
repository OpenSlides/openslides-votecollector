from openslides.core.config import config
from openslides.core.exceptions import ProjectorException
from openslides.assignments.models import AssignmentPoll
from openslides.motions.models import MotionPoll
from openslides.utils.projector import ProjectorElement

from .models import Keypad, Seat, MotionPollKeypadConnection, AssignmentPollKeypadConnection, VoteCollector


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
            if config['votecollector_seating_plan']:
                yield from Seat.objects.all()
                keypads = Keypad.objects.all()
                yield from keypads
                for keypad in keypads:
                    # Yield user of each keypad
                    if keypad.user is not None:
                        yield keypad.user
            yield from MotionPollKeypadConnection.objects.filter(poll=motionpoll)

    def get_collection_elements_required_for_this(self, collection_element, config_entry):
        # If MPKC or Keypad is updated send only this element to projectors.
        # Else use default (which means a huge parsing of requirements).
        if collection_element.collection_string == MotionPollKeypadConnection.get_collection_string():
            output = [collection_element]
        elif collection_element.collection_string == Keypad.get_collection_string():
            output = [collection_element]
        elif collection_element.collection_string == VoteCollector.get_collection_string():
            output = []
        elif collection_element.information.get('votecollector_voting_msg_toggled'):
            output = []
        # TODO: Add new elif if seating plan config changed, use "information.get('changed_config')"
        else:
            output = super().get_collection_elements_required_for_this(collection_element, config_entry)
        return output


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
            yield assignmentpoll.assignment
            yield assignmentpoll.assignment.agenda_item
            for option in assignmentpoll.options.all():
                yield option.candidate
            if config['votecollector_seating_plan']:
                yield from Seat.objects.all()
                keypads = Keypad.objects.all()
                yield from keypads
                for keypad in keypads:
                    # Yield user of each keypad
                    if keypad.user is not None:
                        yield keypad.user
            yield from AssignmentPollKeypadConnection.objects.filter(poll=assignmentpoll)

    def get_collection_elements_required_for_this(self, collection_element, config_entry):
        # If APKC or Keypad is updated send only this element to projectors.
        # Else use default (which means a huge parsing of requirements).
        if collection_element.collection_string == AssignmentPollKeypadConnection.get_collection_string():
            output = [collection_element]
        elif collection_element.collection_string == Keypad.get_collection_string():
            output = [collection_element]
        elif collection_element.information.get('votecollector_voting_msg_toggled'):
            output = []
        # TODO: Add new elif if seating plan config changed, use "information.get('changed_config')"
        else:
            output = super().get_collection_elements_required_for_this(collection_element, config_entry)
        return output


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
