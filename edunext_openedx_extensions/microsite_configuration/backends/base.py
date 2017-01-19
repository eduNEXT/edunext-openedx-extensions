"""
Microsite configuration backend module.

Contains the base classes for microsite backends.
"""
try:
    from microsite_configuration.backends.base import (  # pylint: disable=unused-import
        BaseMicrositeBackend,
        BaseMicrositeTemplateBackend,
    )
except ImportError:
    raise ImportError("Edunext microsites app was unable to load base backends")
