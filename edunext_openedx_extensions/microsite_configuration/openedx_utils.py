"""
Edunext microsites utils imported for openedx apps
"""
# importing microsite_configuration module from openedx
try:
    import microsite_configuration as openedx_microsites  # pylint: disable=unused-import
except ImportError:
    raise ImportError("Edunext microsites app was unable to load microsite functions")
