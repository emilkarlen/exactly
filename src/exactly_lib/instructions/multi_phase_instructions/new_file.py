from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.argument_rendering import path_syntax
from exactly_lib.help_texts.concepts import CURRENT_WORKING_DIRECTORY_CONCEPT_INFO
from exactly_lib.instructions.multi_phase_instructions.utils import instruction_embryo as embryo
from exactly_lib.instructions.multi_phase_instructions.utils.instruction_part_utils import PartsParserFromEmbryoParser, \
    MainStepResultTranslatorForErrorMessageStringResult
from exactly_lib.instructions.utils.documentation import documentation_text as dt
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.named_element.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.named_element.symbol import string_resolver
from exactly_lib.named_element.symbol.path_resolver import FileRefResolver
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, PhaseLoggingPaths
from exactly_lib.test_case_utils.parse import parse_here_document
from exactly_lib.test_case_utils.parse.parse_file_ref import parse_file_ref_from_parse_source
from exactly_lib.test_case_utils.parse.rel_opts_configuration import argument_configuration_for_file_creation, \
    RELATIVITY_VARIANTS_FOR_FILE_CREATION
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.file_utils import ensure_parent_directory_does_exist_and_is_a_directory, write_new_text_file
from exactly_lib.util.textformat.structure import structures as docs


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self, name: str):
        super().__init__(name, {})

    def single_line_description(self) -> str:
        return 'Creates a file'

    def main_description_rest(self) -> list:
        return (
            rel_path_doc.default_relativity_for_rel_opt_type(_PATH_ARGUMENT.name,
                                                             REL_OPT_ARG_CONF.options.default_option) +
            dt.paths_uses_posix_syntax())

    def invokation_variants(self) -> list:
        arguments = path_syntax.mandatory_path_with_optional_relativity(
            _PATH_ARGUMENT,
            REL_OPT_ARG_CONF.path_suffix_is_required)
        here_doc_arg = a.Single(a.Multiplicity.MANDATORY,
                                instruction_arguments.HERE_DOCUMENT)
        return [
            InvokationVariant(self._cl_syntax_for_args(arguments),
                              docs.paras('Creates an empty file.')),
            InvokationVariant(self._cl_syntax_for_args(arguments + [here_doc_arg]),
                              docs.paras('Creates a file with contents given by a "here document".')),
        ]

    def syntax_element_descriptions(self) -> list:
        return rel_path_doc.relativity_syntax_element_descriptions(_PATH_ARGUMENT,
                                                                   REL_OPT_ARG_CONF.options) + \
               [
                   dt.here_document_syntax_element_description(self.instruction_name(),
                                                               instruction_arguments.HERE_DOCUMENT),
               ]

    def _see_also_cross_refs(self) -> list:
        concepts = rel_path_doc.see_also_concepts(REL_OPT_ARG_CONF.options)
        rel_path_doc.add_concepts_if_not_listed(concepts, [CURRENT_WORKING_DIRECTORY_CONCEPT_INFO])
        return [concept.cross_reference_target for concept in concepts]


class FileInfo(tuple):
    def __new__(cls,
                path_resolver: FileRefResolver,
                contents: string_resolver.StringResolver):
        return tuple.__new__(cls, (path_resolver, contents))

    @property
    def file_ref(self) -> FileRefResolver:
        return self[0]

    @property
    def contents(self) -> string_resolver.StringResolver:
        return self[1]

    @property
    def references(self) -> list:
        return self.file_ref.references + self.contents.references


class TheInstructionEmbryo(embryo.InstructionEmbryo):
    def __init__(self, file_info: FileInfo):
        self.file_info = file_info

    @property
    def symbol_usages(self) -> list:
        return self.file_info.references

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             logging_paths: PhaseLoggingPaths,
             os_services: OsServices):
        return self.custom_main(environment.path_resolving_environment_pre_or_post_sds)

    def custom_main(self, environment: PathResolvingEnvironmentPreOrPostSds) -> str:
        return create_file(self.file_info, environment)


class EmbryoParser(embryo.InstructionEmbryoParser):
    def parse(self, source: ParseSource) -> TheInstructionEmbryo:
        file_ref = parse_file_ref_from_parse_source(source, REL_OPT_ARG_CONF)
        contents = string_resolver.string_constant('')
        if source.is_at_eol__except_for_space:
            source.consume_current_line()
        else:
            contents = parse_here_document.parse_as_last_argument(False, source)
        file_info = FileInfo(file_ref, contents)
        return TheInstructionEmbryo(file_info)


PARTS_PARSER = PartsParserFromEmbryoParser(EmbryoParser(),
                                           MainStepResultTranslatorForErrorMessageStringResult())


def create_file(file_info: FileInfo,
                environment: PathResolvingEnvironmentPreOrPostSds) -> str:
    """
    :return: None iff success. Otherwise an error message.
    """
    file_path = file_info.file_ref.resolve(environment.symbols).value_post_sds(environment.sds)
    try:
        if file_path.exists():
            return 'File does already exist: {}'.format(file_path)
    except NotADirectoryError:
        return 'Part of path exists, but perhaps one in-the-middle-component is not a directory: %s' % str(file_path)
    failure_message = ensure_parent_directory_does_exist_and_is_a_directory(file_path)
    if failure_message is not None:
        return failure_message
    contents_str = file_info.contents.resolve_value_of_any_dependency(environment)
    try:
        write_new_text_file(file_path, contents_str)
    except IOError:
        return 'Cannot create file: {}'.format(file_path)
    return None


_PATH_ARGUMENT = instruction_arguments.PATH_ARGUMENT

RELATIVITY_VARIANTS = RELATIVITY_VARIANTS_FOR_FILE_CREATION

REL_OPT_ARG_CONF = argument_configuration_for_file_creation(_PATH_ARGUMENT.name)
