import pathlib

from exactly_lib.section_document import model
from exactly_lib.section_document.parsing_configuration import SectionsConfiguration, DocumentParser
from .impl import document_parser as _impl


def new_parser_for(configuration: SectionsConfiguration) -> DocumentParser:
    return _impl.DocumentParserForSectionsConfiguration(configuration)


def parse(configuration: SectionsConfiguration,
          source_file_path: pathlib.Path) -> model.Document:
    return _impl.parse(configuration, source_file_path)
