from exactly_lib.help.cross_reference_id import CrossReferenceId


class SingularNameAndCrossReference(tuple):
    def __new__(cls,
                singular_name: str,
                cross_reference_target: CrossReferenceId):
        return tuple.__new__(cls, (singular_name, cross_reference_target))

    @property
    def singular_name(self) -> str:
        return self[0]

    @property
    def cross_reference_target(self) -> CrossReferenceId:
        return self[1]
