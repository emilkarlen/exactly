from exactly_lib.definitions.test_case import file_check_properties
from exactly_lib.impls import file_properties
from exactly_lib.impls.file_properties import FileType
from exactly_lib.impls.text_render import header_rendering
from exactly_lib.util.str_.str_constructor import ToStringObject


def unexpected_of_file_type(file_type: FileType) -> ToStringObject:
    return unexpected(file_properties.TYPE_INFO[file_type].description)


def unexpected(target: ToStringObject) -> ToStringObject:
    return header_rendering.unexpected_attr_of_obj(file_check_properties.CONTENTS,
                                                   target)
