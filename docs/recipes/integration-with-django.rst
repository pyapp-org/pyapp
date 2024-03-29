Integration with Django
=======================

PyApp factories and injection can be used in Django projects by initialising the
pyApp settings object. As this system is largely inspired by the Django config
integration is fairly straight forward.

The safest time to mirror the configuration is after the ready event is raised by
Django. There are two options here:

1. Create a new Django App
2. Use an appropriate existing app.

Add to the ``ready`` method of your *App* class:

.. code-block:: python

    class MyApp:
        def ready(self):
            # Merge Django config into pyApp config.
            from django.conf import settings as django_settings
            from pyapp.conf import settings as pyapp_settings
            from pyapp.conf.loaders import ObjectLoader
            pyapp_settings.load(ObjectLoader(django_settings))

``ObjectLoader`` is a special loader that reads configuration variable from an
existing object; in this case the Django settings object.
