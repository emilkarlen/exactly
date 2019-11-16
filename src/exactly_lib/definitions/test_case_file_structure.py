from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.test_case.phase_names import PHASE_NAME_DICTIONARY
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType


class TcDirInfo:
    def __init__(self,
                 identifier: str,
                 informative_name: str,
                 single_line_description_str: str):
        self._single_line_description_str = single_line_description_str
        self._identifier = identifier
        self._informative_name = informative_name

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def informative_name(self) -> str:
        return self._informative_name

    @property
    def single_line_description_str(self) -> str:
        return self._single_line_description_str


_FORMAT_MAP = {
    'phase': PHASE_NAME_DICTIONARY,
    'os_process': misc_texts.OS_PROCESS_NAME.singular,
}


def _format(x: str) -> str:
    return x.format_map(_FORMAT_MAP)


HDS_CASE_INFO = TcDirInfo(
    'home',
    'home directory',
    'Default location of persistent helper files, that should probably not be modified.',
)

HDS_ACT_INFO = TcDirInfo(
    'act-home',
    'act-home directory',
    _format('Default location of files referenced from {phase[act]} phase, that should probably not be modified.'),
)

HDS_DIR_INFOS_IN_DISPLAY_ORDER = (
    HDS_ACT_INFO,
    HDS_CASE_INFO,
)

SDS_ACT_INFO = TcDirInfo(
    'act',
    'act directory',
    _format('The current directory when {phase[setup]:syntax} begins'),
)

SDS_RESULT_INFO = TcDirInfo(
    'result',
    'result directory',
    _format('Stores {os_process} outcome of {phase[act]:syntax}, '
            'so that {phase[assert]:syntax} may check it'),
)

SDS_TMP_INFO = TcDirInfo(
    'tmp',
    'tmp directory',
    'Reserved for custom helper files, used by the test case implementation',
)

SDS_DIR_INFOS_IN_DISPLAY_ORDER = (
    SDS_ACT_INFO,
    SDS_RESULT_INFO,
    SDS_TMP_INFO,
)

TD_DIR_INFO_DICT = {
    RelOptionType.REL_HDS_ACT: HDS_ACT_INFO,
    RelOptionType.REL_HDS_CASE: HDS_CASE_INFO,

    RelOptionType.REL_ACT: SDS_ACT_INFO,
    RelOptionType.REL_RESULT: SDS_RESULT_INFO,
    RelOptionType.REL_TMP: SDS_TMP_INFO,
}
