from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.help.concepts.names_and_cross_references import CURRENT_WORKING_DIRECTORY_CONCEPT_INFO
from exactly_lib.help_texts.argument_rendering import path_syntax
from exactly_lib.instructions.multi_phase_instructions.utils.main_step_executor_for_single_method_executor import \
    MainStepExecutorForGenericMethodWithStringErrorMessage
from exactly_lib.instructions.multi_phase_instructions.utils.parser import InstructionPartsParserThatConsumesCurrentLine
from exactly_lib.instructions.utils.arg_parse.rel_opts_configuration import argument_configuration_for_file_creation
from exactly_lib.instructions.utils.documentation import documentation_text as dt
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase
from exactly_lib.instructions.utils.instruction_parts import InstructionParts
from exactly_lib.instructions.utils.pre_or_post_validation import ConstantSuccessValidator
from exactly_lib.section_document.parser_implementations.token_stream2 import TokenStream2
from exactly_lib.section_document.parser_implementations.token_stream_parse import TokenParser
from exactly_lib.symbol.concrete_values import FileRefResolver
from exactly_lib.symbol.value_resolvers.path_resolving_environment import PathResolvingEnvironmentPostSds
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, PhaseLoggingPaths


class TheInstructionDocumentation(InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase):
    def __init__(self, name: str, is_in_assert_phase: bool = False):
        super().__init__(name, {}, is_in_assert_phase)

    def single_line_description(self) -> str:
        return self._format('Creates a directory')

    def _main_description_rest_body(self) -> list:
        text = """\
            Creates parent directories if needed.


            Does nothing if the given directory already exists.
            """
        return (self._paragraphs(text) +
                rel_path_doc.default_relativity_for_rel_opt_type(_PATH_ARGUMENT.name,
                                                                 RELATIVITY_VARIANTS.options.default_option) +
                dt.paths_uses_posix_syntax())

    def invokation_variants(self) -> list:
        arguments = path_syntax.mandatory_path_with_optional_relativity(
            _PATH_ARGUMENT,
            RELATIVITY_VARIANTS.options.is_rel_symbol_option_accepted,
            RELATIVITY_VARIANTS.path_suffix_is_required)
        return [
            InvokationVariant(self._cl_syntax_for_args(arguments),
                              []),
        ]

    def syntax_element_descriptions(self) -> list:
        return rel_path_doc.relativity_syntax_element_descriptions(_PATH_ARGUMENT,
                                                                   RELATIVITY_VARIANTS.options)

    def _see_also_cross_refs(self) -> list:
        concepts = rel_path_doc.see_also_concepts(RELATIVITY_VARIANTS.options)
        rel_path_doc.add_concepts_if_not_listed(concepts, [CURRENT_WORKING_DIRECTORY_CONCEPT_INFO])
        return [concept.cross_reference_target for concept in concepts]


def parse(rest_of_line) -> FileRefResolver:
    tokens = TokenParser(TokenStream2(rest_of_line))

    target_file_ref = tokens.consume_file_ref(RELATIVITY_VARIANTS)
    tokens.report_superfluous_arguments_if_not_at_eol()
    return target_file_ref


def make_dir_in_current_dir(environment: PathResolvingEnvironmentPostSds,
                            dir_path_resolver: FileRefResolver) -> str:
    """
    :return: None iff success. Otherwise an error message.
    """
    dir_path = dir_path_resolver.resolve(environment.symbols).file_path_post_sds(environment.sds)
    try:
        if dir_path.is_dir():
            return None
    except NotADirectoryError:
        return 'Part of PATH exists, but is not a directory: %s' % str(dir_path)
    try:
        dir_path.mkdir(parents=True)
    except FileExistsError:
        return 'PATH exists, but is not a directory: {}'.format(dir_path)
    except NotADirectoryError:
        return 'Clash with existing file: {}'.format(dir_path)
    return None


class Parser(InstructionPartsParserThatConsumesCurrentLine):
    def _parse(self, rest_of_line: str) -> InstructionParts:
        target_file_ref = parse(rest_of_line)
        return InstructionParts(ConstantSuccessValidator(),
                                TheMainStepExecutor(target_file_ref),
                                symbol_usages=tuple(target_file_ref.references))


class TheMainStepExecutor(MainStepExecutorForGenericMethodWithStringErrorMessage):
    def __init__(self, target_path: FileRefResolver):
        self.target_path = target_path

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                logging_paths: PhaseLoggingPaths,
                os_services: OsServices) -> str:
        return make_dir_in_current_dir(environment.path_resolving_environment,
                                       self.target_path)


_PATH_ARGUMENT = path_syntax.PATH_ARGUMENT

RELATIVITY_VARIANTS = argument_configuration_for_file_creation(_PATH_ARGUMENT.name, True)
