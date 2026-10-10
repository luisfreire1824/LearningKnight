"""Learning Knight placement check: content check.

    python3 tools/check_assessment.py content/assessment-en.a.json

Flags answer giveaways (the correct choice is the longest, or choices differ a lot
in length), duplicate ids, and reading passages whose difficulty is out of order.
Prints a Flesch-Kincaid grade per passage. It's a rough guide: it counts sentence
and word length, not how hard the ideas or words are.
Exit code 1 if anything is flagged.
"""
import json, re, sys

SPREAD_PHRASE = 1.30   # vocabulary meanings: longest / shortest
SPREAD_READING = 1.20  # reading answers: same rule as unit sentence choices
LEVEL_ORDER = ["g4", "g6", "g8", "g10", "g12", "col", "pro"]


def syllables(word):
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    if len(w) <= 3:
        return 1
    w = re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "", w)
    w = re.sub(r"^y", "", w)
    return max(1, len(re.findall(r"[aeiouy]{1,2}", w)))


def fk_grade(text):
    sentences = max(1, len(re.findall(r'[.!?]+(?:\s|$|")', text)))
    words = re.findall(r"[A-Za-z][A-Za-z'-]*", text)
    syl = sum(syllables(w) for w in words)
    return 0.39 * len(words) / sentences + 11.8 * syl / len(words) - 15.59, len(words)


def check_options(iid, opts, answer, spread, problems):
    lens = [len(o) for o in opts]
    if len(set(o.lower() for o in opts)) != len(opts):
        problems.append(f"{iid}: duplicate options")
    if lens[answer] > max(l for i, l in enumerate(lens) if i != answer):
        problems.append(f"{iid}: correct option is the unique longest")
    single = all(re.fullmatch(r"[A-Za-z-]+", o) for o in opts)
    if not single and max(lens) / min(lens) > spread:
        problems.append(f"{iid}: option lengths spread {min(lens)}-{max(lens)} chars (over {round((spread - 1) * 100)}%)")


def main(path):
    A = json.load(open(path))
    problems, ids = [], []
    for lv in A["vocab"]["levels"] + [{"id": "parts", "items": A["vocab"]["parts"]}]:
        for it in lv["items"]:
            ids.append(it["id"])
            check_options(it["id"], it["options"], it["answer"], SPREAD_PHRASE, problems)
            if "[" not in it["sentence"]:
                problems.append(f"{it['id']}: sentence doesn't mark the tested word with [ ]")
        if lv["id"] != "parts" and len(lv["items"]) != 10:
            problems.append(f"vocab level {lv['id']}: {len(lv['items'])} items (10 keeps the 90% pass mark meaningful: 9 of 10)")
    last = None
    for lv in A["reading"]["levels"]:
        grades = []
        for p in lv["passages"]:
            g, n = fk_grade(" ".join(p["paragraphs"]))
            grades.append(g)
            print(f"  {lv['id']:4} {p['title'][:34]:34} grade {g:4.1f}  {n} words")
            skills = sorted(q["skill"] for q in p["questions"])
            if skills != sorted(A["skills"]):
                problems.append(f"{p['id']}: needs one question per skill, has {skills}")
            for q in p["questions"]:
                ids.append(q["id"])
                check_options(q["id"], q["options"], q["answer"], SPREAD_READING, problems)
                if q["skill"] == "vocab":
                    m = re.search(r"what does (\w+) mean", q["stem"])
                    if not m or m.group(1) not in " ".join(p["paragraphs"]):
                        problems.append(f"{q['id']}: tested word not found in the passage")
        avg = sum(grades) / len(grades)
        if last is not None and avg <= last:
            problems.append(f"reading level {lv['id']}: average grade {avg:.1f} isn't above the level below ({last:.1f})")
        last = avg
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        problems.append(f"duplicate ids: {sorted(dup)}")
    levels = [l["id"] for l in A["vocab"]["levels"]]
    if levels != [l for l in LEVEL_ORDER if l in levels]:
        problems.append("vocab levels out of order")
    print(f"{A['id']} form {A['form']} v{A['version']}: {len(ids)} questions")
    for p in problems:
        print("  FLAG:", p)
    print("PASS" if not problems else f"FAIL ({len(problems)} flagged)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
