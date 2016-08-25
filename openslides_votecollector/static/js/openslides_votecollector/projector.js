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
    function ($scope, Config, Motion, Keypad, Seat, MotionPollKeypadConnection, MotionPollFinder, SeatingPlan) {
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
        Seat.findAll().then(function (seats) {
            $scope.$watch(function () {
              return MotionPollKeypadConnection.lastModified();
            }, function () {
                var allMPKCs = MotionPollKeypadConnection.getAll();
                Keypad.findAll().then(function (keypads) {
                    // Extract all votes from collection of MotionPollKeypadConnection objects
                    var votes = {};
                    angular.forEach(allMPKCs, function (mpkc) {
                        if (mpkc.poll_id === pollId) {
                            // Get seat id from keypad
                            var keypad = _.find(keypads, function (keypad) {
                                return keypad.keypad_id == mpkc.keypad_id;
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
            });
        });
    }
]);

}());
