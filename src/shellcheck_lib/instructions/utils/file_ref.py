import pathlib

from shellcheck_lib.test_case.sections.common import HomeAndEds


class FileRef:
    def __init__(self,
                 exists_pre_eds: bool,
                 file_name: str):
        self.__exists_pre_eds = exists_pre_eds
        self._file_name = file_name

    @property
    def file_name(self) -> str:
        return self._file_name

    def file_path_pre_eds(self, home_dir_path: pathlib.Path) -> pathlib.Path:
        """
        Can only be used if the files exists pre-EDS.
        """
        raise NotImplementedError()

    def file_path_post_eds(self, home_and_eds: HomeAndEds) -> pathlib.Path:
        raise NotImplementedError()

    @property
    def exists_pre_eds(self) -> bool:
        return self.__exists_pre_eds


def rel_home(file_name: str) -> FileRef:
    return _FileRefRelHome(file_name)


def rel_cwd(file_name: str) -> FileRef:
    return _FileRefRelCwd(file_name)


def rel_tmp_internal(file_name: str) -> FileRef:
    return _FileRefRelTmpInternal(file_name)


def rel_tmp_user(file_name: str) -> FileRef:
    return _FileRefRelTmpUser(file_name)


class _FileRefRelHome(FileRef):
    def __init__(self, file_name: str):
        super().__init__(True, file_name)

    def file_path_pre_eds(self, home_dir_path: pathlib.Path) -> pathlib.Path:
        """
        Can only be used if the files exists pre-EDS.
        """
        return home_dir_path / self._file_name

    def file_path_post_eds(self, home_and_eds: HomeAndEds) -> pathlib.Path:
        return self.file_path_pre_eds(home_and_eds.home_dir_path)


class _FileRefForFileThatDoesNotExistPreEdsBase(FileRef):
    def __init__(self, file_name: str):
        super().__init__(False, file_name)

    def file_path_post_eds(self, home_and_eds: HomeAndEds) -> pathlib.Path:
        raise NotImplementedError()

    def file_path_pre_eds(self, home_dir_path: pathlib.Path) -> pathlib.Path:
        """
        Can only be used if the files exists pre-EDS.
        """
        raise ValueError('This file does not exist before EDS is constructed')


class _FileRefRelCwd(_FileRefForFileThatDoesNotExistPreEdsBase):
    def __init__(self, file_name: str):
        super().__init__(file_name)

    def file_path_post_eds(self, home_and_eds: HomeAndEds) -> pathlib.Path:
        return pathlib.Path.cwd() / self._file_name


class _FileRefRelTmpUser(_FileRefForFileThatDoesNotExistPreEdsBase):
    def __init__(self, file_name: str):
        super().__init__(file_name)

    def file_path_post_eds(self, home_and_eds: HomeAndEds) -> pathlib.Path:
        return home_and_eds.eds.tmp.user_dir / self._file_name


class _FileRefRelTmpInternal(_FileRefForFileThatDoesNotExistPreEdsBase):
    def __init__(self, file_name: str):
        super().__init__(file_name)

    def file_path_post_eds(self, home_and_eds: HomeAndEds) -> pathlib.Path:
        return home_and_eds.eds.tmp.internal_dir / self._file_name
