# -*- coding: utf-8 -*-
"""抓取 bookai.top 的 ChatGPT 职业/人设提示词页面，解析正文为 Markdown。"""
import io, json, os, re, sys, time
import urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser

BASE = "https://bookai.top"
OUT = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(OUT, "raw")
os.makedirs(RAW, exist_ok=True)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def get(url, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9"})
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            last = e
            time.sleep(1.2 * (i + 1))
    raise last


def sitemap_urls():
    xml = get(BASE + "/sitemap.xml")
    urls = re.findall(r"<loc>(.*?)</loc>", xml)
    return [u for u in urls if "/docs/ChatGPT-Prompt-Professionals/" in u]


class MD(HTMLParser):
    """把 <article> 正文里的 HTML 转成轻量 Markdown。"""
    BLOCK = {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li",
             "table", "tr", "blockquote", "pre", "section"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.skip = 0
        self.pre = 0
        self.href = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style"):
            self.skip += 1
            return
        if self.skip:
            return
        cls = a.get("class", "") or ""
        if tag == "a" and "hash-link" in cls:
            self.skip += 1
            return
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.out.append("\n\n" + "#" * int(tag[1]) + " ")
        elif tag == "li":
            self.out.append("\n- ")
        elif tag == "p":
            self.out.append("\n\n")
        elif tag == "br":
            self.out.append("\n")
        elif tag in ("strong", "b"):
            self.out.append("**")
        elif tag in ("em", "i"):
            self.out.append("*")
        elif tag == "code":
            if not self.pre:
                self.out.append("`")
        elif tag == "pre":
            self.pre += 1
            self.out.append("\n\n```\n")
        elif tag == "tr":
            self.out.append("\n| ")
        elif tag in ("td", "th"):
            self.out.append(" | ")
        elif tag == "blockquote":
            self.out.append("\n\n> ")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
            return
        if self.skip:
            if tag == "a":
                self.skip = max(0, self.skip - 1)
            return
        if tag in ("strong", "b"):
            self.out.append("**")
        elif tag in ("em", "i"):
            self.out.append("*")
        elif tag == "code":
            if not self.pre:
                self.out.append("`")
        elif tag == "pre":
            self.pre = max(0, self.pre - 1)
            self.out.append("\n```\n")
        elif tag in ("p", "ul", "ol", "table", "blockquote", "div", "section"):
            self.out.append("\n")

    def handle_data(self, d):
        if self.skip:
            return
        if self.pre:
            self.out.append(d)
        else:
            self.out.append(re.sub(r"[ \t\r\n]+", " ", d))


def to_md(html):
    p = MD()
    p.feed(html)
    txt = "".join(p.out)
    txt = re.sub(r"[ \t]+\n", "\n", txt)
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    return txt.strip()


def slice_body(html):
    i = html.find('class="theme-doc-markdown')
    if i < 0:
        return ""
    j = html.find('class="theme-doc-footer', i)
    if j < 0:
        j = html.find("<footer", i)
    return html[i:j]


def slice_header(html):
    """取 h1 与「最后更新」之间的介绍区块之外，只留 h1 文本。"""
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
    return re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else ""


def parse(url, html):
    fn = url.rsplit("/", 1)[-1]
    title_raw = slice_header(html)
    title = re.sub(r"\s*-\s*提示词模板.*$", "", title_raw).strip()
    title = re.sub(r"\s*[|｜].*$", "", title).strip()
    desc = ""
    m = re.search(r'<meta data-rh="true" name="description" content="(.*?)"', html)
    if m:
        desc = m.group(1)
    body = to_md(slice_body(html))
    # 去掉正文里可能混入的"最后更新时间"
    body = re.sub(r"最后\s*由.*?更新", "", body).strip()
    return {
        "slug": fn,
        "url": url,
        "title": title,
        "title_raw": title_raw,
        "desc": desc,
        "body": body,
    }


def main():
    urls = sitemap_urls()
    print("urls:", len(urls), flush=True)
    recs, errs = [], []
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(get, u): u for u in urls}
        for n, f in enumerate(as_completed(futs), 1):
            u = futs[f]
            try:
                html = f.result()
                with open(os.path.join(RAW, u.rsplit("/", 1)[-1] + ".html"), "w", encoding="utf-8") as fh:
                    fh.write(html)
                recs.append(parse(u, html))
            except Exception as e:
                errs.append((u, str(e)))
            if n % 25 == 0:
                print("  %d/%d" % (n, len(urls)), flush=True)
    recs.sort(key=lambda r: r["slug"].lower())
    with open(os.path.join(OUT, "prompts_raw.json"), "w", encoding="utf-8") as fh:
        json.dump(recs, fh, ensure_ascii=False, indent=1)
    print("ok:", len(recs), "err:", len(errs))
    for u, e in errs:
        print("  FAIL", u, e[:120])


if __name__ == "__main__":
    main()
