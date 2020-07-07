from exactly_lib.instructions.assert_.utils.assertion_part import IdentityAssertionPart
from exactly_lib.type_system.logic.string_model import StringModel


class FileContentsAssertionPart(IdentityAssertionPart[StringModel]):
    """
    A :class:`AssertionPart` that is given
    the path of a file to operate on.

    This class is just a marker for more informative types.

    Behaviour is identical to :class:`AssertionPart`.
    """
