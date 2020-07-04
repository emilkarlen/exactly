from exactly_lib.instructions.assert_.utils.assertion_part import IdentityAssertionPart
from exactly_lib.type_system.logic.string_matcher import StringMatcherModel


class FileContentsAssertionPart(IdentityAssertionPart[StringMatcherModel]):
    """
    A :class:`AssertionPart` that is given
    the path of a file to operate on.

    This class is just a marker for more informative types.

    Behaviour is identical to :class:`AssertionPart`.
    """
