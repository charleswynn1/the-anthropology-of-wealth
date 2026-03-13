#!/usr/bin/env python3
"""
MoneyMath — General TTS Audio Generation Pipeline
Generates narration audio from script sections using ElevenLabs.

Usage:
  1. Edit SECTIONS below with your script text
  2. Set PROJECT_NAME to your project folder name
  3. Run: python3 generate_audio.py
"""

import base64
import json
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

PROJECT_NAME = "gold-became-money"  # Folder name under public/ and src/

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
    ("s1_hook", """There are one hundred eighteen elements in the periodic table. Every single one of them was a candidate for money. And a chemist who went through the list, one by one, eliminating every element that would explode, corrode, melt in your hand, poison you, disappear into the air, or require a furnace hotter than any ancient civilization could build, arrived at exactly five survivors.

Hmm, out of one hundred eighteen, only five pass the test.

And then silver tarnishes. Rhodium and palladium were not even discovered until the eighteen hundreds. Platinum requires temperatures that no ancient forge could reach. That leaves one. Gold. The only element that passed every filter, in every civilization, before any king or empire ever made a decision about it.

Chemistry chose gold before humans did. What humans did with that choice is the part nobody teaches you."""),

    ("s2_chemistry", """Start with the gases. Helium, neon, oxygen, hydrogen. You cannot hold a gas in your pocket. You cannot stamp it or divide it. Gone. Then the liquids at room temperature. Mercury is liquid at room temperature and it will kill you through your skin. Gone. Then the radioactive elements. Uranium, plutonium, radium. Carrying radioactive money would make you sick and then dead. Gone.

Then there are the elements that react violently with air or water. Sodium bursts into flame when it touches moisture. Potassium is worse. Cesium will explode on contact with air. Any metal that cannot sit in a market stall in open weather is useless as money. Gone.

That clears most of the table. What you are left with are the metals that resist corrosion. Iron rusts. Copper turns green. Lead is too soft and too common. Tin, aluminum, zinc. All too reactive, too common, or too fragile. The more you narrow the criteria, the shorter the list gets.

Alright, now you are down to the precious metals. The noble metals. The ones that resist corrosion and can survive thousands of years in the ground without changing. Platinum, palladium, rhodium, iridium, osmium, silver, and gold.

Osmium and iridium are so rare that they barely exist in workable quantities anywhere on Earth. Rhodium and palladium were completely unknown to ancient people, not discovered until the eighteen hundreds. Platinum melts at seventeen hundred and sixty eight degrees Celsius. Ancient forges could not reliably reach that temperature. You could not smelt it, could not shape it, could not make coins from it. That eliminates platinum.

Silver comes close. Silver is excellent money in many ways. But silver tarnishes. Left in the open air, it reacts with sulfur compounds and turns black. In a world before industrial refining and chemical cleaning, tarnished silver is harder to assess. Trust erodes.

Gold does not tarnish. Gold does not rust. Gold does not react with air, water, acids, or most common chemicals. Gold is soft enough to work with simple tools. Gold is dense enough that a small piece holds significant value. Gold is rare enough that you cannot dig it up in your backyard, but common enough that civilizations across the world were able to find it.

Yeah, every other candidate has one fatal flaw. Gold has none. The universe constrained the choice before any human made it.

The oldest gold objects ever found were buried in a place called Varna, in what is now Bulgaria. Six thousand five hundred years ago. A construction worker named Raycho Marinov was digging a cable trench in October nineteen seventy two when his bucket hit something. He stopped and called the authorities. What they found was more gold than had been discovered anywhere in the world from that era combined. Thousands of artifacts. Grave forty three held a man who had been buried with a gold sheathed mace and gold ornaments so numerous that archaeologists spent weeks cataloging them. The person in that grave is now believed to have been a metalsmith. The craftsman who could work gold was, six thousand five hundred years ago, among the most powerful people in society.

Gold was not money yet. It was something more powerful than money. It was the material that every culture that touched it decided was different. Sacred. Eternal. The flesh of gods. The sweat of the sun.

The transition from sacred to monetary was slow. But the chemistry made it inevitable."""),

    ("s3_lydia", """Six hundred and thirty years before Christ, in a small kingdom in what is now western Turkey, someone had an idea that changed commerce forever.

The Lydians lived along a river called the Pactolus. The Pactolus ran through gold deposits and naturally washed out a gold silver alloy called electrum. Lydian merchants were already using weighed lumps of electrum in trade. But every transaction required a scale. Every transaction required testing the purity of the metal. Every trade between strangers was a negotiation about whether the metal was what it claimed to be.

Then someone stamped a mark onto a lump of electrum. That stamp was a guarantee. Whoever put that stamp there was saying: this piece of metal is the weight and purity I am promising. You do not need your scales. You do not need your touchstone. You have my word, made physical.

Check this out: one of the earliest surviving electrum coins carries an inscription that translates as I am the signet of Phanes. Herodotus mentions a mercenary commander named Phanes of Halicarnassus, a Greek soldier who served in Egypt. If these are the same person, the first coin in history was not issued by a government. It was issued by a soldier, as a personal guarantee to the men he was paying. The sovereign monopoly on money came later. The very first coin was a mercenary's promise.

Okay, around five hundred and fifty years before Christ, King Croesus of Lydia transformed this personal innovation into a state monopoly. He introduced the world's first pure gold coins of standardized purity, the Croeseid, and the world's first bimetallic system with separate gold and silver coins at a fixed exchange ratio. The design showed a lion facing a bull. The stamp was royal. The guarantee was the kingdom itself.

The Persians conquered Lydia in five hundred forty seven years before Christ. And the very first thing they did with the Lydian monetary system was adopt it. Because it worked. The Persian gold daric was calibrated to precisely one month's wages for a mercenary foot soldier. The daric traveled wherever soldiers traveled. Monetary integration of the ancient Mediterranean world was driven, substantially, by soldiers demanding portable pay.

And once you had reliable coinage, you could build empires. Literally. The word soldier derives from solidus, the name of a gold coin, not from any weapon or warrior tradition.

In three hundred twelve years after Christ's death, the Emperor Constantine introduced a new gold coin called the solidus. Four and a half grams of nearly pure gold. And that coin did not change in weight or purity for over seven hundred years. Seven centuries. If you were a merchant in Alexandria in the year eight hundred, you could take a gold solidus out of your purse and another merchant would accept it without hesitation, without weighing it, without testing it. The coin's reputation preceded it across the known world. It circulated from England to China, from Scandinavia to sub-Saharan Africa.

In Florence, starting in twelve fifty two, the gold florin was minted at three and a half grams of twenty four carat gold. It held that exact specification for two hundred eighty one years, through wars, banking crises, famines, and the Black Death. The Florentine Republic ended in fifteen thirty three. The florin's monetary discipline ended with the republic. When republican governance ended, monetary honesty ended with it.

Trust in gold was not just a financial convenience. It was civilization's operating system. When emperors maintained it, armies stayed loyal, trade expanded, commerce was possible between strangers who shared no language and no law. When emperors broke it, the consequences were measured in mutinies and market collapses."""),

    ("s4_potosi", """In fifteen forty five, Spanish prospectors in the high Andes of what is now Bolivia found a mountain.

The mountain was called Cerro Rico. The Rich Mountain. And underneath it was the largest silver deposit ever discovered in the history of the world. Enough silver to change the price of everything on Earth.

The Spanish called it the silver mountain that would fund their empire forever. They were half right.

Alright, here is how they extracted it. The Spanish colonial government imposed a system called the mita. It conscripted one in seven adult indigenous men in the surrounding region, rotating annually. Thirteen thousand men per year were legally required to spend a year in the mines. They descended on Monday morning with a single candle tied to their foreheads. They did not come back up until Saturday. The shafts went down six hundred feet. The temperature swung from freezing deep in the rock to blazing at the surface. Workers carried loads of ore weighing up to three hundred pounds on their backs up rickety ladders, in darkness, by candlelight.

The silver refining process required mercury. The Spanish found the mercury at Huancavelica, seven hundred miles to the north, in what is now Peru. Workers at Huancavelica walked barefoot through ore mixtures saturated with mercury for weeks at a time, absorbing it through the skin. The Spanish called Huancavelica the mine of death. They built a hospital there so workers could recover enough to return. Conservative scholarly estimates put direct deaths in and immediately around the mines at well over one million people across the colonial period. Total indigenous population collapse across the broader region was many times larger, from disease, displacement, forced labor, and mercury poisoning combined.

That's crazy, right? The silver that funded the first global monetary system, the first time a single metal circulated from Bolivia to Seville to Manila to China, was extracted by a system that killed its workers as a matter of operating procedure.

By sixteen hundred, twenty five thousand tons of silver had been shipped to Spain. The Price Revolution swept across Western Europe. Prices rose three to six times over the century following fifteen fifty. The silver was, in effect, quantitative easing on a continental scale. Every merchant and farmer in Europe felt it in the price of bread.

And Spain, which controlled both mountains of death and the world's largest silver extraction operation, went bankrupt in fifteen fifty seven, fifteen seventy five, and fifteen ninety six. Three times in forty years.

The mechanism was direct. Too much silver caused such severe domestic inflation that Spanish goods became uncompetitive. Manufacturing collapsed. Spain became dependent on foreign imports. The treasure that was supposed to make Spain eternal was flowing immediately through Spain into the hands of Dutch, English, and Chinese merchants who were selling Spain the goods it could no longer make for itself. The country with the most money in the world had the most unstable economy in Europe.

The people who dug it out of the ground received nothing. The people who received it destroyed themselves with it. The people who built stable long term wealth were the ones on the receiving end of Spanish spending, not the Spanish crown that owned the mountain."""),

    ("s5_gold_standard", """Hmm, here is something most people get wrong about the gold standard. They think it was an era of monetary stability, but it was an era of stability for one particular group of people and systematic extraction for another.

The mechanism is worth understanding precisely, because it still shapes every monetary policy debate you will hear in your lifetime.

Under a gold standard, the money supply is tied to the amount of gold a government holds. If you need more money, you need more gold. If you run out of gold, you cannot expand the money supply no matter what is happening to your economy. The consequence is deflationary pressure any time shocks hit. Prices fall while debts stay fixed at their original nominal value.

Think about what that means for a farmer. A farmer in the American Midwest in eighteen ninety borrows one thousand dollars to buy land when wheat is selling for one dollar a bushel. He owes the bank one thousand bushels worth of wheat, roughly. Five years later, the price of wheat has fallen to fifty cents a bushel. His debt is still one thousand dollars. Now he needs to sell two thousand bushels to pay the same debt. His income fell by half. His debt burden doubled. In real terms, without anyone changing the number on his loan contract, his debt became twice as large.

This was not a glitch. This was the system working as designed. Creditors who hold gold backed debt are protected from inflation. Every dollar of principal they are owed comes back to them in full, in hard money, undiluted. Creditors love gold money for this reason. The gold standard is an excellent system if you are the one holding the debt.

William Jennings Bryan stood up at the Democratic National Convention in eighteen ninety six and said it plainly. He was thirty six years old. He had been rehearsing the closing lines of his speech for years, testing different versions. When he delivered the final version, people screamed and threw hats and canes in the air. He said: you shall not crucify mankind upon a cross of gold. He was talking about compound interest and fixed rate mortgages. He was talking about the farmer whose real debt had doubled without the number on the contract changing. He lost the election. The gold standard survived.

World War One revealed the gold standard's structural weakness. When war broke out in August nineteen fourteen, every major belligerent suspended gold convertibility within weeks. War required spending twelve times what taxes could provide. You cannot fight a modern industrial war inside the constraints of a gold standard. Every government understood this immediately. The gold standard was suspended not because economists recommended it but because it was incompatible with survival.

After the war, the major powers tried to restore it. Britain went back to gold in nineteen twenty five at the prewar exchange rate, a decision Keynes called catastrophic. The prewar rate overvalued the pound, made British exports too expensive, and delivered a decade of stagnation.

Then the Great Depression hit. Banks failed. The natural response was to expand the money supply to provide liquidity and stop the bank runs. Under the gold standard, that was illegal. The money supply could only be as large as the gold reserve. Governments watched banks fail and could not act. The contraction fed itself.

Yeah, Sweden left the gold standard in nineteen thirty one. By nineteen thirty six, its industrial production was fourteen percent above nineteen twenty nine levels. France held on until nineteen thirty six. By then, its industrial production was twenty six percent below nineteen twenty nine. The countries that left gold first recovered first. Not some of them. All of them. Without exception. The correlation between gold standard exit and economic recovery is one of the clearest relationships in the history of macroeconomics.

The gold standard did not fail because it was badly managed. It failed because its core feature, the thing that made creditors love it, was also the thing that made crises into depressions. It could not bend. And a system that cannot bend, eventually breaks."""),

    ("s6_nixon", """August thirteenth, nineteen seventy one. Richard Nixon gathers fifteen senior advisers at Camp David and orders a communications blackout. No calls out. No advance notice to allies. No warning to the Federal Reserve, the IMF, or the governments of Europe.

Paul Volcker, the Undersecretary of Treasury for Monetary Affairs, had already told Nixon that waiting any longer risked a catastrophic wave of gold redemption requests on Monday morning. Britain had just requested the conversion of three billion dollars in dollar reserves to gold. West Germany had abandoned the dollar peg in May. The math had been impossible for years. Everyone in that room knew it. There were far more dollar claims on US gold than there was gold to cover them. France's Charles de Gaulle had spent the previous decade shipping gold from Fort Knox to Paris, recognizing the contradiction. The United States held two thirds of the world's monetary gold in nineteen forty four. By nineteen seventy one, those reserves had been substantially depleted by a decade of dollar outflows.

Volcker drafted options on a yellow legal pad. Treasury Secretary John Connally pushed for the boldest move: close the gold window entirely, impose a surcharge on imports, announce wage and price controls, and seize maximum political initiative in one move. Nixon agreed.

On Sunday night, August fifteenth, Nixon went on television. He told the country the United States would no longer exchange dollars for gold. No consultation with allies. No negotiation. One speech. The French government called it monetary aggression. Connally was asked how foreign governments would react. He said: the dollar is our currency, but it is your problem.

The decision was announced as temporary, and it has never been reversed.

By nineteen seventy three, all major currencies were floating. Their values set by markets, not by gold. For the first time in recorded human history, the entire world operated on a monetary system with no commodity anchor whatsoever. The Lydian coin. The Byzantine solidus. The Florentine florin. The classical gold standard. Bretton Woods. Six thousand years of monetary systems, all of them tethered in some form to a physical metal. Gone in one Sunday night speech.

Alright, and here is what replaced it. Not nothing. Kissinger, in nineteen seventy four, negotiated a deal with Saudi Arabia. The United States would guarantee Saudi military security. In exchange, all Saudi oil sales would be priced exclusively in US dollars. By nineteen seventy five, all OPEC nations were pricing oil in dollars. The gold standard was replaced by an oil standard. If you wanted energy, you needed dollars. The mechanism was different but the power relationship was identical. Control the reserve commodity, control global finance."""),

    ("s7_modern", """Gold hit thirty five dollars an ounce in nineteen seventy one, the last price Nixon defended. In January of twenty twenty six, it hit four thousand six hundred eighty nine dollars per ounce, an all time intraday high. By March of twenty twenty six, spot gold was trading at over five thousand dollars per ounce. That is more than one hundred forty five times the nineteen seventy one price, in fifty five years of fiat currency.

Hmm, you might think that is just inflation. Prices go up. Dollars buy less. The number on gold went up because the dollar weakened. And that is part of the story.

In twenty twenty two, the United States and its Western allies froze approximately three hundred billion dollars in Russian central bank reserves, following Russia's invasion of Ukraine. This was unprecedented. The foreign exchange reserves of a major economy, held in Western financial institutions, were rendered inaccessible by executive order. No court order. No negotiation. A decision, and the money was frozen.

Every central bank in the world watched that happen and drew the same conclusion. Dollar reserves held in foreign institutions can be seized. Gold held in your own vaults cannot. Gold cannot be frozen remotely. Gold is immune to financial sanctions. Gold sitting in your own basement vault is yours regardless of what any foreign government decides.

Within months, central bank gold purchases accelerated dramatically. Two thousand twenty two, two thousand twenty three, and two thousand twenty four each saw central banks buying more than one thousand metric tons of gold. That was more than double the pace of the prior decade. A survey in twenty twenty five found forty three percent of central banks planned to increase gold holdings in the coming year. Poland added ninety tons in twenty twenty four. India added seventy three tons. China does not disclose its purchases accurately but is widely believed to be the largest buyer of all.

These are not fringe economies hedging against the dollar on ideological grounds. These are the finance ministries and central banks of major economies, operating on a calculated assessment of risk. They are looking at what happened to Russian reserves. They are looking at the structural pressure on the dollar's share of global reserves, which has fallen from over seventy percent in the early two thousands to approximately fifty eight percent in twenty twenty five. They are looking at a fiat monetary system that is fifty three years old and asking: what is the one asset that has preserved value across every monetary system change in the last six thousand years?

The answer is the same one the Lydians found along the Pactolus River. The same one Constantine stamped four and a half grams of at a time. The same one the Spanish extracted at the cost of millions of lives. The same one Nixon closed the window on in one Sunday night speech.

Gold is not money. There is no gold standard. No currency on Earth is redeemable for gold. And the people who run the world's fiat monetary system are buying gold at the fastest rate in fifty years. They are not announcing what that means. The purchases are in the public record. The reasoning is visible in the data. They are hedging against the system they manage."""),

    ("s8_close", """Hmm, here is the thing about money that six thousand years of history keeps proving.

Every monetary system feels permanent to the people living inside it. The Byzantine solidus lasted seven centuries and then collapsed in a single generation of debasement. The gold standard of the eighteen seventies was described by its champions as a permanent achievement of civilization. It lasted forty four years. Bretton Woods was designed to stabilize the postwar world forever. Nixon ended it in a weekend.

The chemistry chose gold. It was the only viable answer, given ancient technology, given the properties available in the physical world. That part was not a choice. But everything else was.

Every element of the gold system was a choice: who controlled the mint, who set the rules, whose debts were protected and whose were doubled in real terms by deflation, who descended a shaft six hundred feet deep by candlelight, and who got to walk into Camp David and close the gold window while everyone else found out about it on Sunday night television.

Every monetary system is a political choice dressed as a natural fact. The gold standard was not nature. It was a system built by people with power to serve people with power, and when it could no longer serve that function without destroying the economies around it, it was discarded. The fiat system that replaced it is also a political choice, also with beneficiaries, also with costs that are distributed unevenly and often invisibly.

The central banks buying gold are not predicting the end of fiat currency. They are hedging against the possibility that the system they manage might, in some future they cannot fully see, face a challenge it cannot absorb. That is the honest signal in the data. Fifty three years of fiat money is the longest the world has ever gone without any monetary anchor. The experiment is still running.

Gold began as the flesh of gods. It became the stamp of kings. It built empires and collapsed them and traveled from Bolivia to Manila to London and back. It was the thing armies fought for, farmers were destroyed by, and ordinary people saved in the form of coins and jewelry for six thousand years. In nineteen seventy one, officially, it stopped being money.

Yeah, but if you look at what the people who control money are actually doing with their reserves, gold never really left the room. And understanding why that is true is how you start seeing through every monetary argument anyone is ever going to make to you, for the rest of your life.

If you want to understand how the system that replaced gold works, and why the debt built inside it reaches into every ordinary life in a way most people never trace back to its source, that is exactly what this channel is here for. Subscribe and we will keep going."""),
]

# ══════════════════════════════════════════════════════════
# GENERATION — No need to edit below this line
# ══════════════════════════════════════════════════════════

OUT = ROOT / f"projects/{PROJECT_NAME}/audio"
OUT.mkdir(parents=True, exist_ok=True)


def _seconds_to_srt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _alignment_to_words(chars, start_times, end_times, time_offset=0.0):
    entries = []
    current_word = ""
    word_start = None
    for i, char in enumerate(chars):
        t_start = start_times[i]
        t_end = end_times[i]
        if char == " " or i == len(chars) - 1:
            if i == len(chars) - 1 and char != " ":
                current_word += char
                t_end_final = t_end
            else:
                t_end_final = t_start
            if current_word.strip():
                entries.append({
                    "word": current_word.strip(),
                    "start": word_start + time_offset,
                    "end": t_end_final + time_offset,
                })
            current_word = ""
            word_start = None
        else:
            if word_start is None:
                word_start = t_start
            current_word += char
    return entries


def _words_to_srt(word_entries, words_per_block=5):
    lines = []
    index = 1
    i = 0
    while i < len(word_entries):
        block = word_entries[i: i + words_per_block]
        block_start = block[0]["start"]
        block_end = block[-1]["end"]
        text = " ".join(w["word"] for w in block)
        lines.append(str(index))
        lines.append(f"{_seconds_to_srt_time(block_start)} --> {_seconds_to_srt_time(block_end)}")
        lines.append(text)
        lines.append("")
        index += 1
        i += words_per_block
    return "\n".join(lines)


def generate_tts():
    all_word_entries = []   # accumulated across sections for combined SRT
    cumulative_offset = 0.0

    for fname, text in SECTIONS:
        mp3_path = OUT / f"{fname}.mp3"
        json_path = OUT / f"{fname}.json"
        srt_path  = OUT / f"{fname}.srt"

        if mp3_path.exists() and json_path.exists():
            print(f"  SKIP {fname} (exists)")
            # Still load alignment to keep cumulative offset accurate
            data = json.loads(json_path.read_text())
            end_times = data.get("character_end_times_seconds", [])
            section_duration = end_times[-1] if end_times else 0.0
            cumulative_offset += section_duration
            continue

        words = len(text.split())
        print(f"  TTS: {fname} (~{words} words)")
        try:
            response = client.text_to_speech.convert_with_timestamps(
                voice_id=VOICE_ID,
                text=text,
                model_id=MODEL,
                output_format=FMT,
                voice_settings=VOICE_SETTINGS,
            )

            # Save MP3  (response.audio_base_64 uses underscore — ElevenLabs SDK quirk)
            audio_bytes = base64.b64decode(response.audio_base_64)
            mp3_path.write_bytes(audio_bytes)

            # Save alignment JSON
            alignment = response.alignment
            chars      = alignment.characters
            start_times = alignment.character_start_times_seconds
            end_times   = alignment.character_end_times_seconds
            alignment_data = {
                "characters": chars,
                "character_start_times_seconds": start_times,
                "character_end_times_seconds": end_times,
            }
            json_path.write_text(json.dumps(alignment_data, indent=2))

            # Save per-section SRT
            word_entries = _alignment_to_words(chars, start_times, end_times)
            srt_path.write_text(_words_to_srt(word_entries))

            # Accumulate for combined SRT (offset by cumulative duration of prior sections)
            word_entries_offset = _alignment_to_words(
                chars, start_times, end_times, time_offset=cumulative_offset
            )
            all_word_entries.extend(word_entries_offset)
            section_duration = end_times[-1] if end_times else 0.0
            cumulative_offset += section_duration

            char_count = len(text)
            cost = log_elevenlabs_cost(OUT.parent, "tts", char_count, fname)
            print(f"    OK  {mp3_path.name}  |  {srt_path.name}  |  {json_path.name}  (cost: ${cost:.4f})")

        except Exception as e:
            print(f"    FAIL: {e}")

    # Write combined SRT for the full video (used for YouTube upload)
    if all_word_entries:
        combined_srt_path = OUT / f"{PROJECT_NAME}.srt"
        combined_srt_path.write_text(_words_to_srt(all_word_entries))
        print(f"\n  Combined SRT → {combined_srt_path}")


if __name__ == "__main__":
    print(f"=== Generating TTS for project: {PROJECT_NAME} ===")
    print(f"    Voice: {VOICE_ID}")
    print(f"    Output: {OUT}\n")
    generate_tts()
    print("\n=== Done! ===")
    for f in sorted(OUT.glob("*.mp3")):
        size = f.stat().st_size
        print(f"  {f.name}  ({size // 1024} KB)")
