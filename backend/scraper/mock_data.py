"""
mock_data.py
Generates realistic fake Meta Ad Library records for 15 competitors across
three owned brands: Bebodywise, Man Matters, and Little Joys.

Schema emitted matches the `competitor_ads` Supabase table expected by the
seed endpoint and the frontend dashboard.
"""

from __future__ import annotations

import random
import uuid
from datetime import date, timedelta

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TODAY = date.today()

# Owned brands → verticals they compete in
BRAND_META: dict[str, dict] = {
    "bebodywise": {
        "label": "Bebodywise",
        "vertical": "women_wellness",
        "themes": ["weight", "immunity", "energy", "confidence"],
    },
    "man_matters": {
        "label": "Man Matters",
        "vertical": "mens_wellness",
        "themes": ["hair_loss", "performance", "energy", "confidence"],
    },
    "little_joys": {
        "label": "Little Joys",
        "vertical": "kids_wellness",
        "themes": ["immunity", "parenting", "safety", "energy"],
    },
}

# 5 competitors per owned brand  (15 total)
COMPETITORS: dict[str, list[dict]] = {
    "bebodywise": [
        {"name": "OZiva", "page_id": "101234567890001", "country": "IN"},
        {"name": "WOW Life Science", "page_id": "101234567890002", "country": "IN"},
        {"name": "Carbamide Forte", "page_id": "101234567890003", "country": "IN"},
        {"name": "HK Vitals", "page_id": "101234567890004", "country": "IN"},
        {"name": "Saffola Fittify", "page_id": "101234567890005", "country": "IN"},
    ],
    "man_matters": [
        {"name": "Beardo", "page_id": "101234567890006", "country": "IN"},
        {"name": "Ustraa", "page_id": "101234567890007", "country": "IN"},
        {"name": "The Man Company", "page_id": "101234567890008", "country": "IN"},
        {"name": "Bombay Shaving Company", "page_id": "101234567890009", "country": "IN"},
        {"name": "Boldfit", "page_id": "101234567890010", "country": "IN"},
    ],
    "little_joys": [
        {"name": "Himalaya Baby", "page_id": "101234567890011", "country": "IN"},
        {"name": "Mamaearth Kids", "page_id": "101234567890012", "country": "IN"},
        {"name": "Sebamed Baby", "page_id": "101234567890013", "country": "IN"},
        {"name": "Mother Sparsh", "page_id": "101234567890014", "country": "IN"},
        {"name": "Chicco India", "page_id": "101234567890015", "country": "IN"},
    ],
}

AD_FORMATS = ["static", "video", "carousel"]
FORMAT_WEIGHTS = [0.40, 0.35, 0.25]   # static most common, carousel least

EMOTIONAL_TONES = ["aspiration", "fear", "trust", "urgency", "social_proof", "humor"]
TONE_WEIGHTS    = [0.30, 0.20, 0.20, 0.15, 0.10, 0.05]

PLATFORMS = ["facebook", "instagram", "facebook,instagram"]
PLATFORM_WEIGHTS = [0.25, 0.35, 0.40]

# Spend ranges (INR/day estimates) keyed by rough tier
SPEND_TIERS = {
    "low":    (500,   3_000),
    "mid":    (3_000, 15_000),
    "high":   (15_000, 60_000),
    "viral":  (60_000, 2_00_000),
}

CTA_OPTIONS = [
    "Shop Now", "Learn More", "Get Offer", "Sign Up",
    "Order Now", "Book Now", "Download", "Watch More",
]

# ---------------------------------------------------------------------------
# Ad copy templates keyed by theme + emotional tone
# Each tuple: (headline, body)
# ---------------------------------------------------------------------------

COPY_BANK: dict[str, dict[str, list[tuple[str, str]]]] = {
    "hair_loss": {
        "fear": [
            ("Losing More Hair Every Day?", "Don't ignore the signs. DHT-blocking formula clinically proven to stop hair fall in 4 weeks. Start your hair recovery today."),
            ("Your Hair Is Thinning — Act Now", "Every shower drain tells a story. Reclaim fuller, thicker hair before it's too late. Dermatologist-recommended solution inside."),
        ],
        "aspiration": [
            ("The Mane You Always Wanted", "Science-backed hair growth serum trusted by 5 lakh+ Indian men. See visible density in just 8 weeks."),
            ("Thick Hair. Confident You.", "Biotin + Redensyl + Anagain — the triple-action formula that brings your hair back to life."),
        ],
        "trust": [
            ("Clinically Tested. Dermatologist Approved.", "Our DHT blocker has 3 published studies backing its efficacy. No harsh chemicals. No side effects."),
            ("4.7★ from 18,000 Real Users", "Men across India trust this formula for hair regrowth. Read their unfiltered reviews before you decide."),
        ],
        "urgency": [
            ("Only 200 Hair Kits Left — 40% Off", "Monsoon hair fall season is here. Grab the complete 3-month kit before stock runs out."),
            ("Flash Sale: Hair Growth Kit ₹999", "Price goes back to ₹1,899 at midnight. 72 hrs only."),
        ],
        "social_proof": [
            ("10 Lakh Men Can't Be Wrong", "Join India's largest men's hair wellness community. Real results, real people — see the before & afters."),
            ("Ranveer's Hair Secret? This Kit.", "Thousands of men share their transformation. Now it's your turn."),
        ],
        "humor": [
            ("Hair Today, Here Tomorrow (If You Act Fast)", "Receding hairline? We've got a plan. Spoiler: it's not a hat."),
            ("Your Comb Called. It Misses You.", "Stop finding excuses. Start finding your hair. Our growth serum works."),
        ],
    },
    "energy": {
        "fear": [
            ("Still Tired at 3PM?", "Afternoon energy crashes are ruining your productivity. B12 + Iron + Ashwagandha complex designed for all-day stamina."),
            ("Caffeine Is a Bandage, Not a Fix", "Hiding fatigue behind coffee? Discover the root cause and fix it with targeted micronutrients."),
        ],
        "aspiration": [
            ("Feel Unstoppable from 6AM to 10PM", "Elite energy stack: CoQ10 + Shilajit + Vitamin D3. No jitters. No crash. Just clean power."),
            ("Your Best Day Starts Here", "Wake up refreshed, stay sharp all day. Clinically dosed formula for sustained vitality."),
        ],
        "trust": [
            ("FSSAI Certified. Lab Tested. Safe.", "Every batch of our energy supplement is third-party tested for purity and potency."),
            ("Formulated by IIT-Alumni Nutritionists", "Science, not hype. Our energy blend is peer-reviewed and physician-recommended."),
        ],
        "urgency": [
            ("Monsoon Offer: Buy 2 Get 1 Free", "Stock running low. Grab your 3-month energy supply at 33% off before it sells out."),
            ("48-Hour Flash: Energy Kit at ₹799", "Regular price ₹1,299. Sale ends Sunday midnight. Tap to claim."),
        ],
        "social_proof": [
            ("8 Lakh Customers. 4.6 Stars.", "India's fastest-growing energy supplement. Trusted by working professionals, athletes, and new moms."),
            ("Priya Lost Her 3PM Slump in 2 Weeks", "Read how 50,000 women ditched their caffeine dependency with this daily capsule."),
        ],
        "humor": [
            ("Coffee Has Left the Chat", "Introducing the upgrade your energy levels have been waiting for. No side-eyes from your barista."),
            ("Warning: May Cause Excessive Productivity", "Side effects include finishing your to-do list, surprising your boss, and annoying your lazier colleagues."),
        ],
    },
    "immunity": {
        "fear": [
            ("Sick Again This Season?", "Frequent colds signal a weakened immune system. Zinc + Vitamin C + Elderberry — the immunity trio that works."),
            ("Your Family's Shield Is Low", "Post-pandemic immunity gaps are real. Don't wait for the next viral wave to act."),
        ],
        "aspiration": [
            ("Build a Body That Fights Back", "365-day immunity formula with 12 clinically proven botanicals. Feel invincible, naturally."),
            ("Strong Immunity. Stronger Family.", "When you're healthy, everyone thrives. Start the family immunity ritual today."),
        ],
        "trust": [
            ("AYUSH-Approved Immunity Booster", "Rooted in Ayurveda, proven by science. 6 clinical trials. Trusted by 20 lakh families."),
            ("Pediatrician Recommended for Kids 2+", "Safe, gentle, effective. Formulated with child nutritionists for growing immune systems."),
        ],
        "urgency": [
            ("Season Change Alert — Protect Now", "Weather shifts weaken immunity. Limited-time 30-day immunity kit at 45% off."),
            ("Back-to-School Immunity Pack — Only ₹499", "Expiry: this Sunday. Get your kids school-ready and germ-proof."),
        ],
        "social_proof": [
            ("15 Lakh Families Trust This Formula", "India's #1 kids immunity brand for 3 years running. See what parents are saying."),
            ("Viral: Mom's 12-Month Immunity Challenge", "She gave her kids this daily — zero sick days in a year. Watch her story."),
        ],
        "humor": [
            ("Germs, Consider Yourself Warned", "Our immunity stack didn't come to play. Neither did your kid's white blood cells — with this formula."),
            ("The Only Time 'Going Viral' Is Bad", "Upgrade your family's firewall. No subscription required."),
        ],
    },
    "weight": {
        "fear": [
            ("Stubborn Belly Fat Won't Budge?", "Hours at the gym, strict diet — and still no results? Metabolic blockers might be the hidden culprit."),
            ("Yo-Yo Dieting Is Damaging Your Metabolism", "Every crash diet makes the next one harder. Break the cycle with a science-backed approach."),
        ],
        "aspiration": [
            ("Your Dream Body Is 12 Weeks Away", "Clinically studied fat metabolism formula + personalized nutrition coaching. Real results, not shortcuts."),
            ("Confident. Fit. Radiant.", "Lose the weight you've been carrying — literally and figuratively. 30,000 women already have."),
        ],
        "trust": [
            ("ICMR-Aligned Nutrition Formula", "Developed by registered dietitians. No banned substances. Transparent ingredient labeling."),
            ("Backed by 3 RCTs. Not Just Testimonials.", "Our weight management protocol has clinical evidence behind every claim. Read the studies."),
        ],
        "urgency": [
            ("New Year Kit: 40% Off Ends Tonight", "Your health resolution deserves real support. Grab the 90-day transformation kit before midnight."),
            ("Summer Body Sale — 3 Days Left", "₹2,499 kit now ₹1,499. Includes meal plan + app access. Hurry."),
        ],
        "social_proof": [
            ("Sunita Lost 11kg in 4 Months", "No starvation. No gym dependency. Real food, smart supplements, lasting change."),
            ("30,000 Women Transformed. You're Next.", "See the before-and-afters, read the reviews — then decide."),
        ],
        "humor": [
            ("Your Jeans Called. They Want a Reunion.", "We can help. Science-backed, dietitian-approved, salad-not-required approach to fat loss."),
            ("Plot Twist: Your Metabolism Isn't Broken", "It just needs the right support. Here's what 30,000 women discovered."),
        ],
    },
    "performance": {
        "fear": [
            ("Low Testosterone Is More Common Than You Think", "Fatigue, low drive, poor recovery — classic signs most men ignore. Get checked. Get supported."),
            ("Are You Training Hard But Recovering Slow?", "Overtraining without the right micronutrients leads to hormonal imbalance. Fix the root cause."),
        ],
        "aspiration": [
            ("Peak Performance. Every. Single. Day.", "Ashwagandha KSM-66 + Shilajit + D3 + Zinc. The elite men's performance stack."),
            ("Be the Man You Were Built to Be", "Naturally optimized testosterone. Sharper focus. Better recovery. Relentless energy."),
        ],
        "trust": [
            ("KSM-66 Ashwagandha — 24 Clinical Studies", "The most-studied adaptogen in men's health. Proven to raise testosterone, lower cortisol."),
            ("Endorsed by 500+ Sports Nutritionists in India", "Formulated to WADA guidelines. Safe for competitive athletes."),
        ],
        "urgency": [
            ("Pre-Monsoon Performance Sale — 50% Off", "Limited stock of our bestselling T-booster kit. Don't let sluggish energy win."),
            ("72-Hour Flash: Shilajit + Ashwagandha Combo ₹1,199", "Normally ₹2,199. Grab it while the sale lasts."),
        ],
        "social_proof": [
            ("Vikram Gained 4kg Lean Muscle in 8 Weeks", "No steroids. No shortcuts. Just the right natural support stack. See his journey."),
            ("India's #1 Men's Performance Supplement 2024", "Voted by 2 lakh men. 4.8 stars. The numbers speak for themselves."),
        ],
        "humor": [
            ("Your Gym Bag Is Ready. Is Your Testosterone?", "Don't let micronutrient gaps sabotage your gains. Upgrade the tank, not just the engine."),
            ("Dad Strength Is Real. Science Just Made It Realer.", "Natural T-support for men who have real-life demands — and refuse to slow down."),
        ],
    },
    "confidence": {
        "fear": [
            ("Self-Doubt Is a Silent Saboteur", "Anxiety and low confidence often stem from nutritional deficiencies. Magnesium + B-Complex changes the equation."),
            ("Are You Showing Up as Your Best Self?", "Chronic stress depletes the micronutrients that fuel mental clarity and self-assurance."),
        ],
        "aspiration": [
            ("Walk Into Every Room Like You Own It", "Adaptogen-powered mood support. Stress down. Confidence up. You, at 100%."),
            ("Radiate From the Inside Out", "When your body feels balanced, your confidence follows. Start the daily ritual."),
        ],
        "trust": [
            ("Clinically Proven to Reduce Cortisol by 27%", "Ashwagandha KSM-66 in our formula is backed by peer-reviewed research on stress and wellbeing."),
            ("Formulated with Integrative Psychiatrists", "Mental wellness meets nutritional science. Evidence-based. Safe. Effective."),
        ],
        "urgency": [
            ("Confidence Kit: Flash Sale Ends in 12 Hours", "Our bestselling mood + energy bundle — 35% off for the next 12 hours only."),
            ("Only 300 Kits Left at This Price", "Grab it before it's gone. Your best self is waiting."),
        ],
        "social_proof": [
            ("'I Finally Feel Like Myself Again' — Neha, 32", "20,000 women share their confidence transformation. See what changed for them."),
            ("Top-Rated Wellness Supplement on Trustpilot India", "4.9/5 stars. 12,000 verified reviews. Real people. Real change."),
        ],
        "humor": [
            ("Imposter Syndrome: Meet Your Match", "Science-backed confidence support. For when 'fake it till you make it' has officially run its course."),
            ("Confidence — Now Available in Capsule Form (Kind Of)", "Okay, it's not magic. But 28 days in, you'll swear it is."),
        ],
    },
    "parenting": {
        "fear": [
            ("Is Your Child Getting Enough Nutrition?", "85% of Indian kids are deficient in at least one key micronutrient. Don't let gaps affect their development."),
            ("Screen Time Is Up. Attention Span Is Down.", "Support your child's focus and cognitive development with the nutrients their growing brain needs."),
        ],
        "aspiration": [
            ("Raise Curious, Thriving Kids", "DHA + Choline + Iron — the brain development trio pediatricians recommend from Year 1."),
            ("Every Parent's Dream: A Healthy, Happy Child", "Our kids' wellness range is designed to make nutrition simple, safe, and something kids actually enjoy."),
        ],
        "trust": [
            ("Recommended by 10,000 Pediatricians in India", "Safe from 2 years. No artificial colors. No added sugar. FSSAI certified."),
            ("Moms Love It. Pediatricians Approve It.", "3rd-party lab tested, allergen-labeled, and formulated specifically for Indian children's dietary needs."),
        ],
        "urgency": [
            ("Back-to-School Nutrition Kit — Limited Stock", "School season is here. Grab the complete 30-day kids' nutrition kit before it sells out."),
            ("Monsoon Immunity Sale: 40% Off Kids Range", "Protect your child through season change. Offer valid while stocks last."),
        ],
        "social_proof": [
            ("2 Million Happy Moms and Counting", "India's most trusted kids' wellness brand — rated 4.8 stars by verified parents nationwide."),
            ("Priya's Son Went from Picky Eater to Nutrition Champion", "How one mom transformed mealtimes and filled the nutrient gaps. Watch her story."),
        ],
        "humor": [
            ("Finally: A Supplement Your Kids Won't Spit Out", "Mango flavored. Sneakily nutritious. Parents approved; kids obsessed."),
            ("Vegetables? Overrated. Micronutrients? Essential.", "When broccoli is a war zone, we've got backup. 12 essential nutrients. Zero arguments."),
        ],
    },
    "safety": {
        "fear": [
            ("Not All Baby Products Are as Safe as They Claim", "Hidden parabens and sulfates in 'gentle' products. Always check what's in your baby's skincare."),
            ("Your Baby's Skin Is 5x More Permeable Than Yours", "Toxins absorb faster. Demand higher safety standards. Choose clinically tested baby care."),
        ],
        "aspiration": [
            ("Pure. Gentle. Safe from Day One.", "Dermatologist-tested, hypoallergenic baby care range. Because your baby deserves nothing less."),
            ("The Gold Standard in Baby Safety", "EWG Verified. EU Compliant. Free from 1300+ harmful chemicals. Peace of mind, bottled."),
        ],
        "trust": [
            ("Dermatologist Tested on Sensitive Newborn Skin", "Our formulas undergo clinical patch testing on the most delicate skin type — your newborn's."),
            ("Certified Safe by European Pediatric Dermatology Society", "When it comes to your baby, over-qualified beats under-tested every time."),
        ],
        "urgency": [
            ("Baby Safety Kit — New Season, New Formula", "Upgraded formulation with added ceramides. Introductory price valid for the first 500 orders."),
            ("Limited Edition: Monsoon Baby Care Bundle ₹799", "Everything your baby needs through the damp season. Grab before it's gone."),
        ],
        "social_proof": [
            ("50 Lakh Moms Trust This Brand", "India's most recommended baby care range for sensitive skin. 4 national parenting awards."),
            ("Hospital-Preferred Brand in 200+ NICU Units", "When hospitals choose us for newborns, that's the safety signal parents trust."),
        ],
        "humor": [
            ("Your Baby Can't Read Ingredient Labels. We Did It for Them.", "Zero parabens. Zero sulfates. Zero nonsense. 100% for the tiny human who runs your life."),
            ("NICU-Safe Means Parent-Approved Overkill (You're Welcome)", "We went above and beyond so you don't have to wonder. Just enjoy the baby smell."),
        ],
    },
}


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _random_date_in_window(min_days_ago: int, max_days_ago: int) -> date:
    offset = random.randint(min_days_ago, max_days_ago)
    return TODAY - timedelta(days=offset)


def _spend_for_format(fmt: str) -> tuple[int, int]:
    """Video and carousel ads typically attract higher spend."""
    if fmt == "video":
        tier = random.choices(
            ["mid", "high", "viral"], weights=[0.40, 0.40, 0.20]
        )[0]
    elif fmt == "carousel":
        tier = random.choices(
            ["mid", "high", "viral"], weights=[0.50, 0.35, 0.15]
        )[0]
    else:
        tier = random.choices(
            ["low", "mid", "high"], weights=[0.40, 0.45, 0.15]
        )[0]
    lo, hi = SPEND_TIERS[tier]
    daily_spend = random.randint(lo, hi)
    # return a range (Meta reports min/max across the lifetime)
    variance = int(daily_spend * random.uniform(0.1, 0.3))
    return daily_spend, daily_spend + variance


def _end_date(start: date, force_active: bool = False) -> tuple[date | None, bool]:
    """
    ~65% of ads are still active (end_date = None).
    Older ads have higher probability of having ended.
    """
    age_days = (TODAY - start).days
    # Probability of being stopped increases with age
    stop_prob = min(0.70, age_days / 120)
    if force_active or random.random() > stop_prob:
        return None, True
    stopped_days_ago = random.randint(1, min(age_days - 1, 30))
    return TODAY - timedelta(days=stopped_days_ago), False


def _pick_copy(theme: str, tone: str) -> tuple[str, str]:
    pool = COPY_BANK.get(theme, {}).get(tone)
    if not pool:
        # fallback to any tone in that theme
        all_copies = []
        for copies in COPY_BANK.get(theme, {}).values():
            all_copies.extend(copies)
        if not all_copies:
            return ("Check Our Latest Offer", "Discover our newest product range. Limited time availability.")
        return random.choice(all_copies)
    return random.choice(pool)


# ---------------------------------------------------------------------------
# Core generator
# ---------------------------------------------------------------------------

def generate_mock_ads() -> list[dict]:
    """
    Returns a list of dicts, each representing one row in `competitor_ads`.
    Generates roughly 8–14 ads per competitor = 120–210 total records.
    Spread across last 90 days; some start 60+ days ago to test longevity.
    """
    records: list[dict] = []

    for brand_key, brand_info in BRAND_META.items():
        for competitor in COMPETITORS[brand_key]:
            # Decide how many ads this competitor is running (8–14)
            num_ads = random.randint(8, 14)

            for _ in range(num_ads):
                ad_id = f"mock_{uuid.uuid4().hex[:16]}"
                fmt = random.choices(AD_FORMATS, weights=FORMAT_WEIGHTS)[0]
                tone = random.choices(EMOTIONAL_TONES, weights=TONE_WEIGHTS)[0]

                # Pick a theme that fits this brand's competitive space
                theme = random.choice(brand_info["themes"])

                headline, body_text = _pick_copy(theme, tone)

                # Date spread: ~30% of ads are 60+ days old (longevity signal)
                if random.random() < 0.30:
                    start = _random_date_in_window(60, 90)
                else:
                    start = _random_date_in_window(1, 59)

                end, is_active = _end_date(start)

                spend_min, spend_max = _spend_for_format(fmt)
                days_running = (
                    (TODAY - start).days if is_active
                    else ((end - start).days if end else 0)
                )

                platform = random.choices(PLATFORMS, weights=PLATFORM_WEIGHTS)[0]
                cta = random.choice(CTA_OPTIONS)

                # Carousel gets multiple card count
                num_cards = random.randint(3, 6) if fmt == "carousel" else None

                records.append({
                    "id": str(uuid.uuid4()),
                    "ad_id": ad_id,
                    "competitor_name": competitor["name"],
                    "competitor_page_id": competitor["page_id"],
                    "brand": brand_key,
                    "vertical": brand_info["vertical"],
                    "ad_format": fmt,
                    "message_theme": theme,
                    "emotional_tone": tone,
                    "headline": headline,
                    "body_text": body_text,
                    "cta": cta,
                    "platform": platform,
                    "estimated_spend_min": spend_min,
                    "estimated_spend_max": spend_max,
                    "start_date": start.isoformat(),
                    "end_date": end.isoformat() if end else None,
                    "is_active": is_active,
                    "days_running": days_running,
                    "num_cards": num_cards,
                    "country": competitor["country"],
                    "source": "mock",
                })

    # Deterministic shuffle so repeated calls differ in order but cover all brands
    random.shuffle(records)
    return records


# ---------------------------------------------------------------------------
# Metadata helpers used by the API layer
# ---------------------------------------------------------------------------

def get_brand_keys() -> list[str]:
    return list(BRAND_META.keys())


def get_competitor_names() -> list[str]:
    names = []
    for comps in COMPETITORS.values():
        names.extend(c["name"] for c in comps)
    return names
