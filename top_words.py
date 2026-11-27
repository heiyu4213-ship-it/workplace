#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""统计一个文本文件里出现次数最多的 N 个词。

用法示例：
    python3 top_words.py 文本.txt
    python3 top_words.py 文本.txt -n 20 --stopwords
    python3 top_words.py 文本.txt --case-sensitive

说明：
    * 默认只识别拉丁字母单词（允许内部出现 ' 或 -），大小写不敏感。
    * --stopwords 会过滤 the/a/of/and 等常见英文虚词，让结果更能反映内容。
    * 中文分词需要额外依赖（如 jieba），这里保持零依赖，所以不处理中文。
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

WORD_RE = re.compile(r"[A-Za-z]+(?:['’\-][A-Za-z]+)*")

# 常见英文虚词：过滤后剩下的多为实词
STOPWORDS = frozenset("""
a about above after again against all am an and any are as at be because been
before being below between both but by can could did do does doing down during
each few for from further had has have having he her here hers herself him
himself his how i if in into is it its itself just me more most my myself no
nor not now of off on once only or other our ours ourselves out over own same
she should so some such than that the their theirs them themselves then there
these they this those through to too under until up very was we were what when
where which while who whom why will with would you your yours yourself
yourselves
""".split())


def read_text(path: Path) -> tuple[str, str]:
    """按常见编码依次尝试解码，返回 (文本, 实际编码)。"""
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "utf-8", "gb18030", "latin-1"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("unknown", raw, 0, 1, "无法识别文件编码")


def iter_words(text: str, case_sensitive: bool):
    for m in WORD_RE.finditer(text):
        w = m.group(0)
        yield w if case_sensitive else w.lower()


def main() -> int:
    ap = argparse.ArgumentParser(description="统计文本文件里出现最多的词")
    ap.add_argument("path", type=Path, help="要统计的文本文件")
    ap.add_argument("-n", "--top", type=int, default=20, help="显示前几名（默认 20）")
    ap.add_argument("--stopwords", action="store_true", help="过滤常见英文虚词")
    ap.add_argument("--case-sensitive", action="store_true", help="区分大小写")
    ap.add_argument("--min-length", type=int, default=1, help="最短单词长度（默认 1）")
    args = ap.parse_args()

    if not args.path.is_file():
        print(f"错误：找不到文件 {args.path}", file=sys.stderr)
        return 1

    try:
        text, encoding = read_text(args.path)
    except UnicodeDecodeError as e:
        print(f"错误：无法解码 {args.path}（{e}）", file=sys.stderr)
        return 1

    words = [
        w for w in iter_words(text, args.case_sensitive)
        if len(w) >= args.min_length
        and not (args.stopwords and w.lower() in STOPWORDS)
    ]
    if not words:
        print("错误：文件里没有可统计的单词", file=sys.stderr)
        return 1

    counts = Counter(words)
    total = len(words)
    ranked = counts.most_common(max(0, args.top))

    print(f"文件：{args.path}")
    print(f"编码：{encoding}    单词总数：{total:,}    不同单词：{len(counts):,}")
    print()
    print(f"{'排名':>4}  {'单词':<{max(len(w) for w, _ in ranked)}}  {'次数':>6}  {'占比':>7}")
    print("-" * 46)
    top_count = ranked[0][1]
    for i, (word, cnt) in enumerate(ranked, 1):
        share = cnt / total
        bar = "█" * max(1, round(cnt / top_count * 12))
        print(f"{i:>4}  {word:<{max(len(w) for w, _ in ranked)}}  {cnt:>6,}  {share:>6.2%}  {bar}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
