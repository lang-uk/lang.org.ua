from io import StringIO
from itertools import islice
from typing import Iterator, List, TypeVar

import markdown
from bs4 import BeautifulSoup


T = TypeVar('T')


def md_to_text(md):
    html = markdown.markdown(md)
    soup = BeautifulSoup(html, features="html.parser")
    return soup.get_text()


def unmark_element(element, stream=None):
    if stream is None:
        stream = StringIO()
    if element.text:
        stream.write(element.text)
    for sub in element:
        unmark_element(sub, stream)
    if element.tail:
        stream.write(element.tail)
    return stream.getvalue()


# patching Markdown
markdown.Markdown.output_formats["plain"] = unmark_element
__md = markdown.Markdown(output_format="plain")
__md.stripTopLevelTags = False


def md_to_text2(text):
    return __md.convert(text.replace("**", ""))


def batch_iterator(iterator: Iterator[T], batch_size: int = 50) -> Iterator[List[T]]:
    iterator = iter(iterator)
    while True:
        batch = list(islice(iterator, batch_size))
        if not batch:
            return
        yield batch
