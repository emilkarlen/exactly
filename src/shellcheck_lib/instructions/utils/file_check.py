from shellcheck_lib.instructions.utils.file_properties import FilePropertiesCheck
from shellcheck_lib.instructions.utils.file_ref import FileRef
from shellcheck_lib.test_case.sections.common import HomeAndEds


class FileRefCheck:
    def __init__(self,
                 file_reference: FileRef,
                 file_properties: FilePropertiesCheck):
        self.__file_reference = file_reference
        self.__file_properties = file_properties

    def apply(self, home_and_eds: HomeAndEds):
        raise NotImplementedError()
