(function () {

'use strict';

angular.module('OpenSlidesApp.openslides_votecollector.site', [
    'OpenSlidesApp.openslides_votecollector'
])

.config([
    'mainMenuProvider',
    'gettext',
    function (mainMenuProvider, gettext) {
        mainMenuProvider.register({
            'ui_sref': 'openslides_votecollector.keypad.list',
            'img_class': 'wifi',
            'title': 'VoteCollector',
            'weight': 700,
            'perm': 'openslides_votecollector.can_manage',
        });
    }
])

.config([
    '$stateProvider',
    function ($stateProvider) {
        $stateProvider
        .state('openslides_votecollector', {
            url: '/votecollector',
            abstract: true,
            template: "<ui-view/>",
        })
        .state('openslides_votecollector.keypad', {
            abstract: true,
            template: "<ui-view/>",
        })
        .state('openslides_votecollector.keypad.list', {
            resolve: {
                keypads: function (Keypad) {
                    return Keypad.findAll();
                },
                seats: function (Seat) {
                    return Seat.findAll();
                },
                vc: function(VoteCollector) {
                    return VoteCollector.find(1);
                }
            }
        })
        .state('openslides_votecollector.keypad.import', {
            url: '/import',
            controller: 'KeypadImportCtrl',
            resolve: {
                keypads: function(Keypad) {
                    return Keypad.findAll();
                },
                seats: function (Seat) {
                    return Seat.findAll();
                }
            }
        })
        .state('openslides_votecollector.motionpoll', {
            abstract: true,
            template: "<ui-view/>",
        })
        .state('openslides_votecollector.motionpoll.detail', {
            url: '/motionpoll/:id',
            controller: 'MotionPollVoteDetailCtrl',
            resolve: {
                motionpollkeypadconnections: function (MotionPollKeypadConnection) {
                    return MotionPollKeypadConnection.findAll();
                },
                keypads: function (Keypad) {
                    return Keypad.findAll();
                }
            }
        })
        .state('openslides_votecollector.assignmentpoll', {
            abstract: true,
            template: "<ui-view/>",
        })
        .state('openslides_votecollector.assignmentpoll.detail', {
            url: '/assignmentpoll/:id',
            controller: 'AssignmentPollVoteDetailCtrl',
            resolve: {
                assignmentpollkeypadconnections: function (AssignmentPollKeypadConnection) {
                    return AssignmentPollKeypadConnection.findAll();
                },
                keypads: function (Keypad) {
                    return Keypad.findAll();
                }
            }
        })
    }
])

// Service for generic keypad form (create and update)
.factory('KeypadForm', [
    'gettextCatalog',
    'User',
    'Seat',
    function (gettextCatalog, User, Seat) {
        return {
            // ngDialog for keypad form
            getDialog: function (keypad) {
                var resolve = {};
                if (keypad) {
                    resolve = {
                        keypad: function () {
                            return keypad;
                        }
                    }
                }
                return {
                    template: 'static/templates/openslides_votecollector/keypad-form.html',
                    controller: (keypad) ? 'KeypadUpdateCtrl' : 'KeypadCreateCtrl',
                    className: 'ngdialog-theme-default',
                    closeByEscape: false,
                    closeByDocument: false,
                    resolve: (resolve) ? resolve : null
                }
            },
            // angular-formly fields for keypad form
            getFormFields: function () {
                return [
                {
                    key: 'user_id',
                    type: 'select-single',
                    templateOptions: {
                        label: gettextCatalog.getString('Participant'),
                        options: User.getAll(),
                        ngOptions: 'option.id as option.full_name for option in to.options',
                        placeholder: '(' + gettextCatalog.getString('Anonymous') + ')'
                    }
                },
                {
                    key: 'keypad_id',
                    type: 'input',
                    templateOptions: {
                        label: gettextCatalog.getString('Keypad ID'),
                        type: 'number',
                        required: true
                    }
                },
                {
                    key: 'seat_id',
                    type: 'select-single',
                    templateOptions: {
                        label: gettextCatalog.getString('Seat'),
                        options: Seat.getAll(),
                        ngOptions: 'option.id as option.number for option in to.options',
                        placeholder: gettextCatalog.getString('--- Select seat ---')
                    }
                }
                ]
            }
        }
    }
])

.controller('KeypadListCtrl', [
    '$scope',
    '$http',
    '$timeout',
    'ngDialog',
    'SeatingPlan',
    'KeypadForm',
    'Keypad',
    'User',
    'Seat',
    'VoteCollector',
    function ($scope, $http, $timeout, ngDialog, SeatingPlan, KeypadForm, Keypad, User, Seat, VoteCollector) {
        Keypad.bindAll({}, $scope, 'keypads');
        User.bindAll({}, $scope, 'users');
        Seat.bindAll({}, $scope, 'seats');
        VoteCollector.bindOne(1, $scope, 'vc');
        $scope.alert = {};

        // setup table sorting
        $scope.sortColumn = 'keypad_id';
        $scope.reverse = false;
        // function to sort by clicked column
        $scope.toggleSort = function ( column ) {
            if ( $scope.sortColumn === column ) {
                $scope.reverse = !$scope.reverse;
            }
            $scope.sortColumn = column;
        };
        // define custom search filter string
        $scope.getFilterString = function (keypad) {
            var seat = '', user = '';
            if (keypad.seat) {
                seat = keypad.seat.number;
            }
            if (keypad.user) {
                user = keypad.user.get_full_name();
            }
            return [
                keypad.keypad_id,
                seat,
                user
            ].join(" ");
        };

        // open new/edit dialog
        $scope.openDialog = function (keypad) {
            ngDialog.open(KeypadForm.getDialog(keypad));
        };

        // *** delete mode functions ***
        $scope.isDeleteMode = false;
        // check all checkboxes
        $scope.checkAll = function () {
            angular.forEach($scope.keypads, function (keypad) {
                keypad.selected = $scope.selectedAll;
            });
        };
        // uncheck all checkboxes if isDeleteMode is closed
        $scope.uncheckAll = function () {
            if (!$scope.isDeleteMode) {
                $scope.selectedAll = false;
                angular.forEach($scope.keypads, function (keypad) {
                    keypad.selected = false;
                });
            }
        };
        // delete selected keypads
        $scope.deleteMultiple = function () {
            angular.forEach($scope.keypads, function (keypad) {
                if (keypad.selected)
                    Keypad.destroy(keypad.id);
            });
            $scope.isDeleteMode = false;
            $scope.uncheckAll();
        };
        // delete single keypad
        $scope.delete = function (keypad) {
            Keypad.destroy(keypad.id);
        };

        // save changed keypad user
        $scope.saveUser = function (user) {
            User.save(user);
        };

        // keypad system test
        $scope.startSysTest = function () {
            $scope.device = null;

            angular.forEach($scope.keypads, function (keypad) {
                keypad.in_range = false;
                keypad.battery_level = -1;
            })

            $http.get('/votecollector/device/').then(
                function (success) {
                    if (success.data.error) {
                        $scope.device = success.data.error;
                    }
                    else {
                        $scope.device = success.data.device;
                        if (success.data.connected) {
                            $http.get('/votecollector/start_ping/').then(
                                function (success) {
                                    if (success.data.error) {
                                        $scope.device = success.data.error;
                                    }
                                    else {
                                        // Stop test after 1 min.
                                        $timeout(function () {
                                            if ($scope.vc.is_voting && $scope.vc.voting_mode == 'Test') {
                                                $scope.stopSysTest();
                                            }
                                        }, 60000);
                                    }
                                }
                            );
                        }
                     }
                },
                function (failure) {
                    $scope.device = $scope.vc.getErrorMessage(failure.status, failure.statusText);
                }
            );
        };

        $scope.stopSysTest = function () {
            $http.get('/votecollector/stop/');
        };

        // Generate seating plan with empty seats
        $scope.seatingPlan = SeatingPlan.generateRows(Seat.getAll());

        $scope.changeSeat = function (seat, result) {
            seat.number = result;
            // Inject the changed seat object back into DS store.
            Seat.inject(seat);
            // Save change seat object on server.
            Seat.save(seat).then(
                function (success) {},
                function (error) {}
            );
        }

    }
])

.controller('KeypadCreateCtrl', [
    '$scope',
    'Keypad',
    'KeypadForm',
    function ($scope, Keypad, KeypadForm) {
        $scope.model = {};
        // get all form fields
        $scope.formFields = KeypadForm.getFormFields();

        // save keypad
        $scope.save = function (keypad) {
            Keypad.create(keypad).then(
                function (success) {
                    $scope.closeThisDialog();
                },
                function (error) {
                    var message = '';
                    for (var e in error.data) {
                        message += e + ': ' + error.data[e] + ' ';
                    }
                    $scope.alert = {type: 'danger', msg: message, show: true};
                }
            );
        };
    }
])

.controller('KeypadUpdateCtrl', [
    '$scope',
    'Keypad',
    'KeypadForm',
    'keypad',
    function ($scope, Keypad, KeypadForm, keypad) {
        $scope.alert = {};
        // set initial values for form model by create deep copy of keypad object
        // so list/detail view is not updated while editing
        $scope.model = angular.copy(keypad);

        // get all form fields
        $scope.formFields = KeypadForm.getFormFields();

        // save keypad
        $scope.save = function (keypad) {
            // inject the changed keypad (copy) object back into DS store
            Keypad.inject(keypad);
            // save change keypad object on server
            Keypad.save(keypad).then(
                function (success) {
                    $scope.closeThisDialog();
                },
                function (error) {
                    // save error: revert all changes by restore
                    // (refresh) original keypad object from server
                    Keypad.refresh(keypad);
                    var message = '';
                    for (var e in error.data) {
                        message += e + ': ' + error.data[e] + ' ';
                    }
                    $scope.alert = {type: 'danger', msg: message, show: true};
                }
            );
        };
    }
])

.controller('KeypadImportCtrl', [
    '$scope',
    '$http',
    'gettext',
    'gettextCatalog',
    'CsvDownload',
    'Keypad',
    'User',
    'Seat',
    function ($scope, $http, gettext, gettextCatalog, CsvDownload, Keypad, User, Seat) {
        $scope.csvConfig = {
            accept: '.csv, .txt',
            encodingOptions: ['UTF-8', 'ISO-8859-1'],
            parseConfig: {
                skipEmptyLines: true,
            },
        };

        var FIELDS = ['title', 'first_name', 'last_name', 'structure_level', 'number',
        'groups', 'comment', 'is_active', 'is_present', 'is_committee', 'default_password',
        'keypad_id', 'seat_label'];
        $scope.keypads = [];
        $scope.onCsvChange = function (csv) {
            // All keypad objects are already loaded via the resolve statement from ui-router.
            var keypads = Keypad.getAll();
            $scope.keypads = [];

            var csvKeypads = [];
            _.forEach(csv.data, function (row) {
                if (row.length >= 2) {
                    var filledRow = _.zipObject(FIELDS, row);
                    csvKeypads.push(filledRow);
                }
            });
            _.forEach(csvKeypads, function (keypaduser) {
                keypaduser.selected = true;
                // check if given keypaduser already exists
                if (keypaduser.first_name == '' && keypaduser.last_name == '') {
                    // no personalized keypad -> anonymous user
                    keypaduser.user_id = null;
                } else {
                    keypaduser.fullname = [keypaduser.title, keypaduser.first_name,
                        keypaduser.last_name, keypaduser.structure_level].join(' ');
                    angular.forEach(User.getAll(), function(user) {
                        user.fullname = [user.title, user.first_name, user.last_name, user.structure_level].join(' ');
                        if (user.fullname == keypaduser.fullname) {
                            keypaduser.user_id = user.id;
                        }
                    });
                    if (!keypaduser.user_id) {
                        keypaduser.importerror = true;
                        keypaduser.name_error = gettext('Error: Participant not found.');
                        keypaduser.user_id = -1;
                    }
                    if (keypaduser.user_id && Keypad.filter({ 'user_id': keypaduser.user_id }).length > 0) {
                        keypaduser.importerror = true;
                        keypaduser.name_error = gettext('Error: Keypad with this participant already exists.');
                    }
                }

                // check if given seat label already exists
                if (keypaduser.seat_label == '') {
                    keypaduser.seat_id = null;
                } else {
                    angular.forEach(Seat.getAll(), function(seat) {
                        if (seat.number == keypaduser.seat_label) {
                            // check if the seat id already assigned to a keypad
                            angular.forEach(Keypad.getAll(), function(keypad) {
                                if (keypad.seat_id == seat.id) {
                                    keypaduser.importerror = true;
                                    keypaduser.seat_error = gettext('Error: The seat is already assigned to a keypad.');
                                }
                            });
                            keypaduser.seat_id = seat.id;
                        }
                    });
                }

                // check if keypad id already exists
                angular.forEach(Keypad.getAll(), function(keypad) {
                    if (keypad.keypad_id == keypaduser.keypad_id) {
                        keypaduser.importerror = true;
                        keypaduser.keypad_error = gettext('Error: Keypad ID already exists.');
                    }
                });

                // validate keypad id
                var num = parseInt(keypaduser.keypad_id);
                if (isNaN(num) || num <= 0) {
                    keypaduser.importerror = true;
                    keypaduser.keypad_error = gettext('Error: Keypad ID must be a positive integer value.')
                }
                else {
                    keypaduser.keypad_id = num;
                    if (Keypad.filter({ 'keypad_id': keypaduser.keypad_id }).length > 0) {
                        keypaduser.importerror = true;
                        keypaduser.keypad_error = gettext('Error: Keypad ID already exists.');
                    }
                }

                $scope.keypads.push(keypaduser);
            });
            $scope.calcStats();
        };

        // Stats
        $scope.calcStats = function() {
            // not imported: if importerror
            $scope.keypadsWillNotBeImported = 0;
            // imported: all others
            $scope.keypadsWillBeImported = 0;

            $scope.keypads.forEach(function(keypad) {
                if (!keypad.selected || keypad.importerror) {
                    $scope.keypadsWillNotBeImported++;
                } else {
                    $scope.keypadsWillBeImported++;
                }
            });
        };

        // import from csv file
        $scope.import = function () {
            $scope.csvImporting = true;
            _.forEach($scope.keypads, function (keypad) {
                if (keypad.selected && !keypad.importerror) {
                    var keypadobject = {
                        'keypad_id': keypad.keypad_id,
                        'user_id': keypad.user_id,
                        'seat_id': keypad.seat_id
                    }
                    Keypad.create(keypadobject).then(
                        function(success) {
                            keypad.imported = true;
                        }
                    );
                }
            });
            $scope.csvimported = true;
        };

        // clear csv import preview
        $scope.clear = function () {
            $scope.keypads = null;
        };

        // download CSV example file
        $scope.downloadCSVExample = function () {
            var element = document.getElementById('downloadLink');

            var makeHeaderline = function () {
                var headerline = ['Title', 'Given name', 'Surname', 'Structure level', 'Participant number', 'Groups',
                    'Comment', 'Is active', 'Is present', 'Is a committee', 'Initial password',
                    'Keypad ID', 'Seat'];
                return _.map(headerline, function (entry) {
                    return gettextCatalog.getString(entry);
                });
            };
            var csvRows = [makeHeaderline(),
                // example entries
                ['Dr.', 'Max', 'Mustermann', 'Berlin','1234567890', '', 'xyz', '1', '1', '', '', '1', '1'],
                ['', 'John', 'Doe', 'Washington','75/99/8-2', '', 'abc', '1', '1', '', '', '2', '2'],
                ['', 'Fred', 'Bloggs', 'London', '', '', '', '', '', '', '', '3', '3'],
                ['', '', 'Executive Board', '', '', '', '', '', '', '1', '', '4', '4'],

            ];
            CsvDownload(csvRows, 'keypads-example.csv');
        }


    }
])

// Button at template hook motionPollSmallButtons
.run([
    'templateHooks',
    function (templateHooks) {
        templateHooks.registerHook({
            Id: 'motionPollSmallButtons',
            template: '<div class="spacer" ng-if="poll.has_votes">' +
                      '<a ui-sref="openslides_votecollector.motionpoll.detail({id: poll.id})">' +
                      '<button class="btn btn-xs btn-default">' +
                      '<i class="fa fa-table" aria-hidden="true"></i> ' +
                      '{{ \'Single votes\' | translate }}' +
                      '</button></a></div>'
        })
    }
])

.controller('MotionPollVoteDetailCtrl', [
    '$scope',
    '$stateParams',
    '$http',
    'Keypad',
    'Projector',
    'User',
    'MotionPoll',
    'MotionPollFinder',
    'MotionPollKeypadConnection',
    'Motion',
    function ($scope, $stateParams, $http, Keypad, Projector, User, MotionPoll, MotionPollFinder, MotionPollKeypadConnection, Motion) {
        // Find motion and poll from URL parameter (via $stateparams).
        _.assign($scope, MotionPollFinder.find(Motion.getAll(), $stateParams.id));
        // Bind poll to scope for autoupdate of total vote result
        MotionPoll.bindOne($scope.poll.id, $scope, 'poll');

        $scope.$watch(
            function () {
                return MotionPollKeypadConnection.lastModified();
            },
            function () {
                // Create table for single votes
                $scope.votesList = [];
                angular.forEach(MotionPollKeypadConnection.getAll(), function(mpkc) {
                    if (mpkc.poll_id == $scope.poll.id) {
                        var keypad = null;
                        if (mpkc.keypad_id) {
                            keypad = Keypad.get(mpkc.keypad_id);
                            var user = null;
                            if (keypad.user_id) {
                                user = User.get(keypad.user_id);
                            }
                        }
                        $scope.votesList.push({
                            user: user,
                            keypad: keypad,
                            serial_number: mpkc.serial_number,
                            value: mpkc.value
                        });
                    }
                });
            }
        );

        $scope.isProjected = function (poll_id) {
            // Returns true if there is a projector element with the same
            // name and the same id of poll.
            var projector = Projector.get(1);
            var isProjected;
            if (typeof projector !== 'undefined') {
                var self = this;
                var predicate = function (element) {
                    return element.name == "votecollector/motionpoll" &&
                        typeof element.id !== 'undefined' &&
                        element.id == poll_id;
                };
                isProjected = typeof _.findKey(projector.elements, predicate) === 'string';
            } else {
                isProjected = false;
            }
            return isProjected;
        };

        $scope.projectSlide = function () {
            return $http.post(
                '/rest/core/projector/1/prune_elements/',
                [{name: 'votecollector/motionpoll', id: $scope.poll.id}]
            );
        };

        $scope.anonymizeVotes = function () {
            return $http.post(
                '/rest/openslides_votecollector/motion-poll-keypad-connection/anonymize_votes/',
                {poll_id: $scope.poll.id}
            ).then(function (success) {}, function (error) {});
        };
    }
])

// Button at template hook assignmentPollSmallButtons
.run([
    'templateHooks',
    function (templateHooks) {
        templateHooks.registerHook({
            Id: 'assignmentPollSmallButtons',
            template: '<div class="spacer" ng-if="poll.has_votes">' +
                      '<a ui-sref="openslides_votecollector.assignmentpoll.detail({id: poll.id})">' +
                      '<button class="btn btn-sm btn-default">' +
                      '<i class="fa fa-table" aria-hidden="true"></i> ' +
                      '{{ \'Single votes\' | translate }}' +
                      '</button></a></div>'
        })
    }
])

.controller('AssignmentPollVoteDetailCtrl', [
    '$scope',
    '$http',
    '$stateParams',
    'Keypad',
    'Projector',
    'User',
    'AssignmentPoll',
    'AssignmentPollFinder',
    'AssignmentPollKeypadConnection',
    'Assignment',
    function ($scope, $http, $stateParams, Keypad, Projector, User, AssignmentPoll, AssignmentPollFinder, AssignmentPollKeypadConnection, Assignment) {
        // Find assignment and poll from URL parameter (via $stateparams).
        _.assign($scope, AssignmentPollFinder.find(Assignment.getAll(), $stateParams.id));
        // Bind poll to scope for autoupdate of total vote result
        AssignmentPoll.bindOne($scope.poll.id, $scope, 'poll');

        $scope.$watch(
            function () {
                return AssignmentPollKeypadConnection.lastModified();
            },
            function () {
                // Create table for single votes
                $scope.votesList = [];
                angular.forEach(AssignmentPollKeypadConnection.getAll(), function (apkc) {
                    if (apkc.poll_id == $scope.poll.id) {
                        var keypad = null;
                        if (apkc.keypad_id) {
                            keypad = Keypad.get(apkc.keypad_id);
                            var user = null;
                            if (keypad.user_id) {
                                user = User.get(keypad.user_id);
                            }
                        }
                        var candidate = null;
                        if (apkc.candidate_id) {
                            candidate = User.get(apkc.candidate_id);
                        }
                        $scope.votesList.push({
                            user: user,
                            keypad: keypad,
                            serial_number: apkc.serial_number,
                            value: apkc.value,
                            candidate: candidate
                        });
                    }
                });
            }
        );

        $scope.isProjected = function (poll_id) {
            // Returns true if there is a projector element with the same
            // name and the same id of poll.
            var projector = Projector.get(1);
            var isProjected;
            if (typeof projector !== 'undefined') {
                var self = this;
                var predicate = function (element) {
                    return element.name == "votecollector/assignmentpoll" &&
                        typeof element.id !== 'undefined' &&
                        element.id == poll_id;
                };
                isProjected = typeof _.findKey(projector.elements, predicate) === 'string';
            } else {
                isProjected = false;
            }
            return isProjected;
        };

        $scope.projectSlide = function () {
            return $http.post(
                '/rest/core/projector/1/prune_elements/',
                [{name: 'votecollector/assignmentpoll', id: $scope.poll.id}]
            );
        };


        $scope.anonymizeVotes = function () {
            return $http.post(
                '/rest/openslides_votecollector/assignment-poll-keypad-connection/anonymize_votes/',
                {poll_id: $scope.poll.id}
            ).then(function (success) {}, function (error) {});
        };
    }
])

.controller('VotingCtrl', [
    '$scope',
    '$http',
    'gettextCatalog',
    'MotionPollKeypadConnection',
    'Projector',
    'VoteCollector',
    function ($scope, $http,  gettextCatalog, MotionPollKeypadConnection, Projector, VoteCollector) {
        VoteCollector.find(1);
        VoteCollector.bindOne(1, $scope, 'vc');

        var clearForm = function () {
            $scope.poll.yes = null;
            $scope.poll.no = null;
            $scope.poll.abstain = null;
            $scope.poll.votesvalid = null;
            $scope.poll.votesinvalid = null;
            $scope.poll.votescast = null;
        };

        $scope.canStartVoting = function () {
            return $scope.vc !== undefined && $scope.poll.votescast === null &&
                (!$scope.vc.is_voting || $scope.vc.voting_mode == 'Item' || $scope.vc.voting_mode == 'Test');
        };

        $scope.canStopVoting = function () {
            return $scope.vc !== undefined && $scope.vc.is_voting && $scope.vc.voting_mode == 'MotionPoll' &&
                $scope.vc.voting_target == $scope.poll.id;
        };

        $scope.canClearVotes = function () {
            return $scope.vc !== undefined && $scope.poll.votescast !== null;
        };

        $scope.startVoting = function () {
            $scope.$parent.$parent.$parent.alert = {};

            // Start votecollector.
            $http.get('/votecollector/start_voting/' + $scope.poll.id + '/').then(
                function (success) {
                    if (success.data.error) {
                        $scope.$parent.$parent.$parent.alert = { type: 'danger', msg: success.data.error, show: true };
                    }
                },
                function (failure) {
                    $scope.$parent.$parent.$parent.alert = {
                        type: 'danger',
                        msg: $scope.vc.getErrorMessage(failure.status, failure.statusText),
                        show: true };
                }
            );
        };

        $scope.stopVoting = function () {
            // TODO: Clear seating plan (MotionPollKeypadConnections) if results are not saved after stop voting.
            $scope.$parent.$parent.$parent.alert = {};

            // Stop votecollector.
            $http.get('/votecollector/stop/').then(
                function (success) {
                    if (success.data.error) {
                        $scope.$parent.$parent.$parent.alert = { type: 'danger',
                            msg: success.data.error, show: true };
                    }
                    else {
                        $http.get('/votecollector/result_voting/' + $scope.poll.id + '/').then(
                            function (success) {
                                if (success.data.error) {
                                    $scope.$parent.$parent.$parent.alert = { type: 'danger',
                                        msg: success.data.error, show: true };
                                }
                                else {
                                    // Store result in DS model; updates form inputs.
                                    $scope.poll.yes = success.data.votes[0];
                                    $scope.poll.no = success.data.votes[1];
                                    $scope.poll.abstain = success.data.votes[2];
                                    $scope.poll.votesvalid = $scope.poll.yes + $scope.poll.no + $scope.poll.abstain;
                                    $scope.poll.votesinvalid = 0;
                                    $scope.poll.votescast = $scope.poll.votesvalid;

                                    // Prompt user to save result.
                                    $scope.$parent.$parent.$parent.alert = {
                                        type: 'info',
                                        msg: gettextCatalog.getString('Motion voting has finished.') + ' ' +
                                             gettextCatalog.getString('Received votes:') + ' ' +
                                             $scope.poll.votescast + ' / ' + $scope.vc.voters_count + '. ' +
                                             gettextCatalog.getString('Save this result now!'),
                                        show: true
                                    };
                                }
                            }
                        );
                    }
                },
                function (failure) {
                    $scope.$parent.$parent.$parent.alert = {
                        type: 'danger',
                        msg: $scope.vc.getErrorMessage(failure.status, failure.statusText),
                        show: true };
                }
            );
        };

        $scope.clearVotes = function () {
            $scope.$parent.$parent.$parent.alert = {};
            $http.get('/votecollector/clear_voting/' + $scope.poll.id + '/').then(
                function (success) {
                    clearForm();
                }
            );
        };

        $scope.getVotingStatus = function () {
            if ($scope.vc !== undefined) {
                if ($scope.vc.is_voting && $scope.vc.voting_mode == 'Test') {
                    return gettextCatalog.getString('System test is running.');
                }
                if ($scope.vc.is_voting && $scope.vc.voting_mode == 'Item') {
                    return gettextCatalog.getString('Speakers voting is running for agenda item') + ' ' +
                        $scope.vc.voting_target + '.';
                }
                if ($scope.vc.is_voting && $scope.vc.voting_mode == 'AssignmentPoll') {
                    return gettextCatalog.getString('An election is running.');
                }
                if ($scope.vc.is_voting && $scope.vc.voting_mode == 'MotionPoll') {
                    if ($scope.vc.voting_target != $scope.poll.id) {
                        return gettextCatalog.getString('Another motion voting is running.');
                    }
                    var allMPKCs = MotionPollKeypadConnection.filter({poll_id: $scope.poll.id});
                    $scope.votes_received = allMPKCs.length;
                    return gettextCatalog.getString('Votes received:') + ' ' +
                        // TODO: Add voting duration.
                        $scope.votes_received + ' / ' + $scope.vc.voters_count;
                }
            }
            return '';
        };

        $scope.projectSlide = function () {
            return $http.post(
                '/rest/core/projector/1/prune_elements/',
                [{name: 'votecollector/motionpoll', id: $scope.poll.id}]
            );
        };

        $scope.isProjected = function () {
            // Returns true if there is a projector element with the same
            // name and the same id of $scope.poll.
            var projector = Projector.get(1);
            var isProjected;
            if (typeof projector !== 'undefined') {
                var self = this;
                var predicate = function (element) {
                    return element.name == "votecollector/motionpoll" &&
                        typeof element.id !== 'undefined' &&
                        element.id == $scope.poll.id;
                };
                isProjected = typeof _.findKey(projector.elements, predicate) === 'string';
            } else {
                isProjected = false;
            }
            return isProjected;
        }
    }
])

.controller('ElectionCtrl', [
    '$scope',
    '$http',
    'gettextCatalog',
    'AssignmentPollKeypadConnection',
    'Config',
    'Projector',
    'VoteCollector',
    function ($scope, $http, gettextCatalog, AssignmentPollKeypadConnection, Config, Projector, VoteCollector) {
        VoteCollector.find(1);
        VoteCollector.bindOne(1, $scope, 'vc');

        var clearForm = function () {
            if ($scope.poll.pollmethod == 'yna') {
                var id = $scope.poll.options[0].candidate_id;
                $scope.poll['yes_' + id] = null;
                $scope.poll['no_' + id] = null;
                $scope.poll['abstain_' + id] = null;
            }
            else {
                for (var i = 0; i < $scope.poll.options.length; i++) {
                    $scope.poll['vote_' + $scope.poll.options[i].candidate_id] = null;
                }
            }
            $scope.poll.votesvalid = null;
            $scope.poll.votesinvalid = null;
            $scope.poll.votescast = null;
        };

        $scope.canStartVoting = function () {
            var enabled = $scope.poll.assignment.open_posts == 1 &&
                ($scope.poll.pollmethod == 'votes' || $scope.poll.pollmethod == 'yna');
            return enabled && $scope.vc !== undefined  && $scope.poll.votescast === null &&
                    (!$scope.vc.is_voting || $scope.vc.voting_mode == 'Item' || $scope.vc.voting_mode == 'Test');
        };

        $scope.canStopVoting = function () {
            return $scope.vc !== undefined && $scope.vc.is_voting && $scope.vc.voting_mode == 'AssignmentPoll' &&
                $scope.vc.voting_target == $scope.poll.id;
        };

        $scope.canClearVotes = function () {
            return $scope.vc !== undefined && $scope.poll.votescast !== null;
        };

        $scope.startVoting = function () {
            $scope.$parent.$parent.$parent.alert = {};

            // Start votecollector.
            var url;
            if ($scope.poll.pollmethod == 'votes') {
                // Unlock all keys including 0/10 (allow invalid keys).
                url = '/votecollector/start_election/' + $scope.poll.id + '/10/';
            } else {
                url = '/votecollector/start_election_one/' + $scope.poll.id + '/';
            }

            $http.get(url).then(
                function (success) {
                    if (success.data.error) {
                        $scope.$parent.$parent.$parent.alert = { type: 'danger', msg: success.data.error, show: true };
                    }
                },
                function (failure) {
                    $scope.$parent.$parent.$parent.alert = {
                        type: 'danger',
                        msg: $scope.vc.getErrorMessage(failure.status, failure.statusText),
                        show: true };
                }
            );
        };

        $scope.stopVoting = function () {
            $scope.$parent.$parent.$parent.alert = {};

            // Stop votecollector.
            $http.get('/votecollector/stop/').then(
                function (success) {
                    if (success.data.error) {
                        $scope.$parent.$parent.$parent.alert = { type: 'danger',
                            msg: success.data.error, show: true };
                    }
                    else {
                        // Get votecollector result.
                        $http.get('/votecollector/result_election/' + $scope.poll.id + '/').then(
                            function (success) {
                                if (success.data.error) {
                                    $scope.$parent.$parent.$parent.alert = { type: 'danger',
                                        msg: success.data.error, show: true };
                                }
                                else {
                                    // Store result in DS model, updates form inputs.
                                    if ($scope.poll.pollmethod == 'yna') {
                                        var id = $scope.poll.options[0].candidate_id;
                                        $scope.poll['yes_' + id] = success.data.votes[0];
                                        $scope.poll['no_' + id] = success.data.votes[1];
                                        $scope.poll['abstain_' + id] = success.data.votes[2];
                                        $scope.poll.votesvalid =
                                            success.data.votes[0] + success.data.votes[1] + success.data.votes[2];
                                        $scope.poll.votesinvalid = 0;
                                    }
                                    else {
                                        var key;
                                        for (var i = 0; i < $scope.poll.options.length; i++) {
                                            key = 'vote_' + $scope.poll.options[i].candidate_id;
                                            $scope.poll[key] = success.data.votes[key];
                                        }
                                        $scope.poll.votesvalid = success.data.votes['valid'];
                                        $scope.poll.votesinvalid = success.data.votes['invalid'];
                                    }
                                   $scope.poll.votescast = $scope.poll.votesvalid + $scope.poll.votesinvalid;

                                    // Prompt user to save result.
                                    $scope.$parent.$parent.$parent.alert = {
                                        type: 'info',
                                        msg: gettextCatalog.getString('Election voting has finished.') + ' ' +
                                             gettextCatalog.getString('Received votes:') + ' ' +
                                             $scope.poll.votescast + ' / ' + $scope.vc.voters_count + '. ' +
                                             gettextCatalog.getString('Save this result now!'),
                                        show: true
                                    };
                                }
                            }
                        );
                    }
                },
                function (failure) {
                    $scope.$parent.$parent.$parent.alert = {
                        type: 'danger',
                        msg: $scope.vc.getErrorMessage(failure.status, failure.statusText),
                        show: true };
                }
            );
        };

        $scope.clearVotes = function () {
            $scope.$parent.$parent.$parent.alert = {};
            $http.get('/votecollector/clear_election/' + $scope.poll.id + '/').then(
                function (success) {
                    clearForm();
                }
            );
        };

        $scope.getVotingStatus = function () {
            if ($scope.vc !== undefined) {
                if ($scope.vc.is_voting && $scope.vc.voting_mode == 'Test') {
                    return gettextCatalog.getString('System test is running.');
                }
                if ($scope.vc.is_voting && $scope.vc.voting_mode == 'Item') {
                    return gettextCatalog.getString('Speakers voting is running for agenda item') + ' ' +
                        $scope.vc.voting_target + '.';
                }
                if ($scope.vc.is_voting && $scope.vc.voting_mode == 'MotionPoll') {
                    return gettextCatalog.getString('A motion voting is running.');
                }
                if ($scope.vc.is_voting && $scope.vc.voting_mode == 'AssignmentPoll') {
                    if ($scope.vc.voting_target != $scope.poll.id) {
                        return gettextCatalog.getString('Another election is running.');
                    }
                    var allAPKCs = AssignmentPollKeypadConnection.filter({poll_id: $scope.poll.id});
                    $scope.votes_received = allAPKCs.length;
                    return gettextCatalog.getString('Votes received:') + ' ' +
                        // TODO: Add voting duration.
                        $scope.votes_received + ' / ' + $scope.vc.voters_count;
                }
            }
            return '';
        };

        $scope.projectSlide = function () {
            return $http.post(
                '/rest/core/projector/1/prune_elements/',
                [{name: 'votecollector/assignmentpoll', id: $scope.poll.id}]
            );
        };

        $scope.isProjected = function (poll_id) {
            // Returns true if there is a projector element with the same
            // name and the same id of $scope.poll.
            var projector = Projector.get(1);
            var isProjected;
            if (typeof projector !== 'undefined') {
                var self = this;
                var predicate = function (element) {
                    return element.name == "votecollector/assignmentpoll" &&
                        typeof element.id !== 'undefined' &&
                        element.id == poll_id;
                };
                isProjected = typeof _.findKey(projector.elements, predicate) === 'string';
            } else {
                isProjected = false;
            }
            return isProjected;
        }
    }
])

.controller('SpeakerListCtrl', [
    '$scope',
    '$http',
    'VoteCollector',
    function ($scope, $http, VoteCollector) {
        VoteCollector.find(1);
        VoteCollector.bindOne(1, $scope, 'vc');

        $scope.canStartVoting = function () {
            return $scope.vc !== undefined && (!$scope.vc.is_voting ||
                    ($scope.vc.voting_mode == 'Item' && $scope.vc.voting_target != $scope.item.id) ||
                    $scope.vc.voting_mode == 'Test');
        };

        $scope.canStopVoting = function () {
            return $scope.vc !== undefined && $scope.vc.is_voting && $scope.vc.voting_mode == 'Item' &&
                $scope.vc.voting_target == $scope.item.id;
        };

        $scope.startVoting = function () {
            $scope.vcAlert = {};
            $http.get('/votecollector/start_speaker_list/' + $scope.item.id + '/').then(
                function (success) {
                    if (success.data.error) {
                        $scope.vcAlert = { type: 'danger', msg: success.data.error, show: true };
                    }
                },
                function (failure) {
                    $scope.vcAlert = {
                        type: 'danger',
                        msg: $scope.vc.getErrorMessage(failure.status, failure.statusText),
                        show: true };
                }
            );
        };

        $scope.stopVoting = function () {
            $scope.vcAlert = {};
            $http.get('/votecollector/stop/').then(
                function (success) {
                    if (success.data.error) {
                        $scope.vcAlert = { type: 'danger', msg: success.data.error, show: true };
                    }
                },
                function (failure) {
                    $scope.vcAlert = {
                        type: 'danger',
                        msg: $scope.vc.getErrorMessage(failure.status, failure.statusText),
                        show: true };
                }
            );
        };
    }
])

// VotingCtrl at template hook motionPollFormButtons
.run([
    'templateHooks',
    function (templateHooks) {
        templateHooks.registerHook({
            Id: 'motionPollFormButtons',
            template:
                '<div ng-controller="VotingCtrl" ng-init="poll=$parent.$parent.model" class="spacer">' +
                    '<button type="button" ng-if="canStartVoting()" ' +
                        'ng-click="startVoting()"' +
                        'class="btn btn-default">' +
                        '<i class="fa fa-wifi" aria-hidden="true"></i> ' +
                        '{{ \'Start voting\' | translate }}</button> ' +
                    '<button type="button" ng-if="canStopVoting()" ' +
                        'ng-click="stopVoting()"' +
                        'class="btn btn-primary">' +
                        '<i class="fa fa-wifi" aria-hidden="true"></i> '+
                        '{{ \'Stop voting\' | translate }}</button> ' +
                    '<button type="button" ng-if="canClearVotes()" ' +
                        'ng-click="clearVotes()"' +
                        'class="btn btn-default">' +
                        '<i class="fa fa-trash" aria-hidden="true"></i> '+
                        '{{ \'Clear votes\' | translate }}</button> ' +
                    '<button type="button" os-perms="core.can_manage_projector" class="btn btn-default"' +
                      ' ng-class="{ \'btn-primary\': isProjected() }"' +
                      ' ng-click="projectSlide()"' +
                      ' title="{{ \'Project vote result\' | translate }}">' +
                      '<i class="fa fa-video-camera"></i> ' +
                      '{{ \'Voting result\' | translate }}</button>' +
                    '<p>{{ getVotingStatus() }}</p>' +
                '</div>'
        })
    }
])

// ElectionCtrl at template hook assignmentPollFormButtons
.run([
    'templateHooks',
    function (templateHooks) {
        templateHooks.registerHook({
            Id: 'assignmentPollFormButtons',
            template:
                '<div ng-controller="ElectionCtrl" ng-init="poll=$parent.$parent.model" class="spacer">' +
                    '<button type="button" ng-if="canStartVoting()" ' +
                        'ng-click="startVoting()"' +
                        'class="btn btn-default">' +
                        '<i class="fa fa-wifi" aria-hidden="true"></i> '+
                        '{{ \'Start election\' | translate }}</button> ' +
                    '<button type="button" ng-if="canStopVoting()" ' +
                        'ng-click="stopVoting()"' +
                        'class="btn btn-primary">' +
                        '<i class="fa fa-wifi" aria-hidden="true"></i> '+
                        '{{ \'Stop election\' | translate }}</button> ' +
                    '<button type="button" ng-if="canClearVotes()" ' +
                        'ng-click="clearVotes()"' +
                        'class="btn btn-default">' +
                        '<i class="fa fa-wifi" aria-hidden="true"></i> '+
                        '{{ \'Clear votes\' | translate }}</button> ' +
                    '<button type="button" os-perms="core.can_manage_projector" class="btn btn-default"' +
                      ' ng-class="{ \'btn-primary\': isProjected(poll.id) }"' +
                      ' ng-click="projectSlide()"' +
                      ' title="{{ \'Project election result\' | translate }}">' +
                      '<i class="fa fa-video-camera"></i> ' +
                      '{{ \'Election result\' | translate }}</button>' +
                    '<p>{{ getVotingStatus() }}</p>' +
                '</div>'
        })
    }
])

// SpeakerListCtrl at template hook itemDetailListOfSpeakersButtons
.run([
    'gettextCatalog',
    'templateHooks',
    function (gettextCatalog, templateHooks) {
        templateHooks.registerHook({
            Id: 'itemDetailListOfSpeakersButtons',
            template:
                '<div ng-controller="SpeakerListCtrl" ng-init="item=$parent.$parent.item" class="spacer">' +
                    '<button ng-if="canStartVoting()" ' +
                        'ng-click="startVoting()"' +
                        'class="btn btn-sm btn-default">' +
                        '<i class="fa fa-wifi" aria-hidden="true"></i> '+
                        '{{ \'Start speakers voting\' | translate }}</button> ' +
                    '<button ng-if="canStopVoting()" ' +
                        'ng-click="stopVoting()"' +
                        'class="btn btn-sm btn-primary">' +
                        '<i class="fa fa-wifi" aria-hidden="true"></i> '+
                        '{{ \'Stop speakers voting\' | translate }}</button> ' +
                    '<uib-alert ng-show="vcAlert.show" type="{{ vcAlert.type }}" ng-click="vcAlert={}" close="vcAlert={}">' +
                        '{{ vcAlert.msg }}</uib-alert>' +
                '</div>'
        })
    }
])

// Mark config strings for translation in javascript
.config([
    'gettext',
    function (gettext) {
        // config stings
        gettext('Distribution method for keypads');
        gettext('Use anonymous keypads only');
        gettext('Use personalized keypads only');
        gettext('Use anonymous and personalized keypads');
        gettext('URL of VoteCollector');
        gettext('Example: http://localhost:8030');
        gettext("Overlay message 'Vote started'");
        gettext('Please vote now!');
        gettext('Use live voting for motions');
        gettext('Incoming votes will be shown on projector while voting is active.');
        gettext('Show seating plan');
        gettext('Incoming votes will be shown in seating plan on projector for keypads with assigned seats.');
        gettext('Show grey seats on seating plan');
        gettext('Incoming votes will be shown in grey on seating plan. You can see only WHICH seat has voted but not HOW.');

        // template hook strings
        gettext('Start voting');
        gettext('Stop voting');
        gettext('Start election');
        gettext('Stop election');
        gettext('Start speakers voting');
        gettext('Stop speakers voting');
        gettext('Single votes');
        gettext('Voting result');
        gettext('Project vote result');
        gettext('Election result');
        gettext('Project election result');
        gettext('Clear votes');

        // permission strings
        gettext('Can manage VoteCollector');
    }
])

}());
