import pathlib

from exactly_lib.test_case.file_ref import FileRef
from exactly_lib.test_case.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds, \
    PathResolvingEnvironmentPreSds, PathResolvingEnvironmentPostSds
from exactly_lib.test_case.value_definition import ValueReference


class _FileRefWithConstantLocationBase(FileRef):
    """
    Base class for `FileRef`s who's "relativity" is constant.
    """

    def __init__(self, exists_pre_sds: bool, file_name: str):
        super().__init__(file_name)
        self.__exists_pre_sds = exists_pre_sds

    def value_references(self) -> list:
        return []

    def exists_pre_sds(self) -> bool:
        return self.__exists_pre_sds

    def file_path_pre_or_post_sds(self, environment: PathResolvingEnvironmentPreOrPostSds) -> pathlib.Path:
        if self.__exists_pre_sds:
            return self.file_path_pre_sds(environment)
        else:
            return self.file_path_post_sds(environment)


class FileRefRelSds(_FileRefWithConstantLocationBase):
    def __init__(self, file_name: str):
        super().__init__(False, file_name)

    def file_path_pre_sds(self, environment: PathResolvingEnvironmentPreSds) -> pathlib.Path:
        """
        Can only be used if the files exists pre-SDS.
        """
        raise ValueError('This file does not exist before SDS is constructed')


def absolute_file_name(file_name: str) -> FileRef:
    return _FileRefAbsolute(file_name)


def rel_home(file_name: str) -> FileRef:
    return _FileRefRelHome(file_name)


def rel_cwd(file_name: str) -> FileRefRelSds:
    return _FileRefRelCwd(file_name)


def rel_act(file_name: str) -> FileRefRelSds:
    return _FileRefRelAct(file_name)


def rel_tmp_internal(file_name: str) -> FileRefRelSds:
    return _FileRefRelTmpInternal(file_name)


def rel_tmp_user(file_name: str) -> FileRefRelSds:
    return _FileRefRelTmpUser(file_name)


def rel_value_definition(file_name: str, value_definition_name: str) -> FileRef:
    return _FileRefRelValueDefinition(file_name, value_definition_name)


class _FileRefAbsolute(_FileRefWithConstantLocationBase):
    def __init__(self, file_name: str):
        super().__init__(True, file_name)

    def file_path_pre_sds(self, environment: PathResolvingEnvironmentPreSds) -> pathlib.Path:
        return pathlib.Path(self._file_name)

    def file_path_post_sds(self, environment: PathResolvingEnvironmentPostSds) -> pathlib.Path:
        raise ValueError('This file exists pre-SDS')


class _FileRefRelHome(_FileRefWithConstantLocationBase):
    def __init__(self, file_name: str):
        super().__init__(True, file_name)

    def file_path_pre_sds(self, environment: PathResolvingEnvironmentPreSds) -> pathlib.Path:
        return environment.home_dir_path / self._file_name

    def file_path_post_sds(self, environment: PathResolvingEnvironmentPostSds) -> pathlib.Path:
        raise ValueError('This file exists pre-SDS')


class _FileRefRelCwd(FileRefRelSds):
    def __init__(self, file_name: str):
        super().__init__(file_name)

    def file_path_post_sds(self, environment: PathResolvingEnvironmentPostSds):
        return pathlib.Path.cwd() / self._file_name


class _FileRefRelAct(FileRefRelSds):
    def __init__(self, file_name: str):
        super().__init__(file_name)

    def file_path_post_sds(self, environment: PathResolvingEnvironmentPostSds):
        return environment.sds.act_dir / self._file_name


class _FileRefRelTmpUser(FileRefRelSds):
    def __init__(self, file_name: str):
        super().__init__(file_name)

    def file_path_post_sds(self, environment: PathResolvingEnvironmentPostSds):
        return environment.sds.tmp.user_dir / self._file_name


class _FileRefRelTmpInternal(FileRefRelSds):
    def __init__(self, file_name: str):
        super().__init__(file_name)

    def file_path_post_sds(self, environment: PathResolvingEnvironmentPostSds):
        return environment.sds.tmp.internal_dir / self._file_name


class _FileRefRelValueDefinition(FileRef):
    def __init__(self, file_name: str, value_definition_name: str):
        super().__init__(file_name)
        self.value_definition_name = value_definition_name

    def value_references(self) -> list:
        return [ValueReference(self.value_definition_name)]

    def exists_pre_sds(self) -> bool:
        raise NotImplementedError()

    def file_path_post_sds(self, environment: PathResolvingEnvironmentPostSds) -> pathlib.Path:
        raise NotImplementedError()

    def file_path_pre_sds(self, environment: PathResolvingEnvironmentPreSds) -> pathlib.Path:
        return [ValueReference(self.value_definition_name)]
