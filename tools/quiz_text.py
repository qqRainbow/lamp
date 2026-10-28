# Regenerates QUIZ_TEXT in lamp.html: the verse shown after each quiz answer, in every version,
# from the `at:` references in QUIZ. Run from the project folder after adding questions:
#   py tools/quiz_text.py lamp.html        (python3 on a Mac)
import json, sys, re
page = sys.argv[1] if len(sys.argv) > 1 else "lamp.html"
html = open(page, encoding="utf-8").read()
BOOKS = re.findall(r'"([^"]+)"', re.search(r"const BOOKS = \[(.*?)\];", html, re.S)[1])
BOOKS_FR = json.loads(re.search(r"const BOOKS_FR = (\[.*?\]);", html, re.S)[1])
LSG_AT = {"Jonah 1:17": (31, 1, 0)}  # Louis Segond numbers this verse Jonas 2:1
bibles = {k: json.load(open(f"{k}.json", encoding="utf-8")) for k in ("kjv", "bsb", "web", "lsg")}
texts = {}
quiz = html[html.index("const QUIZ = ["):]
quiz = quiz[:quiz.index("\n];")]  # only the quiz questions, not other lists that also use `at:`
for ref in sorted(set(re.findall(r'[{,] at: "([^"]+)"', quiz))):
    m = re.match(r"(.+) (\d+):(\d+)(?:-(\d+))?$", ref)
    b, c, v1 = BOOKS.index("Psalms" if m[1] == "Psalm" else m[1]), int(m[2]) - 1, int(m[3]) - 1; v2 = int(m[4] or m[3]) - 1
    fr_name = "Psaume" if b == 18 else None
    e = {k: " ".join(x for x in bibles[k][b][c][v1:v2 + 1] if x) for k in ("kjv", "bsb", "web")}
    lb, lc, lv1 = LSG_AT.get(ref, (b, c, v1)); lv2 = lv1 + (v2 - v1)
    e["lsg"] = " ".join(bibles["lsg"][lb][lc][lv1:lv2 + 1])
    e["lsgRef"] = f"{fr_name or BOOKS_FR[lb]} {lc + 1}:{lv1 + 1}" + (f"-{lv2 + 1}" if lv2 != lv1 else "")
    texts[ref] = e
block = "const QUIZ_TEXT = {\n" + ",\n".join(f"  {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}" for k, v in texts.items()) + "\n};"
html, n = re.subn(r"const QUIZ_TEXT = \{\n.*?\n\};", lambda _: block, html, flags=re.S)
assert n == 1
open(page, "w", encoding="utf-8", newline="\n").write(html)
print(len(texts), "verses written to", page)
