from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir_contents


class HomeAndSdsContents(tuple):
    def __new__(cls,
                home_dir_contents: DirContents = empty_dir_contents(),
                sds_contents: sds_populator.SdsPopulator = sds_populator.empty()):
        return tuple.__new__(cls, (home_dir_contents,
                                   sds_contents))

    @property
    def home_dir_contents(self) -> DirContents:
        return self[0]

    @property
    def sds_contents(self) -> sds_populator.SdsPopulator:
        return self[1]
