# -*- coding: utf-8 -*-
"""解析「场景模板库」型页面的表格：模块 → 子模块 → 场景 / Prompt 模板。"""
import json, os, re
from html.parser import HTMLParser

OUT = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(OUT, "raw")


class LibParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.h2 = ""
        self.h3 = ""
        self.rows = []
        self.tables = 0
        self.bad = []
        self.mode = None          # 'h2' / 'h3' / 'th' / 'td'
        self.buf = []
        self.row = []
        self.in_thead = False
        self.in_table = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class", "") or ""
        if tag in ("h2", "h3") and "anchor" in cls:
            self.mode = tag
            self.buf = []
        elif tag == "table":
            self.in_table = True
            self.tables += 1
        elif tag == "thead":
            self.in_thead = True
        elif tag == "tr":
            self.row = []
        elif tag in ("td", "th"):
            self.mode = tag
            self.buf = []

    def handle_endtag(self, tag):
        if tag in ("h2", "h3") and self.mode == tag:
            t = re.sub(r"\s+", " ", "".join(self.buf)).strip()
            t = re.sub(r"[\U0001F300-\U0001FAFF\u2600-\u27BF\uFE0F\u200b\u200c\u200d]", "", t).strip()
            if tag == "h2":
                self.h2, self.h3 = t, ""
            else:
                self.h3 = t
            self.mode = None
        elif tag == "thead":
            self.in_thead = False
        elif tag in ("td", "th") and self.mode == tag:
            self.row.append(re.sub(r"\s+", " ", "".join(self.buf)).strip())
            self.mode = None
        elif tag == "tr":
            if self.in_thead or not self.row:
                self.row = []
                return
            if len(self.row) != 2:
                self.bad.append(self.row)
            else:
                self.rows.append({"g": self.h2, "s": self.h3, "n": self.row[0], "p": self.row[1]})
            self.row = []
        elif tag == "table":
            self.in_table = False

    def handle_data(self, d):
        if self.mode:
            self.buf.append(d)


def parse(path):
    p = LibParser()
    p.feed(open(path, encoding="utf-8").read())
    # 丢掉非模板区（使用技巧 / 相关资源 / 为什么…）
    drop = ("为什么", "使用技巧", "相关资源", "核心角色Prompt")
    rows = [r for r in p.rows if not any(k in r["g"] for k in drop)]
    groups = []
    for r in rows:
        if not groups or groups[-1]["g"] != r["g"]:
            groups.append({"g": r["g"], "subs": []})
        g = groups[-1]
        key = r["s"] or "常规"
        if not g["subs"] or g["subs"][-1]["s"] != key:
            g["subs"].append({"s": key, "items": []})
        g["subs"][-1]["items"].append({"n": r["n"], "p": r["p"]})
    return groups, len(rows), p.bad, p.tables


if __name__ == "__main__":
    d = json.load(open(os.path.join(OUT, "prompts.json"), encoding="utf-8"))
    libs = [r for r in d["prompts"] if r["kind"] == "库"]
    print("库型页面:", len(libs))
    total = 0
    for r in libs:
        path = os.path.join(RAW, r["slug"] + ".html")
        groups, n, bad, nt = parse(path)
        total += n
        flag = "" if not bad else "  ⚠ 异常行 %d" % len(bad)
        print("  %-26s 模块%2d 子模块%2d 模板%3d 表%2d%s"
              % (r["slug"], len(groups), sum(len(g["subs"]) for g in groups), n, nt, flag))
        if bad:
            print("     ", bad[:2])
    print("模板总数:", total)
