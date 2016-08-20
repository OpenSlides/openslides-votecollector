from django.apps import AppConfig

from . import __description__, __verbose_name__, __version__


class VoteCollectorAppConfig(AppConfig):
    name = 'openslides_votecollector'
    verbose_name = __verbose_name__
    description = __description__
    version = __version__
    angular_site_module = True
    angular_projector_module = False
    js_files = [
        'js/openslides_votecollector/base.js',
        'js/openslides_votecollector/site.js'
    ]

    def ready(self):
        # Load projector elements.
        # Do this by just importing all from these files.
        # from . import projector  # noqa

        # Import all required stuff.
        from openslides.core.config import config
        from openslides.core.signals import post_permission_creation
        from openslides.utils.rest_api import router
        from .config_variables import get_config_variables
        from .signals import (
            add_default_seating_plan,
            add_permissions_to_builtin_groups
        )
        from .urls import urlpatterns
        from .views import KeypadViewSet, MotionPollKeypadConnectionViewSet, SeatViewSet

        # Define config variables
        config.update_config_variables(get_config_variables())

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
        router.register(self.get_model('Seat').get_collection_string(), SeatViewSet)
        router.register(self.get_model('Keypad').get_collection_string(), KeypadViewSet)
        router.register(self.get_model('MotionPollKeypadConnection').get_collection_string(), MotionPollKeypadConnectionViewSet)

        # Provide plugin urlpatterns to application configuration
        self.urlpatterns = urlpatterns
