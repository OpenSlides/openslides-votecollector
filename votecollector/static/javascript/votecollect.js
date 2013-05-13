/**
 * JavaScript functions for VoteCollector Plugin.
 *
 * :copyright: 2012-2013 by Oskar Hahn, Emanuel Schütze
 * :license: GNU GPL, see LICENSE for more details.
 */

starting = false;
active_keypads = 0;

function vote_status() {
    $.ajax({
        type: 'GET',
        url: '/votecollector/votingstatus/' + get_poll_id() + '/',
        dataType: 'json',
        success: function(data) {
            if (data['error']) {
                $('#votecollector').hide();
                set_status(data['error']);
            } else {
                if (data['in_vote']) {
                    starting = false;
                    $('form input[name!="csrfmiddlewaretoken"]').attr('readonly', '1');
                    $('#votecollector').show().addClass('in_vote').html("<i class='icon icon-stop icon-white'></i> "+gettext('Stop Polling')).unbind().click(stop_voting);
                    var seconds = data['seconds'] % 60;
                    var minutes = (data['seconds'] - seconds)  / 60;
                    var time;
                    if (seconds.toString().length == 1){
                        seconds = '0' + seconds;
                    }
                    time = interpolate(gettext("%s:%s min"), [minutes, seconds]);
                    set_status('<br>' + interpolate(gettext("Poll is running since %s."), [time]) + '<br>' + interpolate(gettext('%s of %s votes are cast.'), [data['count'], data['active_keypads']]));
                    active_keypads = data['active_keypads'];

                } else if (starting != true) {
                    $('#votecollector').show().removeClass('in_vote').html("<i class='icon icon-play icon-white'></i> "+gettext('Start Polling')).unbind().click(start_voting);
                    set_status();
                }
            }
        }
    });
}

function set_status(status) {
    if (status) {
        $('#votecollector_status').html(status).show();
    } else {
        $('#votecollector_status').html('').slideUp();
    }
}

function clear_form() {
    set_form('', '', '', '', '');
}

function set_form(yes, no, contained, votesinvalid, votecast) {
    option_id = get_option_id();
    $('#id_option-' + option_id + '-Yes').val(yes);
    $('#id_option-' + option_id + '-No').val(no);
    $('#id_option-' + option_id + '-Abstain').val(contained);
    $('#id_pollform-votesinvalid').val(votesinvalid);
    $('#id_pollform-votescast').val(votecast);
}

function start_voting() {
    starting = true;
    set_status(gettext('start voting...'))
    clear_form();
    $.ajax({
        type: 'GET',
        url: '/votecollector/start/' + get_poll_id() + '/',
        dataType: 'json',
        success: function(data) {
            if (data.error) {
                set_status('');
                alert(data['error']);
            }
            vote_status();
        }
    });
}

function get_poll_id() {
    return $('#poll_id').html();
}

function get_option_id() {
    return $('form input[name!="csrfmiddlewaretoken"]').attr('id').split('-')[1];
}

function stop_voting() {
    set_status(gettext('stop voting...'))
    $.ajax({
        type: 'GET',
        url: '/votecollector/stop/' + get_poll_id() + '/',
        dataType: 'json',
        success: function(data) {
            vote_status();
            $.ajax({
                type: 'GET',
                url: '/votecollector/votingresults/',
                dataType: 'json',
                success: function(data) {
                    new_message(interpolate(gettext('The vote is over. %s out of %s votes collected. Do you want to save this values?'),[data['voted'], active_keypads]), 'info');
                    set_form(data['yes'], data['no'], data['abstain'], 0, data['voted']);
                }
            });
        }
    });
}

function receive_vote_status() {
    vote_status();
    setTimeout("receive_vote_status()", 1000);
}

$(function () {
    // get voting status to alter the page
    receive_vote_status();
});
