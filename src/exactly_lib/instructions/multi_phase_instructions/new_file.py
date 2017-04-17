from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.help.concepts.names_and_cross_references import CURRENT_WORKING_DIRECTORY_CONCEPT_INFO
from exactly_lib.instructions.utils.arg_parse import parse_here_document
from exactly_lib.instructions.utils.arg_parse.parse_file_ref import parse_file_ref_from_parse_source
from exactly_lib.instructions.utils.arg_parse.rel_opts_configuration import argument_configuration_for_file_creation, \
    RELATIVITY_VARIANTS_FOR_FILE_CREATION
from exactly_lib.instructions.utils.documentation import documentation_text as dt
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.concrete_values import FileRefResolver
from exactly_lib.symbol.value_resolvers.path_resolving_environment import PathResolvingEnvironmentPostSds
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.file_utils import ensure_parent_directory_does_exist_and_is_a_directory, write_new_text_file
from exactly_lib.util.string import lines_content
from exactly_lib.util.textformat.structure import structures as docs


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self, name: str, may_use_value_definitions: bool = False):
        super().__init__(name, {})
        self.may_use_value_definitions = may_use_value_definitions
        self.rel_opt_arg_conf = argument_configuration_for_file_creation(_PATH_ARGUMENT.name,
                                                                         may_use_value_definitions)

    def single_line_description(self) -> str:
        return 'Creates a file'

    def main_description_rest(self) -> list:
        return (
            rel_path_doc.default_relativity_for_rel_opt_type(_PATH_ARGUMENT.name,
                                                             self.rel_opt_arg_conf.options.default_option) +
            dt.paths_uses_posix_syntax())

    def invokation_variants(self) -> list:
        arguments = rel_path_doc.mandatory_path_with_optional_relativity(_PATH_ARGUMENT,
                                                                         self.may_use_value_definitions,
                                                                         self.rel_opt_arg_conf.path_suffix_is_required)
        here_doc_arg = a.Single(a.Multiplicity.MANDATORY, dt.HERE_DOCUMENT)
        return [
            InvokationVariant(self._cl_syntax_for_args(arguments),
                              docs.paras('Creates an empty file.')),
            InvokationVariant(self._cl_syntax_for_args(arguments + [here_doc_arg]),
                              docs.paras('Creates a file with contents given by a "here document".')),
        ]

    def syntax_element_descriptions(self) -> list:
        return rel_path_doc.relativity_syntax_element_descriptions(_PATH_ARGUMENT,
                                                                   self.rel_opt_arg_conf.options) + \
               [
                   dt.here_document_syntax_element_description(self.instruction_name(),
                                                               dt.HERE_DOCUMENT),
               ]

    def _see_also_cross_refs(self) -> list:
        concepts = rel_path_doc.see_also_concepts(self.rel_opt_arg_conf.options)
        rel_path_doc.add_concepts_if_not_listed(concepts, [CURRENT_WORKING_DIRECTORY_CONCEPT_INFO])
        return [concept.cross_reference_target for concept in concepts]


class FileInfo(tuple):
    def __new__(cls,
                path_resolver: FileRefResolver,
                contents: str):
        return tuple.__new__(cls, (path_resolver, contents))

    @property
    def file_ref(self) -> FileRefResolver:
        return self[0]

    @property
    def contents(self) -> str:
        return self[1]


def parse(source: ParseSource,
          may_use_value_definitions: bool = False) -> FileInfo:
    rel_opt_arg_conf = argument_configuration_for_file_creation(_PATH_ARGUMENT.name,
                                                                may_use_value_definitions)
    file_ref = parse_file_ref_from_parse_source(source, rel_opt_arg_conf)
    contents = ''
    if source.is_at_eol__except_for_space:
        source.consume_current_line()
    else:
        lines = parse_here_document.parse_as_last_argument(False, source)
        contents = lines_content(lines)
    return FileInfo(file_ref, contents)


def create_file(file_info: FileInfo,
                environment: PathResolvingEnvironmentPostSds) -> str:
    """
    :return: None iff success. Otherwise an error message.
    """
    file_path = file_info.file_ref.resolve(environment.value_definitions).file_path_post_sds(environment.sds)
    try:
        if file_path.exists():
            return 'File does already exist: {}'.format(file_path)
    except NotADirectoryError:
        return 'Part of path exists, but perhaps one in-the-middle-component is not a directory: %s' % str(file_path)
    failure_message = ensure_parent_directory_does_exist_and_is_a_directory(file_path)
    if failure_message is not None:
        return failure_message
    try:
        write_new_text_file(file_path, file_info.contents)
    except IOError:
        return 'Cannot create file: {}'.format(file_path)
    return None


_PATH_ARGUMENT = dt.PATH_ARGUMENT

RELATIVITY_VARIANTS = RELATIVITY_VARIANTS_FOR_FILE_CREATION
