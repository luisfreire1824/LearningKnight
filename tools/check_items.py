"""Learning Knight content check.

Run before any unit ships:
    python3 tools/check_items.py content/<unit>.json

Flags multiple-choice giveaways (length, part of speech), lopsided yes/no
answers, and gaps in coverage. Exit code 1 if anything is flagged.
Part of speech comes from the Academic Vocabulary List lexicon in
tools/pos_lexicon.json (Gardner & Davies, academicwords.info).
"""
import json, re, sys, pathlib
from collections import Counter

HERE = pathlib.Path(__file__).parent
LEX = json.loads((HERE / "pos_lexicon.json").read_text())
SPREAD = 1.20  # sentence options: longest / shortest must stay within 20%


def tags(word):
    """Possible (part of speech, form) pairs for a single-word option."""
    w = word.lower()
    out = set()
    for p in LEX.get(w, []):
        out.add((p, "base"))
    for suf, form, fix in (("ed", "ed", [""]), ("d", "ed", [""]), ("ied", "ed", ["y"]),
                           ("s", "s", [""]), ("es", "s", [""])):
        if w.endswith(suf):
            stem = w[: -len(suf)]
            for f in fix:
                for p in LEX.get(stem + f, []):
                    if p in ("v", "n"):
                        out.add((p if form == "ed" else p, form))
    return out


def definable(word, unit):
    """After a first wrong answer the app shows what each choice means, so every
    single-word option needs a definition: a unit word (any simple inflection)
    or a glossary entry."""
    w = word.lower()
    cards = {x["word"] for x in unit["words"]}
    gloss = set(unit.get("glossary", {}))
    for c in (w, w[:-2] if w.endswith("ed") else None, w[:-1] if w.endswith("d") else None,
              w[:-3] + "y" if w.endswith("ied") else None, w[:-1] if w.endswith("s") else None):
        if c and (c in cards or c in gloss):
            return True
    return False


def check_mcq(item, problems):
    opts, ans = item["options"], item["answer"]
    iid = item["id"]
    if not 0 <= ans < len(opts):
        problems.append(f"{iid}: answer index out of range")
        return
    if len(set(o.lower() for o in opts)) != len(opts):
        problems.append(f"{iid}: duplicate options")
    single = all(re.fullmatch(r"[A-Za-z-]+", o) for o in opts)
    lens = [len(o) for o in opts]
    correct = lens[ans]
    others = [l for i, l in enumerate(lens) if i != ans]
    if single:
        if correct > max(others):
            problems.append(f"{iid}: correct option '{opts[ans]}' is the unique longest single word")
        tagsets = [tags(o) for o in opts]
        unknown = [o for o, t in zip(opts, tagsets) if not t]
        if unknown:
            problems.append(f"{iid}: part of speech unknown for {unknown}; check by hand")
        else:
            shared = set.intersection(*tagsets)
            if not shared:
                problems.append(f"{iid}: options don't share a part of speech/form: "
                                + ", ".join(f"{o}={sorted(t)}" for o, t in zip(opts, tagsets)))
    else:
        if max(lens) / min(lens) > SPREAD:
            problems.append(f"{iid}: option lengths spread {min(lens)}-{max(lens)} chars (over 20%)")
        if correct > max(others) * SPREAD:
            problems.append(f"{iid}: correct option is >20% longer than the next")


def main(path):
    unit = json.loads(pathlib.Path(path).read_text())
    problems, notes = [], []
    words = {w["key"] for w in unit["words"]}
    mcqs = [i for i in unit["items"] if i["type"] == "mcq"]
    mcqs += [s["phone"] for s in unit.get("sentence", [])]
    mcqs += unit["passage"]["questions"]
    for it in mcqs:
        check_mcq(it, problems)
        if all(re.fullmatch(r"[A-Za-z-]+", o) for o in it["options"]):
            undefined = [o for o in it["options"] if not definable(o, unit)]
            if undefined:
                problems.append(f"{it['id']}: no definition for {undefined} (add to glossary; shown after a first wrong answer)")

    # yes/no balance per group
    groups = {}
    for it in unit["items"]:
        if it["type"] == "binary":
            groups.setdefault(it["use"], []).append(it["answer"])
    for g, answers in groups.items():
        c = Counter(answers)
        top = max(c.values()) / len(answers)
        if len(answers) >= 4 and top > 0.7:
            problems.append(f"binary group '{g}': {top:.0%} of answers are the same option")

    # coverage: every word needs 2+ meaning items and spelling tips
    per = Counter(w for it in unit["items"] for w in it.get("words", []))
    for w in words:
        if per[w] < 2:
            problems.append(f"word '{w}': only {per[w]} meaning items (need 2+ for review)")
        # Missed-words practice must be able to ask a different multiple-choice question than the one missed.
        # Story questions don't count: they only make sense right after the story.
        n_mc = sum(1 for it in unit["items"] if it["type"] == "mcq" and w in it.get("words", []))
        if n_mc < 2:
            problems.append(f"word '{w}': only {n_mc} stand-alone multiple-choice item(s) (need 2+ so practice doesn't repeat the missed one)")
    for w in unit["words"]:
        if not w.get("spelling"):
            notes.append(f"word '{w['key']}': no spelling tips (generic feedback will be used)")
        fam = {f.lower() for f in w.get("family", [])}
        opp = {o["w"].lower() for o in w.get("opposite", [])}
        if fam & opp:
            problems.append(f"word '{w['key']}': {sorted(fam & opp)} listed as both family and opposite")
        for s in w.get("spelling", []):
            if s["slip"] == w["word"]:
                problems.append(f"word '{w['key']}': correct spelling listed as a slip")

    # passage tags point at real words
    for para in unit["passage"]["paragraphs"]:
        for tag in re.findall(r"\[([^\]]+)\]", para):
            key = tag.split("|")[-1]
            if key not in words:
                problems.append(f"passage tag [{tag}] doesn't match a unit word")

    print(f"{unit['id']} v{unit['version']}: {len(mcqs)} multiple-choice items, "
          f"{sum(len(v) for v in groups.values())} yes/no items checked")
    for n in notes:
        print("  note:", n)
    for p in problems:
        print("  FLAG:", p)
    print("  answer order: shuffled by the app at run time")
    print("PASS" if not problems else f"FAIL ({len(problems)} flagged)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
