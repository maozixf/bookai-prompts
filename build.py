# -*- coding: utf-8 -*-
"""bookai.top 职业提示词 → 分类速查（Markdown / JSON / 可搜索 HTML）"""
import json, os, re

from parse_lib import parse as parse_lib

OUT = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(OUT, "prompts_raw.json"), encoding="utf-8"))

CATS = {
    "内容·文案·写作": """Advertising-Copywriter Content-Architect Content-Editor Content-Marketing-Manager
        Content-Moderator Content-Performance-Analyst Content-Strategist Digital-Content-Planner
        Digital-Publishing-Editor Digital-Storyteller eBook-Author Editor Press-Release-Writer
        Professional-Blogger Technical-Blog-Writer Technical-Editor Technical-Writer UX-Copywriter
        White-Paper-Writer API-Documentation-Writer unknown""",
    "市场·SEO·增长": """Ad-Creative-Planner Ad-Placement-Specialist App-Promotion-Specialist Brand-Manager
        Competitive-Analysis-Specialist Competitive-Intelligence-Analyst Conversion-Rate-Optimization-Specialist
        Digital-Advertising-Specialist Digital-Marketing-Specialist Digital-Strategist Growth-Hacker
        Influencer-Marketing-Specialist Keyword-Research-Analyst Link-Building-Specialist Local-SEO-Specialist
        Market-Research-Analyst Marketing Marketing-Specialist Public-Opinion-Analyst Rich-Media-SEO-Specialist
        SEM-Specialist SEO-Audit-Specialist SEO-Content-Strategist SEO-Developer SEO-Expert
        SEO-Localization-Specialist SEO-Specialist SEO-Testing-Specialist Search-Engine-Evaluator
        Technical-SEO-Specialist User-Acquisition-Specialist User-Growth-Specialist Social-Media-Ad-Placement-Specialist
        Social-Media-Advertising-Specialist""",
    "运营·电商·社媒": """Community-Manager Community-Operations Content-Operations Content-Operations-Manager
        E-commerce-Operations Live-Streamer Merchant-Operations New-Media-Operations Product-Operations
        Product-Operations-Manager Social-Media-CRM-Manager Social-Media-Manager Social-Media-Monitoring-Specialist
        Social-Media-Operations Supply-Chain-Analyst Traffic-Operations User-Operations""",
    "产品·项目·管理": """Business-Analyst ERP-Consultant IT-Change-Management-Specialist IT-Consultant IT-Project-Manager
        IT-Service-Delivery-Manager Knowledge-Management-Specialist Product-Manager Product-Marketing-Manager
        Project-Coordinator Project-Management Project-Manager Strategy-Product-Manager Technical-Product-Manager""",
    "软件研发·架构·运维": """Blockchain-Developer Blockchain-Engineer Cloud-Computing-Engineer Cloud-Native-Architect
        Container-Technology-Specialist Cross-platform-Developer DevOps-Engineer Embedded-Software-Engineer
        Embedded-Systems-Engineer Front-end-Developer Frontend-Engineer Full-stack-Developer Full-stack-Developers
        IoT-Developer IT-Architect IT-System-Administrator Microservices-Architect Mini-Program-Developer
        Mobile-App-Developer Mobile-Developer Mobile-Game-Developer Network-Administrator Network-Engineer
        Operations-Engineer Social-Media-Algorithm-Specialist Software-Developer Software-Engineer
        System-Architect Systems-Integration-Engineer Database-Administrator""",
    "数据·分析·BI": """Business-Data-Analysis Business-Intelligence-Analyst Business-Intelligence-Developer
        Business-Intelligence-Engineer Data-Analyst Data-Analytics-Engineer Data-Architect Data-Engineer
        Data-Governance-Specialist Data-Mining-Engineer Data-Scientist Data-Visualization-Engineer
        Data-Visualization-Specialist ETL-Developer Operations-Analyst Operations-Research-Analyst
        Predictive-Analyst Social-Media-Analyst Social-Media-ROI-Analyst Social-Media-Trend-Forecasting-Analyst
        Statistical-Analyst User-Behavior-Analyst Web-Analyst Website-Operations-Data-Analysis""",
    "AI·算法·量化": """AI-Engineer Algorithm-Engineer Artificial-Intelligence-Engineer Machine-Learning-Engineer
        Quantitative-Developer Search-Algorithm-Engineer""",
    "测试·质量": """Automation-Test-Engineer QA-Engineer Quality-Assurance-Analyst Test-Engineer""",
    "设计·创意·视觉": """3D-Modeler Animation-Designer Brand-Designer Creative-Director Digital-Artist Game-Art-Designer
        Game-Designer Graphic-Designer Illustrator Interaction-Designer Motion-Designer UI-Designer
        User-Experience-Designer User-Experience-Researcher User-Interface-Designer User-Researcher
        UX-Designer Web-Designer""",
    "视频·音频·直播": """Audio-Engineer Podcast-Host Short-Video-Creator Video-Animator Video-Cataloger
        Video-Content-Curator Video-Data-Analyst Video-Editor Video-Effects-Artist Video-Interview-Director
        Video-Metadata-Specialist Video-Platform-Manager Video-Producer Video-Quality-Assurance-Specialist
        Video-Script-Writer""",
    "安全·风控·合规": """Application-Security-Engineer Cybersecurity-Analyst Cybersecurity-Engineer
        Data-Privacy-Officer Data-Privacy-Specialist Digital-Forensics-Analyst Identity-Authentication-Specialist
        Information-Security-Analyst Information-Security-Engineer IT-Auditor Penetration-Testing-Engineer
        Risk-Control-Analyst Risk-Management-Specialist Security-Operations-Engineer Vulnerability-Mining-Engineer""",
    "财务·法务·商务": """Actuary Budget-Analyst Compliance-Analyst Financial-Advisor Financial-Analyst
        Financial-Planning-Analyst Investment-Analyst Legal-Affairs Legal-Specialist
        Mergers-and-Acquisitions-Analyst Procurement Procurement-Specialist Revenue-Management-Analyst
        Tax-Analyst Social-Media-Legal-Advisor""",
    "人事·行政·培训": """Administration Administrative-Assistant HR-Specialist Human-Resources%20Management
        Human-Resources-Specialist Technical-Trainer""",
    "销售·客户服务": """Business-Development-Manager Customer-Experience-Analyst Customer-Insights-Analyst
        Customer-Relationship-Manager Customer-Service-Representative Customer-Success-Manager
        Online-Customer-Service Sales-Operations Sales-Representative Technical-Sales-Engineer
        Technical-Support-Engineer Technical-Support-Specialist Social-Media-Customer-Service-Representative""",
    "通用人设·跨界": """Doctor Philosopher""",
}
CAT_EMOJI = {"内容·文案·写作": "📝", "市场·SEO·增长": "🔍", "运营·电商·社媒": "🛒",
             "产品·项目·管理": "📈", "软件研发·架构·运维": "💻", "数据·分析·BI": "📊",
             "AI·算法·量化": "🤖", "测试·质量": "🧪", "设计·创意·视觉": "🎨",
             "视频·音频·直播": "🎥", "安全·风控·合规": "🔐", "财务·法务·商务": "⚖️",
             "人事·行政·培训": "🏢", "销售·客户服务": "💼", "通用人设·跨界": "🧠"}
slug2cat, slug2emoji = {}, {}
for c, s in CATS.items():
    for x in s.split():
        assert x not in slug2cat, x
        slug2cat[x] = c
        slug2emoji[x] = CAT_EMOJI[c]


def clean_body(b):
    b = re.sub(r'^class="[^"]*">\s*', "", b)
    b = re.sub(r"^#\s+.*?\n", "", b, count=1)
    b = re.sub(r"^>\s*\n+", "", b, flags=re.M)
    b = re.sub(r"最后更新：.*?AI模型\s*\n*", "", b)
    return b.strip()


def clean_title(t):
    t = re.sub(r"\s*[|｜].*$", "", t)
    t = re.sub(r"\s*-\s*提示词模板.*$", "", t)
    t = re.sub(r"ChatGPT提示词\s*\d{4}\s*$", "", t)
    return t.strip()


def split_title(t):
    t = t.strip()
    emoji = ""
    m = re.match(r"^([\U0001F300-\U0001FAFF\u2600-\u27BF\uFE0F\u2B00-\u2BFF\u2139\u2695]+)\s*", t)
    if m:
        emoji = m.group(1).replace("\ufe0f", "").strip()
        t = t[m.end():]
    p = re.split(r"\s+-\s+", t, maxsplit=1)
    return emoji, p[0].strip(), (p[1].strip() if len(p) > 1 else "")


def section(b, name):
    m = re.search(r"^##\s*%s\s*$(.*?)(?=^##\s|\Z)" % re.escape(name), b, re.S | re.M)
    if not m:
        return []
    return [re.sub(r"^[-*]\s*", "", l).strip() for l in m.group(1).strip().splitlines()
            if re.match(r"^[-*]\s*\S", l.strip())]


def modules(b):

    out = []
    for m in re.finditer(r"^##\s*\**(.+?)\**\s*$", b, re.M):
        t = m.group(1).replace("*", "").strip()
        t = re.sub(r"[\U0001F300-\U0001FAFF\u2600-\u27BF\uFE0F]", "", t).strip()
        t = re.sub(r"^[一二三四五六七八九十]+、\s*", "", t).strip()
        if t and t not in ("技能", "背景", "工作方式", "输出格式", "回答风格", "回答限制"):
            out.append(t)
    return out


def core_of(b, kind):
    if kind == "库":
        m = re.search(r"##\s*核心角色Prompt.*?```[a-zA-Z]*\n(.*?)```", b, re.S)
        if m:
            return m.group(1).strip()
    m = re.search(r"^>\s*$\s*\n*(你现在是.*?)(?=\n##\s|\Z)", b, re.S | re.M)
    if m:
        return m.group(1).strip()
    head = re.split(r"\n##\s", b, maxsplit=1)[0].strip()
    return head or b


# 同义词/口误映射：正文里几乎不出现平台名与业务黑话，靠这层把用户的话接到岗位
ALIAS = {
    "小红书|抖音|公众号|百家号|视频号|爆款|涨粉|选题|私域|引流": "Social-Media-Operations New-Media-Operations Content-Operations Short-Video-Creator",
    "直播|带货|主播|连麦": "Live-Streamer E-commerce-Operations",
    "详情页|主图|卖点|选品|店铺|电商|转化率": "Advertising-Copywriter E-commerce-Operations Merchant-Operations",
    "标题|开头|钩子|文案|润色|改写|校对|错别字": "Advertising-Copywriter Content-Editor Editor Technical-Editor",
    "prd|需求|原型|优先级|迭代|用户故事": "Strategy-Product-Manager Product-Manager Business-Analyst",
    "竞品|对标|拆解": "Competitive-Analysis-Specialist Competitive-Intelligence-Analyst",
    "调研|问卷|访谈|用户画像|焦点小组": "User-Researcher Market-Research-Analyst User-Experience-Researcher",
    "看板|报表|取数|sql|excel|透视表": "Data-Analyst Data-Visualization-Specialist Business-Intelligence-Analyst",
    "ab|a/b|实验|漏斗|归因|留存|北极星": "Data-Scientist Conversion-Rate-Optimization-Specialist Web-Analyst",
    "数仓|etl|数据管道|清洗|埋点": "Data-Engineer ETL-Developer Data-Architect",
    "简历|面试|jd|招聘|绩效|薪酬|员工关系|离职|劳动法|社保": "Human-Resources%20Management HR-Specialist Human-Resources-Specialist",
    "合同|劳动合同|知识产权|诉讼|合规|条款": "Legal-Affairs Legal-Specialist Compliance-Analyst",
    "报销|发票|预算|成本|毛利|三张表|现金流|财务": "Financial-Analyst Budget-Analyst Financial-Planning-Analyst",
    "融资|bp|估值|投资|尽调|并购": "Investment-Analyst Mergers-and-Acquisitions-Analyst Financial-Analyst",
    "保险|精算|赔付": "Actuary Risk-Management-Specialist",
    "客服|客诉|退款|售后|话术|工单": "Customer-Service-Representative Online-Customer-Service Technical-Support-Specialist",
    "销售|谈判|逼单|报价|线索|客户跟进|crm": "Sales-Operations Sales-Representative Customer-Relationship-Manager",
    "供应链|采购|供应商|招投标|库存": "Supply-Chain-Analyst Procurement Procurement-Specialist",
    "广告|投放|信息流|千川|roi|预算分配|素材": "Digital-Advertising-Specialist Ad-Placement-Specialist Ad-Creative-Planner",
    "seo|关键词|外链|收录|排名|百度|谷歌": "SEO-Expert SEO-Specialist Keyword-Research-Analyst SEO-Audit-Specialist",
    "社群|裂变|拉新|增长|冷启动|留存": "Community-Operations Growth-Hacker User-Growth-Specialist User-Acquisition-Specialist",
    "视频|剪辑|分镜|口播|字幕|短视频|拍摄": "Video-Editor Video-Script-Writer Short-Video-Creator Video-Producer",
    "播客|音频|录音|收音|混音": "Podcast-Host Audio-Engineer",
    "海报|logo|vi|配色|版式|平面|视觉": "Graphic-Designer Brand-Designer Brand-Manager",
    "插画|头像|表情包|手绘": "Illustrator Digital-Artist",
    "3d|建模|渲染|材质|绑定": "3D-Modeler Game-Art-Designer",
    "动效|动画|转场|ae": "Motion-Designer Animation-Designer Video-Effects-Artist",
    "游戏|关卡|数值|玩法|策划": "Game-Designer Mobile-Game-Developer",
    "前端|react|vue|页面|组件|css": "Frontend-Engineer Front-end-Developer UI-Designer",
    "后端|接口|api|微服务|数据库|并发": "Software-Engineer Microservices-Architect Database-Administrator",
    "小程序|公众号开发|h5": "Mini-Program-Developer Cross-platform-Developer",
    "app|安卓|ios|移动端": "Mobile-App-Developer Mobile-Developer",
    "运维|服务器|k8s|kubernetes|docker|部署|监控|sre": "Operations-Engineer DevOps-Engineer Container-Technology-Specialist",
    "测试|用例|自动化|缺陷|bug|回归|qa": "Test-Engineer QA-Engineer Automation-Test-Engineer",
    "安全|渗透|漏洞|等保|攻防|入侵|加固": "Penetration-Testing-Engineer Information-Security-Engineer Security-Operations-Engineer",
    "风控|反欺诈|薅羊毛|异常交易|规则": "Risk-Control-Analyst Risk-Management-Specialist",
    "隐私|个人信息|gdpr|数据合规|脱敏": "Data-Privacy-Officer Data-Privacy-Specialist Data-Governance-Specialist",
    "大模型|ai|prompt|rag|微调|llm|智能体": "Machine-Learning-Engineer AI-Engineer Artificial-Intelligence-Engineer",
    "算法|推荐|搜索|排序|特征": "Search-Algorithm-Engineer Algorithm-Engineer",
    "量化|回测|策略|因子": "Quantitative-Developer",
    "教学|课程|培训|讲师|课件": "Technical-Trainer Technical-Writer",
    "医生|症状|诊断|用药|健康": "Doctor",
    "哲学|人生|意义|伦理|思辨": "Philosopher",
    "商业计划|商业模式|行业分析": "Business-Analyst Investment-Analyst",
    "项目管理|排期|里程碑|风险|甘特": "Project-Management Project-Manager Project-Coordinator",
}
ALIAS_MAP = {}
for k, v in ALIAS.items():
    for t in k.split("|"):
        for s in v.split():
            ALIAS_MAP.setdefault(s, []).append(t)

recs = []
for r in d:
    b = clean_body(r["body"])
    emoji, cn, en = split_title(clean_title(r["title"]))
    if "核心角色Prompt" in b:
        kind = "库"
    elif re.search(r"^##\s*\*\*?[一二三四五六七八九十]+、", b, re.M):
        kind = "清单"
    elif re.search(r"^##\s*技能\s*$", b, re.M):
        kind = "人设"
    else:
        kind = "文"

    skills = section(b, "技能")
    if kind == "库":
        m = re.search(r"\*\*使用本页Prompt的优势\*\*[：:]\s*\n+((?:-.*\n)+)", b)
        skills = [x.strip("- ").strip() for x in m.group(1).splitlines()] if m else []
    if kind in ("清单", "文") and not skills:
        skills = modules(b)

    tpl = 0
    if kind == "库":
        groups, tpl, _bad, _nt = parse_lib(os.path.join(OUT, "raw", r["slug"] + ".html"))
    else:
        groups = []
    if kind == "清单":
        tpl = len(re.findall(r"^-\s*\S", b, re.M))

    core = core_of(b, kind)
    copy_text = core if kind in ("库", "文") else b
    intro = next((l.strip() for l in b.splitlines()
                  if l.strip() and not l.strip().startswith(("#", "-", "|", ">", "```"))), "")

    recs.append({
        "slug": r["slug"], "url": r["url"],
        "emoji": emoji or slug2emoji.get(r["slug"], ""),
        "cn": cn, "en": en, "kind": kind,
        "cat": slug2cat[r["slug"]],
        "intro": intro, "skills": skills[:8],
        "core": core, "copy": copy_text, "tpl": tpl, "templates": groups,
        "alias": " ".join(ALIAS_MAP.get(r["slug"], [])),
        "search": " ".join([cn, en, r["slug"], " ".join(skills),
                             " ".join(ALIAS_MAP.get(r["slug"], [])),
                             b[:3000]]).lower().replace("\n", " "),
    })

order = list(CATS.keys())
recs.sort(key=lambda r: (order.index(r["cat"]), r["cn"]))
by_slug = {r["slug"]: r for r in recs}
KIND_LABEL = {"人设": "结构化人设", "清单": "角色+问题清单", "库": "角色+场景模板库", "文": "长文角色"}

SCEN = [
    ("写小红书 / 抖音文案，起标题、写钩子", ["Social-Media-Operations", "Content-Operations", "Short-Video-Creator"]),
    ("写公众号长文 / 深度稿", ["Content-Editor", "Content-Strategist", "Professional-Blogger"]),
    ("写电商详情页、卖点提炼", ["Advertising-Copywriter", "E-commerce-Operations", "Merchant-Operations"]),
    ("写广告素材与 AB 文案", ["Ad-Creative-Planner", "Digital-Advertising-Specialist"]),
    ("做网站 SEO，关键词与内容规划", ["SEO-Expert", "SEO-Specialist", "Keyword-Research-Analyst"]),
    ("排查站点 SEO 技术问题", ["SEO-Audit-Specialist", "SEO-Developer", "Technical-SEO-Specialist"]),
    ("做用户增长 / 拉新活动方案", ["Growth-Hacker", "User-Acquisition-Specialist", "User-Growth-Specialist"]),
    ("写 PRD、拆需求、定优先级", ["Strategy-Product-Manager", "Product-Manager", "Business-Analyst"]),
    ("排项目计划、控进度与风险", ["Project-Management", "Project-Manager", "Project-Coordinator"]),
    ("做竞品分析、市场调研", ["Competitive-Analysis-Specialist", "Market-Research-Analyst", "Competitive-Intelligence-Analyst"]),
    ("写 SQL / 做数据看板与报表", ["Data-Analyst", "Data-Visualization-Specialist", "Business-Intelligence-Analyst"]),
    ("做 A/B 实验与指标归因", ["Data-Scientist", "Conversion-Rate-Optimization-Specialist", "Web-Analyst"]),
    ("清洗数据、搭数仓管道", ["Data-Engineer", "ETL-Developer", "Data-Architect"]),
    ("写前后端代码、做功能实现", ["Full-stack-Developer", "Front-end-Developer", "Software-Engineer"]),
    ("设计系统架构、做技术选型", ["System-Architect", "Microservices-Architect", "Cloud-Native-Architect"]),
    ("配 CI/CD、上云部署、容器化", ["Operations-Engineer", "DevOps-Engineer", "Container-Technology-Specialist"]),
    ("做大模型应用、Prompt 与 RAG", ["Machine-Learning-Engineer", "AI-Engineer", "Algorithm-Engineer"]),
    ("写测试用例、做自动化测试", ["Test-Engineer", "Automation-Test-Engineer", "QA-Engineer"]),
    ("做 UI 界面 / 视觉稿评审", ["UX-Designer", "UI-Designer", "Graphic-Designer"]),
    ("做用户调研、访谈提纲与洞察", ["User-Researcher", "User-Experience-Researcher", "User-Experience-Designer"]),
    ("剪视频、写分镜与脚本", ["Video-Editor", "Video-Script-Writer", "Video-Producer"]),
    ("做安全评估、渗透测试报告", ["Penetration-Testing-Engineer", "Information-Security-Engineer", "Security-Operations-Engineer"]),
    ("写风控规则、评估业务风险", ["Risk-Control-Analyst", "Risk-Management-Specialist", "Compliance-Analyst"]),
    ("做财务分析、预算与经营测算", ["Financial-Advisor", "Financial-Analyst", "Budget-Analyst"]),
    ("审合同、看合规风险", ["Legal-Affairs", "Legal-Specialist", "Compliance-Analyst"]),
    ("写 JD、面试题、员工沟通", ["Human-Resources%20Management", "HR-Specialist", "Administrative-Assistant"]),
    ("写销售话术、客户跟进与逼单", ["Sales-Operations", "Sales-Representative", "Customer-Success-Manager"]),
    ("处理客诉、建客服话术库", ["Customer-Service-Representative", "Online-Customer-Service", "Technical-Support-Specialist"]),
    ("写技术文档 / API 文档 / 白皮书", ["Technical-Writer", "API-Documentation-Writer", "White-Paper-Writer"]),
    ("找人设陪聊、要跨界专业视角", ["Doctor", "Philosopher", "Editor"]),
]

json.dump({"source": "https://bookai.top/docs/category/chatgpt-prompt提示词-职业",
           "count": len(recs), "categories": order, "scenarios": SCEN, "prompts": recs},
          open(os.path.join(OUT, "prompts.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------------- Markdown ----------------
L = []
A = L.append
A("# ChatGPT 职业 / 人设提示词 · 分类速查")
A("")
A("> 来源：[bookai.top 职业提示词栏目](https://bookai.top/docs/category/chatgpt-prompt提示词-职业) ｜ 共 **%d** 条，正文全部离线存档。" % len(recs))
A("> 用法：不知道挑哪个 → 查「一、场景速查」；知道岗位 → 查「二、大类索引」。")
A("> 形态：**结构化人设**（背景/技能/输出格式）· **角色+问题清单**（现成提问可直接发）· **角色+场景模板库**（一条角色 prompt + 十几条细分模板）。")
A("")
A("## 一、场景速查：我要做的事 → 用哪个")
A("")
A("| 我要做的事 | 推荐（按优先级） |")
A("| --- | --- |")
for task, slugs in SCEN:
    items = []
    for s in slugs:
        r = by_slug.get(s)
        if r:
            items.append("[%s %s](%s)" % (r["emoji"], r["cn"], r["url"]))
    A("| %s | %s |" % (task, " · ".join(items)))
A("")
A("## 二、大类索引")
A("")
A("| 大类 | 条数 | 模板库 / 清单型 |")
A("| --- | --- | --- |")
for c in order:
    sub = [r for r in recs if r["cat"] == c]
    A("| [%s](#%s) | %d | %d |" % (c, c.replace("·", ""), len(sub),
                                   sum(1 for r in sub if r["kind"] in ("库", "清单"))))
A("")
A("---")
for c in order:
    sub = [r for r in recs if r["cat"] == c]
    A("")
    A("## %s（%d）" % (c, len(sub)))
    A("")
    A("| 提示词 | 形态 | 擅长什么 | 原文 |")
    A("| --- | --- | --- | --- |")
    for r in sub:
        if r["kind"] == "库":
            sk = "核心角色 + %d 条细分场景模板" % r["tpl"]
        elif r["kind"] == "清单":
            sk = "现成问题清单 %d 条 · " % r["tpl"] + "、".join(r["skills"][:3])
        else:
            sk = "、".join(r["skills"][:4]) if r["skills"] else r["intro"][:46]
        A("| %s **%s**%s | %s | %s | [打开](%s) |"
          % (r["emoji"], r["cn"], (" <sub>%s</sub>" % r["en"]) if r["en"] else "",
             KIND_LABEL[r["kind"]], sk.replace("|", "/"), r["url"]))
A("")
open(os.path.join(OUT, "ChatGPT职业提示词-分类速查.md"), "w", encoding="utf-8").write("\n".join(L))

F = ["# ChatGPT 职业 / 人设提示词 · 全文合集（%d 条）\n" % len(recs),
     "来源：bookai.top ｜ 把 `text` 代码块整段复制到对话开头即可使用。\n"]
cur = None
for r in recs:
    if r["cat"] != cur:
        cur = r["cat"]
        F.append("\n---\n\n# ▍%s\n" % cur)
    F.append("\n## %s %s · %s  `%s`\n" % (r["emoji"], r["cn"], r["en"], KIND_LABEL[r["kind"]]))
    F.append("<sub>%s</sub>\n" % r["url"])
    F.append("\n```text\n%s\n```\n" % r["copy"])
    if r["kind"] == "库":
        F.append("\n**场景模板库 · %d 条**\n" % r["tpl"])
        for g in r["templates"]:
            F.append("\n### %s\n" % g["g"])
            for sub in g["subs"]:
                F.append("\n**%s**\n\n| 场景 | Prompt 模板 |\n| --- | --- |" % sub["s"])
                for it in sub["items"]:
                    F.append("| %s | %s |" % (it["n"], it["p"].replace("|", "/")))
open(os.path.join(OUT, "ChatGPT职业提示词-全文合集.md"), "w", encoding="utf-8").write("\n".join(F))

LIB_TOTAL = sum(r["tpl"] for r in recs if r["kind"] == "库")
# ---------- 场景模板库单独成册 ----------
T = ["# ChatGPT 职业提示词 · 场景模板库合集（%d 条）\n" % LIB_TOTAL,
     "bookai.top 上有 15 个页面是「核心角色 Prompt + 场景模板库」结构，共 %d 条现成模板。"
     % LIB_TOTAL,
     "用法：先贴核心角色 Prompt，再按需要贴一条场景模板。\n",
     "| 页面 | 模块 | 模板数 |\n| --- | --- | --- |"]
for r in recs:
    if r["kind"] == "库":
        T.append("| [%s %s](%s) | %d | %d |"
                 % (r["emoji"], r["cn"], r["url"], len(r["templates"]), r["tpl"]))
for r in recs:
    if r["kind"] != "库":
        continue
    T.append("\n---\n\n## %s %s（%d 条）\n" % (r["emoji"], r["cn"], r["tpl"]))
    T.append("原文：%s\n" % r["url"])
    T.append("\n**核心角色 Prompt**\n\n```text\n%s\n```\n" % r["core"])
    for g in r["templates"]:
        T.append("\n### %s\n" % g["g"])
        for sub in g["subs"]:
            T.append("\n**%s**\n\n| 场景 | Prompt 模板 |\n| --- | --- |" % sub["s"])
            for it in sub["items"]:
                T.append("| %s | %s |" % (it["n"], it["p"].replace("|", "/")))
open(os.path.join(OUT, "ChatGPT职业提示词-场景模板库合集.md"), "w", encoding="utf-8").write("\n".join(T))
print("模板库合集: %d 条" % LIB_TOTAL)

print("总量 %d ｜ 库 %d ｜ 清单 %d ｜ 人设 %d ｜ 文 %d" % (
    len(recs), *[sum(1 for r in recs if r["kind"] == k) for k in ("库", "清单", "人设", "文")]))
for c in order:
    print("  %-16s %d" % (c, sum(1 for r in recs if r["cat"] == c)))
