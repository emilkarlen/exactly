from exactly_lib.impls.instructions.assert_.utils.assertion_part import IdentityAssertionPart
from exactly_lib.type_val_prims.string_source.string_source import StringSource


class FileContentsAssertionPart(IdentityAssertionPart[StringSource]):
    """
    A :class:`AssertionPart` that is given
    the path of a file to operate on.

    This class is just a marker for more informative types.

    Behaviour is identical to :class:`AssertionPart`.
    """
