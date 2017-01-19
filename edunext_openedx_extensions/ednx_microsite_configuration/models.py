"""
Model to store a microsite in the database.

The object is stored as a json representation of the python dict
that would have been used in the settings.

"""
# Note: The Microsite model will be migrated to this file soon from open-edx
# microsite_configuration app
try:
    from microsite_configuration.models import Microsite  # pylint: disable=unused-import
except ImportError:
    raise ImportError("Edunext microsites app was unable to load Microsite model")
