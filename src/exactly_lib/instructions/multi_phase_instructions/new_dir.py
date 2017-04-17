from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.help.concepts.names_and_cross_references import CURRENT_WORKING_DIRECTORY_CONCEPT_INFO
from exactly_lib.instructions.utils.arg_parse.parse_file_ref import parse_file_ref
from exactly_lib.instructions.utils.arg_parse.rel_opts_configuration import argument_configuration_for_file_creation, \
    RELATIVITY_VARIANTS_FOR_FILE_CREATION
from exactly_lib.instructions.utils.documentation import documentation_text as dt
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream2 import TokenStream2
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case_file_structure.path_resolving_environment import PathResolvingEnvironmentPostSds
from exactly_lib.value_definition.concrete_values import FileRefResolver


class TheInstructionDocumentation(InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase):
    def __init__(self, name: str, may_use_value_definitions: bool = False, is_in_assert_phase: bool = False):
        super().__init__(name, {}, is_in_assert_phase)
        self.may_use_value_definitions = may_use_value_definitions
        self.path_arg = _PATH_ARGUMENT
        self.rel_opt_arg_conf = argument_configuration_for_file_creation(_PATH_ARGUMENT.name,
                                                                         may_use_value_definitions)

    def single_line_description(self) -> str:
        return self._format('Creates a directory')

    def _main_description_rest_body(self) -> list:
        text = """\
            Creates parent directories if needed.


            Does nothing if the given directory already exists.
            """
        return (self._paragraphs(text) +
                rel_path_doc.default_relativity_for_rel_opt_type(_PATH_ARGUMENT.name,
                                                                 self.rel_opt_arg_conf.options.default_option) +
                dt.paths_uses_posix_syntax())

    def invokation_variants(self) -> list:
        arguments = rel_path_doc.mandatory_path_with_optional_relativity(_PATH_ARGUMENT,
                                                                         self.may_use_value_definitions,
                                                                         self.rel_opt_arg_conf.path_suffix_is_required)
        return [
            InvokationVariant(self._cl_syntax_for_args(arguments),
                              []),
        ]

    def syntax_element_descriptions(self) -> list:
        return rel_path_doc.relativity_syntax_element_descriptions(_PATH_ARGUMENT,
                                                                   self.rel_opt_arg_conf.options)

    def _see_also_cross_refs(self) -> list:
        concepts = rel_path_doc.see_also_concepts(self.rel_opt_arg_conf.options)
        rel_path_doc.add_concepts_if_not_listed(concepts, [CURRENT_WORKING_DIRECTORY_CONCEPT_INFO])
        return [concept.cross_reference_target for concept in concepts]


def parse(argument: str,
          may_use_value_definitions: bool = False) -> FileRefResolver:
    source = TokenStream2(argument)
    rel_opt_arg_conf = argument_configuration_for_file_creation(_PATH_ARGUMENT.name, may_use_value_definitions)
    destination_path = parse_file_ref(source, rel_opt_arg_conf)

    if not source.is_null:
        raise SingleInstructionInvalidArgumentException('Superfluous arguments: ' + str(source.remaining_source))
    return destination_path


def make_dir_in_current_dir(environment: PathResolvingEnvironmentPostSds,
                            dir_path_resolver: FileRefResolver) -> str:
    """
    :return: None iff success. Otherwise an error message.
    """
    dir_path = dir_path_resolver.resolve(environment.value_definitions).file_path_post_sds(environment.sds)
    try:
        if dir_path.is_dir():
            return None
    except NotADirectoryError:
        return 'Part of path exists, but is not a directory: %s' % str(dir_path)
    try:
        dir_path.mkdir(parents=True)
    except FileExistsError:
        return 'Path exists, but is not a directory: {}'.format(dir_path)
    except NotADirectoryError:
        return 'Clash with existing file: {}'.format(dir_path)
    return None


def execute_and_return_sh(environment: PathResolvingEnvironmentPostSds,
                          dir_path_resolver: FileRefResolver) -> sh.SuccessOrHardError:
    error_message = make_dir_in_current_dir(environment, dir_path_resolver)
    return sh.new_sh_success() if error_message is None else sh.new_sh_hard_error(error_message)


_PATH_ARGUMENT = dt.PATH_ARGUMENT

RELATIVITY_VARIANTS = RELATIVITY_VARIANTS_FOR_FILE_CREATION
