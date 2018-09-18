from exactly_lib.definitions.cross_ref.app_cross_ref import CrossReferenceId
from exactly_lib.definitions.formatting import SectionName


class SectionInfo:
    """Information about a section, useful in help texts"""

    def __init__(self,
                 name: SectionName):
        self._section_name = name

    @property
    def name(self) -> SectionName:
        return self._section_name

    @property
    def cross_ref_target(self) -> CrossReferenceId:
        raise NotImplementedError('abstract method')

    def instruction_cross_ref_target(self, instruction_name: str) -> CrossReferenceId:
        raise NotImplementedError('abstract method')
