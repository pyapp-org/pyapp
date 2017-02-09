__name__ = 'Sample Extension'
__version__ = '3.2.1'

# Default settings file to use
__default_settings__ = '.default_settings'

# Checks module
__checks__ = 'tests.sample_ext.checks'


set_ready = False


def ready(**_):
    global set_ready
    set_ready = True
