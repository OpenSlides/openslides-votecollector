(function () {

'use strict';

angular.module('OpenSlidesApp.openslides_votecollector', ['OpenSlidesApp.users', 'OpenSlidesApp.core'])

.factory('VoteCollector', [
    'DS',
    'gettext',
    function (DS, gettext) {
        return DS.defineResource({
            name: 'openslides_votecollector/vote-collector',
            methods: {
                getErrorMessage: function (status, text) {
                    if (status == 503) {
                        return gettext('VoteCollector not running!');
                    }
                    return status + ': ' + text;
                }
            }
        });
    }
])

.factory('Keypad', [
    'DS',
    'gettext',
    'jsDataModel',
    function (DS, gettext, jsDataModel) {
        var name = 'openslides_votecollector/keypad',
            powerLevel = ['', gettext('full'), gettext('medium'), gettext('low'), gettext('empty')],
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
                    return this.user === undefined || this.user.is_present;
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
    'Keypad',
    function (DS, Keypad) {
        return DS.defineResource({
            name: 'openslides_votecollector/seat',
            relations: {
                hasOne: {
                    'openslides_votecollector/keypad': {
                        localField: 'keypad',
                        localKey: 'keypad_id'
                    }
                }
            },
            methods: {
                isActive: function () {
                    var seat = this;
                    var keypad = _.find(Keypad.getAll(), function(keypad) {
                        return keypad.seat_id == seat.id;
                    });
                    return keypad ? keypad.isActive() : undefined;
                }
            }
        });
    }
])

.factory('MotionPollKeypadConnection', [
    'DS',
    function (DS) {
        return DS.defineResource({
            name: 'openslides_votecollector/motion-poll-keypad-connection',
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

.factory('MotionPollFinder', [
    function () {
        return {
            find: function (motions, pollId) {
                // Find motion and poll from poll id.
                var i = -1;
                var result = {};
                while (++i < motions.length && !result.poll) {
                    result.poll = _.find(
                        motions[i].polls,
                        function (poll) {
                            return poll.id == pollId;
                        }
                    );
                    if (result.poll) {
                        result.motion = motions[i];
                    }
                }
                return result;
            }
        }
    }
])

.factory('AssignmentPollKeypadConnection', [
    'DS',
    function (DS) {
        return DS.defineResource({
            name: 'openslides_votecollector/assignment-poll-keypad-connection',
        });
    }
])

.factory('AssignmentPollFinder', [
    function () {
        return {
            find: function (assignments, pollId) {
                // Find assignment and poll from poll id.
                var i = -1;
                var result = {};
                while (++i < assignments.length && !result.poll) {
                    result.poll = _.find(
                        assignments[i].polls,
                        function (poll) {
                            return poll.id == pollId;
                        }
                    );
                    if (result.poll) {
                        result.assignment = assignments[i];
                    }
                }
                return result;
            }
        }
    }
])

.factory('SeatingPlan', [
    'Config',
    function (Config) {
        return {
            generateRows: function (seats, votes, keys) {
                // Generate seating plan with votes or empty seats
                var seatingPlan = {};
                var maxXAxis = _.reduce(seats, function (max, seat) {
                    return seat.seating_plan_x_axis > max ? seat.seating_plan_x_axis : max;
                }, 0);
                var maxYAxis = _.reduce(seats, function (max, seat) {
                    return seat.seating_plan_y_axis > max ? seat.seating_plan_y_axis : max;
                }, 0);
                seatingPlan.rows = _.map(_.range(maxYAxis), function () {
                    return _.map(_.range(maxXAxis), function () {
                        return {};
                    });
                });
                angular.forEach(seats, function (seat) {
                    var css = 'seat';
                    var key;
                    if (votes && votes[seat.id]) {
                        css += ' ' + votes[seat.id];
                    }
                    if (keys && keys[seat.id]) {
                        key = keys[seat.id];
                    }
                    seatingPlan.rows[seat.seating_plan_y_axis-1][seat.seating_plan_x_axis-1] = {
                        'css': css,
                        'number': seat.number,
                        'id': seat.id,
                        'key': key,
                        'is_active': seat ? seat.isActive() : null
                    };
                });
                return seatingPlan;
            },
            generateHTML: function (seats, votes, poll, keys) {
                // get seatingPlan rows
                var seatingPlan = this.generateRows(seats, votes, keys);

                // prebuild seatingPlan html table to speed up template rendering
                var table = '<table>';
                angular.forEach(seatingPlan.rows, function(row) {
                    table += '<tr>';
                    angular.forEach(row, function(seat) {
                        var css = '';
                        css += seat.css ? seat.css : '';
                        table += '<td class="' + css + '">';
                        if (seat.is_active) {
                            table += seat.number;
                        }
                        if (seat.key && poll.pollmethod == 'votes') {
                            table += '<span class="key">' + seat.key + '</span>';
                        }
                        table += '</td>';
                    })
                });
                return table;
            }
        };
    }
])

.config([
    'OpenSlidesPluginsProvider',
    function(OpenSlidesPluginsProvider) {
        OpenSlidesPluginsProvider.registerPlugin({
            name: 'openslides_votecollector',
            display_name: 'VoteCollector',
            languages: ['de']
        });
    }
])

.run(['VoteCollector', 'Keypad', 'Seat', 'MotionPollKeypadConnection', 'AssignmentPollKeypadConnection',
    function (VoteCollector, Keypad, Seat, MotionPollKeypadConnection, AssignmentPollKeypadConnection) {}]);

}());
