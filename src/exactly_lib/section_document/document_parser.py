from pathlib import Path
from typing import Optional

from exactly_lib.section_document import model
from exactly_lib.section_document.parse_source import ParseSource


class DocumentParser:
    """
    Base class for parsers that parse a "plain file"
    (i.e., a file that do not need pre-processing).
    """

    def parse(self,
              source_file_path: Optional[Path],
              file_reference_relativity_root_dir: Path,
              source: ParseSource) -> model.Document:
        """
        :param source_file_path: None iff the source is not a file - e.g. stdin.
        :param file_reference_relativity_root_dir: A directory that file reference paths are relative to.
        :param source: The source to parse - the contents of source_file_path, if the source is from a file.
        :raises ParseError The test case cannot be parsed.
        """
        raise NotImplementedError('abstract method')
