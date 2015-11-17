from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException, SingleInstructionParserSource
from . import file_ref
from . import parse_here_document
from . import parse_file_ref
from shellcheck_lib.instructions.utils.parse_here_document import HereDocumentContentsParsingException


class HereDocOrFileRef(tuple):
    def __new__(cls,
                here_document: list,
                file_reference: file_ref.FileRef):
        return tuple.__new__(cls, (here_document, file_reference))

    @property
    def is_here_document(self) -> bool:
        return self.here_document is not None

    @property
    def here_document(self) -> list:
        return self[0]

    @property
    def file_reference(self) -> file_ref.FileRef:
        return self[1]


def parse(first_line_arguments: list,
          source: SingleInstructionParserSource) -> (HereDocOrFileRef, list):
    try:
        here_doc = parse_here_document.parse_as_last_argument(False, first_line_arguments, source)
        return HereDocOrFileRef(here_doc, None), []
    except HereDocumentContentsParsingException as ex:
        raise ex
    except SingleInstructionInvalidArgumentException:
        try:
            (file_reference, remaining_arguments) = parse_file_ref.parse_relative_file_argument(first_line_arguments)
            return HereDocOrFileRef(None, file_reference), remaining_arguments
        except SingleInstructionInvalidArgumentException:
            msg = 'Neither Here Document or File Reference: {}'.format(first_line_arguments)
            raise SingleInstructionInvalidArgumentException(msg)
