# Data engineering Fundamentals, F2 Change over time: diagnostic (10 questions, 90% to pass).
# Correct answer first; the app shuffles. concept = what a miss says to learn.
def Q(id, concept, stem, options, why, table=None):
    q = {"id": "de-f2-" + id, "concept": concept, "stem": stem, "options": options, "answer": 0, "why": why}
    if table: q["table"] = table
    return q

# One customer's type 2 versions, shown with the two questions that use it.
VERSIONS = {"cols": ["customer_sk", "customer_id", "region", "effective_from", "effective_to", "is_current"],
            "rows": [["101", "C-77", "East", "2024-01-01", "2026-02-28", "N"], ["245", "C-77", "West", "2026-03-01", "9999-12-31", "Y"]]}

F2 = [
  Q("type1", "SCD type 1: overwrite",
    "A customer moves from the East region to the West region in March. Region is a type 1 attribute. What does a Q1 sales-by-region report show for this customer?",
    ["All of Q1 rolls up under West", "Jan, Feb East; March under West", "All of Q1 rolls up under East", "Q1 split evenly across both"],
    "Type 1 overwrites the old value, so history is restated: every past sale now rolls up to West, as if the customer had always been there."),
  Q("type2", "SCD type 2: new row per change",
    "Same customer, but region is now a type 2 attribute. What does the Q1 sales-by-region report show?",
    ["Jan and Feb under East, March under West", "All of Q1 under West, the current value", "All of Q1 under East, the original value", "Only March sales; earlier rows are dropped"],
    "Type 2 adds a new row (new surrogate key) when region changes. Sales made before March point to the East version, sales after to the West version, so history stays as it was."),
  Q("cols", "Type 2 housekeeping columns",
    "Which columns does a type 2 dimension typically add to manage versions?",
    ["Effective date, end date and a current flag", "A created-by user and a last-modified user", "A row hash and the source file's name only", "A version number for each column that changes"],
    "Effective and end dates say when each version applied; a current-row flag makes \"latest version\" queries simple. Row hashes help detect changes, but don't manage versions on their own.",
    VERSIONS),
  Q("lookup", "Joining facts to the right version",
    "A sale on March 10 is loaded for customer C-77, whose versions are shown here. Which customer key should the fact row get?",
    ["245, the version in effect then", "101, the customer's first version", "Both keys, one fact row for each", "C-77, the ID from the source"],
    "The fact gets the surrogate key of the version whose effective dates cover the transaction date. That's what keeps type 2 history correct.",
    VERSIONS),
  Q("type3", "SCD type 3: previous value column",
    "Sales territories are being redrawn once. For a year, leadership wants to see results under both the old and the new territories. Which approach fits best?",
    ["Type 3: current and prior territory columns", "Type 1: overwrite territory with the new one", "Type 2: add a new row per changed customer", "Type 0: keep the original territory forever"],
    "Type 3 keeps the current value and one previous value side by side, so every row can be reported both ways. It suits a single, planned reorganization, not ongoing change."),
  Q("type0", "SCD type 0: never changes",
    "A customer's credit score at signup should never change, even when the source system updates the current score. How do you treat it?",
    ["Type 0: keep the original value as is", "Type 1: overwrite it with each update", "Type 2: add a row for each new score", "Type 3: keep the current and prior score"],
    "Type 0 means the attribute is fixed at its original value. The current score, if needed, is a separate attribute with its own type."),
  Q("process", "Dimension history vs process facts",
    "A support ticket's status changes several times a day, and the business wants average hours between status changes. Where should status changes be recorded?",
    ["A fact with one row per status change", "Type 2 history on the ticket dimension", "Type 1 status overwritten on the ticket", "A type 3 column with the previous status"],
    "Events you want to measure belong in a fact table (a transaction or accumulating snapshot), not as dimension versions. Type 2 is for descriptive attributes, not workflow timing."),
  Q("latefact", "Late-arriving facts",
    "A sale from 10 days ago arrives today. Since then, the customer changed region (type 2). Which customer version should the sale join to?",
    ["The version in effect that day", "The current version, as of today", "The first version ever recorded", "Whichever version was loaded last"],
    "Late facts look up the version effective on the event date, not the load date. Using the current version would put the sale in the wrong region."),
  Q("latedim", "Late-arriving dimensions",
    "Orders arrive for a customer who isn't in the customer dimension yet; their details come tomorrow. What is the common approach?",
    ["Add a placeholder row, update it later", "Drop the orders until the customer exists", "Load the orders with a null customer key", "Hold all of today's orders until tomorrow"],
    "An inferred (placeholder) member keeps the facts loaded with a valid key. When the real details arrive, the placeholder is updated in place."),
  Q("mini", "Rapidly changing attributes: mini-dimension",
    "Customer age band and income band change often and are making a type 2 customer dimension grow very fast. What is a common fix?",
    ["Move them into a mini-dimension", "Switch the whole dimension to type 1", "Store the bands as text on each fact", "Rebuild the dimension once a month"],
    "A mini-dimension holds the combinations of fast-changing bands, with its own key on the fact. The main customer dimension stops churning, and history is still kept."),
]
