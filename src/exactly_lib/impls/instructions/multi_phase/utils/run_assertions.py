from exactly_lib.definitions import misc_texts


def single_line_description_as_assertion(non_assertion_description: str) -> str:
    return non_assertion_description + ', and PASS iff its {} is 0'.format(misc_texts.EXIT_CODE)
