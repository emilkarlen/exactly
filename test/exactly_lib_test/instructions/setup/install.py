import unittest

from exactly_lib.instructions.setup import install as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType
from exactly_lib_test.instructions.setup.test_resources.instruction_check import TestCaseBase, Arrangement, \
    Expectation
from exactly_lib_test.instructions.test_resources.assertion_utils import sh_check, svh_check
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants, \
    equivalent_source_variants__with_source_check
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_contents_check as sds_contents_check
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_resources.file_structure import DirContents, File, Dir, empty_file, empty_dir


class TestParse(unittest.TestCase):
    def test_fail_when_there_is_no_arguments(self):
        instruction_argument = ''
        for source in equivalent_source_variants(self, instruction_argument):
            with self.assertRaises(SingleInstructionInvalidArgumentException):
                sut.Parser().parse(source)

    def test_fail_when_there_is_more_than_two_arguments(self):
        instruction_argument = 'argument1 argument2 argument3'
        for source in equivalent_source_variants(self, instruction_argument):
            with self.assertRaises(SingleInstructionInvalidArgumentException):
                sut.Parser().parse(source)

    def test_succeed_when_there_is_exactly_one_argument(self):
        instruction_argument = 'single-argument'
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            sut.Parser().parse(source)

    def test_succeed_when_there_is_exactly_two_arguments(self):
        instruction_argument = 'argument1 argument2'
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            sut.Parser().parse(source)

    def test_argument_shall_be_parsed_using_shell_syntax(self):
        instruction_argument = "'argument 1' 'argument 2'"
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            sut.Parser().parse(source)


class TestCaseBaseForParser(TestCaseBase):
    def _run(self,
             instruction_argument: str,
             arrangement: Arrangement,
             expectation: Expectation):
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            self._check(sut.Parser(), source, arrangement, expectation)


class TestValidationErrorScenarios(TestCaseBaseForParser):
    def test_ERROR_when_file_does_not_exist__without_explicit_destination(self):
        self._run('source-that-do-not-exist',
                  Arrangement(),
                  Expectation(pre_validation_result=svh_check.is_validation_error()))

    def test_ERROR_when_file_does_not_exist__with_explicit_destination(self):
        self._run('source-that-do-not-exist destination',
                  Arrangement(),
                  Expectation(pre_validation_result=svh_check.is_validation_error()))


class TestSuccessfulScenarios(TestCaseBaseForParser):
    def test_install_file__without_explicit_destination(self):
        file_name = 'existing-file'
        file_to_install = DirContents([(File(file_name,
                                             'contents'))])
        self._run(file_name,
                  Arrangement(home_dir_contents=file_to_install),
                  Expectation(main_side_effects_on_files=sds_contents_check.act_dir_contains_exactly(
                      file_to_install))
                  )

    def test_install_file__with_explicit_destination__non_existing_file(self):
        src = 'src-file'
        dst = 'dst-file'
        self._run('{} {}'.format(src, dst),
                  Arrangement(home_dir_contents=DirContents([(File(src,
                                                                   'contents'))])),
                  Expectation(
                      main_side_effects_on_files=sds_contents_check.act_dir_contains_exactly(
                          DirContents([(File(dst,
                                             'contents'))])))
                  )

    def test_install_file__with_explicit_destination__existing_directory(self):
        src = 'src-file'
        dst = 'dst-dir'
        file_to_install = File(src, 'contents')
        home_dir_contents = [file_to_install]
        act_dir_contents = [empty_dir(dst)]
        act_dir_contents_after = [Dir(dst, [file_to_install])]
        self._run('{} {}'.format(src, dst),
                  Arrangement(
                      home_dir_contents=DirContents(home_dir_contents),
                      sds_contents_before_main=sds_populator.contents_in(RelSdsOptionType.REL_ACT,
                                                                         DirContents(act_dir_contents))),
                  Expectation(
                      main_side_effects_on_files=sds_contents_check.act_dir_contains_exactly(
                          DirContents(act_dir_contents_after)))
                  )

    def test_install_directory__without_explicit_destination(self):
        src_dir = 'existing-dir'
        files_to_install = DirContents([Dir(src_dir,
                                            [File('a', 'a'),
                                             Dir('d', []),
                                             Dir('d2',
                                                 [File('f', 'f')])
                                             ])])
        self._run(src_dir,
                  Arrangement(home_dir_contents=files_to_install),
                  Expectation(main_side_effects_on_files=sds_contents_check.act_dir_contains_exactly(
                      files_to_install))
                  )

    def test_install_directory__with_explicit_destination__existing_directory(self):
        src_dir = 'existing-dir'
        dst_dir = 'existing-dst-dir'
        files_to_install = [Dir(src_dir,
                                [File('a', 'a'),
                                 Dir('d', []),
                                 Dir('d2',
                                     [File('f', 'f')])
                                 ])]
        act_dir_contents_before = DirContents([empty_dir(dst_dir)])
        act_dir_contents_after = DirContents([Dir(dst_dir, files_to_install)])
        self._run('{} {}'.format(src_dir, dst_dir),
                  Arrangement(
                      home_dir_contents=DirContents(files_to_install),
                      sds_contents_before_main=sds_populator.contents_in(RelSdsOptionType.REL_ACT,
                                                                         act_dir_contents_before)),
                  Expectation(
                      main_side_effects_on_files=sds_contents_check.act_dir_contains_exactly(
                          act_dir_contents_after))
                  )


class TestFailingScenarios(TestCaseBaseForParser):
    def test_destination_already_exists__without_explicit_destination(self):
        file_name = 'existing-file'
        file_to_install = DirContents([(File(file_name,
                                             'contents'))])
        self._run(file_name,
                  Arrangement(
                      home_dir_contents=file_to_install,
                      sds_contents_before_main=sds_populator.contents_in(RelSdsOptionType.REL_ACT,
                                                                         DirContents(
                                                                             [empty_file(file_name)]))),
                  Expectation(
                      main_result=sh_check.is_hard_error())
                  )

    def test_destination_already_exists__with_explicit_destination(self):
        src = 'src-file-name'
        dst = 'dst-file-name'
        home_dir_contents = DirContents([(empty_file(src))])
        act_dir_contents = DirContents([empty_file(dst)])
        self._run('{} {}'.format(src, dst),
                  Arrangement(
                      home_dir_contents=home_dir_contents,
                      sds_contents_before_main=sds_populator.contents_in(RelSdsOptionType.REL_ACT,
                                                                         act_dir_contents)
                  ),
                  Expectation(
                      main_result=sh_check.is_hard_error()
                  )
                  )

    def test_destination_already_exists_in_destination_directory(self):
        src = 'src-file-name'
        dst = 'dst-dir-name'
        home_dir_contents = DirContents([(empty_file(src))])
        act_dir_contents = DirContents([Dir(dst,
                                            [empty_file(src)])])
        self._run('{} {}'.format(src, dst),
                  Arrangement(
                      home_dir_contents=home_dir_contents,
                      sds_contents_before_main=sds_populator.contents_in(RelSdsOptionType.REL_ACT,
                                                                         act_dir_contents)),
                  Expectation(
                      main_result=sh_check.is_hard_error())
                  )


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParse),
        unittest.makeSuite(TestValidationErrorScenarios),
        unittest.makeSuite(TestFailingScenarios),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


if __name__ == '__main__':
    unittest.main()
