import enum
import pathlib

from exactly_lib.help_texts import instruction_arguments
from exactly_lib.named_element.symbol.path_resolver import FileRefResolver
from exactly_lib.named_element.symbol.string_resolver import StringResolver
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case_utils.err_msg import diff_msg_utils
from exactly_lib.test_case_utils.err_msg.path_description import path_value_with_relativity_name_prefix
from exactly_lib.test_case_utils.parse import parse_here_document, parse_file_ref
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionArgumentConfiguration
from exactly_lib.util.cli_syntax import option_parsing
from exactly_lib.util.cli_syntax.elements import argument as a

CONFIGURATION = parse_file_ref.ALL_REL_OPTIONS_CONFIG

FILE_ARGUMENT_OPTION = a.OptionName(long_name='file')


class SourceType(enum.Enum):
    STRING = 1
    HERE_DOC = 2
    PATH = 3


class StringResolverOrFileRef(tuple):
    def __new__(cls,
                source_type: SourceType,
                string_resolver: StringResolver,
                file_reference: FileRefResolver):
        return tuple.__new__(cls, (source_type,
                                   string_resolver,
                                   file_reference,
                                   (string_resolver.references
                                    if string_resolver is not None
                                    else file_reference.references)))

    @property
    def source_type(self) -> SourceType:
        return self[0]

    @property
    def is_file_ref(self) -> bool:
        """
        Tells if the source is a path.
        If not, it is either a string or a here doc accessed via `string_resolver`
        """
        return self.source_type is SourceType.PATH

    @property
    def string_resolver(self) -> StringResolver:
        """
        :return: Not None iff :class:`SourceType` is NOT `SourceType.PATH`
        """
        return self[1]

    @property
    def file_reference_resolver(self) -> FileRefResolver:
        """
        :return: Not None iff :class:`SourceType` is `SourceType.PATH`
        """
        return self[2]

    @property
    def symbol_usages(self) -> list:
        return self[3]


def parse_from_parse_source(source: ParseSource,
                            conf: RelOptionArgumentConfiguration = CONFIGURATION) -> StringResolverOrFileRef:
    source.consume_initial_space_on_current_line()
    if source.is_at_eol:
        return _raise_ex(source)
    remaining_part_of_current_line = source.remaining_part_of_current_line
    first_argument = remaining_part_of_current_line.split(maxsplit=1)[0]
    if option_parsing.matches(FILE_ARGUMENT_OPTION, first_argument):
        source.consume(len(first_argument))
        source.consume_initial_space_on_current_line()
        file_reference = parse_file_ref.parse_file_ref_from_parse_source(source, conf)
        return StringResolverOrFileRef(SourceType.PATH, None, file_reference)
    elif first_argument.startswith(parse_here_document.DOCUMENT_MARKER_PREFIX):
        here_doc = parse_here_document.parse_as_last_argument(False, source)
        return StringResolverOrFileRef(SourceType.HERE_DOC, here_doc, None)
    else:
        string_resolver = parse_string.parse_string_resolver_from_parse_source(source)
        return StringResolverOrFileRef(SourceType.STRING, string_resolver, None)


def _raise_ex(source: ParseSource) -> StringResolverOrFileRef:
    msg = 'Neither a "here document" nor a file reference: {}'.format(source.remaining_part_of_current_line)
    raise SingleInstructionInvalidArgumentException(msg)


class ExpectedValueResolver(diff_msg_utils.ExpectedValueResolver):
    def __init__(self,
                 prefix: str,
                 expected_contents: StringResolverOrFileRef):
        self._prefix = prefix
        self.expected_contents = expected_contents

    def resolve(self, environment: i.InstructionEnvironmentForPostSdsStep) -> str:
        prefix = ''
        if self._prefix:
            prefix = self._prefix + ' '
        return prefix + self._expected_obj_description(environment)

    def _expected_obj_description(self, environment: i.InstructionEnvironmentForPostSdsStep) -> str:
        source_type = self.expected_contents.source_type
        if source_type is SourceType.HERE_DOC:
            return instruction_arguments.HERE_DOCUMENT.name
        elif source_type is SourceType.STRING:
            return instruction_arguments.STRING.name
        else:
            resolving_env = environment.path_resolving_environment_pre_or_post_sds
            path_value = self.expected_contents.file_reference_resolver.resolve(resolving_env.symbols)
            path_description = path_value_with_relativity_name_prefix(path_value,
                                                                      resolving_env.home_and_sds,
                                                                      pathlib.Path.cwd())
            return 'file ' + path_description
