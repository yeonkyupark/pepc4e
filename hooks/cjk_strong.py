"""한국어 조사 앞의 굵게(**...**) 표기를 <strong>으로 바꾸는 MkDocs 훅.

Markdown 규칙상 닫는 **가 ')' 같은 문장부호 뒤에 오고 바로 다음에 한글 조사가 붙으면
(예: **전략(strategy)**은) 굵게로 인식되지 않는다. 렌더링 전에 **...**를 <strong>...</strong>로
바꿔 이 문제를 없앤다. 코드 블록과 인라인 코드는 건드리지 않는다.
"""
import re

FENCE = re.compile(r"^(\s*)(`{3,}|~{3,})")
CODE_SPAN = re.compile(r"(`+)(.+?)\1")
STRONG = re.compile(r"\*\*(?=\S)(.+?)(?<=\S)\*\*")


def _convert(line):
    parts, last = [], 0
    for m in CODE_SPAN.finditer(line):
        parts.append(STRONG.sub(r"<strong>\1</strong>", line[last:m.start()]))
        parts.append(m.group(0))
        last = m.end()
    parts.append(STRONG.sub(r"<strong>\1</strong>", line[last:]))
    return "".join(parts)


def on_page_markdown(markdown, **kwargs):
    out, fence = [], None
    for line in markdown.split("\n"):
        m = FENCE.match(line)
        if fence:
            if m and m.group(2)[0] == fence[0] and len(m.group(2)) >= len(fence):
                fence = None
            out.append(line)
        elif m:
            fence = m.group(2)
            out.append(line)
        else:
            out.append(_convert(line))
    return "\n".join(out)
