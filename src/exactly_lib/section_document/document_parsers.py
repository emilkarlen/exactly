from pathlib import Path

from exactly_lib.section_document import model
from exactly_lib.section_document.document_parser import DocumentParser
from exactly_lib.section_document.section_parsing import SectionsConfiguration
from .impl import document_parser as _impl


def new_parser_for(configuration: SectionsConfiguration) -> DocumentParser:
    return _impl.DocumentParserForSectionsConfiguration(configuration)


def parse(configuration: SectionsConfiguration,
          source_file_path: Path) -> model.Document:
    return new_parser_for(configuration).parse_file(source_file_path)
