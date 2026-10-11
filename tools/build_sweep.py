"""Build a sweep level: each word's wrong choices are other words' meanings (same part of speech,
not near-synonyms), picked so the right answer is never the unique longest and lengths stay within 30%."""
import random, json, sys, importlib
def build(mod, level, name, seed=7):
    m = importlib.import_module(mod)  # e.g. sweep_g9_source
    rows = [l.split("|") for l in m.ITEMS.strip().splitlines()]
    syn = {}
    for g in m.SYN:
        for w in g: syn.setdefault(w, set()).update(g)
    rnd = random.Random(seed); items, bad = [], []
    for w, pos, d, s in rows:
        assert "[" in s, w
        L = len(d)
        pool = [r for r in rows if r[0] != w and r[1] == pos and r[0] not in syn.get(w, ()) and w not in syn.get(r[0], ())]
        ok = [r for r in pool if 0.77 * max(L, len(r[2])) <= min(L, len(r[2])) or abs(len(r[2]) - L) <= 3]
        rnd.shuffle(ok)
        pick = None
        for i in range(len(ok)):
            for j in range(i + 1, len(ok)):
                for k in range(j + 1, len(ok)):
                    c = [ok[i], ok[j], ok[k]]; Ls = [L] + [len(x[2]) for x in c]
                    if max(Ls) / min(Ls) <= 1.3 and L <= max(Ls[1:]) and len({x[2] for x in c}) == 3:
                        pick = c; break
                if pick: break
            if pick: break
        if not pick: bad.append((w, pos, L, len(pool))); continue
        items.append({"id": f"sw-{level}-{w}", "word": w, "pos": pos, "sentence": s, "options": [d] + [x[2] for x in pick], "answer": 0})
    return {"id": level, "name": name, "items": items}, bad
if __name__ == "__main__":
    lv, bad = build(sys.argv[1], sys.argv[2], sys.argv[3])
    print(len(lv["items"]), "items;", "unplaced:", bad)
    json.dump(lv, open(sys.argv[4], "w"), indent=1, ensure_ascii=False)
