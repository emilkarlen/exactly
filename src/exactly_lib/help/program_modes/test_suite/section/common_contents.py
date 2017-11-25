from exactly_lib import program_info
from exactly_lib.help_texts import formatting
from exactly_lib.util.textformat.parse import normalize_and_parse


def file_ref_contents_description(case_or_suite_string: str) -> list:
    return normalize_and_parse(_TEXT.format(case=case_or_suite_string,
                                            program_name=formatting.program_name(program_info.PROGRAM_NAME)))


_TEXT = """\
Each line specifies zero or more test {case}s to include in the suite,
by giving the names of files that contain individual test {case}s.


File names are relative the location of the test suite file.


A test {case} file can have any name - {program_name} does not put any restriction on file names.


Each line consists of a single file name glob pattern:


```
file.{case}
*.{case}
**/the.{case}
**/test-{case}s/*.{case}
```
"""
