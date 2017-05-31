import pathlib

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds


class PreOrPostSdsValue:
    """
    A value that may be dependent on the home and/or SDS directories,
    so that it needs access to these to compute it.

    """

    def exists_pre_sds(self) -> bool:
        raise NotImplementedError()

    def value_pre_sds(self, home_dir_path: pathlib.Path):
        """
        :raises ValueError: This value exists only post-SDS.
        """
        raise ValueError(str(self) + ': This value exists post SDS')

    def value_post_sds(self, home_and_sds: HomeAndSds):
        """
        :raises ValueError: This value exists pre-SDS.
        """
        raise ValueError(str(self) + ': This value exists pre SDS')

    def value_pre_or_post_sds(self, home_and_sds: HomeAndSds):
        if self.exists_pre_sds():
            return self.value_pre_sds(home_and_sds.home_dir_path)
        else:
            return self.value_post_sds(home_and_sds)
