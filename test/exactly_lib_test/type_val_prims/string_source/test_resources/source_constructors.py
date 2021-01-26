import tempfile
import unittest
from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager, Callable

from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder
from exactly_lib_test.type_val_deps.dep_variants.test_resources import application_environment
from exactly_lib_test.type_val_prims.string_source.test_resources.multi_obj_assertions import SourceConstructors, \
    SourceConstructor
from exactly_lib_test.util.file_utils.test_resources import tmp_file_spaces

DirFileSpaceGetter = Callable[[unittest.TestCase, MessageBuilder], ContextManager[DirFileSpace]]


@contextmanager
def get_dir_file_space_with_existing_dir(put: unittest.TestCase,
                                         message_builder: MessageBuilder) -> ContextManager[DirFileSpace]:
    with tempfile.TemporaryDirectory(prefix='exactly') as tmp_dir_name:
        yield tmp_file_spaces.tmp_dir_file_space_for_test(Path(tmp_dir_name))


class SourceConstructorWAppEnvForTest(SourceConstructor, ABC):
    def __init__(self,
                 get_dir_file_space: DirFileSpaceGetter
                 = get_dir_file_space_with_existing_dir,
                 ):
        self._get_dir_file_space = get_dir_file_space

    @abstractmethod
    def new_with(self,
                 put: unittest.TestCase,
                 message_builder: MessageBuilder,
                 app_env: ApplicationEnvironment,
                 ) -> ContextManager[StringSource]:
        pass

    @contextmanager
    def new(self, put: unittest.TestCase, message_builder: MessageBuilder) -> ContextManager[StringSource]:
        with self._get_dir_file_space(put, message_builder) as dir_file_space:
            app_env = application_environment.application_environment_for_test(dir_file_space)
            with self.new_with(put, message_builder, app_env) as string_source:
                yield string_source


class SourceConstructorsBuilder(ABC):
    @abstractmethod
    def app_env_for_no_freeze(self,
                              put: unittest.TestCase,
                              message_builder: MessageBuilder
                              ) -> ContextManager[ApplicationEnvironment]:
        pass

    @abstractmethod
    def app_env_for_freeze(self,
                           put: unittest.TestCase,
                           message_builder: MessageBuilder,
                           ) -> ContextManager[ApplicationEnvironment]:
        pass

    @abstractmethod
    def new_with(self,
                 put: unittest.TestCase,
                 message_builder: MessageBuilder,
                 app_env: ApplicationEnvironment) -> StringSource:
        pass

    def build(self) -> SourceConstructors:
        return SourceConstructors(
            _SourceConstructorFromBuilder(self, self.app_env_for_no_freeze),
            _SourceConstructorFromBuilder(self, self.app_env_for_freeze),
        )


class _SourceConstructorFromBuilder(SourceConstructor):
    def __init__(self,
                 builder: SourceConstructorsBuilder,
                 get_app_env: Callable[[unittest.TestCase, MessageBuilder], ContextManager[ApplicationEnvironment]],
                 ):
        self.builder = builder
        self.get_app_env = get_app_env

    @contextmanager
    def new(self, put: unittest.TestCase, message_builder: MessageBuilder) -> ContextManager[StringSource]:
        with self.get_app_env(put, message_builder) as app_env:
            yield self.builder.new_with(put, message_builder, app_env)
