import pathlib

from exactly_lib.instructions.utils.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure


class FileRef:
    def __init__(self,
                 exists_pre_sds: bool,
                 file_name: str):
        self.__exists_pre_sds = exists_pre_sds
        self._file_name = file_name

    @property
    def file_name(self) -> str:
        return self._file_name

    def file_path_pre_sds(self, home_dir_path: pathlib.Path) -> pathlib.Path:
        """
        :raises ValueError: This file exists only post-SDS.
        """
        raise NotImplementedError()

    def file_path_post_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        """
        :raises ValueError: This file exists pre-SDS.
        """
        raise NotImplementedError()

    def file_path_pre_or_post_sds(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        if self.exists_pre_sds:
            return self.file_path_pre_sds(home_and_sds.home_dir_path)
        else:
            return self.file_path_post_sds(home_and_sds.sds)

    @property
    def exists_pre_sds(self) -> bool:
        return self.__exists_pre_sds


class FileRefRelEds(FileRef):
    def __init__(self, file_name: str):
        super().__init__(False, file_name)

    def file_path_pre_sds(self, home_dir_path: pathlib.Path) -> pathlib.Path:
        """
        Can only be used if the files exists pre-SDS.
        """
        raise ValueError('This file does not exist before SDS is constructed')

    def file_path_rel_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()

    def file_path_post_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return self.file_path_post_sds(sds)


def absolute_file_name(file_name: str) -> FileRef:
    return _FileRefAbsolute(file_name)


def rel_home(file_name: str) -> FileRef:
    return _FileRefRelHome(file_name)


def rel_cwd(file_name: str) -> FileRefRelEds:
    return _FileRefRelCwd(file_name)


def rel_act(file_name: str) -> FileRefRelEds:
    return _FileRefRelAct(file_name)


def rel_tmp_internal(file_name: str) -> FileRefRelEds:
    return _FileRefRelTmpInternal(file_name)


def rel_tmp_user(file_name: str) -> FileRefRelEds:
    return _FileRefRelTmpUser(file_name)


class _FileRefAbsolute(FileRef):
    def __init__(self, file_name: str):
        super().__init__(True, file_name)

    def file_path_pre_sds(self, home_dir_path: pathlib.Path) -> pathlib.Path:
        return pathlib.Path(self._file_name)

    def file_path_post_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        raise ValueError('This file exists pre-SDS')


class _FileRefRelHome(FileRef):
    def __init__(self, file_name: str):
        super().__init__(True, file_name)

    def file_path_pre_sds(self, home_dir_path: pathlib.Path) -> pathlib.Path:
        return home_dir_path / self._file_name

    def file_path_post_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        raise ValueError('This file exists pre-SDS')


class _FileRefRelCwd(FileRefRelEds):
    def __init__(self, file_name: str):
        super().__init__(file_name)

    def file_path_post_sds(self, sds: SandboxDirectoryStructure):
        return pathlib.Path.cwd() / self._file_name


class _FileRefRelAct(FileRefRelEds):
    def __init__(self, file_name: str):
        super().__init__(file_name)

    def file_path_post_sds(self, sds: SandboxDirectoryStructure):
        return sds.act_dir / self._file_name


class _FileRefRelTmpUser(FileRefRelEds):
    def __init__(self, file_name: str):
        super().__init__(file_name)

    def file_path_post_sds(self, sds: SandboxDirectoryStructure):
        return sds.tmp.user_dir / self._file_name


class _FileRefRelTmpInternal(FileRefRelEds):
    def __init__(self, file_name: str):
        super().__init__(file_name)

    def file_path_post_sds(self, sds: SandboxDirectoryStructure):
        return sds.tmp.internal_dir / self._file_name


class FileRefValidatorBase(PreOrPostSdsValidator):
    def __init__(self,
                 file_ref: FileRef):
        self.file_ref = file_ref

    def _validate_path(self, file_path: pathlib.Path) -> str:
        """
        :return: Error message iff validation was applicable and validation failed.
        """
        raise NotImplementedError()

    def validate_pre_sds_if_applicable(self, home_dir_path: pathlib.Path) -> str:
        if self.file_ref.exists_pre_sds:
            return self._validate_path(self.file_ref.file_path_pre_sds(home_dir_path))
        return None

    def validate_post_sds_if_applicable(self, sds: SandboxDirectoryStructure) -> str:
        if not self.file_ref.exists_pre_sds:
            return self._validate_path(self.file_ref.file_path_post_sds(sds))
        return None
