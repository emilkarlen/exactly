from exactly_lib.instructions.utils.arg_parse import parse_file_ref
from exactly_lib.instructions.utils.arg_parse import parse_here_document
from exactly_lib.instructions.utils.arg_parse.parse_here_document import HereDocumentContentsParsingException
from exactly_lib.instructions.utils.arg_parse.rel_opts_configuration import RelOptionArgumentConfiguration
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.concrete_values import FileRefResolver

CONFIGURATION = parse_file_ref.ALL_REL_OPTIONS_CONFIG


class HereDocOrFileRef(tuple):
    def __new__(cls,
                here_document: list,
                file_reference: FileRefResolver):
        return tuple.__new__(cls, (here_document, file_reference))

    @property
    def is_here_document(self) -> bool:
        return self.here_document is not None

    @property
    def is_file_ref(self) -> bool:
        return not self.is_here_document

    @property
    def here_document(self) -> list:
        return self[0]

    @property
    def file_reference_resolver(self) -> FileRefResolver:
        return self[1]


def parse_from_parse_source(source: ParseSource,
                            conf: RelOptionArgumentConfiguration = CONFIGURATION) -> HereDocOrFileRef:
    try:
        copy_of_source = source.copy
        here_doc = parse_here_document.parse_as_last_argument(False, copy_of_source)
        source.catch_up_with(copy_of_source)
        source.consume_current_line()
        return HereDocOrFileRef(here_doc, None)
    except HereDocumentContentsParsingException as ex:
        raise ex
    except SingleInstructionInvalidArgumentException:
        try:
            file_reference = parse_file_ref.parse_file_ref_from_parse_source(source, conf)
            return HereDocOrFileRef(None, file_reference)
        except SingleInstructionInvalidArgumentException:
            msg = 'Neither a "here document" nor a file reference: {}'.format(source.remaining_part_of_current_line)
            raise SingleInstructionInvalidArgumentException(msg)
