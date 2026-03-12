#!/usr/bin/env python3
"""
MoneyMath — General Image Generation Pipeline
Generates scene images using Gemini with an optional reference character image.

Usage:
  1. Set USE_REF_IMAGE = True/False depending on whether a character reference is needed
  2. If True, place your character reference image at reference/character.png
  3. Edit IMAGES below with your scene prompts
  4. Set PROJECT_NAME to your project folder name
  5. Run: python3 generate_images.py
"""

import os
import sys
import time
import base64
import concurrent.futures
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

from cost_tracker import log_gemini_image_cost

# ══════════════════════════════════════════════════════════
# API KEYS — Loaded from .env (more keys = faster parallel generation)
# ══════════════════════════════════════════════════════════

API_KEYS = [
    os.getenv("GEMINI_API_KEY"),
    os.getenv("GEMINI_KEY_1"),
    os.getenv("GEMINI_KEY_2"),
    os.getenv("GEMINI_KEY_3"),
    os.getenv("GEMINI_KEY_4"),
    os.getenv("GEMINI_KEY_5"),
    os.getenv("GEMINI_KEY_6"),
    os.getenv("GEMINI_KEY_7"),
    os.getenv("GEMINI_KEY_8"),
]
API_KEYS = [k for k in API_KEYS if k]
if not API_KEYS:
    print("ERROR: No GEMINI API keys found in .env")
    sys.exit(1)
print(f"Loaded {len(API_KEYS)} API keys")

# ══════════════════════════════════════════════════════════
# CONFIGURATION — Edit these for each new video
# ══════════════════════════════════════════════════════════

PROJECT_NAME = "origin-of-debt"  # Folder name under public/

MODEL = "gemini-3.1-flash-image-preview"

# Set to False to skip reference image (pure scene/documentary style)
USE_REF_IMAGE = True

# Reference character image — only loaded if USE_REF_IMAGE is True
REF_IMAGE_BYTES = None
REF_MIME = "image/png"
if USE_REF_IMAGE:
    REF_IMAGE_PATH = ROOT / "reference/character.png"
    REF_IMAGE_BYTES = REF_IMAGE_PATH.read_bytes()
    _ext = REF_IMAGE_PATH.suffix.lower()
    REF_MIME = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}.get(_ext.lstrip("."), "image/png")
    print(f"Loaded reference image: {REF_IMAGE_PATH} ({len(REF_IMAGE_BYTES) // 1024} KB)")
    print(f"Reference image type: {REF_MIME}")
else:
    print("Reference image: disabled (USE_REF_IMAGE = False)")

# Character base identity — face, skin tone, body type only. NO clothing.
# Each image prompt must specify scene-appropriate attire explicitly.
# The character MUST appear in every image — no objects-only shots.
# His position depends on the scene: examining a document, standing near a
# storefront, watching a crowd, etc. He is the visual focus for personal/
# emotional moments; background or peripheral for historical/data scenes.
CHAR = "The character from the reference image"

# Visual style constants
STYLE = "Cinematic documentary illustration, photorealistic detail, dramatic chiaroscuro lighting, rich warm colors, historically accurate, National Geographic quality."

# ══════════════════════════════════════════════════════════
# IMAGE PROMPTS — word-level precision: one image per narration sentence/phrase
# Each image illustrates the exact sentence being spoken at that moment.
# ══════════════════════════════════════════════════════════

IMAGES = [

    # ── H: Hook (s1_hook) ──

    ("H01", f"Extreme closeup of ancient Sumerian cuneiform script pressed into wet clay, a reed stylus resting beside it, warm amber candlelight illuminating the wedge shaped marks, the word amargi barely visible among the dense inscriptions. {STYLE}"),

    ("H02", f"A single clay tablet the size of a hand, lying flat on a stone surface in a shaft of morning light, cuneiform marks densely carved across its face, dust and antiquity visible in every crevice. {STYLE}"),

    ("H03", f"The single Sumerian cuneiform symbol for amargi, displayed large against a deep charcoal background, golden light behind it, radiating quiet power, ancient and absolute. {STYLE}"),

    ("H04", f"A Sumerian farmer, head bowed, standing outside a massive clay walled temple at dusk, hands open at his sides, the weight of unpayable debt visible in his posture. The city of Lagash visible behind him. {STYLE}"),

    ("H05", f"The same Sumerian farmer now standing upright, looking toward the horizon, a different posture entirely, the posture of a person whose debt has just been cancelled, the word AMARGI carved into the stone wall beside him. {STYLE}"),

    ("H06", f"Rams horns being lifted to mouths by three figures on a Mesopotamian city wall at golden hour, the city spreading below them, sound implied in the lifted instruments and open sky. {STYLE}"),

    # ── W: The Word (s2_the_word) ──

    ("W01", f"Aerial view of the ancient Mesopotamian river valleys, the Tigris and Euphrates visible as dark ribbons through flat tan land, small farming settlements visible at the edges, reeds growing at the banks, circa 3000 BCE. {STYLE}"),

    ("W02", f"A Sumerian farmer kneeling in a grain field at harvest time, examining stalks of barley that have grown poorly, his face carrying the arithmetic of a bad harvest, not enough to pay back what was borrowed. {STYLE}"),

    ("W03", f"Interior of an ancient Sumerian temple storage room, massive clay jars of grain stacked in rows, a priest administrator in formal dress reviewing clay tablets by oil lamp light. {STYLE}"),

    ("W04", f"Closeup of a Sumerian scribe's hands pressing a sharpened reed stylus into wet clay, making precise cuneiform marks, a line of completed loan records drying on a shelf beside him. {STYLE}"),

    ("W05", f"A Sumerian farmer standing across from a temple scribe at a low clay table, listening to terms being read aloud, pressing his seal into wet clay as his signature, the moment the debt begins. Humble posture. Formal setting. Power imbalance visible. {STYLE}"),

    ("W06", f"Ancient Sumerian tablet showing the cuneiform word for interest alongside a carved image of a calf beside a cow, illustrating the origin of the concept of compound growth. Held in a museum display light. {STYLE}"),

    ("W07", f"A Sumerian family huddled in a small clay dwelling at night, father looking at his hands, mother holding a child, the anxiety of an unpayable debt filling the space, specifically the fear of losing children to temple labor. {STYLE}"),

    ("W08", f"Wide view of a Mesopotamian city during a jubilee proclamation, a public square filled with people, a herald on a raised platform reading a royal decree, rams horns blowing, the atmosphere electric with collective relief. {STYLE}"),

    ("W09", f"A broken clay tablet in two pieces on a stone floor, the debt record split apart, the visual metaphor of debt cancellation, the record destroyed, the obligation gone. Warm lamplight on the fragments. {STYLE}"),

    ("W10", f"A Sumerian farmer walking away from the temple through a city gate toward the countryside, full stride, head up, a man returning home, the feeling of amargi visible in every line of his body. Evening light behind him. {STYLE}"),

    ("W11", f"A busy Mesopotamian marketplace circa 3000 BCE before coins existed, merchants exchanging grain sacks and livestock, clay token trades being made, no metal currency visible anywhere, the ancient world running entirely on commodity barter and credit. {STYLE}"),

    ("W12", f"A simple clay tablet showing two hand drawn lines: one climbing steeply labeled DEBT WITH INTEREST, one rising slowly labeled CROP YIELD, the gap between them widening over years, carved by a Sumerian scribe to show the mathematical impossibility of repayment when interest outpaces harvest. {STYLE}"),

    ("W13", f"An ancient cuneiform dictionary tablet displayed in museum archival light, a curator's gloved finger pointing to the word amargi among hundreds of symbols, the oldest recorded word for freedom identified in a clay document approximately five thousand years old. {STYLE}"),

    # ── B: Babylon / Ancient Wisdom (s3_ancient_wisdom) ──

    ("B01", f"A young Babylonian student in a temple scribal school, approximately fifteen years old, seated cross legged with a clay tablet on his lap, working through a compound interest calculation, his teacher watching from behind. Warm interior light. {STYLE}"),

    ("B02", f"Closeup of an ancient Babylonian clay tablet covered in mathematical notation, showing exponential growth calculations for compound interest, a school exercise from approximately 2000 BCE. Museum quality lighting. {STYLE}"),

    ("B03", f"Split image composition: on the left, a line showing exponential compound interest growth curving sharply upward; on the right, a line showing agricultural growth rising slowly and steadily. Both lines drawn in ancient Babylonian style on aged clay. The gap between them is enormous. {STYLE}"),

    ("B04", f"The Hammurabi Stele, the massive seven foot black basalt column covered in cuneiform inscriptions, standing in a museum, a shaft of dramatic light illuminating the relief carving of Hammurabi receiving the law from the sun god Shamash at the top. {STYLE}"),

    ("B05", f"Extreme closeup of the cuneiform text on the Hammurabi Stele, dense wedge shaped marks filling the frame, with a faint overlay showing the translated words: MAXIMUM INTEREST RATE: THIRTY THREE PERCENT. {STYLE}"),

    ("B06", f"King Hammurabi seated on a throne, a royal administrator before him presenting a clay tablet, other officials watching, the scene of a debt cancellation decree being formally issued in the Babylonian palace, circa 1754 BCE. {STYLE}"),

    ("B07", f"Babylonian city scene during a jubilee: former debt slaves being released from temple service, reuniting with families in a public courtyard, the scene carrying deep emotional weight without sentimentality. {STYLE}"),

    ("B08", f"Ancient map or aerial illustration of the Near East, showing the great ancient cities Lagash, Ur, Uruk, Babylon, marked as centers of financial innovation and debt law, trade routes connecting them across the landscape. {STYLE}"),

    ("B09", f"A clay tablet from the Yale Babylonian Collection showing mathematical calculations, held in white gloved museum hands under careful light, one of the oldest compound interest calculations in human history. {STYLE}"),

    ("B10", f"Ancient Babylonian classroom scene: ten young scribal students all bent over clay tablets doing the same compound interest doubling time problem, one student looking up with visible unease at the answer he has just calculated. {STYLE}"),

    ("B11", f"Side by side comparison visual: left panel shows an ancient stone tablet carved with the words THIRTY THREE PERCENT MAXIMUM in period accurate script; right panel shows a modern payday loan sign in a storefront window reading FOUR HUNDRED PERCENT APR. Same visual structure, five thousand years apart. {STYLE}"),

    ("B12", f"Wide exterior view of a modern payday loan storefront at night, neon signs reflected on wet pavement, a person entering the door, the ancient debt trap with new lighting and signage, the architectural structure of extraction unchanged. {STYLE}"),

    # ── D: Dismantling Part 1 (s4_dismantling_pt1) ──

    ("D01", f"Interior of a medieval Catholic cathedral under construction, stone arches rising overhead, money changing hands between a Church official and a merchant, a document being signed, the Church doing what its own doctrine prohibited. Dramatic shaft of light from a high window. {STYLE}"),

    ("D02", f"A medieval illuminated manuscript open to a page discussing usury, showing a moneylender being condemned by religious figures, rich gold leaf borders around the text, the imagery of moral prohibition against charging interest. {STYLE}"),

    ("D03", f"John Calvin in his Geneva study circa 1545, seated at a writing desk, quill in hand, reading by candlelight, mid thought, the specific moment before he writes the argument that will dismantle a thousand years of Church law. {STYLE}"),

    ("D04", f"A Protestant church congregation in Geneva in the 1550s, a merchant class audience, men in dark wool coats listening to a sermon, the social class that would benefit most from Calvin's theological permission to charge interest. {STYLE}"),

    ("D05", f"A medieval English debtors prison exterior, stone walls, small barred windows, a street scene with people passing by ignoring the hands reaching through the bars, circa seventeen hundreds. Grim gray light. {STYLE}"),

    ("D06", f"Interior of the Marshalsea debtors prison in London, men of various social classes sitting on benches or lying on straw, some reading by thin window light, the particular misery of people imprisoned not for violence but for poverty. {STYLE}"),

    ("D07", f"John Dickens, Charles Dickens father, seated alone in a cell in the Marshalsea prison in London, eighteen twenty four, a man of decent bearing in reduced circumstances, staring at his hands. The debt he owes: forty pounds to a baker. {STYLE}"),

    ("D08", f"A twelve year old boy walking past the high stone wall of the Marshalsea prison on his way to work in the early morning, a small figure beside a massive wall, carrying the knowledge that his father is on the other side. {STYLE}"),

    ("D09", f"Young Charles Dickens inside a boot blacking factory, pasting labels on jars of shoe polish alongside older workers, the factory dim and industrial, his clothing worn but his eyes observing everything, storing what will become his greatest novels. {STYLE}"),

    ("D10", f"An illustration styled as a Victorian woodcut showing a creditor handing a sheriff a debt warrant while a family watches in the background, the legal machinery of debt enforcement in nineteenth century England and America. {STYLE}"),

    ("D21", f"Three ancient religious texts displayed side by side on a table: a Judaic Torah scroll, a handwritten Quran page, and a Latin Bible, each open to a passage condemning usury, three faiths across three centuries all arriving at the same conclusion about charging interest on necessity. {STYLE}"),

    ("D22", f"A medieval Church ledger open to a page with columns labeled Exchange Fees, Charitable Donations, and Service Charges, the words written in elaborate calligraphy hiding the fact that each line is an interest payment in disguise, candlelight warming the deception. {STYLE}"),

    ("D23", f"A group of Protestant merchants in a dark wood paneled counting house in 1540s Antwerp, one man reading Calvin's letter aloud, the others leaning forward with expressions of visible relief and barely contained anticipation, a century of prohibition about to end in this room. {STYLE}"),

    ("D24", f"An adult Charles Dickens at his writing desk in Victorian London, surrounded by handwritten manuscript pages, looking up from his work with quiet resolve, the portraits of his most famous impoverished characters visible on the wall behind him, memory becoming literature. {STYLE}"),

    # ── D: Dismantling Part 2 (s4_dismantling_pt2) ──

    ("D11", f"A Black sharecropper family on the porch of a weathered wooden shack in the American South, circa eighteen ninety, looking at a white landowner's representative who holds a leather bound ledger, the annual settlement, which will show they still owe more than they earned. {STYLE}"),

    ("D12", f"Closeup of a plantation ledger from the Reconstruction era, handwritten columns showing debts for seed, fertilizer, food, and tools, with final numbers that always result in a balance owed, the accounting system of debt bondage. {STYLE}"),

    ("D13", f"A Black family working a cotton field in the American South, eighteen eighties, the horizon wide and flat, the work relentless, the family bound to this land not by chains but by a debt that cannot be repaid because the math is controlled by others. {STYLE}"),

    ("D14", f"Exterior of a company store in a Southern plantation town, circa nineteen ten, a line of Black sharecroppers waiting to purchase necessities on credit, prices marked on a chalkboard above the counter, prices they cannot verify, cannot compare, cannot escape. {STYLE}"),

    ("D15", f"Alonzo Bailey, a Black man in his thirties in work clothes, standing outside a courthouse in Montgomery County Alabama, nineteen oh eight, calm and straight backed despite the weight of what the state is charging him with: leaving a job. {STYLE}"),

    ("D16", f"The United States Supreme Court building in Washington DC, nineteen eleven, with a Black man and his attorney approaching the steps, representing the moment Alonzo Bailey's case reached the highest court and won a legal victory that changed almost nothing. {STYLE}"),

    ("D17", f"Robert L. Hill, a Black farmer in Arkansas, standing before a congregation of approximately one hundred sharecroppers in a rural church in Hoop Spur, Arkansas, September nineteen nineteen, explaining a lawsuit to demand an accounting of cotton prices, the meeting that changed everything. {STYLE}"),

    ("D18", f"The aftermath of the Elaine Massacre, Phillips County Arkansas, October nineteen nineteen: federal soldiers moving through the area, with a quiet documentary weight, the visual record of what happened when Black Americans tried to demand honest accounting of their earnings. {STYLE}"),

    ("D19", f"A historical document titled PROGRESSIVE FARMERS AND HOUSEHOLD UNION OF AMERICA, the founding papers of Robert L. Hill's union, whose only demand was an honest accounting of cotton sales, held under archival light. {STYLE}"),

    ("D20", f"A cotton price chart showing the market price at thirty five to forty cents per pound alongside a separate column showing the price received by Black sharecroppers at fifteen cents per pound, circa nineteen nineteen, the gap that Robert L. Hill organized to close. {STYLE}"),

    ("D25", f"An Alabama state legal document from nineteen oh eight titled An Act to Prevent Fraud in the Performance of Contracts for Personal Services, the law that made leaving a wage advance a criminal offense, held in archival display light, the mechanism of legal debt bondage made visible. {STYLE}"),

    ("D26", f"The official record of Bailey v. Alabama, a Supreme Court decision document dated nineteen eleven, stamped JUDGMENT FOR PLAINTIFF, representing a legal victory that changed almost nothing because Alabama immediately passed replacement legislation. {STYLE}"),

    ("D27", f"Alabama state legislature in session circa nineteen twelve, lawmakers gathered around a table drafting replacement peonage legislation after the Supreme Court ruling, the scene of a legal system closing one door and opening another to achieve the same end. {STYLE}"),

    ("D28", f"A Black laborer in the Mississippi Delta in nineteen forty five, still working a plantation under debt terms, decades after the Supreme Court ruling, the words PEONAGE ENDED 1867 visible on an off camera sign while the reality around him tells a different story. {STYLE}"),

    ("D29", f"Robert L. Hill photographed in Kansas after fleeing Arkansas in nineteen nineteen, standing outside a modest house far from home, a man who survived by leaving, looking toward the horizon with the particular expression of someone who won and lost simultaneously. {STYLE}"),

    ("D30", f"A row of history textbooks on a library shelf, their spines visible, with no title containing Robert L. Hill, Elaine Massacre, or Progressive Farmers Union, the systematic absence of a name that belongs in American history. {STYLE}"),

    # ── M: Modern Part 1 (s5_modern_pt1) ──

    ("M01", f"A residential street in Fresno California on the morning of September eighteenth, nineteen fifty eight, a mail carrier pushing a cart from house to house, sliding identical envelopes into each mailbox, the street sunny and quiet, the significance of the moment invisible. {STYLE}"),

    ("M02", f"Closeup of a hand opening a mailbox and removing an envelope from Bank of America, September nineteen fifty eight, inside, a small blue and gold BankAmericard that the recipient never applied for, a credit card arriving uninvited. {STYLE}"),

    ("M03", f"A nineteen fifties American family at their kitchen table opening the Bank of America envelope and examining the credit card with expressions of confusion and curiosity, an entire household looking at a financial product they did not ask for. {STYLE}"),

    ("M04", f"A mid level bank executive in a nineteen fifties suit, at a desk in a Bank of America office surrounded by maps of California and stacks of credit card envelopes, the architect of the Fresno Drop, before the scandal. {STYLE}"),

    ("M05", f"A nineteen fifties post office loading dock, postal workers loading hundreds of boxes into mail delivery trucks, each box filled with BankAmericard envelopes destined for sixty five thousand Fresno residents, the logistics of mass debt deployment. {STYLE}"),

    ("M06", f"A newspaper headline from nineteen fifty eight reading BANK CARD FRAUD RAMPANT IN FRESNO PILOT PROGRAM alongside a photo of a mail carrier, the scandal that followed the drop, the product that survived its own failure. {STYLE}"),

    ("M07", f"A nineteen sixty five American living room, a woman paying bills at a desk, a pile of credit card statements on one side and a checkbook on the other, debt has arrived as a lifestyle product, normalized, domestic, seemingly manageable. {STYLE}"),

    ("M08", f"A Congressional hearing room, nineteen seventy, lawmakers holding up credit cards and gesturing at testimony, the moment Congress passed a law making unsolicited card mailings illegal, after one hundred million cards had already been distributed. {STYLE}"),

    ("M17", f"A symbolic visualization of one hundred million credit card envelopes stacked in a vast warehouse to the ceiling, postal workers dwarfed by the scale, the sheer volume of unsolicited debt distributed to Americans before Congress intervened. {STYLE}"),

    ("M18", f"A nineteen sixty five American suburban kitchen counter where a credit card sits unopened in its Bank of America envelope next to a pile of household bills, the debt product nobody requested now part of every American home, the quiet colonization of ordinary life. {STYLE}"),

    ("M19", f"A Bank of America boardroom in the late nineteen fifties, executives standing at a large map of the United States with red pins marking expansion targets for credit card distribution beyond California, the planning session for the national debt deployment. {STYLE}"),

    ("M20", f"A nineteen sixty eight American street scene: a department store, a gas station, a restaurant, each with a BankAmericard accepted here sign in the window, the infrastructure of revolving credit made ubiquitous, consumer debt woven into the fabric of ordinary commerce. {STYLE}"),

    # ── M: Modern Part 2 (s5_modern_pt2) ──

    ("M09", f"A computer terminal in a nineteen eighty nine office showing the first FICO credit score calculation interface, a number from three hundred to eight fifty appearing on a green on black screen, the moment individual creditworthiness became a quantified product. {STYLE}"),

    ("M10", f"A Black family standing outside a suburban home in the nineteen fifties that they were denied the right to purchase, a Federal Housing Administration APPROVED stamp visible on the adjacent white family's mortgage documents, the visual of redlining and its consequences for wealth building. {STYLE}"),

    ("M11", f"A nineteen fifties neighborhood map with certain neighborhoods outlined in red marker, the literal redlining maps used by the Federal Housing Administration from nineteen thirty four to nineteen sixty eight to deny mortgages in Black neighborhoods. Archives quality. {STYLE}"),

    ("M12", f"Split screen: left side shows a white credit score dashboard reading seven hundred thirty with a green bar; right side shows a Black credit score dashboard reading six hundred thirty nine with a yellow red bar, the ninety one point gap, visualized without caricature. {STYLE}"),

    ("M13", f"A city block map showing the locations of every payday lender in a predominantly Black neighborhood, dozens of markers clustered together, overlaid with the same map for a predominantly white neighborhood with only a few markers visible. The eight times concentration ratio, visualized. {STYLE}"),

    ("M14", f"Interior of a payday loan store, fluorescent lights, a customer at the counter completing paperwork, a sign on the wall reading FOUR HUNDRED PERCENT APR REQUIRED DISCLOSURE in small print, the legal requirement buried in plain sight. {STYLE}"),

    ("M15", f"A close up of a student loan statement showing a graduate's loan balance twenty years after graduation: the original balance one hundred thousand dollars, the current balance ninety five thousand dollars after twenty years of payments, barely moved. {STYLE}"),

    ("M16", f"A split image: on the left, a Babylonian temple scribe recording a farmer's debt in a clay ledger at interest rates capped at thirty three percent; on the right, a payday loan clerk entering a loan at four hundred percent APR into a computer terminal. Same transaction. Five thousand years apart. Same result. {STYLE}"),

    ("M21", f"A FICO credit score breakdown displayed as a clear chart: Payment History thirty five percent, Amounts Owed thirty percent, Length of Credit History fifteen percent, Credit Mix ten percent, New Credit ten percent, the five components of a number that determines financial access in America. {STYLE}"),

    ("M22", f"A nineteen eighty nine loan office interior: a credit report showing a low score lies on the desk, and behind the loan officer on the wall hangs a nineteen fifties era redlining map with Black neighborhoods outlined in red, the direct pipeline from federal exclusion to credit score visible in one frame. {STYLE}"),

    ("M23", f"A magnifying glass held over a credit score gap showing six hundred thirty nine versus seven hundred thirty, and through the glass the words THIRTY FOUR YEARS OF REDLINED MORTGAGES are visible, structural exclusion converted into a number. {STYLE}"),

    ("M24", f"A neighborhood map of a major American city showing the footprint of nineteen fifties FHA redlined areas outlined in red, with modern payday loan locations marked as yellow dots concentrated almost entirely within the same red outline, the same geography targeted across two different eras. {STYLE}"),

    ("M25", f"Side by side comparison: a nineteen ten Southern company store with prices written on a chalkboard the customers cannot verify, and a twenty twenty payday loan store with APR disclosed in small print on a sign the customers cannot calculate. Same architecture of extraction. Different century. {STYLE}"),

    # ── C: Close (s6_close) ──

    ("C01", f"A Sumerian farmer returning to his home, a modest clay dwelling at the edge of a field, his wife and children visible in the doorway, the word amargi written in cuneiform above the entrance, the image of debt cancellation as homecoming. {STYLE}"),

    ("C02", f"A Babylonian mathematician at a clay tablet, stylus in hand, having just completed the exponential compound interest calculation that proves debt always grows faster than an economy, looking at the result with the expression of someone who understands the full weight of what they have just proven. {STYLE}"),

    ("C03", f"Ancient jubilee scene: a Babylonian king on a raised platform announcing the debt cancellation, rams horns sounding across the city, the crowd below erupting in visible relief, thirty times in a thousand years, this happened. {STYLE}"),

    ("C04", f"Two parallel rivers of water flowing: one flowing slowly and steadily, labeled ECONOMY; one flowing rapidly and accelerating, labeled COMPOUND INTEREST, the gap between them widening as they flow. Ancient Mesopotamian artistic style. {STYLE}"),

    ("C05", f"A split timeline image: on the left side, ancient Babylon with a debt cancellation decree being read in a public square; on the right side, modern America with a minimum payment table from a credit card statement, the ancient solution and the modern substitute, side by side. {STYLE}"),

    ("C06", f"A Black family today, in contemporary clothes, sitting around a kitchen table with student loan statements, credit card bills, and a payday loan receipt, the modern version of the same debt trap, inside the same mathematical structure, five thousand years after Babylon named it. {STYLE}"),

    ("C07", f"The original clay cone of Urukagina, the artifact from approximately twenty three hundred BCE that contains the first recorded use of the word amargi, held in museum quality display lighting, the oldest word for freedom preserved in clay. {STYLE}"),

    ("C08", f"A single ray of morning light falling on a clay tablet on which the word amargi is carved in ancient cuneiform script, the word for freedom, the word for debt cancellation, the oldest definition of what it means to be released from obligation, still readable five thousand years later. {STYLE}"),

    ("C09", f"A visual relay race timeline spanning five thousand years: a Babylonian scribe passing a clay debt tablet to a medieval monk, who passes it to a Calvinist merchant, who passes it to an English creditor, who passes it to a Southern landowner, who passes it to a credit card company, who passes it to a payday lender, the same mechanism handed forward across history. {STYLE}"),

    ("C10", f"A modern Black American in contemporary clothes sitting at a kitchen table with financial documents, and through the window behind him a ghostly overlay shows an ancient Mesopotamian temple scribe recording identical debt obligations in clay, the machine unchanged across five thousand years. {STYLE}"),

    ("C11", f"Dawn light breaking over an ancient Mesopotamian river valley, golden illumination spreading across flat land, the first light of morning making everything visible that was hidden in darkness, a metaphor for seeing clearly what was designed to stay opaque. {STYLE}"),

    ("C12", f"Two contrasting images in a single frame: on the left, Sumerian farmers walking away from the temple in golden evening light after debt cancellation, heading home; on the right, a modern kitchen table with a credit card statement showing a minimum payment that has not touched the principal in twenty years, the jubilee and its absence, side by side. {STYLE}"),

]

# ══════════════════════════════════════════════════════════
# GENERATION — No need to edit below this line
# ══════════════════════════════════════════════════════════

IMG_DIR = ROOT / f"projects/{PROJECT_NAME}/images"
IMG_DIR.mkdir(parents=True, exist_ok=True)


def generate_image(name, prompt, api_key):
    """Generate a single image using Gemini, with or without reference character."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    try:
        if USE_REF_IMAGE and REF_IMAGE_BYTES:
            contents = [
                types.Part.from_bytes(data=REF_IMAGE_BYTES, mime_type=REF_MIME),
                f"Using the attached image as a character reference, generate this scene in the EXACT same art style (Boondocks-style animation, bold linework, flat cel-shading). The character in every image must look like the man in the reference. Scene: {prompt}",
            ]
        else:
            contents = [f"Generate this scene: {prompt}"]

        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
                temperature=0.7,
                image_config=types.ImageConfig(
                    image_size="4K",
                    aspect_ratio="16:9",
                ),
            ),
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                img_data = part.inline_data.data
                mime = part.inline_data.mime_type
                ext = "png" if "png" in mime else "jpg"
                out_path = IMG_DIR / f"{name}.{ext}"
                if isinstance(img_data, str):
                    img_bytes = base64.b64decode(img_data)
                else:
                    img_bytes = img_data
                with open(out_path, "wb") as f:
                    f.write(img_bytes)
                cost = log_gemini_image_cost(IMG_DIR.parent, 1, name)
                print(f"  OK {name} → {out_path} ({len(img_bytes) // 1024} KB, cost: ${cost:.4f})")
                return name, str(out_path), ext
        return name, None, "No image in response"
    except Exception as e:
        print(f"  FAIL {name}: {e}")
        return name, None, str(e)


def main():
    remaining = []
    for name, prompt in IMAGES:
        if (IMG_DIR / f"{name}.png").exists() or (IMG_DIR / f"{name}.jpg").exists():
            print(f"  SKIP {name} (exists)")
        else:
            remaining.append((name, prompt))

    if not remaining:
        print("All images already generated!")
        return

    print(f"\nGenerating {len(remaining)} images using {MODEL}...\n")

    results = {}
    batch_size = len(API_KEYS)
    for batch_start in range(0, len(remaining), batch_size):
        batch = remaining[batch_start:batch_start + batch_size]
        if batch_start > 0:
            print(f"\n  -- Waiting 15s between batches to avoid rate limits --\n")
            time.sleep(15)

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(batch)) as executor:
            futures = {}
            for i, (name, prompt) in enumerate(batch):
                key = API_KEYS[i % len(API_KEYS)]
                futures[executor.submit(generate_image, name, prompt, key)] = name

            for future in concurrent.futures.as_completed(futures):
                name, path, info = future.result()
                results[name] = (path, info)

    print(f"\n=== Summary ===")
    ok = sum(1 for p, _ in results.values() if p)
    print(f"  Generated: {ok}/{len(remaining)}")
    for name, (path, info) in sorted(results.items()):
        status = f"OK → {path}" if path else f"FAIL: {info}"
        print(f"  {name}: {status}")


if __name__ == "__main__":
    print(f"=== Generating images for project: {PROJECT_NAME} ===")
    main()
