import pathlib

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.pre_or_post_sds_value import PreOrPostSdsValue


class StringValue(PreOrPostSdsValue):
    def value_pre_sds(self, home_dir_path: pathlib.Path) -> str:
        """
        :raises ValueError: This value exists only post-SDS.
        """
        raise ValueError(str(self) + ': This value exists post SDS')

    def value_post_sds(self, home_and_sds: HomeAndSds) -> str:
        """
        :raises ValueError: This value exists pre-SDS.
        """
        raise ValueError(str(self) + ': This value exists pre SDS')

    def value_pre_or_post_sds(self, home_and_sds: HomeAndSds) -> str:
        raise NotImplementedError()


class ConstantStringValue(StringValue):
    def __init__(self, string_constant: str):
        self.string_constant = string_constant

    def exists_pre_sds(self) -> bool:
        return True

    def value_pre_sds(self, home_dir_path: pathlib.Path) -> str:
        return self.string_constant

    def value_pre_or_post_sds(self, home_and_sds: HomeAndSds) -> str:
        return self.string_constant
