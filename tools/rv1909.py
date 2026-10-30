# Rebuilds rv.json (Reina-Valera 1909, public domain) from eBible.org's spaRV1909_vpl.zip (https://ebible.org/Scriptures/).
#   python3 tools/rv1909.py spaRV1909_vpl.txt kjv.json rv.json
# eBible fits the text to the KJV's verse numbers: where the Reina-Valera numbers differently (Jonah 1:17 = Jonás 2:1 and
# about 15 other chapter ends) the slot is empty and the extra verse is joined to the chapter's last verse.
import json, re, sys, collections
src, kjvp, out = sys.argv[1:4]
kjv = json.load(open(kjvp, encoding="utf-8"))
CODES = "GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB PSA PRO ECC SOL ISA JER LAM EZE DAN HOS JOE AMO OBA JON MIC NAH HAB ZEP HAG ZEC MAL MAT MAR LUK JOH ACT ROM 1CO 2CO GAL EPH PHI COL 1TH 2TH 1TI 2TI TIT PHM HEB JAM 1PE 2PE 1JO 2JO 3JO JUD REV".split()
UP = "A-ZÁÉÍÓÚÑÜ"
# A printed Bible's drop cap: chapters open with a word or two in capitals ("EN el principio", "Y FUERON acabados",
# "DE SIETE años", "¡OH Jehová"), after the title in the Psalms. Only verse 1 is touched, and only capitals followed by
# a word that isn't, so inscriptions ("YO SOY EL QUE SOY") and the divine name JAH stay as printed. Each word takes the
# form it most often has elsewhere in this Bible ("fueron", but "Jehová"), and a sentence's first letter stays a capital.
lines = [l.rstrip("\n").split(" ", 2) for l in open(src, encoding="utf-8")]
forms = collections.Counter(w for l in lines for w in re.findall(r"\w+", l[2]) if not w.isupper())
def usual(w):
    low, cap = w.lower(), w[0] + w[1:].lower()
    return cap if forms[cap] > forms[low] else low
first = re.compile(rf"(^|[.:?!]\s+)([¡¿]?(?:[{UP}]\s)?)([{UP}]{{2,}}(?:\s[{UP}]{{1,3}}\b)?(?:\s[{UP}]{{2,}})?)(?=[\s,;:.!?]+(\S+))")
def drop_cap(text):
    for m in first.finditer(text):
        run, nxt = m[3], m[4].strip("¡¿,.;:!?()")
        if "JAH" in run.split() or (nxt.upper() == nxt and any(ch.isalpha() for ch in nxt)): continue
        words = [usual(w) for w in run.split()]
        if not m[2].strip("¡¿"): words[0] = words[0][0].upper() + words[0][1:]
        return text[:m.start(3)] + " ".join(words) + text[m.end(3):]
    return text
bible = [[[] for _ in book] for book in kjv]
changed = collections.Counter()
for line in open(src, encoding="utf-8"):
    m = re.match(r"(\S+) (\d+):(\d+) (.*)", line.rstrip("\n"))
    b, c, v, text = CODES.index(m[1]), int(m[2]) - 1, int(m[3]) - 1, m[4]
    text = text.replace("[", "").replace("]", "")
    new = drop_cap(text) if v == 0 else text
    if new != text: changed[re.search(rf"[{UP}]{{2,}}", text)[0]] += 1
    ch = bible[b][c]
    while len(ch) < v: ch.append("")
    ch.append(new.strip())
diffs = []
for b, book in enumerate(kjv):
    for c, ch in enumerate(book):
        n = len(bible[b][c])
        if n < len(ch): bible[b][c] += [""] * (len(ch) - n)
        if n != len(ch): diffs.append((CODES[b], c + 1, len(ch), n))
        for v, t in enumerate(bible[b][c]):
            if not t and (v < len(ch) and ch[v]): diffs.append((CODES[b], c + 1, v + 1, "empty"))
json.dump(bible, open(out, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("drop caps fixed:", sum(changed.values()), changed.most_common(12))
print("chapters or verses differing from KJV:", diffs[:40], len(diffs))
