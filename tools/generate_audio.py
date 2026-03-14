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

PROJECT_NAME = "before-money"  # Folder name under public/ and src/

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
    ("s1_hook", """Before there were coins, before there were banks, before there was anything we would recognize as money, a woman sat down in a merchant house and dictated a letter to her husband. She was worried. The creditors had been coming to the door. She needed silver, not promises, silver, and she needed it now. The letter was pressed into a clay tablet, sealed in a clay envelope, loaded onto a donkey, and began a journey of a thousand miles across ancient Anatolia to her husband in the city of Assur.

That woman's name was Taraam Kubii. She lived approximately nineteen hundred years before Christ. And her letter is the oldest financial stress document in human history.

Hmm. It reads like a text message you might send this week."""),

    ("s2_barter", """Almost everyone thinks money started with barter. Somebody had chickens. Somebody else had wheat. The chicken person wanted wheat, the wheat person wanted chickens, they worked it out. Then barter got complicated, so people invented coins. Coins became paper. Paper became digital. And here we are.

That story is in every high school economics textbook. Adam Smith helped popularize it in seventeen seventy six. And it has one enormous problem: anthropologists and archaeologists spent two hundred years searching for a society that used barter before money existed and they found absolutely nothing.

Alright. No society has ever been documented operating primarily on barter before money existed. Not one. What researchers found instead, in every ancient culture they examined, was credit. Gift economies. Debt records. Temple loans. The oldest written documents on earth are not poetry, not law, not literature. They are grain receipts.

Civilization does not begin with exchange. It begins with obligation. With who owes what to whom. And the thing we now call money grew out of that."""),

    ("s3_cowrie", """Okay, so if barter was not the beginning, what did people actually use? Cowrie shells circulated as money across Africa, South Asia, and China for roughly three thousand years. Small, smooth, white, and shaped in a way that made them almost impossible to fake, they were collected from shallow reefs in the Maldive Islands, traded to India, to China, to West Africa. They were inflation resistant, durable, and beautiful. Whole governments ran on them.

Check this out: the same cowrie shell that a family in the Maldives gathered from a reef would, centuries later, travel in the hold of a European ship across the Atlantic and be exchanged for an enslaved person on the coast of West Africa. The shell that had been trusted for three thousand years became the currency of the slave trade. The people who gathered it never knew."""),

    ("s4_yap", """Yeah, then there are the rai stones of Yap Island in the Pacific. These are limestone discs, some of them twelve feet across, weighing up to four tons. They were quarried on the island of Palau, two hundred fifty miles away, and transported by raft across open ocean at the cost of extraordinary labor and, sometimes, human life.

The stones did not move when ownership transferred. The whole island just agreed who owned which stone, and that knowledge lived in the community's collective memory. There was one stone that had sunk to the bottom of the ocean during transport. The community agreed it had not been lost. Ownership could still be transferred on a stone no one could see or touch, sitting at the bottom of the Pacific Ocean.

That is the oldest version of a distributed ledger. The Yap stone is a blockchain four thousand years before computers. The unit of account existed in shared memory, not in any physical location, and it worked for centuries, until an American sea captain named David O'Keefe arrived in the eighteen seventies with a ship and a dynamite quarry. He imported cheap rai stones by the boatload. In one decade, he introduced inflation to an economy that had never experienced it."""),

    ("s5_tally", """In medieval England, the preferred monetary technology was a piece of hazel wood. The tally stick. A notch cut into the wood represented a specific quantity, grain or silver or labor owed. Then the stick was split down the middle. The creditor kept one half. The debtor kept the other. No two splits were identical. You could not forge one without the matching half.

Alright, the English government ran on tally sticks for seven hundred years. When Henry the First needed to collect taxes in the eleven hundreds, he paid his collectors in tally sticks representing future tax receipts. They circulated as money. They were trusted.

In eighteen thirty four, Parliament decided to retire the tally stick system and burn the old sticks. A workman stoked a furnace beneath the House of Lords with two cartloads of sticks. The flues overheated. The paneling caught fire. By morning, both the House of Lords and the House of Commons had burned to the ground. The painter J.M.W. Turner watched from a boat on the Thames and made two paintings of the fire.

The monetary technology of seven hundred years destroyed its replacement in a single night."""),

    ("s6_cacao", """In Mesoamerica, the currency was cacao beans. Real ones. Chocolate, or more precisely the fermented seeds of the cacao tree, circulated as money throughout the Aztec economy and much of Central America. A tamale cost one bean. A rabbit cost ten beans. A turkey hen cost a hundred beans.

Hmm. And the counterfeit problem was so severe that buyers in the market routinely broke each bean open before accepting it. Counterfeiters had perfected the technique of hollowing out a bean, filling it with a mixture of clay and avocado skin, and resealing it so carefully it was indistinguishable from the outside. Every transaction at scale required physical verification of every unit.

That's crazy. The whole ancient economy ran on a currency you literally had to taste to trust."""),

    ("s7_machine", """Okay. Cowrie shells, rai stones, tally sticks, and cacao beans were all different communities' answers to the same question: what can we all agree to trust? Each one worked, sometimes for centuries. And each one was eventually destroyed, not because it failed, but because it became inconvenient to someone with more power.

But there is a deeper story beneath the objects. In ancient Mesopotamia, the first civilization to build money into a complex institution, a structural trap was being built into every grain loan issued from every temple storehouse.

The interest rate on a grain loan in Sumer was thirty three and one third percent annually. That number was not chosen by market forces. It was chosen because the Mesopotamian counting system was based on sixty, and one third expressed in that system is a perfectly clean fraction. Sixty divided by three is twenty. The interest rate that governed an empire for fifteen hundred years was set for arithmetic convenience.

In a good year, a Babylonian farmer might yield twenty five percent above subsistence. That left something after interest. But one bad harvest, one flood, one drought, and the debt became unpayable. Two bad harvests and the farmer's sons were working in the creditor's household. Three bad harvests and the land was gone. The system was not designed to trap people. It was built in a way that made the trap inevitable under conditions that were themselves inevitable."""),

    ("s8_amargi", """Alright. The kings of Babylon understood this. They had to. When unpayable debt accumulated long enough, farmers abandoned their fields, city populations starved, tax revenues collapsed, and armies went unpaid. Debt was not a moral failure. It was a structural maintenance problem. And the solution was called the mishaarum decree.

At the beginning of a new reign, or during a crisis, the king would proclaim the mishaarum. All agricultural debts canceled. Debt slaves freed. Land returned to its original owners. Merchants who had been using debt claims to accumulate peasant land were required to give it back.

The Sumerian word for this freedom was amargi. It means return to the mother. It is the oldest known written word for freedom in any human language.

That's crazy, right? The first freedom humans ever wrote down was not the freedom of speech, not the freedom of religion, not the freedom to vote. It was the freedom from debt. The first thing civilization needed a word for, when it needed a word for freedom, was a financial word."""),

    ("s9_rome", """Rome stopped doing it.

Roman law in the early Republic allowed for debt bondage so severe that the Twelve Tables, the foundation of Roman law, contained a provision allowing a debtor to be divided among multiple creditors if he owed more than one. Whether that provision was literally practiced is debated by historians. But the fact that it was written into the founding legal document of the civilization that we inherited tells you everything about how Rome understood the relationship between creditor and debtor.

Around three hundred twenty six years before Christ, Rome passed a reform called the lex Poetelia Papiria and abolished physical debt slavery for citizens. That looks like progress. But the debt itself remained. The law canceled the bondage and not the obligation. The land concentrated. Small farmers became tenants on land they used to own. Rome grew enormous and eventually collapsed under the weight of a social structure with no pressure valve.

Okay. Western civilization did not inherit the Mesopotamian tradition of the mishaarum. It inherited Roman creditor law. It inherited the Twelve Tables. It inherited a legal framework built on the principle that debt is a contract, contracts are sacred, and sacred contracts do not get canceled."""),

    ("s10_modern", """So here we are.

A credit card at twenty four percent annual interest in an economy growing at three percent per year. Student loan debt compounding across decades for people whose degree did not deliver the income that would allow repayment. Countries in the developing world borrowing in dollars at interest rates they cannot outpace, then opening their economies to foreign capital as a condition of the next loan.

Yeah. The word stockholder comes from the stock, which was the other half of a tally stick. The language of finance still carries the memory of the old objects. But the reset mechanism is gone. The mishaarum is gone. The amargi is gone. The word for freedom that is also a financial word is now a piece of ancient Sumerian that almost nobody knows.

The ancient world did not cancel debts because the kings were generous. They canceled debts because they understood that a system with no relief valve does not survive. The argument for debt cancellation was not moral. It was pragmatic. And the argument was sound enough that it survived for two thousand years across the most sophisticated civilizations the ancient world ever produced.

Then one tradition, the Roman one, decided not to maintain the machine. And we built our world on that decision.

The first word humans ever wrote for freedom meant getting out of debt. What we have inherited is the version of civilization that decided that kind of freedom would no longer be on offer.

If this video made you see money differently, subscribe. There is a lot more history underneath the system that runs your life."""),
]

# ══════════════════════════════════════════════════════════
# GENERATION — No need to edit below this line (war-dollar archive below)
# ══════════════════════════════════════════════════════════

_WAR_DOLLAR_SECTIONS_ARCHIVE = [
    ("s1_hook", """In nineteen seventy one, the United States broke a promise it had kept for twenty seven years. The dollar was no longer backed by gold. And for the next three years, nobody in Washington had any idea what would back it instead.

Hmm. Think about what that means. Every dollar you have ever earned, saved, or spent has been a piece of paper the United States government promised was worth something. Before nineteen seventy one, that promise was backed by gold. Thirty five dollars could be exchanged for one ounce of gold. Any country in the world could walk up to the US Treasury and make that trade. Then one Sunday evening in August, Nixon went on television and said the trade was off.

The dollar still existed. Banks were still open. Your paycheck still deposited. But the thing backing the dollar had just been removed. Alright. So the question became: what backs it now?

The answer to that question would involve a secret meeting in the Saudi Arabian desert, a deal hidden from the American public for forty one years, and a series of wars whose true cost has never fully been reckoned with."""),

    ("s2_bretton_woods", """To understand why nineteen seventy one mattered so much, you have to go back to nineteen forty four.

World War Two was still being fought. The Allied victory was not yet certain. But American and British economists already knew they needed to plan what money would look like after the war ended. So they gathered at a resort hotel in Bretton Woods, New Hampshire. Forty four nations sent delegates. And over three weeks, they built the financial architecture of the modern world.

The system they created was elegant. The dollar was pegged to gold at thirty five dollars per ounce. Every other currency was pegged to the dollar. If you held dollars, you could exchange them for gold at a fixed rate. This made the dollar the anchor of the entire global economy.

Yeah, it worked for a reason. After the war, the United States held roughly seventy five percent of the world's monetary gold. American factories were untouched. European economies were in ruins. The dollar was, quite literally, as good as gold.

For twenty seven years, the system held. Then Vietnam and the Great Society happened at the same time, and the US started spending more dollars than it had gold to cover."""),

    ("s3_nixon_shock", """By the late nineteen sixties, a problem was developing. The United States had been pumping dollars into the world to finance the Marshall Plan, the Korean War, the Vietnam War, and Lyndon Johnson's Great Society programs all at once. There were now more dollars circulating in the world than there was gold in Fort Knox to back them.

France noticed first. President Charles de Gaulle was suspicious of what he called America's exorbitant privilege. He started converting France's dollar reserves into gold. Other countries followed. The US gold reserves started draining.

By August of nineteen seventy one, the drain had become a crisis. Nixon's Treasury officials warned him that a run on American gold reserves could collapse the system. So on August fifteenth, a Sunday evening, Nixon interrupted prime time television to announce what he called a temporary measure. The United States was suspending the dollar's convertibility into gold.

Okay. That was fifty four years ago. The dollar has never been backed by gold again.

In one television appearance, Nixon ended twenty seven years of monetary order. The dollar became a fiat currency, backed by nothing except the trust that the world placed in the United States government. And that trust needed to be rebuilt fast."""),

    ("s4_dollar_crisis", """In the years after the Nixon Shock, the dollar fell. By some measures it lost about thirty percent of its value against other major currencies through the nineteen seventies. Inflation surged. The exorbitant privilege that France had complained about was vanishing.

The problem was structural. The world had been using dollars as its reserve currency for twenty seven years because dollars were as good as gold. Now they were not. Why would foreign governments continue holding massive reserves of US dollars if the dollar was just paper?

Hmm. Someone in Washington had to come up with an answer. That someone was Henry Kissinger.

Kissinger was Nixon's National Security Adviser and later his Secretary of State. He was arguably the most powerful diplomat in the world. And in the early nineteen seventies, he started working on a geopolitical solution to a monetary problem.

The world had to buy oil. If you could make the world buy oil in dollars, you would recreate global dollar demand without needing gold at all. The oil fields of the Middle East were, in this sense, a potential replacement for the vaults of Fort Knox.

All Kissinger needed was a deal."""),

    ("s5_the_deal", """In June of nineteen seventy four, Henry Kissinger flew to Riyadh, the capital of Saudi Arabia. He met with Saudi officials including Prince Fahd, who would later become king. What was agreed in those meetings would remain secret for over forty years.

The deal, as revealed through a Bloomberg FOIA request in twenty sixteen, had two core elements. The United States would provide military protection to Saudi Arabia, along with weapons and security guarantees. In return, Saudi Arabia would price its oil exclusively in US dollars and invest the enormous revenues from that oil into US Treasury bonds.

Check this out. By nineteen seventy five, every single OPEC nation had adopted dollar pricing for its oil. The entire global oil market was denominated in one currency. And because every country on Earth needs oil, every country on Earth now needed to acquire and hold US dollars, regardless of whether they traded with the United States at all.

The gold standard had been replaced. The new backing for the dollar was not a metal sitting in a vault. It was black liquid flowing through pipelines, priced in one currency, protected by the most powerful military in human history.

The deal was never put to a vote in Congress. It was never disclosed to the American public. It was a diplomatic arrangement between two governments, kept entirely in secret. Alright. The petrodollar system had been born."""),

    ("s6_mechanics", """To understand why this deal was so powerful, you need to understand how petrodollar recycling works.

Step one. You drill oil out of the ground in Saudi Arabia. You sell it to Japan or Germany or Brazil. They pay you in dollars, because oil is priced in dollars and they had to acquire dollars first. You now have an enormous pile of dollars.

Step two. What do you do with all those dollars? You cannot just sit on them. They lose value to inflation if you do. So you invest them. And the safest, most liquid investment in the world, denominated in dollars, is a United States Treasury bond.

Step three. The United States government receives that investment. It has now borrowed money from a foreign oil producer to finance its own spending. The interest it pays on those bonds is modest. The benefit it receives is enormous: the ability to run massive deficits without triggering a currency crisis.

Step four. Those low Treasury yields also keep mortgage rates lower, car loan rates lower, and consumer borrowing costs lower for ordinary Americans. The petrodollar system is, among other things, a hidden subsidy for American borrowing.

Yeah. The cycle runs in a closed loop. Military protection keeps oil flowing, which keeps dollar demand high, which keeps Treasury bond demand high, which keeps American borrowing cheap, which finances more military spending to keep the cycle going."""),

    ("s7_embargo", """The deal was struck in nineteen seventy four. But the crisis that made it necessary had already begun the year before.

In October of nineteen seventy three, the Arab members of OPEC declared an oil embargo against the United States in retaliation for American support of Israel in the Yom Kippur War. The price of oil quadrupled almost overnight. In the United States, gasoline rose from thirty four cents per gallon to eighty four cents per gallon.

Drivers waited in lines stretching around city blocks to fill their tanks, and sometimes could not get gas at all. The speed limit on American highways was lowered to fifty five miles per hour to conserve fuel. Christmas lights were banned in Oregon. Times Square went dark to save electricity. The symbols of American abundance suddenly required rationing.

Alright. For ordinary Americans this was the first time they felt the petrodollar problem in their bodies. The economy that had seemed unstoppable since World War Two was suddenly revealed to be dependent on a resource controlled by kingdoms on the other side of the world."""),

    ("s7_iran", """Then in nineteen seventy nine, the Iranian Revolution happened. The Shah fell. Iranian oil production was cut sharply. Oil prices more than doubled again, reaching thirty nine dollars and fifty cents per barrel. Stagflation, meaning simultaneous high inflation and high unemployment, devastated American families throughout the late nineteen seventies. The auto industry collapsed as buyers switched to fuel efficient Japanese and German cars. The word malaise entered the national vocabulary."""),

    ("s8_carter_doctrine", """President Jimmy Carter, who had built his political identity around human rights and peaceful diplomacy, delivered his State of the Union address in January of nineteen eighty. In that address, he made a declaration that has shaped American military policy ever since. He said: an attempt by any outside force to gain control of the Persian Gulf region will be regarded as an assault on the vital interests of the United States of America, and such an assault will be repelled by any means necessary, including military force.

The Carter Doctrine was historic. For the first time, the United States formally committed its military to defending oil flows in the Persian Gulf. Oil security had become a military obligation, formalized in doctrine.

Hmm. To back that up, Carter created the Rapid Deployment Joint Task Force. Reagan expanded it into US Central Command, or CENTCOM, in nineteen eighty three. Today, CENTCOM oversees all American military operations in the Middle East and coordinates with forty countries in the region. Its forward headquarters is at Al Udeid Air Base in Qatar, where ten thousand US troops are permanently stationed. The US Navy's Fifth Fleet is permanently based in Bahrain, just nineteen miles from the Iranian coast.

The military infrastructure that enforces the petrodollar system was now formally and permanently in place."""),

    ("s9_gulf_war", """In August of nineteen ninety, Saddam Hussein invaded Kuwait. Within hours, oil prices nearly doubled, jumping from around seventeen dollars to over thirty five dollars per barrel.

The United States and a coalition of thirty four nations responded with a military campaign. Iraq had invaded the world's sixth largest oil producer and was now positioned to threaten Saudi Arabia. If Saddam Hussein controlled Persian Gulf oil production, he would control the price of the fuel that ran the global economy.

Operation Desert Storm began in January of nineteen ninety one. One hundred hours of ground combat, and the Kuwaiti oil fields were liberated. Oil prices fell back below twenty dollars per barrel almost immediately after fighting ended.

Yeah. The Gulf War demonstrated the system working exactly as designed. When oil flows were threatened, the military responded. The petrodollar arrangement was enforced."""),

    ("s9_blowback", """But the war created a new problem. To launch the operation, the United States established permanent military bases in Saudi Arabia. Large numbers of American troops were stationed in the land containing Islam's two holiest cities. A young Saudi named Osama bin Laden, who had fought the Soviets in Afghanistan with US support, issued a fatwa against American troops on Saudi soil. His stated primary grievance was the US military presence in the Arabian Peninsula, not the Israeli conflict that Western officials typically cited.

The enforcement mechanism for the petrodollar system had just generated the conditions for its most catastrophic challenge."""),

    ("s10_euros", """In October of the year two thousand, Saddam Hussein did something that had never been done before in the history of the modern oil market. He switched Iraq's oil sales from dollars to euros.

Under the United Nations Oil for Food program, which allowed Iraq to sell oil for humanitarian goods despite sanctions, Iraq began pricing its oil in euros and accepting euro payments. Saddam called it a political decision. He publicly stated that the US dollar was a currency of the enemy.

Some economists at the time dismissed it as symbolic. Others recognized the significance. If Iraq's example spread, if other oil producers began pricing in euros or other currencies, the structural demand for dollars would weaken. The entire petrodollar arrangement rested on the global necessity of acquiring dollars to buy oil. A euro oil market would undermine that necessity.

Alright. Iraq's oil exports under the Oil for Food program were modest. But the precedent was dangerous. Other countries, particularly Iran and Venezuela, were watching."""),

    ("s10_invasion", """Three years later, the United States invaded Iraq. The Bush administration made five hundred and thirty two explicit statements claiming Iraq possessed weapons of mass destruction. None were true. One of the first acts of the American occupation after the fall of Baghdad was to switch Iraq's oil sales back to US dollars."""),

    ("s11_iraq_war", """The Iraq War was projected to cost fifty to sixty billion dollars. That was the number the Bush administration gave to Congress and to the American public.

The actual cost, as estimated by economists Joseph Stiglitz and Linda Bilmes, exceeded three trillion dollars. When you include lifetime veteran care costs through twenty fifty, interest payments on war debt, and broader regional conflicts triggered by the invasion, the Brown University Costs of War Project estimates the total approaches eight trillion dollars.

That's crazy. The projection was off by a factor of at least fifty. No private company, no individual in America could misrepresent costs by a factor of fifty and face zero legal consequence. But the government projected sixty billion and spent three trillion, and the people who made that projection faced no accountability whatsoever.

Alright. The wars were funded in a way unprecedented in American history. Every major American war before this one, including Vietnam, had been accompanied by tax increases. World War Two included a ninety four percent top marginal tax rate. But in twenty oh one and again in twenty oh three, Congress cut taxes while simultaneously launching the most expensive military campaigns in history. The cost was not paid by the generation that voted for the war. It was charged to future generations through debt, and over one trillion dollars in interest on that war debt has already been paid."""),

    ("s12_libya", """The same pattern appeared again in Libya in twenty eleven.

Muammar Gaddafi had ruled Libya since nineteen sixty nine. He was a dictator with a documented history of brutality against dissidents. None of that is in dispute. But in his final years, Gaddafi had also been working on a financial project that alarmed Western officials in ways that had nothing to do with terrorism.

He was building a gold dinar. A pan African, gold backed currency that African nations could use to trade with each other and to sell oil, completely outside the dollar and euro systems. Libya held one hundred and forty three tons of gold for this purpose.

Hmm. Nicolas Sarkozy, the French president, was briefed on the proposal. Documents obtained through Hillary Clinton's emails describe Gaddafi's gold reserves and currency plan as motivating factors in the push for intervention. Sarkozy reportedly described Gaddafi as a threat to the financial security of the world.

That's crazy, right? The public justification for NATO intervention was the protection of civilians. That justification was real. Gaddafi was threatening to massacre rebels in Benghazi. But a State Department email from a Clinton aide cited the gold dinar plan explicitly alongside the human rights rationale. The financial threat appears to have added urgency that a human rights case alone might not have generated.

In October of twenty eleven, Gaddafi was captured and killed. Libya's gold reserves were dispersed. The gold dinar plan ended."""),

    ("s13_the_cost", """Step back and look at the full accounting.

The Brown University Costs of War Project has tracked the financial toll of post September eleventh American military operations. Their estimate for total costs, including veteran care obligations through twenty fifty and interest on war debt, approaches eight trillion dollars.

Okay. Eight trillion dollars. The entire federal budget in twenty twenty four was approximately six and a half trillion dollars. The wars cost more than a full year of everything the United States federal government spends, on every program, every department, every obligation combined.

That eight trillion was borrowed. Every dollar of it added to the national debt, which now stands at thirty eight trillion dollars. The interest payments on that debt currently run over one trillion dollars per year. More than the US spends on Medicaid. More than it spends on all non defense discretionary programs combined.

The opportunity cost is almost impossible to comprehend. The eight trillion spent on post September eleventh wars could have funded the entire United States kindergarten through twelfth grade education system for thirteen years. Military spending creates roughly five jobs per million dollars of investment. Education spending creates thirteen jobs per million dollars. Clean energy spending creates nearly seventeen jobs per million dollars.

Nine hundred thousand people were killed in the post September eleventh conflicts. Thirty seven million were displaced."""),

    ("s14_profiteering", """The wars created enormous wealth for a small number of people and institutions.

Halliburton and its subsidiary KBR received at least thirty nine and a half billion dollars in federal contracts related to the Iraq War. They were awarded a seven billion dollar contract to manage Iraq's oil infrastructure. Only Halliburton was allowed to bid on it. The Defense Contract Audit Agency later found one point four billion dollars in what it called questionable and unsupported costs from Halliburton alone. A separate KPMG audit found eight point eight billion dollars in Iraqi oil revenues that simply could not be accounted for after being distributed by the Coalition Provisional Authority.

Alright. Dick Cheney was the CEO of Halliburton from nineteen ninety five to two thousand, the year he became Vice President. Under his tenure as CEO, Halliburton rose from seventy third to eighteenth on the Pentagon's list of top contractors. When he became Vice President and later pushed for the Iraq War, he continued receiving up to one million dollars per year in deferred compensation from Halliburton.

Paul O'Neill, who served as Bush's Treasury Secretary, later revealed that the very first National Security Council meetings of the Bush presidency, nine months before September eleventh, had included briefing materials titled Plan for Post Saddam Iraq, complete with maps dividing up Iraq's oil fields. The war was being planned before the attack that justified it."""),

    ("s15_cracks", """For five decades, the petrodollar system held. Then the United States began using the dollar itself as a weapon, and the consequences were not what Washington anticipated.

In February of twenty twenty two, the United States and its European allies froze approximately three hundred billion dollars in Russian central bank reserves in response to the invasion of Ukraine. It was the largest financial weapon ever deployed against a major economy. It sent a signal to every country in the world that held dollar reserves: if Washington decided your government was acting unacceptably, your savings could be confiscated overnight.

The response was immediate and global. Russia and China shifted ninety percent of their bilateral trade, representing two hundred and forty billion dollars per year, into yuan. China expanded its CIPS payment system, which now connects four thousand eight hundred banks in one hundred and eighty five countries. Saudi Arabia began accepting yuan for some oil sales to China and signaled interest in joining BRICS. India, Brazil, and the Gulf states began negotiating bilateral trade agreements that bypass the dollar entirely.

Yeah. The dollar's share of global reserves has fallen from seventy one percent in nineteen ninety nine to under fifty seven percent today, the lowest since nineteen ninety four. Every time the US weaponizes dollar access, it gives other countries a stronger reason to build the infrastructure to not need dollars at all. The tool of coercion is accelerating its own obsolescence."""),

    ("s16_today", """On February twenty eighth, twenty twenty six, joint US and Israeli military strikes began against Iran's nuclear and military infrastructure.

Iran responded by mining the Strait of Hormuz, the narrow waterway connecting the Persian Gulf to the global ocean shipping lanes. Approximately twenty million barrels of oil pass through the Strait every single day, representing roughly twenty percent of the entire global oil supply. Within days, tanker traffic dropped by seventy percent. Over one hundred and fifty ships anchored outside the strait, waiting.

Oil prices rose from seventy dollars per barrel to over one hundred and ten dollars per barrel, a forty two percent increase in less than two weeks. Gas prices in the United States jumped from under three dollars per gallon to over three dollars and sixty cents. Airlines immediately announced fuel surcharges. Shipping costs spiked. Developing nations that import oil began facing currency crises.

Okay. Economists estimate the conflict could push US inflation from two point four percent to three percent or higher. The IMF calculates that every ten percent rise in oil prices adds zero point four percent to global inflation and reduces economic growth by zero point one five percent. And the daily cost of military operations ranges from eight hundred million to two billion dollars.

The system built in nineteen seventy four is now fifty two years old. The country it was built around, and in many ways built against, is the same country now at the center of the crisis. And every day the Strait stays closed, the cost of the deal Kissinger made in secret compounds further."""),

    ("s17_close", """Fifty two years ago, Henry Kissinger flew to Riyadh and made a deal in secret. He replaced gold with oil as the dollar's anchor. He turned Middle Eastern wars from things America could choose to fight into things it felt it had to fight. He created a system so deeply embedded in the global economy that most people who live inside it have never been told it exists.

The numbers are now visible. Eight trillion dollars in war costs, thirty eight trillion in national debt, over one trillion in annual interest payments every year, nine hundred thousand people killed, and thirty seven million displaced. The dollar's reserve share is falling for the first time in a generation.

Yeah. The alternatives being built today are real but incomplete. China's CIPS system is growing, but the yuan's share of global reserves is under three percent. BRICS members disagree with each other more than they agree. A sudden collapse of the dollar is not what the evidence points to. A slow erosion, accelerating under the pressure of sanctions overuse and the long term energy transition away from oil, is far more likely.

The deal was struck in secret. The cost has never been fully disclosed to the people who paid it. And the countries that were never asked if they wanted to use American dollars are building a way out. The system will change. The only question is who pays when it does.

If this changed how you think about where money comes from and what backs the dollar in your wallet, hit subscribe. There is more hidden history of money where this came from."""),
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
