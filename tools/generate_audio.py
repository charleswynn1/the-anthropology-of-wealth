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

PROJECT_NAME = "invention-of-the-coin"  # Folder name under public/ and src/

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
    ("s1_hook", """Hmm. There is a river in western Turkey, and for thousands of years, it ran with gold.

Not a legend. The actual river, called the Pactolus, carried flakes and nuggets of a natural gold and silver alloy called electrum down from the mountains into the valley. The people who lived there, the Lydians, collected it. Melted it. And sometime around six hundred and thirty years before the common era, they did something nobody on earth had ever done before.

They made a coin.

And they made it wrong on purpose.

The world's first coin had a golden surface and a silver core, and the government that minted it knew the difference. In that gap, between what the stamp certified and what the metal actually contained, is the entire history of money. Every debasement, every inflation, every pension fund that quietly lost ground and every wage that didn't keep pace traces back to a workshop in ancient Lydia, and a metallurgical trick that has never really stopped."""),

    ("s2_setup", """Okay. Before coins, most ancient economies did not run on barter. That is the story we are told, but it is not quite right.

What they actually ran on was relationship credit. Grain accounting in temples. Debts recorded in clay and stone, settled through reputation, community obligation, and social memory. A farmer in Mesopotamia did not hand over silver at a market stall. He owed grain to the temple, and the temple owed bread to the laborers, and all of it was tracked in a ledger system that everyone more or less trusted because everyone more or less knew each other.

That system had real limits. It did not scale. You could not easily trade with a stranger two hundred miles away. You could not send value across a mountain pass without sending trust along with it. The ancient world needed something portable, standardized, and verifiable by someone who had never met you.

The coin solved that problem. A small piece of metal, stamped with an image that carried the authority of a king or a city, worth exactly what the stamp said it was worth, accepted by anyone who trusted the issuing authority.

Yeah. That was the idea. And within one generation, it turned out that the issuing authority could be trusted to do one thing reliably: issue coins worth less than they appeared."""),

    ("s3_lydia", """Alright. What actually happened at the Lydian mint was not symbolic. It was metallurgical.

The Pactolus River naturally produced electrum at roughly seventy three percent gold. That was the raw material. But the coins the mint produced tested at roughly fifty four percent gold in the core. Modern XRF analysis, performed by Nicholas Cahill and colleagues from the Sardis Expedition, confirmed the gap. The mint was deliberately alloying silver into the electrum to stretch the supply, reducing actual gold content by nearly twenty percentage points.

Then they ran the coins through a process called depletion gilding. Essentially, they treated the surface so that the silver leached away from the outer layer, leaving a surface that read as high gold. The surface came out at seventy three percent gold, matching what the river naturally produced. The core stayed at fifty four percent, and the mint intended it that way.

And on top of that enriched surface, they stamped a lion's head. The mark of the Lydian king. The symbol of royal authority, certifying a value the metal did not contain.

Hmm. Some scholars have been diplomatic about this. They call it fiduciary coinage. They say the face value was based on trust, not metal, and the Lydians understood this implicitly. The historian Sture Bolin was blunter. In his nineteen fifty eight study of ancient coinage, he called the first coins the first numismatic deception.

What is interesting is that both descriptions are correct. The Lydians were not simply fraudsters operating in the dark. They were building a system, and the system required that the stamping authority could set value independently of metal content. The stamp had to mean more than the metal. That was the entire point.

The coin was, from the beginning, a declaration that the state's word was worth more than the substance it certified. And to make that declaration credible, the state needed the physical object to look right, even when it wasn't.

The Lydians gave the world money. And the first thing money was, was a number that meant something different on the inside than it did on the outside."""),

    ("s4_athens", """Greek city states adopted coinage within a century of the Lydian invention, and in Athens, the results were catastrophic for the people at the bottom.

Before coins, farmers in Attica paid their obligations in kind. One sixth of their produce went to wealthy landowners as rent. It was called the hektemoroi system, and it was exploitative, but it had a certain flexibility built in. A bad harvest meant less grain, and less grain meant a smaller payment. The obligation tracked the reality.

Coins changed the structure of the debt. When you borrowed coin denominated silver, the amount was a specific number owed by a specific date, enforceable in a court of law. And the debt grew according to its own internal logic regardless of what was happening in your field.

If the harvest failed, the debt did not shrink. It waited. With interest. And when farmers could not repay, creditors had legal standing to seize not just the land but the family.

Alright. You can still see the evidence of this if you know what to look for. They were called horos stones, mortgage markers, rectangular slabs of limestone that creditors would physically place in a debtor's field as public notice that the land was under claim. Archaeologists have found dozens of them across Attica. A field with a horos stone in it was a field that someone else owned in the eyes of the law, even if the farmer was still working it.

By five hundred and ninety four years before the common era, the crisis was severe enough that Athens needed emergency intervention. They called in a man named Solon, appointed him archon with extraordinary powers, and asked him to fix it.

What Solon did was radical. He canceled all debts. Every single one. He freed every Athenian who had been sold into debt slavery, including those who had been sold abroad, to Egypt, to the Black Sea, to markets across the ancient world. He had the horos stones physically removed from the fields. He outlawed the practice of using an Athenian's body as collateral for a loan.

He called it the seisachtheia. The shaking off of burdens.

And then he wrote a poem, which survives. He described the black earth, which had been enslaved, as now free.

Hmm. Then Solon left Athens for ten years. He went abroad voluntarily, partly to see the world, partly because he understood that if he stayed, both the creditors and the debtors would pressure him to reverse what the other side wanted. He went to Egypt. He went to Cyprus. He let the laws stand on their own.

He was gone for a decade. When he came back, Athens was already rebuilding the debt system. The coins had returned. The credit relationships had returned. The horos stones, in time, returned.

The seisachtheia was extraordinary. It was also temporary. Solon erased the debts that existed, but the structure that created them, a coin denominated system with legally enforceable repayment terms and no debt relief mechanism built in, that remained. And a structure like that does not stay empty for long."""),

    ("s5_alexander", """Yeah. If the coin gave states new power over the people inside their borders, what happened when you scaled that power across an empire tells you something even darker.

When Alexander the Great captured Persepolis in three hundred and thirty years before the common era, he walked into the Persian treasury and found a quantity of accumulated silver and gold that the ancient world had never seen concentrated in one place. Somewhere between one hundred and eighty thousand and two hundred thousand talents of bullion, the product of centuries of Persian tribute collection.

Moving it required roughly three thousand camels and twenty thousand mules. That is not a metaphor for scale. Those are the logistics. Moving the treasury of a conquered empire is a physical problem first.

Alexander did not simply hold the metal. He converted it into coins. His mints struck the silver into currency, and that currency flooded into the economies of the ancient Mediterranean world, into economies that had not asked for it and were not prepared for what it would do to them.

Okay. When you flood a market with new currency, the prices of goods rise. The goods do not change. The amount of money chasing those goods increases. The result is that the same amount of goods costs more coin than it used to. This is not a law of nature. It is the predictable mechanical consequence of injecting a large supply of money into a market without a corresponding increase in what the market produces.

Local economies built on temple credit, barter, and social obligation were flooded with coined money they had not generated and did not control. The value of their existing savings shifted. The prices they paid rose. Their purchasing power declined. All of this happened without anyone in those local economies making a decision. They simply found themselves inside a larger monetary system, operating on the rules of that system, whether they wanted to be or not.

The Portuguese and Dutch traders who operated in West Africa centuries later understood the same principle. West African economies had used cowrie shells as currency for generations, a stable system with its own internal logic. Portuguese traders began importing cowrie shells from the Indian Ocean, where they obtained them cheaply, and flooding West African markets with them in the fifteen hundreds and sixteen hundreds. Billions of shells. The shells already in circulation became worth less as the supply exploded. Local savings evaporated. Prices destabilized.

Alright. They did not fire a single shot to accomplish that destabilization. They just controlled the supply of the thing that defined value, and used that control to extract advantage.

Monetary power is the power to change what things cost for everyone, without their consent. Alexander knew it. The Portuguese traders knew it. And neither group needed to explain it to the people it was happening to."""),

    ("s6_rome", """The Roman denarius, in the time of Augustus, was ninety five to ninety eight percent silver. It was a coin you could trust.

Nero was the first emperor to debase it seriously. In the late fifties of the common era, he reduced the silver content to around ninety percent and shaved the coin's weight slightly. The changes were small enough that most people could not detect them without metallurgical analysis. The coins looked the same. They bought a little less than before.

And then the next emperor made a small adjustment. And the next. And the next. Each debasement was modest enough to be plausible, large enough to matter, and cumulative enough to be devastating over time.

Hmm. By the reign of Septimius Severus, around two hundred years into the common era, the denarius was at roughly fifty percent silver. Severus introduced a new coin, the antoninianus, marketed as a double denarius but containing only about one and a half times the silver of a single denarius. The empire was spending coin value it did not have.

By the time of Gallienus, around two hundred and sixty to two hundred and sixty eight years into the common era, the denarius contained roughly two to five percent silver. It was a bronze coin with a silver wash on the surface, the silver wash already wearing through in some cases. By two hundred and sixty eight, some coins tested at half of one percent silver.

The price of goods across the empire rose roughly one thousand percent between two hundred and three hundred years into the common era. A century. One thousand percent.

Okay. A Roman legionnaire in the late two hundreds received the same number of coins his grandfather had received. He could buy about a third of what his grandfather could buy. He did not understand why, and he could not understand why without access to information the state had no interest in sharing. He just knew that bread cost more than it used to. He petitioned the emperor for a pay raise. The pay raise came in debased coins. The situation did not improve.

An emperor could call in the currency, remint it at lower silver content, and release it back into the economy, effectively extracting the difference without a vote, without an announcement, and usually without anyone in the general public understanding what had just happened. The people who held coins bore the cost. The people who issued coins captured the profit.

The legionnaire, the farmer, the merchant in a provincial town, they did not decide to participate in this system. They used money because that was what money was. And money was what the mint said it was, whether that matched reality or not.

Yeah. The Roman empire survived this for centuries before the Crisis of the Third Century finally compressed fifty plus emperors into less than fifty years, constant debasement, economic collapse across the provinces. The coin did not cause the collapse of Rome. But the gap between the coin's certified value and its actual content, managed for centuries in the interest of the issuing authority and at the expense of the people who used it, was the mechanism that made the collapse as severe as it was."""),

    ("s7_modern", """Alright. The system the Lydian mint built did not end with Lydia, or with Rome, or with Alexander.

The dollar sign, the one you use every time you write a price, has a contested history. One theory, well documented, traces it to the Potosi mint mark, a mark that appears on the Spanish pieces of eight, the coin that became the world's first truly global currency in the fifteen hundreds and sixteen hundreds. Potosi was a silver mountain in present day Bolivia, discovered in fifteen forty five. Between fifteen forty five and eighteen hundred, it produced roughly sixty percent of all the silver mined in the world. The Spanish empire turned that silver into pieces of eight and distributed them across every trading route on earth.

The mita system extracted that silver. Forced indigenous labor, organized by the Spanish colonial administration. Estimates of the death toll from the Potosi mining operations reach into the millions, with some historians putting the number as high as eight million over the life of the mine, though the figure is debated. What is not debated is that the world's first global currency was built on a foundation of forced extraction from people who had no voice in the system they were fueling.

Hmm. The United States government currently collects roughly twenty to thirty billion dollars per year in seigniorage. That is the gap between the face value of the currency it issues and the cost of producing it. A one hundred dollar bill costs a few cents to print. The government collects the difference. This is the same gap the Lydian mint was engineering when it enriched the surface of that electrum stater while diluting the core. The mechanism is three thousand years old. The scale is just larger.

Student loan debt in the United States cannot be discharged in bankruptcy. That rule was established in nineteen seventy six and expanded in nineteen ninety and nineteen ninety eight. What it means, in practice, is that a legally enforced, coin denominated obligation grows according to its own internal logic regardless of the debtor's circumstances. A graduate whose career never materialized, whose health failed, whose industry collapsed, still owes the number. The number does not track reality. It tracks the contract.

Okay. The hektemoroi farmers in Attica understood that feeling. The specific amount, by the specific date, growing regardless of the harvest.

And the milled edge on every coin in your pocket, those little ridges, they were introduced by Isaac Newton. Newton was Master of the Mint from sixteen ninety six to seventeen twenty seven, and one of the practical problems he inherited was coin clipping, the practice of shaving small amounts of silver from coin edges before spending them. Clip enough coins and you accumulate real metal. The milled edge made clipping detectable. Every coin you have ever touched still carries that innovation.

Yeah. Newton's solution was a small mechanical fix to the same problem the Lydians first created: the gap between what a coin looks like and what it actually contains. He solved the clipping problem. The core problem, the structure that creates the incentive to dilute in the first place, that one has not been solved. It has been institutionalized.

The coin itself has largely disappeared from most transactions. You tap a card, you send a transfer, you hold a balance in an app. The metal is gone. The logic is not. The number certified by an authority, backed by trust, carrying an implicit promise about value that the issuing authority reserves the right to adjust, that is still what money is. Aristotle said it in his Politics around three hundred and thirty years before the common era. He understood coins as social conventions, not as objects with inherent value. A coin was worth what the community agreed it was worth, formalized by state authority.

He was right about the mechanism. He was maybe too generous about the word agreed."""),

    ("s8_closing", """Hmm. There is a version of this story where the coin is a great invention that some bad actors later corrupted. That version is comfortable. It lets you believe that money was pure once, and then people ruined it.

The evidence from Sardis does not support that version.

The first coin, the one that started all of this, was engineered to have a gap between its surface and its core. Depletion gilding on the outside. Diluted alloy on the inside. A lion's head stamped on top, certifying a value the metal did not contain. The gap was built into the original design, by the people who invented money, in the first mint that ever operated.

What money did was make trust scalable. Before the coin, trust required relationship, shared history, community. The coin let a stranger in a distant city honor a transaction with someone he had never met and would never meet again, because the stamp carried the authority of a state both of them recognized. That is a genuine and important innovation.

Okay. But when you make trust scalable, you also make the management of trust scalable. Whoever controls what the stamp means controls what the trust is worth. And that control has never, in three thousand years of monetary history, rested with the people who hold the coins.

Solon removed the horos stones from the fields of Attica and called the earth free. Then he left for ten years, and the system rebuilt itself. The people in power were not unusually evil. The structure itself creates the incentive. The mint profits from the gap. The structure that profits from the gap has an interest in maintaining the gap. The people who hold the coins have an interest in closing it. And the people who hold the coins are almost never the people who run the mint.

That tension, between what the stamp certifies and what the substance contains, between the number the issuer sets and the reality the holder lives in, has been the actual content of monetary history for three thousand years.

Alright. If you found this useful, there is more in the feed. The story does not get simpler from here."""),
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
