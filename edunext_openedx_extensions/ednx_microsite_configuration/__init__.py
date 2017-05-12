"""
Edunext microsites app
"""
try:
    from microsite_configuration import microsite  # pylint: disable=unused-import
except ImportError:
    raise ImportError("Edunext microsites app was unable to load microsite functions")
