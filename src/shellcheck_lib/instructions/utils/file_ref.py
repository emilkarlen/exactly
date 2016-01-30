import pathlib

from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.instructions.utils.pre_or_post_validation import PreOrPostEdsValidator
from shellcheck_lib.test_case.phases.common import HomeAndEds


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
        :raises ValueError: This file exists only post-EDS.
        """
        raise NotImplementedError()

    def file_path_post_eds(self, eds: ExecutionDirectoryStructure) -> pathlib.Path:
        """
        :raises ValueError: This file exists pre-EDS.
        """
        raise NotImplementedError()

    def file_path_pre_or_post_eds(self, home_and_eds: HomeAndEds) -> pathlib.Path:
        if self.exists_pre_eds:
            return self.file_path_pre_eds(home_and_eds.home_dir_path)
        else:
            return self.file_path_post_eds(home_and_eds.eds)

    @property
    def exists_pre_eds(self) -> bool:
        return self.__exists_pre_eds


class FileRefRelEds(FileRef):
    def __init__(self, file_name: str):
        super().__init__(False, file_name)

    def file_path_pre_eds(self, home_dir_path: pathlib.Path) -> pathlib.Path:
        """
        Can only be used if the files exists pre-EDS.
        """
        raise ValueError('This file does not exist before EDS is constructed')

    def file_path_rel_eds(self, eds: ExecutionDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()

    def file_path_post_eds(self, eds: ExecutionDirectoryStructure) -> pathlib.Path:
        return self.file_path_post_eds(eds)


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

    def file_path_pre_eds(self, home_dir_path: pathlib.Path) -> pathlib.Path:
        return pathlib.Path(self._file_name)

    def file_path_post_eds(self, eds: ExecutionDirectoryStructure) -> pathlib.Path:
        raise ValueError('This file exists pre-EDS')


class _FileRefRelHome(FileRef):
    def __init__(self, file_name: str):
        super().__init__(True, file_name)

    def file_path_pre_eds(self, home_dir_path: pathlib.Path) -> pathlib.Path:
        return home_dir_path / self._file_name

    def file_path_post_eds(self, eds: ExecutionDirectoryStructure) -> pathlib.Path:
        raise ValueError('This file exists pre-EDS')


class _FileRefRelCwd(FileRefRelEds):
    def __init__(self, file_name: str):
        super().__init__(file_name)

    def file_path_post_eds(self, eds: ExecutionDirectoryStructure):
        return pathlib.Path.cwd() / self._file_name


class _FileRefRelAct(FileRefRelEds):
    def __init__(self, file_name: str):
        super().__init__(file_name)

    def file_path_post_eds(self, eds: ExecutionDirectoryStructure):
        return eds.act_dir / self._file_name


class _FileRefRelTmpUser(FileRefRelEds):
    def __init__(self, file_name: str):
        super().__init__(file_name)

    def file_path_post_eds(self, eds: ExecutionDirectoryStructure):
        return eds.tmp.user_dir / self._file_name


class _FileRefRelTmpInternal(FileRefRelEds):
    def __init__(self, file_name: str):
        super().__init__(file_name)

    def file_path_post_eds(self, eds: ExecutionDirectoryStructure):
        return eds.tmp.internal_dir / self._file_name


class FileRefValidatorBase(PreOrPostEdsValidator):
    def __init__(self,
                 file_ref: FileRef):
        self.file_ref = file_ref

    def _validate_path(self, file_path: pathlib.Path) -> str:
        raise NotImplementedError()

    def validate_pre_eds_if_applicable(self, home_dir_path: pathlib.Path) -> str:
        if self.file_ref.exists_pre_eds:
            return self._validate_path(self.file_ref.file_path_pre_eds(home_dir_path))
        return None

    def validate_post_eds_if_applicable(self, eds: ExecutionDirectoryStructure) -> str:
        if not self.file_ref.exists_pre_eds:
            return self._validate_path(self.file_ref.file_path_post_eds(eds))
        return None
