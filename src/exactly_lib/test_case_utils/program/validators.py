import stat
from typing import Optional

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case_utils.err_msg2.described_path import DescribedPathPrimitive
from exactly_lib.test_case_utils.file_ref_validator import FileRefValidatorBase
from exactly_lib.util.simple_textstruct.rendering import strings


class ExistingExecutableFileValidator(FileRefValidatorBase):
    def _validate_path(self, path: DescribedPathPrimitive) -> Optional[TextRenderer]:
        file_path = path.primitive
        if not file_path.is_file():
            return text_docs.single_line(
                strings.FormatPositional('File does not exist: {}', file_path)
            )
        stat_value = file_path.stat()
        mode = stat_value.st_mode
        if not mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
            return text_docs.single_line(
                strings.FormatPositional('File is not executable. Mode is {}: {}',
                                         stat.filemode(mode),
                                         file_path)
            )
        return None
