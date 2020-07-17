from exactly_lib.definitions.formatting import misc_name_with_formatting
from exactly_lib.util.str_ import name

STEP_PRE_PROCESSING = misc_name_with_formatting(
    name.a_name(name.name_with_plural_s('preprocessing')))

STEP_VALIDATION = misc_name_with_formatting(
    name.a_name(name.name_with_plural_s('validation')))

STEP_EXECUTION = misc_name_with_formatting(
    name.an_name(name.name_with_plural_s('execution')))
