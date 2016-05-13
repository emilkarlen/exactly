import pathlib

from exactly_lib.common.instruction_documentation import InvokationVariant
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.execution.execution_directory_structure import \
    root_dir_for_non_stdout_or_stderr_files_with_replaced_env_vars, SUB_DIR_FOR_REPLACEMENT_SOURCES_UNDER_ACT_DIR, \
    SUB_DIR_FOR_REPLACEMENT_SOURCES_NOT_UNDER_ACT_DIR
from exactly_lib.help.concepts.contents_structure import ConceptDocumentation
from exactly_lib.help.concepts.plain_concepts.environment_variable import ENVIRONMENT_VARIABLE_CONCEPT
from exactly_lib.instructions.assert_.utils.contents_utils import ActualFileTransformer, with_replaced_env_vars_help, \
    ActComparisonActualFileForFileRef, ComparisonActualFile
from exactly_lib.instructions.utils.arg_parse import parse_file_ref
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
from exactly_lib.test_case.phases.common import GlobalEnvironmentForPostEdsPhase
from exactly_lib.util.cli_syntax.elements import argument as a
from .utils import contents_utils
from .utils import contents_utils_for_instr_doc as doc_utils


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(Parser(),
                                  TheInstructionDocumentation(instruction_name))


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self, name: str):
        self.expected_file_arg = a.Named(parse_here_doc_or_file_ref.CONFIGURATION.argument_syntax_name)
        self.actual_file_arg = a.Named(_ACTUAL_RELATIVITY_CONFIGURATION.argument_syntax_name)
        super().__init__(name, {
            'checked_file': self.actual_file_arg.name,
            'EXPECTED_FILE_ARG': self.expected_file_arg.name,
        })
        self.with_replaced_env_vars_option = a.Option(contents_utils.WITH_REPLACED_ENV_VARS_OPTION_NAME)

    def single_line_description(self) -> str:
        return 'Tests the contents of a file.'

    def main_description_rest(self) -> list:
        file_must_exist_paragraphs = self._paragraphs("""\
        FAILs if {checked_file} is not an existing file.""")
        default_rel_paragraphs = rel_opts.default_relativity_for_rel_opt_type(
            parse_here_doc_or_file_ref.CONFIGURATION.argument_syntax_name,
            parse_here_doc_or_file_ref.CONFIGURATION.default_option)
        return file_must_exist_paragraphs + default_rel_paragraphs

    def invokation_variants(self) -> list:
        actual_file = a.Single(a.Multiplicity.MANDATORY,
                               self.actual_file_arg)
        mandatory_empty_arg = a.Single(a.Multiplicity.MANDATORY,
                                       doc_utils.EMPTY_ARGUMENT_CONSTANT)
        mandatory_not_arg = a.Single(a.Multiplicity.MANDATORY,
                                     doc_utils.NOT_ARGUMENT_CONSTANT)
        mandatory_file_arg = a.Single(a.Multiplicity.MANDATORY,
                                      self.expected_file_arg)
        optional_replace_env_vars_option = a.Single(a.Multiplicity.OPTIONAL,
                                                    self.with_replaced_env_vars_option)
        here_doc_arg = a.Single(a.Multiplicity.MANDATORY, dt.HERE_DOCUMENT)
        return [
            InvokationVariant(self._cl_syntax_for_args([actual_file, mandatory_empty_arg]),
                              self._paragraphs('Asserts that {checked_file} is an empty file.')),
            InvokationVariant(self._cl_syntax_for_args([actual_file, mandatory_not_arg, mandatory_empty_arg]),
                              self._paragraphs('Asserts that {checked_file} is a non-empty file.')),
            InvokationVariant(self._cl_syntax_for_args([actual_file,
                                                        optional_replace_env_vars_option,
                                                        rel_opts.OPTIONAL_RELATIVITY_ARGUMENT_USAGE,
                                                        mandatory_file_arg,
                                                        ]),
                              self._paragraphs("""\
                              Asserts that the contents of {checked_file}
                              is equal to the contents of {EXPECTED_FILE_ARG}.
                              """)),
            InvokationVariant(self._cl_syntax_for_args([actual_file,
                                                        optional_replace_env_vars_option,
                                                        here_doc_arg,
                                                        ]),
                              self._paragraphs("""\
                              Asserts that the contents of {checked_file}
                              is equal to the contents of a "here document".
                              """)),
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            rel_opts.relativity_syntax_element_description(self.expected_file_arg,
                                                           parse_here_doc_or_file_ref.CONFIGURATION.accepted_options,
                                                           rel_opts.RELATIVITY_ARGUMENT),
            self._cli_argument_syntax_element_description(self.with_replaced_env_vars_option,
                                                          with_replaced_env_vars_help('the contents of ' +
                                                                                      self.actual_file_arg.name)),
            dt.here_document_syntax_element_description(self.instruction_name(),
                                                        dt.HERE_DOCUMENT),
        ]

    def see_also(self) -> list:
        concepts = rel_opts.see_also_concepts(parse_here_doc_or_file_ref.CONFIGURATION.accepted_options)
        if ENVIRONMENT_VARIABLE_CONCEPT not in concepts:
            concepts.append(ENVIRONMENT_VARIABLE_CONCEPT)
        return list(map(ConceptDocumentation.cross_reference_target, concepts))


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> AssertPhaseInstruction:
        arguments = split_arguments_list_string(source.instruction_argument)
        if not arguments:
            raise SingleInstructionInvalidArgumentException('At least one argument expected (FILE)')
        (comparison_target, remaining_arguments) = parse_actual_file_argument(arguments)
        instruction = contents_utils.try_parse_content(comparison_target,
                                                       _ActualFileTransformer(),
                                                       remaining_arguments,
                                                       source)
        return instruction


class _ActualFileTransformer(ActualFileTransformer):
    def _dst_file_path(self,
                       environment: GlobalEnvironmentForPostEdsPhase,
                       src_file_path: pathlib.Path) -> pathlib.Path:
        root_dir_path = root_dir_for_non_stdout_or_stderr_files_with_replaced_env_vars(environment.eds)
        if not src_file_path.is_absolute():
            src_file_path = pathlib.Path.cwd().resolve() / src_file_path
        src_file_path = src_file_path.resolve()
        return self._dst_file_path_for_absolute_src_path(environment,
                                                         root_dir_path,
                                                         src_file_path)

    @staticmethod
    def _dst_file_path_for_absolute_src_path(environment: GlobalEnvironmentForPostEdsPhase,
                                             root_dir_path: pathlib.Path,
                                             absolute_src_file_path: pathlib.Path) -> pathlib.Path:
        try:
            relative_act_dir = absolute_src_file_path.relative_to(environment.eds.act_dir)
            # path DOES reside under act_dir
            return root_dir_path / SUB_DIR_FOR_REPLACEMENT_SOURCES_UNDER_ACT_DIR / relative_act_dir
        except ValueError:
            # path DOES NOT reside under act_dir
            return (root_dir_path / SUB_DIR_FOR_REPLACEMENT_SOURCES_NOT_UNDER_ACT_DIR).joinpath(
                *absolute_src_file_path.parts[1:])


_ACTUAL_RELATIVITY_CONFIGURATION = parse_file_ref.Configuration(
    parse_file_ref.ALL_REL_OPTIONS_WITH_TARGETS_INSIDE_SANDBOX,
    rel_opts.RelOptionType.REL_PWD,
    'PATH')


def parse_actual_file_argument(arguments: list) -> (ComparisonActualFile, list):
    (file_ref, remaining_arguments) = parse_file_ref.parse_file_ref__list(arguments,
                                                                          _ACTUAL_RELATIVITY_CONFIGURATION)
    return ActComparisonActualFileForFileRef(file_ref), remaining_arguments
