from django.apps import AppConfig

from openslides.utils.projector import register_projector_elements

from . import (
    __description__,
    __license__,
    __url__,
    __verbose_name__,
    __version__
)


class VoteCollectorAppConfig(AppConfig):
    name = 'openslides_votecollector'
    verbose_name = __verbose_name__
    description = __description__
    version = __version__
    license = __license__
    url = __url__
    angular_site_module = True
    angular_projector_module = True
    js_files = [
        'static/js/openslides_votecollector/base.js',
        'static/js/openslides_votecollector/site.js',
        'static/js/openslides_votecollector/projector.js'
    ]

    def ready(self):
        # Import all required stuff.
        from openslides.core.config import config
        from openslides.core.signals import post_permission_creation
        from openslides.utils.rest_api import router
        from .config_variables import get_config_variables
        from .projector import get_projector_elements
        from .signals import (
            add_default_seating_plan,
            add_permissions_to_builtin_groups
        )
        from .urls import urlpatterns
        from .views import (
            AssignmentPollKeypadConnectionViewSet,
            KeypadViewSet,
            MotionPollKeypadConnectionViewSet,
            SeatViewSet,
            VotecollectorViewSet
        )

        # Define projector elements and projector elements.
        config.update_config_variables(get_config_variables())
        register_projector_elements(get_projector_elements())

        # Connect signals.
        post_permission_creation.connect(
            add_permissions_to_builtin_groups,
            dispatch_uid='votecollector_add_permissions_to_builtin_groups'
        )
        post_permission_creation.connect(
            add_default_seating_plan,
            dispatch_uid='votecollector_add_default_seating_plan'
        )

        # Register viewsets.
        router.register(self.get_model('VoteCollector').get_collection_string(), VotecollectorViewSet)
        router.register(self.get_model('Seat').get_collection_string(), SeatViewSet)
        router.register(self.get_model('Keypad').get_collection_string(), KeypadViewSet)
        router.register(self.get_model('MotionPollKeypadConnection').get_collection_string(),
                        MotionPollKeypadConnectionViewSet)
        router.register(self.get_model('AssignmentPollKeypadConnection').get_collection_string(),
                        AssignmentPollKeypadConnectionViewSet)

        # Provide plugin urlpatterns to application configuration
        self.urlpatterns = urlpatterns
