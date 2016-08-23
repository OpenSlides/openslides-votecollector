(function () {

'use strict';

angular.module('OpenSlidesApp.openslides_votecollector', ['OpenSlidesApp.users'])

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

.factory('Voting', [
    '$http',
    '$timeout',
    'gettext',
    function ($http, $timeout, gettext) {
        var scope,
            poll_id = 0,
            is_voting = false;

        var getVotingStatus = function () {
            $http.get('/votecollector/status_yna/' + poll_id + '/').then(
                function (success) {
                    if (success.data.error) {
                        scope.$parent.$parent.$parent.alert = {type: 'danger', msg: success.data.error, show: true};
                        scope.cannot_poll = true;
                        scope.status = '';
                    }
                    else {
                        scope.$parent.$parent.$parent.alert = {};
                        scope.cannot_poll = false;
                        is_voting = success.data.is_polling;
                        if (is_voting) {
                            // TODO: translate
                            scope.command = gettext('Stop voting');
                            scope.status = 'Run time: ' + success.data.elapsed + '. ' +
                                'Votes received: ' + success.data.votes_received +
                                ' of ' + success.data.active_keypads;
                            $timeout(getVotingStatus, 1000);
                        }
                        else {
                            scope.command = gettext('Start voting');
                            scope.status = '';
                        }
                    }
                }
            );
        };

        return {
            setup: function ($scope) {
                scope = $scope;
                poll_id = scope.$parent.$parent.model.id;
                getVotingStatus();
            },
            isVoting: function () {
                return is_voting;
            },
            start: function () {
                // Must clear DS model.
                scope.$parent.$parent.model.yes = null;
                scope.$parent.$parent.model.no = null;
                scope.$parent.$parent.model.abstain = null;
                scope.$parent.$parent.model.votesvalid = null;
                scope.$parent.$parent.model.votesinvalid = null;
                scope.$parent.$parent.model.votescast = null;
                scope.status = 'Voting is starting...'
                scope.$parent.$parent.$parent.alert = {};
                $http.get('/votecollector/start_yna/' + poll_id + '/').then(
                    function (success) {
                        if (success.data.error) {
                            scope.$parent.$parent.$parent.alert = { type: 'danger', msg: success.data.error, show: true };
                            scope.status = gettext('No connection to VoteCollector.')
                        }
                        else {
                            is_voting = true;
                            // scope.command = gettext('Stop voting');
                            // scope.status = '';
                            getVotingStatus();
                        }
                    },
                    function (failure) {
                        scope.$parent.$parent.$parent.alert = { type: 'danger', msg: failure.status + ': ' + failure.statusText, show: true };
                        scope.status = gettext('No connection to VoteCollector.')
                    }
                );
            },
            stop: function () {
                $http.get('/votecollector/stop_yna/' + poll_id + '/').then(
                    function (success) {
                        if (success.data.error) {
                            scope.$parent.$parent.$parent.alert = { type: 'danger', msg: success.data.error, show: true };
                        }
                        else {
                            is_voting = false;
                            scope.command = gettext('Start voting');

                            $http.get('/votecollector/result_yna/' + poll_id + '/').then(
                                function (success) {
                                    if (success.data.error) {
                                        scope.$parent.$parent.$parent.alert = { type: 'danger', msg: success.data.error, show: true };
                                    }
                                    else {
                                        // update DS model.
                                        scope.$parent.$parent.model.yes = success.data.yes;
                                        scope.$parent.$parent.model.no = success.data.no;
                                        scope.$parent.$parent.model.abstain = success.data.abstain;
                                        scope.$parent.$parent.model.votesvalid = success.data.voted;
                                        scope.$parent.$parent.model.votesinvalid = 0;
                                        scope.$parent.$parent.model.votescast = success.data.voted;

                                        // notify user
                                        var message = gettext('Voting has ended. Do you want to save the result?');
                                        scope.$parent.$parent.$parent.alert = { type: 'info', msg: gettext(message), show: true };
                                        scope.status = scope.status.split('. ')[1];
                                    }
                                }
                            );
                        }
                    }
                );
            }
       }
    }
])

.factory('SpeakerList', [
    '$http',
    '$timeout',
    'gettext',
    function ($http, $timeout, gettext) {
        var scope,
            item_id = 0,
            is_active = false;

        var getVotingStatus = function () {
            $http.get('/votecollector/status_speaker_list/' + item_id + '/').then (
                function (success) {
                    if (success.data.error) {
                        scope.collectStatus = success.data.error;
                    }
                    else {
                        is_active = success.data.is_polling;
                        scope.collectStatus = '';
                        if (is_active) {
                            scope.collectCommand = gettext('Stop speaker registration');
                            // scope.collectStatus = gettext('Active...');
                            $timeout(getVotingStatus, 1000);
                        }
                        else {
                            scope.collectCommand = gettext('Start speaker registration');
                            // scope.collectStatus = '';
                        }
                    }
                }
            )
        };

        return {
            setup: function (id, $scope) {
                item_id = id;
                scope = $scope;
                getVotingStatus();

               // Get live speaker list status from server.
            },
            toggle: function () {
                if (is_active) {
                    $http.get('/votecollector/stop_speaker_list/' + item_id + '/').then(
                        function (success) {
                            if (success.data.error) {
                                scope.collectStatus = success.data.error;
                            }
                            else {
                                is_active = false;
                                scope.collectCommand = gettext('Start speaker registration');
                            }
                        }
                     );
                }
                else {
                    $http.get('/votecollector/start_speaker_list/' + item_id + '/').then(
                        function (success) {
                            if (success.data.error) {
                                scope.collectStatus = success.data.error;
                            }
                            else {
                                is_active = true;
                                getVotingStatus();
                            }
                        },
                        function (failure) {
                            // TODO: alert

                            // scope.$parent.$parent.$parent.alert = { type: 'danger', msg: failure.status + ': ' + failure.statusText, show: true };
                        }
                    );
                }
            }
        }
    }
])

.run(['Keypad', 'Seat', function (Keypad, Seat) {}]);

}());
