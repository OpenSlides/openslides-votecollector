(function () {

'use strict';

angular.module('OpenSlidesApp.openslides_votecollector', ['OpenSlidesApp.users'])

.factory('VoteCollector', [
    'DS',
    'gettext',
    function (DS, gettext) {
        return DS.defineResource({
            name: 'openslides_votecollector/votecollector',
            methods: {
                getErrorMessage: function (status, text) {
                    if (status == 503) {
                        return gettext('VoteCollector not running!');
                    }
                    return status + ': ' + text;
                },
                canPing: function () {
                    return !this.is_voting || this.voting_mode == 'SpeakerList';
                },
                canStartVoting: function (poll) {
                    return !this.is_voting || this.voting_mode == 'SpeakerList';
                },
                canStopVoting: function (poll) {
                    return this.is_voting && this.voting_mode == 'YesNoAbstain' && this.voting_target == poll.id;
                },
                canStartSpeakerList: function (item) {
                    return !this.is_voting || (this.voting_mode == 'SpeakerList' && this.voting_target != item.id);
                },
                canStopSpeakerList: function (item) {
                    return this.is_voting && this.voting_mode == 'SpeakerList' && this.voting_target == item.id;
                },
                getVotingStatus: function (poll) {
                    if (this.is_voting) {
                        if (this.voting_mode == 'Ping') {
                            return gettext('System test is runing.');
                        }
                        if (this.voting_mode == 'SpeakerList') {
                            return gettext('Speaker list voting is active for item ' + this.voting_target + '.');
                        }
                        if (this.voting_mode == 'YesNoAbstain') {
                            if (this.voting_target != poll.id) {
                                return gettext('Voting is active for motion poll ' + this.voting_target + '.');
                            }
                            // TODO: translate
                            return gettext('Votes received: ' + this.votes_received + ' of ' + this.voters_count);
                        }
                    }
                    return '';
                }
            }
        });
    }
])

.factory('Keypad', [
    'DS',
    'jsDataModel',
    function (DS, jsDataModel) {
        var name = 'openslides_votecollector/keypad',
            powerLevel = ['', 'full', 'medium', 'low', 'empty'],
            powerCSSIcon = ['', 'full', 'half', 'quarter', 'empty'],
            powerCSSColor = ['', '', '', 'danger', 'danger'];

        return DS.defineResource({
            name: name,
            useClass: jsDataModel,
            computed: {
                // No websocket update on computed!
                active: function () {
                    return this.isActive();
                },
                identified: function () {
                    return this.isIdentified();
                }
            },
            methods: {
                getTitle: function () {
                    return "Keypad " + this.keypad_id;
                },
                isActive: function () {
                    // TODO: inactive if not present?
                    return this.user === undefined || this.user.is_active;
                },
                isIdentified: function () {
                    return this.user !== undefined;
                },
                getSeatNumber: function () {
                    if (this.seat !== undefined) {
                        return this.seat.number;
                    }
                    else {
                        return '-';
                    }
                },
                power: function () {
                    return powerLevel[this.battery_level + 1];
                },
                powerCSSIcon: function () {
                    return powerCSSIcon[this.battery_level + 1]
                },
                powerCSSColor: function () {
                    return powerCSSColor[this.battery_level + 1]
                }
            },
            relations: {
                belongsTo: {
                    'users/user': {
                        localField: 'user',
                        localKey: 'user_id'
                    },
                    'openslides_votecollector/seat': {
                        localField: 'seat',
                        localKey: 'seat_id'
                    }
                }
            }
        });
    }
])

.factory('Seat', [
    'DS',
    function (DS) {
        return DS.defineResource({
            name: 'openslides_votecollector/seat'
        });
    }
])

.factory('MotionPollKeypadConnection', [
    'DS',
    function (DS) {
        return DS.defineResource({
            name: 'openslides_votecollector/motionpollkeypadconnection',
            relations: {
                belongsTo: {
                    'openslides_votecollector/keypad': {
                        localField: 'keypad',
                        localKey: 'keypad_id'
                    },
                }
            }
        });
    }
])

.run(['VoteCollector', 'Keypad', 'Seat', 'MotionPollKeypadConnection',
    function (VoteCollector, Keypad, Seat, MotionPollKeypadConnection) {}]);

}());
