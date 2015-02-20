# -*- coding: utf-8 -*-

import locale

from django.db.models import Max
from django.template.loader import render_to_string

from openslides.config.api import config
from openslides.motion.models import MotionPoll
from openslides.projector.api import SlideError, register_slide, slide_callback
from openslides.utils.exceptions import OpenSlidesError

from .models import Seat


def change_motionpoll_slide_template():
    """
    Overrides motion poll slide entry in the slide_callback dictionary. Raises
    OpenSlidesError if the former entry can not be found.
    """
    if 'motionpoll' not in slide_callback:
        raise OpenSlidesError(
            'Motion app was not properly loaded before loading '
            'openslides-votecollector. Please check you settings, particularly '
            'the INSTALLED_APPS.')

    def motionpoll_slide(**kwargs):
        """
        Returns the html code for the motion poll slide
        """
        # Get motion poll from url pattern argument
        slide_pk = kwargs.get('pk', None)
        try:
            slide = MotionPoll.objects.get(pk=slide_pk)
        except MotionPoll.DoesNotExist:
            raise SlideError
        else:
            # Get context of the slide
            context = slide.get_slide_context()

            # Generate seating plan with empty seats
            seating_plan = {}
            seats = Seat.objects.all()
            max_x_axis = seats.aggregate(Max('seating_plan_x_axis'))['seating_plan_x_axis__max']
            max_y_axis = seats.aggregate(Max('seating_plan_y_axis'))['seating_plan_y_axis__max']
            seating_plan['columns_number'] = max_x_axis
            seating_plan['width'] = '%dem' % (max_x_axis * 4)
            seating_plan['rows'] = [[None for j in range(max_x_axis)] for i in range(max_y_axis)]
            for seat in seats:
                seating_plan['rows'][seat.seating_plan_y_axis-1][seat.seating_plan_x_axis-1] = {'css': 'seat', 'number': seat.number}

            # Add votes to the seating plan and cummarize vote result
            all_keypad_votes = {'Y': 0,  'N': 0, 'A': 0}
            votes_with_seat = 0
            votes_without_seat = 0
            for keypad_data in context['poll'].keypad_data_list.select_related('keypad__seat'):
                all_keypad_votes[keypad_data.value] += 1
                if keypad_data.keypad is not None and keypad_data.keypad.seat:
                    x = keypad_data.keypad.seat.seating_plan_x_axis
                    y = keypad_data.keypad.seat.seating_plan_y_axis
                    seating_plan['rows'][y-1][x-1]['css'] += ' seat-%s' % keypad_data.get_css_value()
                    votes_with_seat += 1
                else:
                    votes_without_seat += 1
            votes_cast = all_keypad_votes['votes_cast'] = all_keypad_votes['Y'] + all_keypad_votes['N'] + all_keypad_votes['A']

            # Add percent values if useful or set all_keypad_votes to None
            # which means that nobody has use a keypad to vote.
            if votes_cast:
                if config['motion_poll_100_percent_base'] == 'WITHOUT_INVALID':
                    all_keypad_votes_percentage = {'Y': 0, 'N': 0, 'A': 0, 'votes_cast': 100}
                    locale.setlocale(locale.LC_ALL, '')
                    for item, votes in all_keypad_votes.items():
                        all_keypad_votes_percentage[item] = '%s' % locale.format('%.1f', votes * 100 / float(votes_cast))
                        all_keypad_votes_percentage[item+"_progress"] = '%.1f' % (votes * 100 / float(votes_cast))
            else:
                if config['votecollector_in_vote']:
                    all_keypad_votes = "{'Y': 0,  'N': 0, 'A': 0}"
                else:
                    all_keypad_votes = None
                all_keypad_votes_percentage = None

            # Add all context data
            context['seating_plan'] = seating_plan
            context['all_keypad_votes'] = all_keypad_votes
            context['all_keypad_votes_percentage'] = all_keypad_votes_percentage
            context['votes_with_seat'] = votes_with_seat
            context['votes_without_seat'] = votes_without_seat

        return render_to_string('openslides_votecollector/motionpoll_slide.html', context)

    register_slide(MotionPoll.slide_callback_name, motionpoll_slide, MotionPoll)


change_motionpoll_slide_template()
