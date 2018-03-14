import shlex
from typing import Dict, Any, Sequence, List


def file_name(fn: str) -> str:
    return shlex.quote(fn)


class StringFormatter:
    """
    Formats strings using str.format_map,
    using an internal format map.
    """

    def __init__(self, format_map: Dict[str, Any]):
        self._format_map = format_map

    def format(self, template_string: str, **kwargs) -> str:
        return template_string.format_map(self.format_dict(**kwargs))

    def format_strings(self, template_strings: Sequence[str], **kwargs) -> List[str]:
        format_map = self.format_dict(**kwargs)
        return [template_string.format_map(format_map)
                for template_string in template_strings]

    def format_dict(self, **kwargs) -> Dict[str, Any]:
        if kwargs:
            return dict(self._format_map, **kwargs)
        else:
            return self._format_map

    def new_with(self, **kwargs):
        return StringFormatter(dict(self._format_map, **kwargs))
