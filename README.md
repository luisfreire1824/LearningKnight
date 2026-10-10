# Learning Knight

A home vocabulary program: short daily sessions, word parts, spaced review,
flash-and-spell, a Missed words list and a parent view. This is the Unit 1.1
prototype (Band 6, prefixes un-, re-, dis-).

## Files
- `index.html` — the whole app (one page, no build step)
- `content/` — lesson content as JSON. New units are new files here.
- `tools/check_items.py` — run before shipping any unit:
  `python3 tools/check_items.py content/vocab-en.b6.m1.u1.json`
  It flags multiple-choice giveaways, missing definitions and thin question banks.

## Where progress is saved
On GitHub Pages, progress is saved in the browser on each device.
Syncing across phone and laptop comes with the Firebase step (planned).
