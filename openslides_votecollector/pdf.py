from django.utils.translation import ugettext as _
from reportlab.platypus import Paragraph

from openslides.config.api import config
from openslides.utils.pdf import stylesheet


def motion_poll_to_pdf_result(pdf, poll):
    """
    Creates a PDF with all results of a personal voting.
    """
    keypad_data_list = poll.keypad_data_list.select_related('keypad__user')
    if (not poll.has_votes() or (
            not keypad_data_list.exclude(keypad__user__exact=None).exists()
            and not keypad_data_list.exclude(serial_number__exact=None).exists())):
        raise Http404
    identifier = ''
    if poll.motion.identifier:
        identifier = ' %s' % poll.motion.identifier
    pdf.append(Paragraph('%s%s: %s' % (_('Motion'), identifier, poll.motion.title), stylesheet['Heading1']))
    pdf.append(Paragraph(_('Result'), stylesheet['Heading1']))
    for keypad_data in keypad_data_list:
        text = []
        if keypad_data.keypad.user:
            text.append(str(keypad_data.keypad.user))
            text.append(' ')
            text.append(keypad_data.keypad.user.structure_level)
        else:
            text.append(_('Anonymous'))
        text.append(' ')
        if keypad_data.serial_number:
            text.append(str(keypad_data.serial_number))
        else:
            text.append(str(keypad_data.keypad.keypad_id))
        text.append(' ')
        text.append(keypad_data.get_value())
        text = ''.join(text)
        pdf.append(Paragraph(text, stylesheet['Normal']))
    return pdf
