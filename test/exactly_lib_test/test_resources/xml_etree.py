from typing import Optional, Dict, Sequence
from xml.etree import ElementTree as ET


def element(tag: str,
            attributes: Optional[Dict[str, str]] = None,
            text: Optional[str] = None,
            tail: Optional[str] = None,
            children: Sequence[ET.Element] = (),
            ) -> ET.Element:
    ret_val = ET.Element(tag)

    if attributes is not None:
        ret_val.attrib.update(attributes)

    ret_val.text = text
    ret_val.tail = tail

    ret_val.extend(children)

    return ret_val
