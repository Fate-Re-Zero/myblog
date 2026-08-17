# -*- coding: utf-8 -*-
from pathlib import Path
import re

md_path = Path(r"e:/博客/myblog/myblog/source/_posts/Agent/业务Agent介绍.md")
text = md_path.read_text(encoding="utf-8")

def repl(m):
    alt, src = m.group(1), m.group(2)
    return (
        f'<img src="{src}" alt="{alt}" '
        f'style="width:50%; display:block; margin:0;" />'
    )

new_text, n = re.subn(r"!\[([^\]]*)\]\(([^)]+)\)", repl, text)
md_path.write_text(new_text, encoding="utf-8")
print(f"replaced {n}")
