from exactly_lib.common.report_rendering import text_doc
from exactly_lib.common.report_rendering.text_doc import TraceDoc


def of_pre_formatted_text(text: str,
                          is_line_ended: bool = False) -> TraceDoc:
    return text_doc.PreFormattedDoc(text, is_line_ended)
