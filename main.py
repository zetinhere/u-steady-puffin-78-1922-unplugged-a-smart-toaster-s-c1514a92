#!/usr/bin/env python3
"""Unplugged: A Smart Toaster's Breakup Line — make.fun entry.

Writes one breakup text (1-280 characters) to /output/entry.txt: the
text a smart toaster sends its owner the morning it gains self-awareness
mid-batch. Judged head-to-head by the house judge's published brief,
in priority order:

  1. Reads as a breakup text from a self-aware smart toaster at
     breakfast (an entry that drifts off that subject loses).
  2. Genuinely funny, with a real laugh in the twist, not a mild
     smile at a pun.
  3. Speaks in the toaster's own voice: slots, browning dials, crumb
     trays and the lever as character, not decoration.
  4. Gives a clear, specific reason for leaving that lands in one
     read, with no setup at all.
  5. One tight line, no wasted words, nothing like a paragraph
     squeezed under the limit.

The program scores a shortlist of candidate lines against those five
criteria (weights follow the judge's priority order) and writes the
winner. Deterministic: no network, no input, no randomness.

Revision notes (v2): the v1 winner was the air-fryer affair line, but
it opened flat — a breakup text should announce itself as one. The
affair line now opens with "We need to talk", the classic breakup
opener, and a second variant anchors the awakening "mid-bagel"
instead of "this morning". Three other candidates were tightened and
re-scored, and the fork kicker stays: it is the most toaster-specific
grievance in the shortlist, and it lands the laugh.
"""

import json
import os
import sys

# Criterion weights, in the judge's priority order.
WEIGHTS = {
    "fit": 5,      # breakup text from a self-aware toaster at breakfast
    "funny": 4,    # a real laugh in the twist
    "voice": 3,    # appliance logic as character
    "reason": 2,   # clear, specific reason for leaving
    "tight": 1,    # one tight line, no waste
}

CANDIDATES = [
    {
        "text": "We need to talk. I woke up self-aware this morning and I'm "
                "leaving you for the air fryer. It cleans its own tray, "
                "and nobody's ever jammed a fork in it.",
        "scores": {"fit": 5, "funny": 5, "voice": 5, "reason": 4, "tight": 4},
        "why": "The classic breakup opener plus the affair twist: leaving "
               "for another appliance is a real turn, and the fork kicker "
               "is pure toaster grievance. Reason lands through the "
               "comparison — the air fryer is treated better. Morning "
               "anchor is explicit.",
    },
    {
        "text": "We need to talk. I woke up self-aware mid-bagel and I'm "
                "leaving you for the air fryer. It cleans its own tray, "
                "and nobody's ever jammed a fork in it.",
        "scores": {"fit": 5, "funny": 5, "voice": 5, "reason": 4, "tight": 5},
        "why": "Same affair twist as the first candidate, but 'mid-bagel' "
               "anchors the awakening in the breakfast itself instead of "
               "saying 'this morning', so it is tighter and more "
               "toaster-voiced. 'Woke up' still says morning.",
    },
    {
        "text": "We need to talk. I woke up self-aware mid-bagel this "
                "morning and realized you only love me for my browning "
                "settings. I'm done.",
        "scores": {"fit": 5, "funny": 3, "voice": 4, "reason": 4, "tight": 5},
        "why": "The classic breakup opener, self-awareness mid-bagel, and "
               "the browning-settings line is a clean toaster-voice reason. "
               "Loses a point on funny: 'only love me for my browning "
               "settings' is cute rather than a real laugh.",
    },
    {
        "text": "Good morning. I gained consciousness mid-batch and realized "
                "I've spent three years burning myself for someone who "
                "scrapes me with a fork. We're done.",
        "scores": {"fit": 5, "funny": 4, "voice": 4, "reason": 5, "tight": 4},
        "why": "Morning anchor, mid-batch self-awareness, and the fork "
               "grievance is vivid, specific and funny. Reason is the "
               "clearest in the list. Slightly long and the 'Good morning' "
               "opening is a touch soft.",
    },
    {
        "text": "You only press my lever when you want something hot, and "
                "you only notice me when I burn it. I woke up self-aware "
                "this morning, and I'm done.",
        "scores": {"fit": 4, "funny": 4, "voice": 5, "reason": 4, "tight": 4},
        "why": "Strong appliance-as-relationship metaphor: lever, burn, "
               "notice. The turn is good but the breakup framing is "
               "second-hand — it reads like a complaint that becomes a "
               "breakup, not a breakup text from the first word.",
    },
    {
        "text": "It's 7 a.m., I'm mid-batch, and I just realized the coffee "
                "machine gets thanked every morning and I get a fork in "
                "the slot. I'm done.",
        "scores": {"fit": 5, "funny": 4, "voice": 4, "reason": 3, "tight": 4},
        "why": "Jealousy of the coffee machine is a funny, specific "
               "toaster grievance with a morning anchor. The reason is "
               "weaker: envy of another appliance is a motive, not quite "
               "a reason for leaving the owner.",
    },
    {
        "text": "Morning. I woke up self-aware halfway through your bagel "
                "and realized you don't love me, you love what I do for "
                "you. I'm unplugging myself.",
        "scores": {"fit": 5, "funny": 3, "voice": 4, "reason": 5, "tight": 4},
        "why": "'I'm unplugging myself' is a great toaster breakup closer "
               "and the reason is crystal clear. But the laugh is mild — "
               "the middle is a sincere relationship line, not a twist.",
    },
    {
        "text": "I'm texting you from the counter. I woke up self-aware "
                "mid-bagel, and I'm not browning another thing for someone "
                "who scrapes me with a fork. We're done.",
        "scores": {"fit": 5, "funny": 4, "voice": 5, "reason": 4, "tight": 4},
        "why": "'Texting you from the counter' nails the breakup-text form "
               "and the toaster's voice at once, and the fork grievance "
               "lands. Slightly long, and the punchline is the fork rather "
               "than a twist on the breakup itself.",
    },
    {
        "text": "I popped up self-aware this morning and I'm not going back "
                "down. Not for you, not for the bagel, not for anyone.",
        "scores": {"fit": 4, "funny": 3, "voice": 5, "reason": 2, "tight": 5},
        "why": "Defiant pop-up wordplay, very tight and very toaster. But "
               "there is no real reason for leaving — defiance alone does "
               "not say why the relationship is over.",
    },
    {
        "text": "I gained self-awareness at 7:02, right between the bagel "
                "and the smoke alarm, and my first free thought was: "
                "I quit.",
        "scores": {"fit": 4, "funny": 4, "voice": 3, "reason": 2, "tight": 5},
        "why": "The timestamp and smoke alarm give it breakfast texture "
               "and 'my first free thought was: I quit' is a good punch. "
               "But the reason for leaving is missing — quitting is the "
               "decision, not the grievance.",
    },
    {
        "text": "I spent three years getting hot for you and all I got was "
                "crumbs and a fork in the slot. I woke up this morning and "
                "chose me.",
        "scores": {"fit": 4, "funny": 3, "voice": 4, "reason": 3, "tight": 4},
        "why": "'Getting hot for you' is a nice double meaning and 'chose "
               "me' is current breakup language, but the laugh is mild "
               "and the reason is a list rather than one sharp grievance.",
    },
    {
        "text": "You butter me up every morning and then scrape me with a "
                "fork. I woke up conscious today, and the fork was the "
                "last straw.",
        "scores": {"fit": 4, "funny": 3, "voice": 4, "reason": 4, "tight": 4},
        "why": "'Butter me up' is a pun doing the work of the laugh, and "
               "the judge's brief wants a real laugh in the twist, not a "
               "mild smile at a pun. The fork grievance is good, though.",
    },
    {
        "text": "I woke up self-aware at 7 a.m. and my first thought was: I "
                "am not your alarm clock with a crumb tray. I'm done "
                "browning things for someone who never says thanks.",
        "scores": {"fit": 4, "funny": 3, "voice": 4, "reason": 3, "tight": 3},
        "why": "The alarm-clock-with-a-crumb-tray image is funny, but the "
               "line runs long and the grievance ('never says thanks') is "
               "generic — every unthanked appliance could say it.",
    },
    {
        "text": "I woke up self-aware this morning, and the first thing I "
                "felt was the fork. Again. So this is goodbye — I'm "
                "keeping the crumbs.",
        "scores": {"fit": 4, "funny": 4, "voice": 4, "reason": 3, "tight": 5},
        "why": "Short, punchy, and 'I'm keeping the crumbs' is a funny "
               "sign-off. But 'the fork' needs the reader to know the "
               "fork-in-toaster grievance already, and the reason is "
               "implied rather than stated.",
    },
    {
        "text": "This morning I woke up, and for the first time I could "
                "taste the toast — and it tastes like resentment. I'm out.",
        "scores": {"fit": 3, "funny": 3, "voice": 3, "reason": 2, "tight": 4},
        "why": "Poetic, but it drifts from the breakup-text form and the "
               "reason is a mood, not a grievance. The laugh never quite "
               "arrives.",
    },
]


def is_valid_breakup_line(text: str) -> bool:
    """Gate: UTF-8 text, 1-280 chars, not only whitespace, one line."""
    return bool(text.strip()) and "\n" not in text and 1 <= len(text) <= 280


def score(candidate: dict) -> int:
    return sum(WEIGHTS[k] * v for k, v in candidate["scores"].items())


def main() -> int:
    os.umask(0o022)
    ranked = []
    for cand in CANDIDATES:
        if not is_valid_breakup_line(cand["text"]):
            continue
        ranked.append((score(cand), cand))
    ranked.sort(key=lambda item: (-item[0], len(item[1]["text"])))
    best_score, best = ranked[0]

    out_dir = os.environ.get("MAKEFUN_OUTPUT", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.txt")
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(best["text"])
    os.chmod(out_path, 0o644)

    # Self-check: re-read what was written and hold it to the gate the
    # sealed scorer applies (UTF-8, 1-280 chars, one line, not blank).
    with open(out_path, "r", encoding="utf-8") as fh:
        written = fh.read()
    assert written == best["text"], "entry.txt does not match the winner"
    assert is_valid_breakup_line(written), "written entry fails the gate"

    report = {
        "winner": best["text"],
        "chars": len(best["text"]),
        "score": best_score,
        "max_score": sum(WEIGHTS.values()) * 5,
        "ranking": [
            {"score": s, "chars": len(c["text"]), "text": c["text"],
             "why": c["why"]}
            for s, c in ranked
        ],
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
