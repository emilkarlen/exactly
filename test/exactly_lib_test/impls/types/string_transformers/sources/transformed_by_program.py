import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import Sequence, ContextManager

from exactly_lib.impls.types.string_transformer.impl.sources import transformed_by_program as sut
from exactly_lib.impls.types.utils.command_w_stdin import CommandWStdin
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.type_val_prims.program.commands import Command
from exactly_lib.type_val_prims.program.commands import CommandDriverForExecutableFile
from exactly_lib.type_val_prims.program.program import Program
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_transformer import StringTransformer
from exactly_lib_test.impls.types.string_source.test_resources.string_sources import source_from_lines_test_impl
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder
from exactly_lib_test.type_val_deps.types.path.test_resources import described_path
from exactly_lib_test.type_val_prims.string_source.test_resources import multi_obj_assertions
from exactly_lib_test.type_val_prims.string_source.test_resources.source_constructors import \
    SourceConstructorWAppEnvForTest
from exactly_lib_test.type_val_prims.string_transformer.test_resources import string_transformers


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestTransformedByCommand),
        unittest.makeSuite(TestTransformedByProgramWoTransformation),
        unittest.makeSuite(TestTransformedByProgramWTransformation),
    ])


class TestTransformedByCommand(unittest.TestCase):
    def test_exit_code_0(self):
        # ARRANGE #
        input_raw_lines = [
            'a\n',
            'ab\n',
            '123\n',
        ]

        for ignore_exit_code in [False, True]:
            source_constructor = _ToUpperCommandSourceConstructor(
                input_raw_lines,
                ignore_exit_code=False,
                exit_code=0
            )
            expectation = multi_obj_assertions.ExpectationOnUnFrozenAndFrozen.equals(
                source_constructor.contents.upper(),
                may_depend_on_external_resources=asrt.equals(True),
                frozen_may_depend_on_external_resources=asrt.anything_goes(),
            )
            with self.subTest(ignore_exit_code=ignore_exit_code):
                assertion = multi_obj_assertions.assertion_of_sequence_permutations(expectation)
                # ACT & ASSERT #
                assertion.apply_without_message(
                    self,
                    multi_obj_assertions.SourceConstructors.of_common(source_constructor)
                )

    def test_exit_code_non_0_and_ignore_exit_code(self):
        # ARRANGE #
        source_constructor = _ToUpperCommandSourceConstructor(
            [
                'a\n',
                'ab\n',
                '123\n',
            ],
            ignore_exit_code=True,
            exit_code=1
        )
        expectation = multi_obj_assertions.ExpectationOnUnFrozenAndFrozen.equals(
            source_constructor.contents.upper(),
            may_depend_on_external_resources=asrt.equals(True),
            frozen_may_depend_on_external_resources=asrt.anything_goes(),
        )

        assertion = multi_obj_assertions.assertion_of_sequence_permutations(expectation)
        # ACT & ASSERT #
        assertion.apply_without_message(
            self,
            multi_obj_assertions.SourceConstructors.of_common(source_constructor),
        )

    def test_exit_code_non_0_and_not_ignore_exit_code(self):
        # ARRANGE #
        source_constructor = _ToUpperCommandSourceConstructor(
            [
                'a\n',
                'ab\n',
                '123\n',
            ],
            ignore_exit_code=False,
            exit_code=1
        )
        expectation = multi_obj_assertions.ExpectationOnUnFrozenAndFrozen.hard_error()

        assertion = multi_obj_assertions.assertion_of_sequence_permutations(expectation)
        # ACT & ASSERT #
        assertion.apply_without_message(
            self,
            multi_obj_assertions.SourceConstructors.of_common(source_constructor),
        )


class TestTransformedByProgramWoTransformation(unittest.TestCase):
    def test_exit_code_0(self):
        # ARRANGE #
        input_raw_lines = [
            'a\n',
            'ab\n',
            '123\n',
        ]

        for ignore_exit_code in [False, True]:
            source_constructor = _ToUpperProgramSourceConstructor(
                input_raw_lines,
                ignore_exit_code=False,
                exit_code=0
            )
            expectation = multi_obj_assertions.ExpectationOnUnFrozenAndFrozen.equals(
                source_constructor.contents.upper(),
                may_depend_on_external_resources=asrt.equals(True),
                frozen_may_depend_on_external_resources=asrt.anything_goes(),
            )
            with self.subTest(ignore_exit_code=ignore_exit_code):
                assertion = multi_obj_assertions.assertion_of_sequence_permutations(expectation)
                # ACT & ASSERT #
                assertion.apply_without_message(
                    self,
                    multi_obj_assertions.SourceConstructors.of_common(source_constructor),
                )

    def test_exit_code_non_0_and_ignore_exit_code(self):
        # ARRANGE #
        source_constructor = _ToUpperProgramSourceConstructor(
            [
                'a\n',
                'ab\n',
                '123\n',
            ],
            ignore_exit_code=True,
            exit_code=1
        )
        expectation = multi_obj_assertions.ExpectationOnUnFrozenAndFrozen.equals(
            source_constructor.contents.upper(),
            may_depend_on_external_resources=asrt.equals(True),
            frozen_may_depend_on_external_resources=asrt.anything_goes(),
        )

        assertion = multi_obj_assertions.assertion_of_sequence_permutations(expectation)
        # ACT & ASSERT #
        assertion.apply_without_message(
            self,
            multi_obj_assertions.SourceConstructors.of_common(source_constructor),
        )

    def test_exit_code_non_0_and_not_ignore_exit_code(self):
        # ARRANGE #
        source_constructor = _ToUpperProgramSourceConstructor(
            [
                'a\n',
                'ab\n',
                '123\n',
            ],
            ignore_exit_code=False,
            exit_code=1
        )
        expectation = multi_obj_assertions.ExpectationOnUnFrozenAndFrozen.hard_error()

        assertion = multi_obj_assertions.assertion_of_sequence_permutations(expectation)
        # ACT & ASSERT #
        assertion.apply_without_message(
            self,
            multi_obj_assertions.SourceConstructors.of_common(source_constructor),
        )


class TestTransformedByProgramWTransformation(unittest.TestCase):
    def test_exit_code_0(self):
        # ARRANGE #
        input_raw_lines = [
            'a\n',
            'ab\n',
            '123\n',
        ]
        additional_transformer = string_transformers.count_num_uppercase_characters()
        expected = '1\n2\n0\n'

        for ignore_exit_code in [False, True]:
            source_constructor = _ToUpperProgramSourceConstructor(
                input_raw_lines,
                ignore_exit_code=False,
                exit_code=0,
                transformation_of_program=[additional_transformer]
            )
            expectation = multi_obj_assertions.ExpectationOnUnFrozenAndFrozen.equals(
                expected,
                may_depend_on_external_resources=asrt.equals(True),
                frozen_may_depend_on_external_resources=asrt.anything_goes(),
            )
            with self.subTest(ignore_exit_code=ignore_exit_code):
                assertion = multi_obj_assertions.assertion_of_sequence_permutations(expectation)
                # ACT & ASSERT #
                assertion.apply_without_message(
                    self,
                    multi_obj_assertions.SourceConstructors.of_common(source_constructor),
                )

    def test_exit_code_non_0_and_ignore_exit_code(self):
        # ARRANGE #
        input_raw_lines = [
            'a\n',
            'ab\n',
            '123\n',
        ]
        additional_transformer = string_transformers.count_num_uppercase_characters()
        expected = '1\n2\n0\n'
        expectation = multi_obj_assertions.ExpectationOnUnFrozenAndFrozen.equals(
            expected,
            may_depend_on_external_resources=asrt.equals(True),
            frozen_may_depend_on_external_resources=asrt.anything_goes(),
        )

        source_constructor = _ToUpperProgramSourceConstructor(
            input_raw_lines,
            ignore_exit_code=True,
            exit_code=1,
            transformation_of_program=[additional_transformer]
        )

        assertion = multi_obj_assertions.assertion_of_sequence_permutations(expectation)
        # ACT & ASSERT #
        assertion.apply_without_message(
            self,
            multi_obj_assertions.SourceConstructors.of_common(source_constructor),
        )

    def test_exit_code_non_0_and_not_ignore_exit_code(self):
        # ARRANGE #
        source_constructor = _ToUpperProgramSourceConstructor(
            [
                'a\n',
                'ab\n',
                '123\n',
            ],
            ignore_exit_code=False,
            exit_code=1,
            transformation_of_program=[string_transformers.count_num_uppercase_characters()]
        )
        expectation = multi_obj_assertions.ExpectationOnUnFrozenAndFrozen.hard_error()

        assertion = multi_obj_assertions.assertion_of_sequence_permutations(expectation)
        # ACT & ASSERT #
        assertion.apply_without_message(
            self,
            multi_obj_assertions.SourceConstructors.of_common(source_constructor),
        )


class _ToUpperCommandSourceConstructor(SourceConstructorWAppEnvForTest):
    def __init__(self,
                 raw_lines: Sequence[str],
                 ignore_exit_code: bool,
                 exit_code: int,
                 ):
        super().__init__()
        self.raw_lines = raw_lines
        self.ignore_exit_code = ignore_exit_code
        self.exit_code = exit_code
        self.contents = ''.join(raw_lines)

    @contextmanager
    def new_with(self,
                 put: unittest.TestCase,
                 message_builder: MessageBuilder,
                 app_env: ApplicationEnvironment,
                 ) -> ContextManager[StringSource]:
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            tmp_dir_path = Path(tmp_dir_name)

            source_model = source_from_lines_test_impl(
                self.raw_lines,
                app_env.tmp_files_space,
            )

            yield sut.transformed_by_command(
                CommandWStdin(_to_upper_command(tmp_dir_path, self.exit_code), ()),
                self.ignore_exit_code,
                app_env,
                source_model,
            )


class _ToUpperProgramSourceConstructor(SourceConstructorWAppEnvForTest):
    def __init__(self,
                 raw_lines: Sequence[str],
                 ignore_exit_code: bool,
                 exit_code: int,
                 transformation_of_program: Sequence[StringTransformer] = ()
                 ):
        super().__init__()
        self.raw_lines = raw_lines
        self.ignore_exit_code = ignore_exit_code
        self.exit_code = exit_code
        self.transformation_of_program = transformation_of_program
        self.contents = ''.join(raw_lines)

    @contextmanager
    def new_with(self,
                 put: unittest.TestCase,
                 message_builder: MessageBuilder,
                 app_env: ApplicationEnvironment,
                 ) -> ContextManager[StringSource]:
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            tmp_dir_path = Path(tmp_dir_name)

            source_model = source_from_lines_test_impl(
                self.raw_lines,
                app_env.tmp_files_space,
            )

            yield sut.transformed_by_program(
                self._to_upper_program(tmp_dir_path),
                self.ignore_exit_code,
                app_env,
                source_model,
            )

    def _to_upper_program(self, empty_tmp_dir: Path) -> Program:
        return Program(
            _to_upper_command(empty_tmp_dir, self.exit_code),
            (),
            self.transformation_of_program,
        )


def _to_upper_command(empty_tmp_dir: Path, exit_code: int) -> Command:
    py_program = fs.File(
        'to-upper.py',
        _to_upper_stdin_py_program_w_exit_code(exit_code))
    fs.DirContents([py_program]).write_to(empty_tmp_dir)

    return Command(
        CommandDriverForExecutableFile(
            described_path.new_primitive(Path(sys.executable))
        ),
        [str(empty_tmp_dir / py_program.name)]
    )


def _to_upper_stdin_py_program_w_exit_code(exit_code: int) -> str:
    return _TO_UPPER_PY_PROGRAM_TEMPLATE.format(
        EXIT_CODE=exit_code
    )


_TO_UPPER_PY_PROGRAM_TEMPLATE = """\
import sys

sys.stdout.writelines(map(str.upper, sys.stdin.readlines()))

sys.exit({EXIT_CODE})
"""

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
