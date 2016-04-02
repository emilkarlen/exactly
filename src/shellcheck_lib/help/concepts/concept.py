from shellcheck_lib.execution.execution_directory_structure import execution_directories
from shellcheck_lib.help.concepts.concept_structure import Name, PlainConceptDocumentation
from shellcheck_lib.help.utils.description import Description
from shellcheck_lib.util.textformat.structure import lists
from shellcheck_lib.util.textformat.structure.core import ParagraphItem
from shellcheck_lib.util.textformat.structure.structures import text


class _Sandbox(PlainConceptDocumentation):
    def __init__(self):
        super().__init__(Name('sandbox'))

    def purpose(self) -> Description:
        return Description(text(_SANDBOX_SINGLE_LINE_DESCRIPTION),
                           [directory_structure_list(execution_directories)])


SANDBOX_CONCEPT = _Sandbox()

_SANDBOX_SINGLE_LINE_DESCRIPTION = """\
The temporary directory where test cases are executed."""


def directory_structure_list(dir_with_sub_dir_list: list) -> ParagraphItem:
    items = []
    for dir_wsd in dir_with_sub_dir_list:
        sub_dirs_items = []
        if dir_wsd.sub_dirs:
            sub_dirs_items = [directory_structure_list(dir_wsd.sub_dirs)]
        items.append(lists.HeaderContentListItem(text(dir_wsd.name + '/'), sub_dirs_items))
    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.VARIABLE_LIST))
