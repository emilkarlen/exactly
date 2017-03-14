import pathlib
import unittest

from exactly_lib.instructions.utils.arg_parse import parse_file_ref as sut
from exactly_lib.instructions.utils.arg_parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream2 import TokenStream2
from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.test_case_file_structure.file_ref_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.test_case_file_structure.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case_file_structure.relative_path_options import REL_CWD_OPTION, REL_TMP_OPTION
from exactly_lib_test.section_document.test_resources.parse_source import assert_source
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check.home_and_sds_utils import \
    home_and_sds_with_act_as_curr_dir
from exactly_lib_test.test_resources.parse import remaining_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()

    ret_val.addTest(unittest.makeSuite(TestParseFromTokenStream2))
    ret_val.addTest(unittest.makeSuite(TestParsesCorrectValueFromTokenStream2WithCustomConfiguration))

    ret_val.addTest(unittest.makeSuite(TestParseFromParseSource))
    ret_val.addTest(unittest.makeSuite(TestParsesCorrectValueFromParseSourceWithCustomConfiguration))
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
            sut.parse_file_ref(TokenStream2(''),
                               sut.ALL_REL_OPTIONS_CONFIG)

    def test_parse_without_option(self):
        ts = TokenStream2('FILENAME arg2')
        file_ref = sut.parse_file_ref(ts, sut.ALL_REL_OPTIONS_CONFIG)
        self.assertEquals('FILENAME',
                          file_ref.file_name)
        self.assertFalse(ts.is_null, 'is-null')
        self.assertEquals('arg2',
                          ts.head.string)

    def test_parse_with_option(self):
        ts = TokenStream2(REL_CWD_OPTION + ' FILENAME arg3 arg4')
        file_ref = sut.parse_file_ref(ts, sut.ALL_REL_OPTIONS_CONFIG)
        self.assertEquals('FILENAME',
                          file_ref.file_name)
        self.assertFalse(ts.is_null, 'is-null')
        self.assertEquals('arg3',
                          ts.head.string)

    def test_fail_when_option_is_only_argument(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref(TokenStream2(REL_CWD_OPTION), sut.ALL_REL_OPTIONS_CONFIG)


class TestParsesCorrectValueFromTokenStream2WithCustomConfiguration(TestParsesBase):
    def test_default_relativity_is_different_than_that_of_default_configuration(self):
        custom_configuration = RelOptionArgumentConfiguration(
            RelOptionsConfiguration(PathRelativityVariants({RelOptionType.REL_ACT}, True),
                                    True,
                                    RelOptionType.REL_ACT),
            'FILE')
        ts = TokenStream2('file.txt')
        file_reference = sut.parse_file_ref(ts, custom_configuration)
        with home_and_sds_with_act_as_curr_dir() as home_and_sds:
            expected_path = home_and_sds.sds.act_dir / 'file.txt'
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds)
            self.assert_is_file_that_does_not_exist_pre_sds(expected_path,
                                                            environment,
                                                            file_reference)
            self.assertTrue(ts.is_null)

    def test_WHEN_an_unsupported_option_is_used_THEN_an_exception_should_be_raised(self):
        custom_configuration = RelOptionArgumentConfiguration(
            RelOptionsConfiguration(PathRelativityVariants({RelOptionType.REL_ACT}, True),
                                    True,
                                    RelOptionType.REL_ACT),
            'FILE')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref(TokenStream2('%s file.txt' % REL_TMP_OPTION),
                               custom_configuration)


class TestParseFromParseSource(unittest.TestCase):
    def test_fail_when_no_arguments(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref_from_parse_source(remaining_source(''), sut.ALL_REL_OPTIONS_CONFIG)

    def test_parse_without_option(self):
        file_ref = sut.parse_file_ref_from_parse_source(remaining_source('FILENAME arg2'),
                                                        sut.ALL_REL_OPTIONS_CONFIG)
        self.assertEquals('FILENAME',
                          file_ref.file_name)
        assert_source(remaining_part_of_current_line=asrt.equals(' arg2'))

    def test_parse_with_option(self):
        file_ref = sut.parse_file_ref_from_parse_source(
            remaining_source(REL_CWD_OPTION + ' FILENAME arg3 arg4'),
            sut.ALL_REL_OPTIONS_CONFIG)
        self.assertEquals('FILENAME',
                          file_ref.file_name)
        assert_source(remaining_part_of_current_line=asrt.equals(' arg3 arg4'))

    def test_parse_with_initial_space(self):
        file_ref = sut.parse_file_ref_from_parse_source(
            remaining_source('   FILENAME'),
            sut.ALL_REL_OPTIONS_CONFIG)
        self.assertEquals('FILENAME',
                          file_ref.file_name)
        assert_source(is_at_eol=asrt.is_true)

    def test_fail_when_option_is_only_argument(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref_from_parse_source(remaining_source(REL_CWD_OPTION),
                                                 sut.ALL_REL_OPTIONS_CONFIG)


class TestParsesCorrectValueFromParseSourceWithCustomConfiguration(TestParsesBase):
    def test_default_relativity_is_different_than_that_of_default_configuration(self):
        custom_configuration = RelOptionArgumentConfiguration(
            RelOptionsConfiguration(PathRelativityVariants({RelOptionType.REL_ACT}, True),
                                    True,
                                    RelOptionType.REL_ACT),
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
            RelOptionsConfiguration(PathRelativityVariants({RelOptionType.REL_ACT}, True),
                                    True,
                                    RelOptionType.REL_ACT),
            'FILE')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref_from_parse_source(remaining_source('%s file.txt' % REL_TMP_OPTION),
                                                 custom_configuration)


def _remaining_source(ts: TokenStream2) -> str:
    return ts.source[ts.position:]


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
