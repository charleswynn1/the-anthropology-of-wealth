#!/usr/bin/env python3
"""
MoneyMath — General TTS Audio Generation Pipeline
Generates narration audio from script sections using ElevenLabs.

Usage:
  1. Edit SECTIONS below with your script text
  2. Set PROJECT_NAME to your project folder name
  3. Run: python3 generate_audio.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from elevenlabs import ElevenLabs

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

from cost_tracker import log_elevenlabs_cost

API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not API_KEY:
    print("ERROR: ELEVENLABS_API_KEY not found in .env")
    sys.exit(1)

client = ElevenLabs(api_key=API_KEY)

# ══════════════════════════════════════════════════════════
# CONFIGURATION — Edit these for each new video
# ══════════════════════════════════════════════════════════

PROJECT_NAME = "origin-of-debt"  # Folder name under public/ and src/

VOICE_ID = "qI0RnYbkDdDRolu3NKE2"
MODEL = "eleven_multilingual_v2"
FMT = "mp3_44100_128"
VOICE_SETTINGS = {
    "stability": 0.50,
    "similarity_boost": 0.65,
    "style": 0.10,
    "use_speaker_boost": True,
    "speed": 1.1,
}

# ══════════════════════════════════════════════════════════
# SCRIPT SECTIONS — Each tuple: (filename, narration text)
# Split long sections into multiple audio files for better
# visual sync (e.g., s3_data_pt1, s3_data_pt2, etc.)
# ══════════════════════════════════════════════════════════

SECTIONS = [
    ("s1_hook", """There is a word. Five thousand years old. And it means freedom.

Okay. It has nothing to do with politics or religion or the freedom your history teacher described.

It means your debt has been cancelled.

That is what freedom meant. To the first people who ever needed a word for it.

And that changes everything you think you know about debt."""),

    ("s2_the_word", """Let me take you back five thousand years to ancient Sumer, what is now Iraq.

Before coins. Before banks. There was already debt.

Farmers along the Tigris and Euphrates borrowed when the harvest failed. Grain from the temple. Seed from the palace. And the temple wrote it down on wet clay: who borrowed, how much, when it was due, and how much extra they owed for the wait.

Hmm. That clay rectangle is the oldest financial document in human history.

Next to the interest, scribes used a word that translates to calves. The first lenders modeled debt growth on a cow producing offspring. You lend the cow, you get back the cow plus the calves. The debt grew the same way, built into the structure, whether the harvest came in or not.

When harvests were bad, farmers borrowed again. The interest grew faster than the crops. Over time a farmer might lose his field. His home. His children, pledged to work in the temple.

Then the king declared a misharum. A clean slate. All agricultural debts. Gone.

The Sumerians of Lagash called that feeling amargi. From ama, mother. And gi, return.

Yeah. Return to mother. When your debt was cancelled, you got to go home.

The oldest word for freedom in any human language. It was not about politics. It described one specific financial event: the moment the number dropped to zero.

Freedom was a financial concept before it was anything else."""),

    ("s3_ancient_wisdom", """The Babylonians were mathematicians. At the standard interest rate in Babylon, about twenty percent per year, a debt doubled in approximately five years. They calculated that. Carved it into clay.

Then they looked at how fast the economy grew: the crops, the harvests, the actual wealth in people's hands.

It did not double in five years. Not even close.

They understood what that gap meant. If you let debt compound and never cancel it, debt will always grow faster than the wealth to repay it, every time, without a single exception. They taught this to teenagers in school, not as an opportunity but as a warning.

So Hammurabi, king of Babylon around seventeen fifty four BCE, capped interest rates. Twenty percent for silver. Thirty three percent for grain. No more. And he issued four separate debt cancellation decrees during his reign. Scholars have identified at least thirty documented cancellations across a thousand years of ancient Mesopotamia.

They did it because they understood the math, not out of generosity.

Hammurabi's maximum interest rate was thirty three percent.

Yeah. The average payday loan in the United States today charges four hundred percent annual interest.

We have not progressed beyond Babylon. We removed the protections Babylon had and replaced them with nothing."""),

    ("s4_dismantling_pt1", """Okay. So what happened? How did we end up here? The release valve was taken apart. Piece by piece. Over centuries.

For roughly a thousand years, the Catholic Church declared that charging interest was a mortal sin. Christianity, Islam, and Judaism all arrived at the same conclusion: turning scarcity and need into personal gain is not what money is for.

But the Church also needed money. So the same institution that banned usury developed workarounds. The Church banned usury and did it anyway. Just under different names.

Then came John Calvin. In the fifteen forties, one letter argued that money lent for productive purposes genuinely creates value, and a modest fee for it was not a sin.

One letter. One generation. The usury prohibition was gone. The merchant class had been waiting for exactly this permission.

In England, if you could not pay your debt, you went to prison. Not to work it off. You just sat. In eighteen twenty four, a man named John Dickens owed forty pounds to a baker. Arrested. Taken to the Marshalsea debtors prison in London.

His son was twelve years old. That boy, Charles, walked past the prison every morning on his way to work in a boot blacking factory.

Hmm. He never forgot it. He turned that memory into the sharpest social critique of his era. A machine that trapped the poor in the very condition it claimed to punish them for."""),

    ("s4_dismantling_pt2", """In eighteen sixty five, the United States abolished slavery. Within twenty years, the Southern planter class replaced it with something that functioned almost identically. Sharecropping.

A freed Black family farmed the land and split the crop. In theory. In practice they also needed seed, tools, and food, and the only place to get it was the landowner's store. On credit. At prices set by the landowner. Recorded in a ledger the farmer could not read.

At the end of the year, the landowner read the accounting.

Yeah. You still owe us.

Enough to stay another year. The landowners controlled the numbers. The farmers could not verify them. The law backed up the ledger.

In Alabama in nineteen oh eight, a Black farm laborer named Alonzo Bailey took a fifteen dollar wage advance, then quit after a month. He was arrested. Convicted. Sentenced to hard labor. His crime: leaving a job after borrowing fifteen dollars. His case reached the Supreme Court. In nineteen eleven, the Court ruled the law violated the Thirteenth Amendment. Alabama immediately passed a new law that accomplished the same thing using different language.

In September of nineteen nineteen, in Elaine, Arkansas, a Black farmer named Robert L. Hill founded a union with one demand. He wanted to see the accounting. Black sharecroppers in his county received fifteen cents a pound for cotton selling at thirty five to forty cents on the open market. He hired an attorney and organized a meeting at a church.

More than two hundred Black people were killed in the response. One hundred twenty two Black residents were charged. Not one white person was prosecuted.

Hmm. The only people on trial were the ones who asked for a receipt.

His name is in almost none of the history books most Americans were ever handed."""),

    ("s5_modern_pt1", """September eighteenth, nineteen fifty eight. Fresno, California.

Sixty five thousand mailboxes opened that day. Inside each one was a small plastic rectangle with a person's name, a credit limit they had not applied for, and a credit card they had not asked for.

Bank of America printed sixty five thousand cards and mailed them to Fresno residents, chosen as a test city because it was isolated enough that if things went wrong, the experiment would not spread too fast.

Things went wrong immediately. The delinquency rate was supposed to be four percent. It came in at twenty two percent. Fraud was rampant. Joseph P. Williams resigned in scandal.

But the product kept going. By nineteen seventy, more than one hundred million unsolicited credit cards had been mailed to Americans who had not asked for them. Congress had to pass a law making the practice illegal.

The consumer credit revolution was not a response to consumer demand. Nobody asked for this. It was a deployment. Banks created the product, put it in people's hands before they had decided they wanted it, and built a multi trillion dollar industry on the obligations that followed.

The Fresno Drop modeled debt on the mail.

Yeah. The consumer debt era was born not with a consumer revolution. It was born with a mail carrier."""),

    ("s5_modern_pt2", """Okay. Nineteen eighty nine. Fair Isaac Corporation formalizes the FICO credit score. Calculated from your financial history.

It does not contain the word race.

It does not need to.

For millions of Black Americans in nineteen eighty nine, that financial history had been shaped by decades of the Federal Housing Administration refusing to back mortgages in Black neighborhoods. Redlining. From nineteen thirty four to nineteen sixty eight, federal policy denied Black Americans access to the primary wealth building tool of the postwar economy.

A mortgage creates credit history. Creates equity. It is one of the main inputs into the score. Black Americans were denied mortgages by federal policy for thirty four years. Then the credit score was invented to measure mortgage history.

The median credit score gap between Black and white Americans is approximately ninety one points. That gap is not measuring individual behavior. It is measuring structural exclusion, converted into a number.

And into that exclusion, something moved in. More than twenty three thousand payday lenders. More than twice the number of McDonald's locations in the country. Four hundred percent annual interest. Eight times more concentrated in Black and Latino neighborhoods than in white neighborhoods, after controlling for income and poverty rates.

Hmm. Race predicts where a payday lender opens its doors.

The company store had a different building, but the math was the same.

Yeah. We built in the minimum payment."""),

    ("s6_close", """Amargi. Return to mother.

The Babylonians treated that as engineering. Compound interest grows faster than any real economy. So the gap between what is owed and what can be repaid has to go somewhere. They decided it would go on the creditors. Through cancellation. Through the jubilee.

Modern financial systems made a different decision. The debtors absorb it. Permanently. Through minimum payments. Through four hundred percent interest that rolls over every two weeks.

The gap has to go somewhere. Ancient Babylon put it on the creditors. The modern system puts it on you.

The trap is not a force of nature. It is a deliberate design.

The Church banned usury and did it anyway. Calvin gave permission and the merchant class moved in. Debtors prisons trapped the poor. Emancipation was followed by sharecropping. Sharecropping by redlining. Redlining by the credit score. The credit score by the payday lender. At every step, the communities with the least power absorbed the most cost.

This is not your fault. You were born inside this machine.

Yeah. But now you can see it.

We inherited the debt but never the jubilee.

That understanding is not the end of the story. It is the beginning of asking a different question."""),
]

# ══════════════════════════════════════════════════════════
# GENERATION — No need to edit below this line
# ══════════════════════════════════════════════════════════

OUT = ROOT / f"projects/{PROJECT_NAME}/audio"
OUT.mkdir(parents=True, exist_ok=True)


def generate_tts():
    for fname, text in SECTIONS:
        out_path = OUT / f"{fname}.mp3"
        if out_path.exists():
            print(f"  SKIP {fname} (exists)")
            continue
        words = len(text.split())
        print(f"  TTS: {fname} (~{words} words)")
        try:
            audio = client.text_to_speech.convert(
                voice_id=VOICE_ID,
                text=text,
                model_id=MODEL,
                output_format=FMT,
                voice_settings=VOICE_SETTINGS,
            )
            with open(out_path, "wb") as f:
                for chunk in audio:
                    f.write(chunk)
            char_count = len(text)
            cost = log_elevenlabs_cost(OUT.parent, "tts", char_count, fname)
            print(f"    OK {out_path} (cost: ${cost:.4f})")
        except Exception as e:
            print(f"    FAIL: {e}")


if __name__ == "__main__":
    print(f"=== Generating TTS for project: {PROJECT_NAME} ===")
    print(f"    Voice: {VOICE_ID}")
    print(f"    Output: {OUT}\n")
    generate_tts()
    print("\n=== Done! ===")
    for f in sorted(OUT.glob("*.mp3")):
        size = f.stat().st_size
        print(f"  {f.name}  ({size // 1024} KB)")
