from django.http import Http404
from django.utils.translation import ugettext as _
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Spacer, LongTable

from openslides.utils.pdf import stylesheet


def motion_poll_to_pdf_result(pdf, poll):
    """
    Create a PDF list of all results of a personal voting.
    """

    keypad_data_list = poll.keypad_data_list.select_related('keypad__user').order_by('serial_number', 'keypad')
    if (not poll.has_votes() or (
            not keypad_data_list.exclude(keypad__user__exact=None).exists()
            and not keypad_data_list.exclude(serial_number__exact=None).exists())):
        raise Http404
    identifier = ''
    if poll.motion.identifier:
        identifier = ' %s' % poll.motion.identifier
    pdf.append(Spacer(0, -1.5 * cm))
    pdf.append(Paragraph('%s%s: %s' % (_('Motion'), identifier, poll.motion.title), stylesheet['Heading3']))

    # total result
    option = poll.get_options()[0]
    totaldata = []
    totaldata.append([
        Paragraph(_('Yes'), stylesheet['Tablecell']),
        Paragraph(str(option['Yes']), stylesheet['Tablecell'])])
    totaldata.append([
        Paragraph(_('No'), stylesheet['Tablecell']),
        Paragraph(str(option['No']), stylesheet['Tablecell'])])
    totaldata.append([
        Paragraph(_('Abstention'), stylesheet['Tablecell']),
        Paragraph(str(option['Abstain']), stylesheet['Tablecell'])])
    totaldata.append([
        Paragraph(_('Valid votes'), stylesheet['Tablecell']),
        Paragraph(poll.print_votesvalid(), stylesheet['Tablecell'])])
    totaltable = LongTable(totaldata, style=[
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEABOVE', (0, 3), (-1, 3), 1, colors.black),
        ])
    totaltable._argW[0] = 3 * cm
    totaltable._argW[1] = 3 * cm
    pdf.append(totaltable)

    pdf.append(Spacer(0, 0.5 * cm))

    # table with single votes
    pdf.append(Paragraph(_('All single votes') + ':', stylesheet['Heading4']))
    data = [['#', _('Name'), _('Keypad serial number'), _('Vote')]]
    counter = 0
    for keypad_data in keypad_data_list:
        counter += 1
        line = []
        line.append(Paragraph(str(counter), stylesheet['Tablecell']))
        if keypad_data.keypad is not None and keypad_data.keypad.user:
            line.append(Paragraph(str(keypad_data.keypad.user), stylesheet['Tablecell']))
        else:
            line.append(Paragraph(_('Anonymous'), stylesheet['Tablecell']))
        if keypad_data.serial_number:
            line.append(Paragraph(str(keypad_data.serial_number), stylesheet['Tablecell']))
        else:
            line.append(Paragraph(str(keypad_data.keypad.keypad_id), stylesheet['Tablecell']))
        line.append(Paragraph(str(keypad_data.get_value()), stylesheet['Tablecell']))

        data.append(line)

    t = LongTable(data, style=[
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEABOVE', (0, 0), (-1, 0), 2, colors.black),
        ('LINEABOVE', (0, 1), (-1, 1), 1, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 2, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
            (colors.white, (.9, .9, .9)))])
    t._argW[0] = 0.75 * cm
    pdf.append(t)
    return pdf
