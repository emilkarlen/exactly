import pathlib

import exactly_lib.instructions.assert_.contents
import exactly_lib.instructions.assert_.utils.contents_utils
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.help.concepts.contents_structure import ConceptDocumentation
from exactly_lib.help.concepts.plain_concepts.environment_variable import ENVIRONMENT_VARIABLE_CONCEPT
from exactly_lib.instructions.assert_.utils.contents_utils import ActualFileTransformer, \
    with_replaced_env_vars_help
from exactly_lib.instructions.utils.arg_parse import parse_here_doc_or_file_ref
from exactly_lib.instructions.utils.arg_parse.parse_utils import split_arguments_list_string
from exactly_lib.instructions.utils.documentation import documentation_text as dt
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_opts
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, \
    SingleInstructionInvalidArgumentException, SingleInstructionParserSource
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.util.cli_syntax.elements import argument as a
from .utils import contents_utils
from .utils import contents_utils_for_instr_doc as doc_utils


def setup_for_stdout(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        ParserForContentsForStdout(),
        TheInstructionDocumentation(instruction_name, 'stdout'))


def setup_for_stderr(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        ParserForContentsForStderr(),
        TheInstructionDocumentation(instruction_name, 'stderr'))


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self, name: str,
                 name_of_checked_file: str):
        self.file_arg = a.Named(parse_here_doc_or_file_ref.CONFIGURATION.argument_syntax_name)
        super().__init__(name, {
            'checked_file': name_of_checked_file,
            'FILE_ARG': self.file_arg.name,
        })
        self.checked_file = name_of_checked_file
        self.with_replaced_env_vars_option = a.Option(contents_utils.WITH_REPLACED_ENV_VARS_OPTION_NAME)

    def single_line_description(self) -> str:
        return self._format('Tests the contents of {checked_file}')

    def main_description_rest(self) -> list:
        return rel_opts.default_relativity_for_rel_opt_type(self.file_arg.name,
                                                            parse_here_doc_or_file_ref.CONFIGURATION.default_option)

    def invokation_variants(self) -> list:
        mandatory_empty_arg = a.Single(a.Multiplicity.MANDATORY,
                                       doc_utils.EMPTY_ARGUMENT_CONSTANT)
        mandatory_not_arg = a.Single(a.Multiplicity.MANDATORY,
                                     doc_utils.NOT_ARGUMENT_CONSTANT)
        mandatory_file_arg = a.Single(a.Multiplicity.MANDATORY,
                                      self.file_arg)
        optional_replace_env_vars_option = a.Single(a.Multiplicity.OPTIONAL,
                                                    self.with_replaced_env_vars_option)
        here_doc_arg = a.Single(a.Multiplicity.MANDATORY, dt.HERE_DOCUMENT)

        return [
            InvokationVariant(self._cl_syntax_for_args([mandatory_empty_arg]),
                              self._paragraphs('Asserts that {checked_file} is empty.')),
            InvokationVariant(self._cl_syntax_for_args([mandatory_not_arg, mandatory_empty_arg]),
                              self._paragraphs('Asserts that {checked_file} is not empty.')),
            InvokationVariant(self._cl_syntax_for_args([optional_replace_env_vars_option,
                                                        here_doc_arg,
                                                        ]),
                              self._paragraphs("""\
                              Asserts that the contents of {checked_file} is equal to
                              the contents of a "here document".
                              """)),
            InvokationVariant(self._cl_syntax_for_args([optional_replace_env_vars_option,
                                                        rel_opts.OPTIONAL_RELATIVITY_ARGUMENT_USAGE,
                                                        mandatory_file_arg,
                                                        ]),
                              self._paragraphs("""\
                              Asserts that the contents of {checked_file} is equal to the contents of {FILE_ARG}.
                              """)),
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            rel_opts.relativity_syntax_element_description(self.file_arg,
                                                           parse_here_doc_or_file_ref.CONFIGURATION.accepted_options,
                                                           rel_opts.RELATIVITY_ARGUMENT),
            self._cli_argument_syntax_element_description(self.with_replaced_env_vars_option,
                                                          with_replaced_env_vars_help(self.checked_file)),
            dt.here_document_syntax_element_description(self.instruction_name(),
                                                        dt.HERE_DOCUMENT),
        ]

    def see_also(self) -> list:
        concepts = rel_opts.see_also_concepts(parse_here_doc_or_file_ref.CONFIGURATION.accepted_options)
        if ENVIRONMENT_VARIABLE_CONCEPT not in concepts:
            concepts.append(ENVIRONMENT_VARIABLE_CONCEPT)
        return list(map(ConceptDocumentation.cross_reference_target, concepts))


_WITH_REPLACED_ENV_VARS_STEM_SUFFIX = '-with-replaced-env-vars.txt'


class ParserForContentsForActualValue(SingleInstructionParser):
    def __init__(self,
                 comparison_actual_value: exactly_lib.instructions.assert_.utils.contents_utils.ComparisonActualFile,
                 actual_value_transformer: ActualFileTransformer):
        self.comparison_actual_value = comparison_actual_value
        self.target_transformer = actual_value_transformer

    def apply(self, source: SingleInstructionParserSource) -> AssertPhaseInstruction:
        arguments = split_arguments_list_string(source.instruction_argument)
        content_instruction = contents_utils.try_parse_content(self.comparison_actual_value,
                                                               self.target_transformer,
                                                               arguments,
                                                               source)
        if content_instruction is None:
            raise SingleInstructionInvalidArgumentException(str(arguments))
        return content_instruction


class ParserForContentsForStdout(ParserForContentsForActualValue):
    def __init__(self):
        super().__init__(contents_utils.StdoutComparisonTarget(),
                         _StdXActualFileTransformerBase())


class ParserForContentsForStderr(ParserForContentsForActualValue):
    def __init__(self):
        super().__init__(contents_utils.StderrComparisonTarget(),
                         _StdXActualFileTransformerBase())


class _StdXActualFileTransformerBase(ActualFileTransformer):
    def _dst_file_path(self,
                       environment: InstructionEnvironmentForPostSdsStep,
                       src_file_path: pathlib.Path) -> pathlib.Path:
        src_stem_name = src_file_path.stem
        directory = src_file_path.parent
        dst_base_name = src_stem_name + _WITH_REPLACED_ENV_VARS_STEM_SUFFIX
        return directory / dst_base_name
