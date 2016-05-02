from exactly_lib.util.textformat.parse import normalize_and_parse


def file_ref_contents_description(case_or_suite_string: str) -> list:
    return normalize_and_parse(_TEXT.format(case=case_or_suite_string))


_TEXT = """\
Each line specifies zero or more test {case}s to include in the suite,
by giving the names of files that contain individual test {case}s.


A test {case} file can have any name - exactly does not put any restriction on file names.


Each line consists of a single file name glob pattern:


```
file.{case}
*.{case}
**/the.{case}
**/test-{case}s/*.{case}
```
"""
