# Learning Knight

A home vocabulary program: short daily sessions, word parts, spaced review,
flash-and-spell, a Missed words list and a parent view. Band 6, Module 1 so far:
Unit 1.1 (un-, re-, dis-) and Unit 1.2 (mis-, pre-, power words analyze and conclude).
Units unlock in order; reviews and the Missed words list draw on every unit learned.

Placement check (home screen): an adaptive vocabulary + reading check, Grade 4 to
Professional. 10 questions per level, a level passes at 90%. Vocabulary first (with
"I don't know" so guesses don't inflate it), then 8 word-part items, then reading:
two original passages per level, five questions each (detail, word in context,
inference, main idea, author's purpose). Results: secure level for each, a reading
skill profile, the words missed. It doesn't change word mastery.

Live site: https://luisfreire1824.github.io/LearningKnight/

## Files
- `index.html` — the whole app (one page, no build step)
- `content/course.json` — the units, in order. A new unit is a new JSON file in
  `content/` plus one line here.
- `firebase-config.js` — Firebase web settings. Empty = this-device-only mode.
- `firestore.rules` — database security rules (paste into the Firebase console)
- `tools/check_items.py` — run before shipping any unit (checks every unit, and
  that words and item ids are unique across the course):
  `python3 tools/check_items.py content/course.json`
- `content/assessment-en.a.json` — placement check, form A. Check it with
  `python3 tools/check_assessment.py content/assessment-en.a.json` (answer-length
  giveaways, one question per reading skill, passage difficulty rising by level).

## Where progress is saved
- Signed in with Google: in your account, synced between phone and laptop.
  Each learner belongs to the person who created it.
- Not signed in: in the browser on that device. Signing in later offers to
  move those learners into the account.

## Sharing a learner's progress
The learner's owner opens Parent view → Share progress → Create invite link and
sends it. Whoever opens it signed in becomes a helper: the learner appears
under "Shared with you" and opens to their Parent view. Helpers can see
progress and review sentences, but can't change progress or who has access.
The owner can remove a helper at any time; links expire after 7 days.

## Firebase setup (one time)
1. Firebase console → Add project (e.g. `learning-knight`). Analytics not needed.
2. Build → Authentication → Get started → Sign-in method → enable **Google**.
3. Authentication → Settings → Authorized domains → add `luisfreire1824.github.io`.
4. Build → Firestore Database → Create database (production mode, a US region).
   Then the Rules tab → paste `firestore.rules` → Publish.
   Re-publish whenever `firestore.rules` changes in this repo.
5. Project settings → Your apps → Web app (`</>`) → register it (no Hosting).
   Copy the `firebaseConfig` values into `firebase-config.js`.

The config values are not secrets; access is enforced by the rules and the
authorized domains list.
