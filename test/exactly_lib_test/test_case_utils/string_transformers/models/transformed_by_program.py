import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import Sequence, ContextManager

from exactly_lib.test_case_utils.string_transformer.impl.identity import IdentityStringTransformer
from exactly_lib.test_case_utils.string_transformer.impl.models import transformed_by_program as sut
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.program.process_execution.command import Command
from exactly_lib.type_system.logic.program.process_execution.commands import CommandDriverForExecutableFile
from exactly_lib.type_system.logic.program.program import Program
from exactly_lib.type_system.logic.program.stdin_data import StdinData
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.type_system.logic.string_transformer import StringTransformer
from exactly_lib_test.test_case_utils.string_models.test_resources.string_models import ModelFromLinesTestImpl
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.type_system.data.test_resources import described_path
from exactly_lib_test.type_system.logic.string_model.test_resources import model_checker
from exactly_lib_test.type_system.logic.string_transformer.test_resources import string_transformers


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
            model_constructor = _ToUpperCommandModelConstructor(
                input_raw_lines,
                ignore_exit_code=False,
                exit_code=0
            )
            expectation = model_checker.Expectation.equals(
                model_constructor.contents.upper()
            )
            with self.subTest(ignore_exit_code=ignore_exit_code):
                checker = model_checker.Checker(
                    self,
                    model_constructor,
                    expectation,
                )
                # ACT & ASSERT #
                checker.check()

    def test_exit_code_non_0_and_ignore_exit_code(self):
        # ARRANGE #
        model_constructor = _ToUpperCommandModelConstructor(
            [
                'a\n',
                'ab\n',
                '123\n',
            ],
            ignore_exit_code=True,
            exit_code=1
        )
        expectation = model_checker.Expectation.equals(
            model_constructor.contents.upper()
        )

        checker = model_checker.Checker(
            self,
            model_constructor,
            expectation,
        )
        # ACT & ASSERT #
        checker.check()

    def test_exit_code_non_0_and_not_ignore_exit_code(self):
        # ARRANGE #
        model_constructor = _ToUpperCommandModelConstructor(
            [
                'a\n',
                'ab\n',
                '123\n',
            ],
            ignore_exit_code=False,
            exit_code=1
        )
        expectation = model_checker.Expectation.hard_error()

        checker = model_checker.Checker(
            self,
            model_constructor,
            expectation,
        )
        # ACT & ASSERT #
        checker.check()


class TestTransformedByProgramWoTransformation(unittest.TestCase):
    def test_exit_code_0(self):
        # ARRANGE #
        input_raw_lines = [
            'a\n',
            'ab\n',
            '123\n',
        ]

        for ignore_exit_code in [False, True]:
            model_constructor = _ToUpperProgramModelConstructor(
                input_raw_lines,
                ignore_exit_code=False,
                exit_code=0
            )
            expectation = model_checker.Expectation.equals(
                model_constructor.contents.upper()
            )
            with self.subTest(ignore_exit_code=ignore_exit_code):
                checker = model_checker.Checker(
                    self,
                    model_constructor,
                    expectation,
                )
                # ACT & ASSERT #
                checker.check()

    def test_exit_code_non_0_and_ignore_exit_code(self):
        # ARRANGE #
        model_constructor = _ToUpperProgramModelConstructor(
            [
                'a\n',
                'ab\n',
                '123\n',
            ],
            ignore_exit_code=True,
            exit_code=1
        )
        expectation = model_checker.Expectation.equals(
            model_constructor.contents.upper()
        )

        checker = model_checker.Checker(
            self,
            model_constructor,
            expectation,
        )
        # ACT & ASSERT #
        checker.check()

    def test_exit_code_non_0_and_not_ignore_exit_code(self):
        # ARRANGE #
        model_constructor = _ToUpperProgramModelConstructor(
            [
                'a\n',
                'ab\n',
                '123\n',
            ],
            ignore_exit_code=False,
            exit_code=1
        )
        expectation = model_checker.Expectation.hard_error()

        checker = model_checker.Checker(
            self,
            model_constructor,
            expectation,
        )
        # ACT & ASSERT #
        checker.check()


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
            model_constructor = _ToUpperProgramModelConstructor(
                input_raw_lines,
                ignore_exit_code=False,
                exit_code=0,
                transformation_of_program=additional_transformer
            )
            expectation = model_checker.Expectation.equals(expected)
            with self.subTest(ignore_exit_code=ignore_exit_code):
                checker = model_checker.Checker(
                    self,
                    model_constructor,
                    expectation,
                )
                # ACT & ASSERT #
                checker.check()

    def test_exit_code_non_0_and_ignore_exit_code(self):
        # ARRANGE #
        input_raw_lines = [
            'a\n',
            'ab\n',
            '123\n',
        ]
        additional_transformer = string_transformers.count_num_uppercase_characters()
        expected = '1\n2\n0\n'
        expectation = model_checker.Expectation.equals(expected)

        model_constructor = _ToUpperProgramModelConstructor(
            input_raw_lines,
            ignore_exit_code=True,
            exit_code=1,
            transformation_of_program=additional_transformer
        )

        checker = model_checker.Checker(
            self,
            model_constructor,
            expectation,
        )
        # ACT & ASSERT #
        checker.check()

    def test_exit_code_non_0_and_not_ignore_exit_code(self):
        # ARRANGE #
        model_constructor = _ToUpperProgramModelConstructor(
            [
                'a\n',
                'ab\n',
                '123\n',
            ],
            ignore_exit_code=False,
            exit_code=1,
            transformation_of_program=string_transformers.count_num_uppercase_characters()
        )
        expectation = model_checker.Expectation.hard_error()

        checker = model_checker.Checker(
            self,
            model_constructor,
            expectation,
        )
        # ACT & ASSERT #
        checker.check()


class _ToUpperCommandModelConstructor(model_checker.ModelConstructor):
    def __init__(self,
                 raw_lines: Sequence[str],
                 ignore_exit_code: bool,
                 exit_code: int,
                 ):
        self.raw_lines = raw_lines
        self.ignore_exit_code = ignore_exit_code
        self.exit_code = exit_code
        self.contents = ''.join(raw_lines)

    @contextmanager
    def new_with(self, app_env: ApplicationEnvironment) -> ContextManager[StringModel]:
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            tmp_dir_path = Path(tmp_dir_name)

            source_model = ModelFromLinesTestImpl(
                self.raw_lines,
                app_env.tmp_files_space,
            )

            yield sut.transformed_by_command(
                _to_upper_command(tmp_dir_path, self.exit_code),
                self.ignore_exit_code,
                app_env,
                source_model,
            )


class _ToUpperProgramModelConstructor(model_checker.ModelConstructor):
    def __init__(self,
                 raw_lines: Sequence[str],
                 ignore_exit_code: bool,
                 exit_code: int,
                 transformation_of_program: StringTransformer = IdentityStringTransformer()
                 ):
        self.raw_lines = raw_lines
        self.ignore_exit_code = ignore_exit_code
        self.exit_code = exit_code
        self.transformation_of_program = transformation_of_program
        self.contents = ''.join(raw_lines)

    @contextmanager
    def new_with(self, app_env: ApplicationEnvironment) -> ContextManager[StringModel]:
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            tmp_dir_path = Path(tmp_dir_name)

            source_model = ModelFromLinesTestImpl(
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
            StdinData(()),
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
