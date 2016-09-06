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
        Motion.findAll().then(
            function (motions) {
                var result = MotionPollFinder.find(motions, pollId);
                $scope.$watch(function () {
                  return Motion.lastModified(result.motion.id);
                }, function () {
                    var result = MotionPollFinder.find(motions, pollId);
                    $scope.motion = Motion.get(result.motion.id);
                    $scope.poll = result.poll;
                });
            }
        );

        MotionPollKeypadConnection.findAll();
        Seat.findAll();
        Keypad.findAll().then(function(keypads){
            angular.forEach(keypads, function(keypad) {
                Keypad.loadRelations(keypad, 'user');
            });
        });
        $scope.$watch(function () {
            return MotionPollKeypadConnection.lastModified() +
                    Keypad.lastModified() +
                    Seat.lastModified() +
                    User.lastModified();
        }, function () {
            var allMPKCs = MotionPollKeypadConnection.getAll();
            var seats = Seat.getAll();
            var keypads = Keypad.getAll();

            // Extract all votes from collection of MotionPollKeypadConnection objects
            var votes = {};
            angular.forEach(allMPKCs, function (mpkc) {
                if (mpkc.poll_id === pollId) {
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
                }
            });
            // Generate seating plan with votes
            $scope.seatingPlan = SeatingPlan.generate(seats, votes);
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
        User.findAll()
        Assignment.findAll().then(
            function (assignments) {
                var result = AssignmentPollFinder.find(assignments, pollId);
                $scope.$watch(function () {
                    if (result.assignment) {
                        return Assignment.lastModified(result.assignment.id);
                    } else {
                        return false;
                    }
                }, function () {
                    var result = AssignmentPollFinder.find(assignments, pollId);
                    $scope.assignment = Assignment.get(result.assignment.id);
                    $scope.poll = result.poll;
                });
            }
        );

        $scope.$watch(
            function () {
                return $scope.poll;
            },
            function () {
                if ($scope.poll) {
                    $scope.ynaVotes = $scope.poll.options[0].getVotes();
                }
            }
        );

        AssignmentPollKeypadConnection.findAll();
        Seat.findAll();
        Keypad.findAll().then(function(keypads){
            angular.forEach(keypads, function(keypad) {
                Keypad.loadRelations(keypad, 'user');
            });
        });
        $scope.$watch(function () {
            return AssignmentPollKeypadConnection.lastModified() +
                    Keypad.lastModified() +
                    Seat.lastModified() +
                    User.lastModified();
        }, function () {
            var allAPKCs = AssignmentPollKeypadConnection.getAll();
            var seats = Seat.getAll();
            var keypads = Keypad.getAll();

            // Extract all votes from collection of MotionPollKeypadConnection objects
            var votes = {};
            var keys = {};
            angular.forEach(allAPKCs, function (apkc) {
                if (apkc.poll_id === pollId) {
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
                }
            });
            // Generate seating plan with votes
            $scope.seatingPlan = SeatingPlan.generate(seats, votes, keys);
        });
    }
]);

}());
