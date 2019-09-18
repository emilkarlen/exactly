import stat
from typing import Optional, Sequence

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case_utils.err_msg2 import path_err_msgs
from exactly_lib.type_system.data.described_path import DescribedPathPrimitive
from exactly_lib.test_case_utils.file_ref_validator import FileRefValidatorBase
from exactly_lib.util.simple_textstruct import structure as text_struct
from exactly_lib.util.simple_textstruct.rendering.renderer import SequenceRenderer
from exactly_lib.util.simple_textstruct.structure import LineElement


class ExistingExecutableFileValidator(FileRefValidatorBase):
    def _validate_path(self, path: DescribedPathPrimitive) -> Optional[TextRenderer]:
        file_path = path.primitive
        if not file_path.exists():
            return path_err_msgs.line_header__primitive(
                'File does not exist',
                path.describer,
            )

        if not file_path.is_file():
            return path_err_msgs.line_header__primitive(
                'File is not a regular file',
                path.describer,
            )

        stat_value = file_path.stat()
        mode = stat_value.st_mode
        if not mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
            return path_err_msgs.line_header__primitive(
                'File is not executable',
                path.describer,
                _ModeExplanationRenderer(mode),
            )
        return None


class _ModeExplanationRenderer(SequenceRenderer[LineElement]):
    def __init__(self, st_mode):
        self._st_mode = st_mode

    def render_sequence(self) -> Sequence[LineElement]:
        return [
            LineElement(text_struct.StringLineObject(
                'Mode is ' + stat.filemode(self._st_mode))
            ),
        ]
