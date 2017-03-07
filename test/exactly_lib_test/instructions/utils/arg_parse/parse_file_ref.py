import pathlib
import sys
import unittest

from exactly_lib.instructions.utils.arg_parse import parse_file_ref as sut
from exactly_lib.instructions.utils.arg_parse import relative_path_options as rel_opts
from exactly_lib.instructions.utils.arg_parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.instructions.utils.arg_parse.relative_path_options import REL_CWD_OPTION, REL_HOME_OPTION, \
    REL_TMP_OPTION
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream2 import TokenStream2
from exactly_lib.test_case.file_ref import FileRef
from exactly_lib.test_case.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib_test.section_document.test_resources.parse_source import assert_source
from exactly_lib_test.test_resources import quoting
from exactly_lib_test.test_resources.execution.home_and_sds_check.home_and_sds_utils import \
    home_and_sds_with_act_as_curr_dir
from exactly_lib_test.test_resources.execution.sds_check.sds_populator import act_dir_contents
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file
from exactly_lib_test.test_resources.parse import remaining_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    # TODO [instr-desc] Remove when new parser structures are fully integrated END
    ret_val.addTest(unittest.makeSuite(TestParseFromTokenStream2))
    ret_val.addTest(unittest.makeSuite(TestParsesCorrectValueFromTokenStream2WithCustomConfiguration))
    ret_val.addTest(unittest.makeSuite(TestParsesCorrectValueFromTokenStream2WithDefaultConfiguration))
    # TODO [instr-desc] Remove when new parser structures are fully integrated END
    ret_val.addTest(unittest.makeSuite(TestParseFromParseSource))
    ret_val.addTest(unittest.makeSuite(TestParsesCorrectValueFromParseSourceWithCustomConfiguration))
    ret_val.addTest(unittest.makeSuite(TestParsesCorrectValueFromParseSourceWithDefaultConfiguration))
    return ret_val


class TestParsesBase(unittest.TestCase):
    def assert_is_file_that_exists_pre_sds(self,
                                           expected_path: pathlib.Path,
                                           environment: PathResolvingEnvironmentPreOrPostSds,
                                           actual: FileRef):
        self.assertTrue(actual.exists_pre_sds(environment.value_definitions))
        self.assertEqual(actual.file_path_pre_sds(environment),
                         expected_path)
        self.assertEqual(actual.file_path_pre_or_post_sds(environment),
                         expected_path)

    def assert_is_file_that_does_not_exist_pre_sds(self,
                                                   expected_path: pathlib.Path,
                                                   environment: PathResolvingEnvironmentPreOrPostSds,
                                                   actual: FileRef):
        self.assertFalse(actual.exists_pre_sds(environment.value_definitions))
        self.assertEqual(actual.file_path_post_sds(environment),
                         expected_path)
        self.assertEqual(actual.file_path_pre_or_post_sds(environment),
                         expected_path)


class TestParseFromTokenStream2(unittest.TestCase):
    def test_fail_when_no_arguments(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref(TokenStream2(''))

    def test_parse_without_option(self):
        ts = TokenStream2('FILENAME arg2')
        file_ref = sut.parse_file_ref(ts)
        self.assertEquals('FILENAME',
                          file_ref.file_name)
        self.assertFalse(ts.is_null, 'is-null')
        self.assertEquals('arg2',
                          ts.head.string)

    def test_parse_with_option(self):
        ts = TokenStream2(REL_CWD_OPTION + ' FILENAME arg3 arg4')
        file_ref = sut.parse_file_ref(ts)
        self.assertEquals('FILENAME',
                          file_ref.file_name)
        self.assertFalse(ts.is_null, 'is-null')
        self.assertEquals('arg3',
                          ts.head.string)

    def test_fail_when_option_is_only_argument(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref(TokenStream2(REL_CWD_OPTION))


class TestParsesCorrectValueFromTokenStream2WithCustomConfiguration(TestParsesBase):
    def test_default_relativity_is_different_than_that_of_default_configuration(self):
        custom_configuration = RelOptionArgumentConfiguration(
            RelOptionsConfiguration({rel_opts.RelOptionType.REL_ACT},
                                    rel_opts.RelOptionType.REL_ACT),
            'FILE')
        ts = TokenStream2('file.txt')
        file_reference = sut.parse_file_ref(ts,
                                            custom_configuration)
        with home_and_sds_with_act_as_curr_dir() as home_and_sds:
            expected_path = home_and_sds.sds.act_dir / 'file.txt'
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds)
            self.assert_is_file_that_does_not_exist_pre_sds(expected_path,
                                                            environment,
                                                            file_reference)
            self.assertTrue(ts.is_null)

    def test_WHEN_an_unsupported_option_is_used_THEN_an_exception_should_be_raised(self):
        custom_configuration = RelOptionArgumentConfiguration(
            RelOptionsConfiguration({rel_opts.RelOptionType.REL_ACT},
                                    rel_opts.RelOptionType.REL_ACT),
            'FILE')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref(TokenStream2('%s file.txt' % REL_TMP_OPTION),
                               custom_configuration)


class TestParsesCorrectValueFromTokenStream2WithDefaultConfiguration(TestParsesBase):
    def test_rel_home(self):
        ts = TokenStream2('%s file.txt' % REL_HOME_OPTION)
        file_reference = sut.parse_file_ref(ts)
        with home_and_sds_with_act_as_curr_dir() as home_and_sds:
            expected_path = home_and_sds.home_dir_path / 'file.txt'
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds)
            self.assert_is_file_that_exists_pre_sds(expected_path,
                                                    environment,
                                                    file_reference)
            self.assertTrue(ts.is_null)

    def test_rel_cwd(self):
        ts = TokenStream2('%s file.txt' % REL_CWD_OPTION)
        file_reference = sut.parse_file_ref(ts)
        with home_and_sds_with_act_as_curr_dir(
                sds_contents=act_dir_contents(DirContents([empty_file('file.txt')]))) as home_and_sds:
            expected_path = home_and_sds.sds.act_dir / 'file.txt'
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds)
            self.assert_is_file_that_does_not_exist_pre_sds(expected_path,
                                                            environment,
                                                            file_reference)
            self.assertTrue(ts.is_null)

    def test_rel_tmp(self):
        ts = TokenStream2('%s file.txt' % REL_TMP_OPTION)
        file_reference = sut.parse_file_ref(ts)
        with home_and_sds_with_act_as_curr_dir() as home_and_sds:
            expected_path = home_and_sds.sds.tmp.user_dir / 'file.txt'
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds)
            self.assert_is_file_that_does_not_exist_pre_sds(expected_path,
                                                            environment,
                                                            file_reference)
            self.assertTrue(ts.is_null)

    def test_absolute(self):
        abs_path = pathlib.Path(sys.executable)
        abs_path_str_source = quoting.file_name(str(abs_path))
        ts = TokenStream2(abs_path_str_source)
        file_reference = sut.parse_file_ref(ts)
        with home_and_sds_with_act_as_curr_dir() as home_and_sds:
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds)
            self.assert_is_file_that_exists_pre_sds(abs_path,
                                                    environment,
                                                    file_reference)
            self.assertTrue(ts.is_null)

    def test_rel_home_is_default(self):
        ts = TokenStream2('file.txt')
        file_reference = sut.parse_file_ref(ts)
        with home_and_sds_with_act_as_curr_dir() as home_and_sds:
            expected_path = home_and_sds.home_dir_path / 'file.txt'
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds)
            self.assert_is_file_that_exists_pre_sds(expected_path,
                                                    environment,
                                                    file_reference)
            self.assertTrue(ts.is_null)


class TestParseFromParseSource(unittest.TestCase):
    def test_fail_when_no_arguments(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref_from_parse_source(remaining_source(''))

    def test_parse_without_option(self):
        file_ref = sut.parse_file_ref_from_parse_source(remaining_source('FILENAME arg2'))
        self.assertEquals('FILENAME',
                          file_ref.file_name)
        assert_source(remaining_part_of_current_line=asrt.equals(' arg2'))

    def test_parse_with_option(self):
        file_ref = sut.parse_file_ref_from_parse_source(
            remaining_source(REL_CWD_OPTION + ' FILENAME arg3 arg4'))
        self.assertEquals('FILENAME',
                          file_ref.file_name)
        assert_source(remaining_part_of_current_line=asrt.equals(' arg3 arg4'))

    def test_parse_with_initial_space(self):
        file_ref = sut.parse_file_ref_from_parse_source(
            remaining_source('   FILENAME'))
        self.assertEquals('FILENAME',
                          file_ref.file_name)
        assert_source(is_at_eol=asrt.is_true)

    def test_fail_when_option_is_only_argument(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref_from_parse_source(remaining_source(REL_CWD_OPTION))


class TestParsesCorrectValueFromParseSourceWithCustomConfiguration(TestParsesBase):
    def test_default_relativity_is_different_than_that_of_default_configuration(self):
        custom_configuration = RelOptionArgumentConfiguration(
            RelOptionsConfiguration({rel_opts.RelOptionType.REL_ACT},
                                    rel_opts.RelOptionType.REL_ACT),
            'FILE')
        file_reference = sut.parse_file_ref_from_parse_source(remaining_source('file.txt'),
                                                              custom_configuration)
        with home_and_sds_with_act_as_curr_dir() as home_and_sds:
            expected_path = home_and_sds.sds.act_dir / 'file.txt'
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds)
            self.assert_is_file_that_does_not_exist_pre_sds(expected_path,
                                                            environment,
                                                            file_reference)

    def test_WHEN_an_unsupported_option_is_used_THEN_an_exception_should_be_raised(self):
        custom_configuration = RelOptionArgumentConfiguration(
            RelOptionsConfiguration({rel_opts.RelOptionType.REL_ACT},
                                    rel_opts.RelOptionType.REL_ACT),
            'FILE')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref_from_parse_source(remaining_source('%s file.txt' % REL_TMP_OPTION),
                                                 custom_configuration)


class TestParsesCorrectValueFromParseSourceWithDefaultConfiguration(TestParsesBase):
    def test_rel_home(self):
        file_reference = sut.parse_file_ref_from_parse_source(remaining_source('%s file.txt' % REL_HOME_OPTION))
        with home_and_sds_with_act_as_curr_dir() as home_and_sds:
            expected_path = home_and_sds.home_dir_path / 'file.txt'
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds)
            self.assert_is_file_that_exists_pre_sds(expected_path,
                                                    environment,
                                                    file_reference)

    def test_rel_cwd(self):
        file_reference = sut.parse_file_ref_from_parse_source(remaining_source('%s file.txt' % REL_CWD_OPTION))
        with home_and_sds_with_act_as_curr_dir(
                sds_contents=act_dir_contents(DirContents([empty_file('file.txt')]))) as home_and_sds:
            expected_path = home_and_sds.sds.act_dir / 'file.txt'
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds)
            self.assert_is_file_that_does_not_exist_pre_sds(expected_path,
                                                            environment,
                                                            file_reference)

    def test_rel_tmp(self):
        file_reference = sut.parse_file_ref_from_parse_source(remaining_source('%s file.txt' % REL_TMP_OPTION))
        with home_and_sds_with_act_as_curr_dir() as home_and_sds:
            expected_path = home_and_sds.sds.tmp.user_dir / 'file.txt'
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds)
            self.assert_is_file_that_does_not_exist_pre_sds(expected_path,
                                                            environment,
                                                            file_reference)

    def test_absolute(self):
        abs_path = pathlib.Path.cwd().resolve()
        abs_path_str = str(abs_path)
        file_reference = sut.parse_file_ref_from_parse_source(remaining_source(abs_path_str))
        with home_and_sds_with_act_as_curr_dir() as home_and_sds:
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds)
            self.assert_is_file_that_exists_pre_sds(abs_path,
                                                    environment,
                                                    file_reference)

    def test_rel_home_is_default(self):
        file_reference = sut.parse_file_ref_from_parse_source(remaining_source('file.txt'))
        with home_and_sds_with_act_as_curr_dir() as home_and_sds:
            expected_path = home_and_sds.home_dir_path / 'file.txt'
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds)
            self.assert_is_file_that_exists_pre_sds(expected_path,
                                                    environment,
                                                    file_reference)


def _remaining_source(ts: TokenStream2) -> str:
    return ts.source[ts.position:]


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
