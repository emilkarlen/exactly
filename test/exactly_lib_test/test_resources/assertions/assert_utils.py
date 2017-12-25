"""
This module should probably be replaced by functionality in ValueAssertion
"""


def assertion_message(message: str,
                      header: str = None):
    return message if not header else header + ': ' + message
