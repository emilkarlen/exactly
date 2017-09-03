import enum

from exactly_lib.named_element.symbol.path_resolver import FileRefResolver
from exactly_lib.named_element.symbol.string_resolver import StringResolver
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_utils.parse import parse_here_document, parse_file_ref
from exactly_lib.test_case_utils.parse.parse_here_document import HereDocumentContentsParsingException
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
    try:
        copy_of_source = source.copy
        here_doc = parse_here_document.parse_as_last_argument(False, copy_of_source)
        source.catch_up_with(copy_of_source)
        if source.is_at_eol__except_for_space:
            source.consume_current_line()
        return StringResolverOrFileRef(SourceType.HERE_DOC, here_doc, None)
    except HereDocumentContentsParsingException as ex:
        raise ex
    except SingleInstructionInvalidArgumentException:
        if source.is_at_eol:
            return _raise_ex(source)
        first_argument = source.remaining_part_of_current_line.split(maxsplit=1)[0]
        if option_parsing.matches(FILE_ARGUMENT_OPTION, first_argument):
            source.consume(len(first_argument))
            source.consume_initial_space_on_current_line()
            file_reference = parse_file_ref.parse_file_ref_from_parse_source(source, conf)
            return StringResolverOrFileRef(SourceType.PATH, None, file_reference)
        else:
            return _raise_ex(source)


def _raise_ex(source: ParseSource) -> StringResolverOrFileRef:
    msg = 'Neither a "here document" nor a file reference: {}'.format(source.remaining_part_of_current_line)
    raise SingleInstructionInvalidArgumentException(msg)
