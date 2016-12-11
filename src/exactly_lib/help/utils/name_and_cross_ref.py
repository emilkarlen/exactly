from exactly_lib.help.cross_reference_id import CrossReferenceId


class SingularNameAndCrossReferenceId(tuple):
    def __new__(cls,
                singular_name: str,
                single_line_description_str: str,
                cross_reference_target: CrossReferenceId):
        return tuple.__new__(cls, (singular_name,
                                   single_line_description_str,
                                   cross_reference_target))

    @property
    def singular_name(self) -> str:
        return self[0]

    @property
    def single_line_description_str(self) -> str:
        return self[1]

    @property
    def cross_reference_target(self) -> CrossReferenceId:
        return self[2]
