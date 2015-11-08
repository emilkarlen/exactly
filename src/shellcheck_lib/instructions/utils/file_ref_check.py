import pathlib

from shellcheck_lib.instructions.utils.file_properties import FilePropertiesCheck
from shellcheck_lib.instructions.utils.file_ref import FileRef
from shellcheck_lib.test_case.sections.common import HomeAndEds


class FileRefCheck:
    def __init__(self,
                 file_reference: FileRef,
                 file_properties: FilePropertiesCheck):
        self.file_reference = file_reference
        self.file_properties = file_properties

    def satisfies_pre_eds_condition(self, home_dir_path: pathlib.Path) -> bool:
        if self.file_reference.exists_pre_eds:
            return self.file_properties.apply(self.file_reference.file_path_pre_eds(home_dir_path))
        return True

    def satisfies_post_eds_condition(self, home_and_eds: HomeAndEds):
        if not self.file_reference.exists_pre_eds:
            return self.file_properties.apply(self.file_reference.file_path_post_eds(home_and_eds))
        return True
