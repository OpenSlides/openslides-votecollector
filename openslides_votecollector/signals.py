from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from openslides.users.models import Group
# from openslides.projector.api import update_projector
# from openslides.projector.projector import Overlay
# from openslides.projector.signals import projector_overlays

from .models import Seat
from .seating_plan import setup_default_plan


def add_permissions_to_builtin_groups(**kwargs):
    """
    Adds the permissions openslides_votecollector.can_manage_votecollector to the group staff.
    """
    content_type = ContentType.objects.get(app_label='openslides_votecollector', model='keypad')

    try:
        staff = Group.objects.get(pk=4)
    except Group.DoesNotExist:
        pass
    else:
        perm_can_manage = Permission.objects.get(content_type=content_type, codename='can_manage_votecollector')
        staff.permissions.add(perm_can_manage)


def add_default_seating_plan(**kwargs):
    """
    Adds a default seating plan if there are no seats in the database.
    """
    if Seat.objects.all().exists():
        # Do nothing if there are seats in the database
        return
    setup_default_plan()


# TODO: projector overlay message
# @receiver(projector_overlays, dispatch_uid='votecollector_overlay_message')
# def overlay_message(sender, **kwargs):
#     """
#     Adds an overlay to show the votecollector message in non live voting mode.
#     """
#     def get_projector_html():
#         """
#         Returns the html for the votecollector message on the projector.
#         """
#         if config['votecollector_in_vote']:
#             key_yes = "<span class='nobr'><img src='/static/img/button-yes.png'> %s</span>" % _('Yes')
#             key_no = "<span class='nobr'><img src='/static/img/button-no.png'> %s</span>" % _('No')
#             key_abstention = "<span class='nobr'><img src='/static/img/button-abstention.png'> %s</span>" % _('Abstention')
#             message = "%s <br> %s &nbsp; %s &nbsp; %s " % (
#                 config['votecollector_vote_started_msg'],
#                 key_yes, key_no, key_abstention)
#             value = render_to_string('openslides_votecollector/overlay_votecollector_projector.html', {'message': message})
#         else:
#             value = None
#         return value
#
#     return Overlay(
#         name='votecollector_message',
#         get_widget_html=None,
#         get_projector_html=get_projector_html,
#         allways_active=True)
