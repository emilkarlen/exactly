import pathlib

from exactly_lib.instructions.utils import relativity_root
from exactly_lib.instructions.utils.arg_parse import relative_path_options
from exactly_lib.test_case.file_ref import FileRef
from exactly_lib.test_case.file_ref_relativity import RelOptionType
from exactly_lib.test_case.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds, \
    PathResolvingEnvironmentPreSds, PathResolvingEnvironmentPostSds
from exactly_lib.test_case.value_definition import FileRefValue, ValueReferenceOfPath
from exactly_lib.util.symbol_table import SymbolTable


class _FileRefWithConstantLocationBase(FileRef):
    """
    Base class for `FileRef`s who's "relativity" is constant.
    """

    def __init__(self, exists_pre_sds: bool, file_name: str):
        super().__init__(file_name)
        self.__exists_pre_sds = exists_pre_sds

    def value_references_of_paths(self) -> list:
        return []

    def exists_pre_sds(self, value_definitions: SymbolTable) -> bool:
        return self.__exists_pre_sds

    def file_path_pre_or_post_sds(self, environment: PathResolvingEnvironmentPreOrPostSds) -> pathlib.Path:
        if self.__exists_pre_sds:
            return self.file_path_pre_sds(environment)
        else:
            return self.file_path_post_sds(environment)


class _FileRefFromRelRootResolver(_FileRefWithConstantLocationBase):
    def __init__(self,
                 rel_root_resolver: relativity_root.RelRootResolver,
                 file_name: str
                 ):
        super().__init__(rel_root_resolver.is_rel_home, file_name)
        self._rel_root_resolver = rel_root_resolver

    def relativity(self, value_definitions: SymbolTable) -> RelOptionType:
        return self._rel_root_resolver.relativity_type

    def file_path_pre_sds(self, environment: PathResolvingEnvironmentPreSds) -> pathlib.Path:
        return self._rel_root_resolver.from_home(environment.home_dir_path) / self._file_name

    def file_path_post_sds(self, environment: PathResolvingEnvironmentPostSds):
        if self._rel_root_resolver.is_rel_cwd:
            root = self._rel_root_resolver.from_cwd()
        else:
            root = self._rel_root_resolver.from_sds(environment.sds)
        return root / self._file_name


def of_rel_root(rel_root_resolver: relativity_root.RelRootResolver,
                file_name: str) -> FileRef:
    return _FileRefFromRelRootResolver(rel_root_resolver, file_name)


def of_rel_option(rel_option: relativity_root.RelOptionType,
                  file_name: str) -> FileRef:
    return _FileRefFromRelRootResolver(relative_path_options.REL_OPTIONS_MAP[rel_option].root_resolver,
                                       file_name)


def absolute_file_name(file_name: str) -> FileRef:
    return _FileRefAbsolute(file_name)


def rel_home(file_name: str) -> FileRef:
    return of_rel_root(relativity_root.resolver_for_home, file_name)


def rel_cwd(file_name: str) -> FileRef:
    return of_rel_root(relativity_root.resolver_for_cwd, file_name)


def rel_act(file_name: str) -> FileRef:
    return of_rel_root(relativity_root.resolver_for_act, file_name)


def rel_tmp_user(file_name: str) -> FileRef:
    return of_rel_root(relativity_root.resolver_for_tmp_user, file_name)


def rel_value_definition(file_name: str, value_reference_of_path: ValueReferenceOfPath) -> FileRef:
    return _FileRefRelValueDefinition(file_name, value_reference_of_path)


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


class _FileRefRelTmpInternal(_FileRefWithConstantLocationBase):
    def __init__(self, file_name: str):
        super().__init__(False, file_name)

    def file_path_pre_sds(self, environment: PathResolvingEnvironmentPreSds) -> pathlib.Path:
        raise ValueError('This file does not exist pre-SDS')

    def file_path_post_sds(self, environment: PathResolvingEnvironmentPostSds):
        return environment.sds.tmp.internal_dir / self._file_name


class _FileRefRelValueDefinition(FileRef):
    def __init__(self,
                 file_name: str,
                 value_reference_of_path: ValueReferenceOfPath):
        super().__init__(file_name)
        self.value_reference_of_path = value_reference_of_path

    def value_references_of_paths(self) -> list:
        return [self.value_reference_of_path]

    def relativity(self, value_definitions: SymbolTable) -> RelOptionType:
        file_ref = self._lookup_file_ref(value_definitions)
        return file_ref.relativity(value_definitions)

    def exists_pre_sds(self, value_definitions: SymbolTable) -> bool:
        file_ref = self._lookup_file_ref(value_definitions)
        return file_ref.exists_pre_sds(value_definitions)

    def file_path_post_sds(self, environment: PathResolvingEnvironmentPostSds) -> pathlib.Path:
        file_ref = self._lookup_file_ref(environment.value_definitions)
        return file_ref.file_path_post_sds(environment)

    def file_path_pre_sds(self, environment: PathResolvingEnvironmentPreSds) -> pathlib.Path:
        file_ref = self._lookup_file_ref(environment.value_definitions)
        return file_ref.file_path_pre_sds(environment)

    def _lookup_file_ref(self, value_definitions: SymbolTable) -> FileRef:
        return lookup_file_ref_from_symbol_table(value_definitions, self.value_reference_of_path.name)


def lookup_file_ref_from_symbol_table(value_definitions: SymbolTable, name: str) -> FileRef:
    value = value_definitions.lookup(name)
    assert isinstance(value, FileRefValue)
    return value.file_ref
