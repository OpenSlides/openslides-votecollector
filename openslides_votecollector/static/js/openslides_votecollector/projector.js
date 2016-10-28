(function () {

'use strict';

angular.module('OpenSlidesApp.openslides_votecollector.projector', ['OpenSlidesApp.openslides_votecollector'])

.config([
    'slidesProvider',
    function(slidesProvider) {
        slidesProvider.registerSlide('voting/prompt', {
            template: 'static/templates/openslides_votecollector/slide_prompt.html'
        });
        slidesProvider.registerSlide('voting/icon', {
            template: 'static/templates/openslides_votecollector/slide_icon.html'
        });
        slidesProvider.registerSlide('votecollector/motionpoll', {
            template: 'static/templates/openslides_votecollector/slide_motionpoll.html',
        });
        slidesProvider.registerSlide('votecollector/assignmentpoll', {
            template: 'static/templates/openslides_votecollector/slide_assignmentpoll.html',
        });
    }
])

.controller('SlidePromptCtrl', [
    '$scope',
    function($scope) {
        // Attention! Each object that is used here has to be dealt with on server side.
        // Add it to the corresponding get_requirements method of the ProjectorElement
        // class.
        $scope.message = $scope.element.message;
        $scope.visible = $scope.element.visible;
    }
])

.controller('SlideIconCtrl', [
    '$scope',
    function($scope) {
        // Attention! Each object that is used here has to be dealt with on server side.
        // Add it to the corresponding get_requirements method of the ProjectorElement
        // class.
        $scope.message = $scope.element.message;
        $scope.visible = $scope.element.visible;
    }
])

.controller('SlideMotionPollCtrl', [
    '$scope',
    'Config',
    'Motion',
    'Keypad',
    'Seat',
    'MotionPollKeypadConnection',
    'MotionPollFinder',
    'SeatingPlan',
    'User',
    function ($scope, Config, Motion, Keypad, Seat, MotionPollKeypadConnection, MotionPollFinder, SeatingPlan, User) {
        // Attention! Each object that is used here has to be dealt on server side.
        // Add it to the coresponding get_requirements method of the ProjectorElement
        // class.
        var pollId = $scope.element.id;
        var result = MotionPollFinder.find(Motion.getAll(), pollId);
        $scope.$watch(function () {
            return Motion.lastModified(result.motion.id);
                // + Agenda.lastModified(result.motion.agenda_item_id);
        }, function () {
            var result = MotionPollFinder.find(Motion.getAll(), pollId);
            $scope.motion = result.motion;
            $scope.poll = result.poll;
        });

        $scope.$watch(function () {
            return MotionPollKeypadConnection.lastModified() +
                    Keypad.lastModified() +
                    Seat.lastModified() +
                    User.lastModified() +
                    Motion.lastModified(result.motion.id);
        }, function () {
            var allMPKCs = MotionPollKeypadConnection.filter({poll_id: pollId});
            var seats = Seat.getAll();
            var keypads = Keypad.getAll();

            // Extract all votes from collection of MotionPollKeypadConnection objects
            // TODO: Use MotionPollBallot to mark seats of represented delegates.
            var votes = {};
            $scope.votes_received = 0;
            if (Config.get('votecollector_live_voting').value) {
                $scope.liveVotes = {yes: 0, no: 0, abstain: 0};
            }
            angular.forEach(allMPKCs, function (mpkc) {
                // Get seat id from keypad
                var keypad = _.find(keypads, function (keypad) {
                    return keypad.id == mpkc.keypad_id;
                });
                var seat_id = keypad ? keypad.seat_id : undefined;
                // Set seat colors
                // TODO: Fix autoupdate if config changes on runtime.
                if (seat_id) {
                    if (Config.get('votecollector_seats_grey').value) {
                        votes[seat_id] = 'seat-grey';
                    } else {
                        switch (mpkc.value) {
                            case 'Y':
                                votes[seat_id] = 'seat-green';
                                break;
                            case 'N':
                                votes[seat_id] = 'seat-red';
                                break;
                            case 'A':
                                votes[seat_id] = 'seat-yellow';
                                break;
                        }
                    }
                }
                if (Config.get('votecollector_live_voting').value) {
                    switch (mpkc.value) {
                        case 'Y':
                            $scope.liveVotes.yes += 1;
                            break;
                        case 'N':
                            $scope.liveVotes.no += 1;
                            break;
                        case 'A':
                            $scope.liveVotes.abstain += 1;
                            break;
                    }
                }
                if (mpkc.value == 'Y' || mpkc.value == 'N' || mpkc.value == 'A') {
                    $scope.votes_received += 1;
                }
            });
            // Generate seating plan with votes
            $scope.seatingPlanTable = SeatingPlan.generateHTML(seats, votes, $scope.poll);
        });
    }
])

.controller('SlideAssignmentPollCtrl', [
    '$scope',
    'Config',
    'Assignment',
    'Keypad',
    'Seat',
    'User',
    'AssignmentPollKeypadConnection',
    'AssignmentPollFinder',
    'SeatingPlan',
    function ($scope, Config, Assignment, Keypad, Seat, User, AssignmentPollKeypadConnection, AssignmentPollFinder, SeatingPlan) {
        // Attention! Each object that is used here has to be dealt on server side.
        // Add it to the coresponding get_requirements method of the ProjectorElement
        // class.
        var pollId = $scope.element.id;
        var result = AssignmentPollFinder.find(Assignment.getAll(), pollId);
        $scope.$watch(function () {
            return Assignment.lastModified(result.assignment_id);
                // + Agenda.lastModified(result.motion.agenda_item_id);
        }, function () {
            var result = AssignmentPollFinder.find(Assignment.getAll(), pollId);
            $scope.assignment = result.assignment;
            $scope.poll = result.poll;
            if ($scope.poll) {
                $scope.ynaVotes = $scope.poll.options[0].getVotes();
            }
        });

        $scope.$watch(function () {
            return AssignmentPollKeypadConnection.lastModified() +
                    Keypad.lastModified() +
                    Seat.lastModified() +
                    User.lastModified() +
                    Assignment.lastModified(result.assignment_id);
        }, function () {
            var allAPKCs = AssignmentPollKeypadConnection.filter({poll_id: pollId});
            var seats = Seat.getAll();
            var keypads = Keypad.getAll();

            // Extract all votes from collection of MotionPollKeypadConnection objects
            var votes = {};
            var keys = {};
            $scope.votes_received = 0;
            if (Config.get('votecollector_live_voting').value) {
                $scope.liveVotes = {yes: 0, no: 0, abstain: 0};
            }
            angular.forEach(allAPKCs, function (apkc) {
                // Get seat id from keypad
                var keypad = _.find(keypads, function (keypad) {
                    return keypad.id == apkc.keypad_id;
                });
                var seat_id = keypad ? keypad.seat_id : undefined;
                // Set seat colors
                // TODO: Fix autoupdate if config changes on runtime.
                if (seat_id) {
                    if (Config.get('votecollector_seats_grey').value) {
                        votes[seat_id] = 'seat-grey';
                    } else {
                        keys[seat_id] = apkc.value;
                        switch (apkc.value) {
                            case 'Y':
                                votes[seat_id] = 'seat-green';
                                break;
                            case 'N':
                                votes[seat_id] = 'seat-red';
                                break;
                            case 'A':
                                votes[seat_id] = 'seat-yellow';
                                break;
                            case '0':
                                votes[seat_id] = 'seat-yellow';
                                break;
                            default:
                                votes[seat_id] = 'seat-voted';
                                break;
                        }
                    }
                }
                if (Config.get('votecollector_live_voting').value) {
                    switch (apkc.value) {
                        case 'Y':
                            $scope.liveVotes.yes += 1;
                            break;
                        case 'N':
                            $scope.liveVotes.no += 1;
                            break;
                        case 'A':
                            $scope.liveVotes.abstain += 1;
                            break;
                    }
                }
                if (apkc.value == 'Y' || apkc.value == 'N' || apkc.value == 'A') {
                    $scope.votes_received += 1;
                }
            });
            // Generate seating plan with votes
            $scope.seatingPlanTable = SeatingPlan.generateHTML(seats, votes, $scope.poll, keys);
        });
    }
]);

}());
