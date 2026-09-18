import os
import re
import json
import logging
from io import BytesIO
from datetime import datetime
from urllib.parse import quote_plus, urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
WEB_RESEARCH_ENABLED = os.getenv(
    "WEB_RESEARCH_ENABLED",
    "true" if os.getenv("VERCEL") else "false"
).strip().lower() == "true"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logger.info(
    "research_config web_research_enabled=%s vercel=%s",
    WEB_RESEARCH_ENABLED,
    bool(os.getenv("VERCEL"))
)

OFFICIAL_COMPETITOR_SOURCES = {
    "Amazon India": "https://www.amazon.in",
    "Amazon": "https://www.amazon.in",
    "Flipkart": "https://www.flipkart.com",
    "Meesho": "https://www.meesho.com",
    "Myntra": "https://www.myntra.com",
    "AJIO": "https://www.ajio.com",
    "Unacademy": "https://unacademy.com",
    "upGrad": "https://www.upgrad.com",
    "Vedantu": "https://www.vedantu.com",
    "Physics Wallah": "https://www.pw.live",
    "Coursera": "https://www.coursera.org",
    "Swiggy": "https://www.swiggy.com",
    "Zomato": "https://www.zomato.com",
    "Blinkit": "https://blinkit.com",
    "Zepto": "https://www.zepto.com",
    "PhonePe": "https://www.phonepe.com",
    "Paytm": "https://paytm.com",
    "Razorpay": "https://razorpay.com",
    "Google Pay": "https://pay.google.com",
    "Microsoft": "https://www.microsoft.com",
    "Google": "https://www.google.com",
    "Salesforce": "https://www.salesforce.com",
    "Oracle": "https://www.oracle.com",
    "Adobe": "https://www.adobe.com",
}

gemini_client = None

if GEMINI_API_KEY:
    try:
        from google import genai
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception:
        gemini_client = None


# ============================================================
# WEB SETTINGS
# ============================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "Chrome/130.0 Safari/537.36"
    )
}


# ============================================================
# BUSINESS FIELDS
# ============================================================

FIELD_KEYWORDS = {
    "Education / EdTech": [
        "education", "college", "school", "student",
        "learning", "course", "tutor", "edtech",
        "training", "exam preparation"
    ],

    "E-commerce / Online Retail": [
        "ecommerce", "e-commerce", "shopping",
        "online store", "retail", "marketplace",
        "fashion store", "products"
    ],

    "Food Delivery / Quick Commerce": [
        "food delivery", "restaurant", "food",
        "grocery", "quick commerce", "delivery",
        "cloud kitchen"
    ],

    "Healthcare / HealthTech": [
        "healthcare", "hospital", "clinic",
        "medical", "doctor", "medicine",
        "healthtech", "patient"
    ],

    "FinTech / Financial Services": [
        "fintech", "finance", "banking",
        "payment", "wallet", "loan",
        "investment", "insurance"
    ],

    "Electric Vehicles / Energy": [
        "electric vehicle", "ev", "battery",
        "charging", "solar", "energy",
        "automobile", "electric car"
    ],

    "Travel / Hospitality": [
        "travel", "hotel", "tourism",
        "flight", "booking", "hospitality"
    ],

    "Software / SaaS": [
        "software", "saas", "platform",
        "application", "app", "technology",
        "cloud software"
    ],

    "AI / Machine Learning": [
        "artificial intelligence", "ai",
        "machine learning", "ml",
        "generative ai", "computer vision",
        "nlp", "deep learning"
    ],

    "Agriculture / AgriTech": [
        "agriculture", "farming", "farmer",
        "agritech", "crop", "irrigation",
        "fertilizer", "agri"
    ],

    "Retail / Local Business": [
        "shop", "store", "local business",
        "retail", "supermarket"
    ]
}


# ============================================================
# KNOWN COMPETITOR KNOWLEDGE
# ============================================================

COMPETITOR_DATABASE = {

    "Education / EdTech": [
        "Unacademy",
        "upGrad",
        "Vedantu",
        "Physics Wallah",
        "Coursera"
    ],

    "E-commerce / Online Retail": [
        "Amazon India",
        "Flipkart",
        "Meesho",
        "Myntra",
        "AJIO"
    ],

    "Food Delivery / Quick Commerce": [
        "Swiggy",
        "Zomato",
        "Blinkit",
        "Zepto",
        "Instamart"
    ],

    "Healthcare / HealthTech": [
        "Apollo",
        "Practo",
        "Tata 1mg",
        "PharmEasy",
        "Fortis"
    ],

    "FinTech / Financial Services": [
        "PhonePe",
        "Paytm",
        "Razorpay",
        "Google Pay",
        "CRED"
    ],

    "Electric Vehicles / Energy": [
        "Tata Motors EV",
        "Mahindra Electric",
        "MG Motor",
        "BYD",
        "Ather Energy"
    ],

    "Travel / Hospitality": [
        "MakeMyTrip",
        "Goibibo",
        "Booking.com",
        "Agoda",
        "Expedia"
    ],

    "Software / SaaS": [
        "Microsoft",
        "Google",
        "Salesforce",
        "Oracle",
        "Adobe"
    ],

    "AI / Machine Learning": [
        "OpenAI",
        "Google",
        "Microsoft",
        "Anthropic",
        "Meta AI"
    ],

    "Agriculture / AgriTech": [
        "DeHaat",
        "AgroStar",
        "Ninjacart",
        "AgriBazaar",
        "Samunnati"
    ],

    "Retail / Local Business": [
        "DMart",
        "Reliance Retail",
        "Walmart",
        "Amazon",
        "Flipkart"
    ]
}


# ============================================================
# UTILITY
# ============================================================

def clean_text(text):
    return re.sub(r"\s+", " ", str(text or "")).strip()


def detect_field(business_idea):
    text = business_idea.lower()

    scores = {}

    for field, keywords in FIELD_KEYWORDS.items():
        score = 0

        for keyword in keywords:
            if keyword in text:
                score += 1

        scores[field] = score

    best_field = max(scores, key=scores.get)

    if scores[best_field] == 0:
        return "General Business"

    return best_field


# ============================================================
# WEB SEARCH
# ============================================================

def web_search(query, limit=8):

    try:
        url = (
            "https://html.duckduckgo.com/html/?q="
            + quote_plus(query)
        )

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=12
        )

        if response.status_code != 200:
            return []

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        results = []

        for item in soup.select(".result")[:limit]:

            link = item.select_one(".result__a")
            snippet = item.select_one(
                ".result__snippet"
            )

            if not link:
                continue

            results.append({
                "title": clean_text(
                    link.get_text(" ", strip=True)
                ),
                "url": link.get("href", ""),
                "snippet": clean_text(
                    snippet.get_text(" ", strip=True)
                    if snippet else ""
                )
            })

        return results

    except Exception:
        return []


# ============================================================
# COMPETITOR DISCOVERY
# ============================================================

def discover_competitors(
    business_idea,
    state,
    field
):

    # Fast mode is ideal for live demos. Set WEB_RESEARCH_ENABLED=true in .env
    # when a slower live web lookup is required.
    search_results = []
    if WEB_RESEARCH_ENABLED:
        search_results = web_search(
            f"{business_idea} competitors in {state} India",
            8
        )

    names = []

    # Known competitors for reliable initial results
    if field in COMPETITOR_DATABASE:
        names.extend(
            COMPETITOR_DATABASE[field]
        )

    # Extract possible company names
    for result in search_results:

        title = result["title"]

        title = re.sub(
            r"\s*[-|:]\s*.*$",
            "",
            title
        )

        if 2 <= len(title) <= 60:
            names.append(title)

    final = []
    seen = set()

    for name in names:

        name = clean_text(name)

        normalized = re.sub(
            r"[^a-z0-9]",
            "",
            name.lower()
        )

        if not normalized:
            continue

        if normalized in seen:
            continue

        seen.add(normalized)

        final.append({
            "name": name,
            "state": state
        })

        if len(final) >= 8:
            break

    if not final:

        final = [
            {
                "name": "Market Leader 1",
                "state": state
            },
            {
                "name": "Market Leader 2",
                "state": state
            },
            {
                "name": "Emerging Competitor",
                "state": state
            }
        ]

    return final


# ============================================================
# COMPETITOR WEB RESEARCH
# ============================================================

def research_competitor(
    competitor,
    business_idea,
    state
):

    name = competitor["name"]

    results = []
    development_results = []
    if WEB_RESEARCH_ENABLED:
        results = web_search(
            f"{name} {business_idea} {state} India",
            5
        )
        development_results = web_search(
            f"{name} latest launch product feature expansion offer",
            4
        )

    combined = results + development_results

    if not combined and WEB_RESEARCH_ENABLED:
        official_url = OFFICIAL_COMPETITOR_SOURCES.get(name)
        if official_url:
            try:
                response = requests.get(
                    official_url,
                    headers=HEADERS,
                    timeout=12
                )
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                title = clean_text(soup.title.get_text(" ", strip=True) if soup.title else name)
                description_tag = soup.select_one('meta[name="description"]')
                description = clean_text(
                    description_tag.get("content", "") if description_tag else ""
                )
                page_text = clean_text(soup.get_text(" ", strip=True))
                combined = [{
                    "title": title,
                    "url": official_url,
                    "snippet": description or page_text[:600]
                }]
            except requests.RequestException:
                combined = []

    text_parts = []

    for item in combined:
        text_parts.append(
            item["title"]
        )
        text_parts.append(
            item["snippet"]
        )

    text = " ".join(text_parts)

    lower = text.lower()

    signals = []

    signal_map = {
        "New Product / Launch": [
            "launch",
            "launched",
            "new product",
            "introduced"
        ],

        "Technology": [
            "ai",
            "artificial intelligence",
            "technology",
            "automation",
            "machine learning"
        ],

        "Expansion": [
            "expansion",
            "expand",
            "new city",
            "new market"
        ],

        "Offers / Pricing": [
            "offer",
            "discount",
            "price",
            "pricing",
            "sale",
            "cashback"
        ],

        "Partnership": [
            "partnership",
            "partner",
            "collaboration"
        ],

        "Customer Experience": [
            "customer",
            "personalization",
            "personalized",
            "support",
            "experience"
        ]
    }

    for category, keywords in signal_map.items():

        if any(
            word in lower
            for word in keywords
        ):
            signals.append(category)

    if not signals:
        signals = []

    logger.info(
        "competitor_research name=%s results=%d signals=%s",
        name,
        len(combined),
        signals
    )

    return {
        "name": name,
        "state": state,
        "research": combined[:10],
        "signals": signals,
        "development": (
            f"{name} is showing activity related to "
            + ", ".join(signals)
            + "."
        )
    }


# ============================================================
# GEMINI ANALYSIS
# ============================================================

def fallback_analysis(business_idea, state, field):
    return {
        "summary": (
            f"{business_idea} is positioned in {field} for the {state} market. "
            "The initial opportunity is to pair a focused local offer with a better digital customer journey."
        ),
        "market_position": (
            "Established competitors usually win on recognition, reach and repeatable operations. "
            "A new entrant should focus on one underserved customer segment before expanding."
        ),
        "advantages": [
            "Opportunity to build a focused local solution",
            "Can use AI for personalization",
            "Can respond faster to customer needs"
        ],
        "improvements": [
            "Improve personalization for the first target customer segment",
            "Strengthen the mobile and digital customer experience",
            "Study competitor pricing and create a clear value proposition",
            "Improve customer support response time",
            "Create state-specific marketing and partnerships"
        ],
        "strategy": [
            "Start with the largest capability gap",
            "Build a clear competitive advantage",
            "Monitor competitor launches",
            "Measure customer satisfaction",
            "Review strategy regularly"
        ]
    }


def parse_ai_json(text):
    """Accept JSON returned with or without a Markdown code fence."""
    cleaned = re.sub(r"^```(?:json)?\\s*", "", (text or "").strip(), flags=re.I)
    cleaned = re.sub(r"\\s*```$", "", cleaned)
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start < 0 or end < start:
        raise ValueError("The AI response did not contain a JSON object.")
    return json.loads(cleaned[start:end + 1])


def ai_analysis(
    business_idea,
    state,
    field,
    competitors,
    provider="auto"
):
    competitor_text = "\n".join(
        [
            f"- {c['name']}: "
            f"{', '.join(c.get('signals', []))}"
            for c in competitors
        ]
    )

    prompt = f"""
You are a strategic business consultant.

Analyze this business:

Business idea:
{business_idea}

State:
{state}

Detected business field:
{field}

Competitors:
{competitor_text}

Determine:

1. Why these competitors are strong.
2. How they are developing.
3. What customers may prefer about them.
4. What this new business is missing.
5. What changes the business should make.
6. What advantages the new business can create.
7. Practical recommendations.
8. Market strategy.
9. Market gaps supported by the competitor signals and research provided. Do not invent
   generic gaps; identify services, capabilities, or customer needs competitors appear
   to be missing or serving weakly.

Return ONLY valid JSON.

Use exactly this structure:

{{
  "summary": "short business analysis",
  "market_position": "market position explanation",
  "advantages": [
    "advantage 1",
    "advantage 2",
    "advantage 3"
  ],
  "improvements": [
    "improvement 1",
    "improvement 2",
    "improvement 3",
    "improvement 4",
    "improvement 5"
  ],
  "strategy": [
    "strategy 1",
    "strategy 2",
    "strategy 3",
    "strategy 4",
    "strategy 5"
  ],
  "market_gaps": [
    {{
      "title": "specific market gap",
      "strength": 75,
      "level": "High Opportunity",
      "why_matters": "short evidence-based explanation using the competitors",
      "business_opportunity": "how this business can use the gap",
      "recommended_differentiator": "a specific feature or service to provide"
    }}
  ]
}}
"""

    # API keys never leave the server. Auto tries the configured providers in order.
    providers = [provider] if provider != "auto" else ["gemini", "groq"]
    for selected_provider in providers:
        try:
            if selected_provider == "gemini" and gemini_client:
                response = gemini_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=prompt
                )
                result = parse_ai_json(response.text)
                result["analysis_provider"] = "Gemini"
                return result

            if selected_provider == "groq" and GROQ_API_KEY:
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": GROQ_MODEL,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.35,
                        "response_format": {"type": "json_object"}
                    },
                    timeout=35
                )
                response.raise_for_status()
                text = response.json()["choices"][0]["message"]["content"]
                result = parse_ai_json(text)
                result["analysis_provider"] = "Groq"
                return result
        except Exception:
            # The dashboard remains useful when an API is unavailable or returns invalid JSON.
            continue

    result = fallback_analysis(business_idea, state, field)
    result["analysis_provider"] = "Local strategic baseline"
    return result


# ============================================================
# STRATEGIC SCORES
# ============================================================

SIGNAL_WEIGHTS = {
    "Technology": 22,
    "New Product / Launch": 18,
    "Expansion": 15,
    "Customer Experience": 13,
    "Partnership": 10,
    "Offers / Pricing": 8,
    "Market Presence": 7,
    "Customer Focus": 7,
}

def calculate_score(
    signals,
    research_count,
    is_target=False
):
    """Calculate a reproducible 0-100 score from one competitor's evidence."""
    observed_signals = {
        clean_text(signal)
        for signal in signals or []
        if clean_text(signal)
    }

    score = sum(
        SIGNAL_WEIGHTS.get(signal, 0)
        for signal in observed_signals
    )

    # Research volume is evidence confidence, not a replacement for signals.
    score += min(max(int(research_count or 0), 0) * 2, 10)

    if is_target:
        score -= 8

    return max(0, min(100, score))


def threat_level(score):

    if score >= 82:
        return "HIGH"

    if score >= 68:
        return "MEDIUM"

    return "LOW"


# ============================================================
# MARKET GAP DETECTOR
# ============================================================

def build_market_gaps(business_idea, competitors, ai_gaps=None):
    """Turn the competitor research already collected into actionable gaps."""
    if len(competitors) < 2:
        return []

    valid_ai_gaps = []
    for gap in ai_gaps or []:
        if not isinstance(gap, dict) or not clean_text(gap.get("title")):
            continue
        try:
            strength = int(float(gap.get("strength", 0) or 0))
        except (TypeError, ValueError):
            strength = 0
        strength = max(0, min(100, strength))
        valid_ai_gaps.append({
            "title": clean_text(gap["title"]),
            "strength": strength,
            "level": clean_text(gap.get("level")) or (
                "High Opportunity" if strength >= 70 else
                "Medium Opportunity" if strength >= 45 else "Low Opportunity"
            ),
            "why_matters": clean_text(gap.get("why_matters")),
            "business_opportunity": clean_text(gap.get("business_opportunity")),
            "recommended_differentiator": clean_text(gap.get("recommended_differentiator"))
        })
    if valid_ai_gaps:
        return valid_ai_gaps[:4]

    signal_options = {
        "Technology": ("Technology and automation", "Build a more intelligent, efficient experience around the needs of {idea} customers.", "Introduce practical automation or AI-assisted workflows tailored to {idea}."),
        "Customer Experience": ("Customer experience and support", "Win customers with a more responsive, guided journey for {idea}.", "Offer proactive support, clear onboarding, and feedback-driven service improvements."),
        "Offers / Pricing": ("Flexible value and pricing", "Create a clearer value proposition for the most important {idea} customer segment.", "Provide transparent packages, trials, or outcome-based pricing where appropriate."),
        "Partnership": ("Local partnerships and ecosystem reach", "Use trusted partners to make {idea} easier to discover and adopt.", "Build partnerships with relevant local organizations, specialists, or distribution channels."),
        "Expansion": ("Focused market coverage", "Serve a specific underserved segment before expanding broadly in {idea}.", "Launch a focused offering for a well-defined local or customer segment."),
        "New Product / Launch": ("Visible product innovation", "Differentiate {idea} with a focused solution to an unmet customer need.", "Maintain a customer-feedback roadmap and release a distinctive high-value feature."),
    }
    total = len(competitors)
    observed = [signal for competitor in competitors for signal in competitor.get("signals", [])]
    gaps = []
    for signal, (title, opportunity, differentiator) in signal_options.items():
        missing = total - sum(signal in competitor.get("signals", []) for competitor in competitors)
        if missing < (total + 1) // 2:
            continue
        strength = round((missing / total) * 100)
        level = "High Opportunity" if strength >= 75 else "Medium Opportunity" if strength >= 50 else "Low Opportunity"
        gaps.append({
            "title": title,
            "strength": strength,
            "level": level,
            "why_matters": f"{missing} of {total} analysed competitors showed no clear {signal.lower()} signal in the collected research.",
            "business_opportunity": opportunity.format(idea=business_idea),
            "recommended_differentiator": differentiator.format(idea=business_idea)
        })
    return sorted(gaps, key=lambda gap: gap["strength"], reverse=True)[:4]


# ============================================================
# SWOT
# ============================================================

def build_swot(
    business_idea,
    field,
    competitors,
    ai_data
):

    return {
        "strengths": [
            f"Focused business idea in {field}",
            "Opportunity to specialize in the target market",
            "Ability to build a differentiated customer experience"
        ],

        "weaknesses": [
            "Lower market recognition than established competitors",
            "Limited initial customer base",
            "May need stronger technology and marketing capabilities"
        ],

        "opportunities": [
            f"Growing opportunities in {state_placeholder(field)}",
            "AI-powered personalization",
            "Local and state-specific customer targeting",
            "Partnerships and digital expansion"
        ],

        "threats": [
            "Established competitors",
            "Price competition",
            "Rapid technology changes",
            "Competitor product launches"
        ]
    }


def state_placeholder(field):
    return "the selected market"


# ============================================================
# CAPABILITY SCORES
# ============================================================

def capability_scores(
    score,
    signal_count
):

    innovation = min(
        95,
        score + signal_count * 2
    )

    market = min(
        95,
        score + 5
    )

    digital = min(
        95,
        score + signal_count * 3
    )

    customer = min(
        95,
        score + 3
    )

    return {
        "innovation": innovation,
        "market": market,
        "digital": digital,
        "customer": customer
    }


# ============================================================
# MAIN ANALYSIS
# ============================================================

def analyze_business(
    business_idea,
    state,
    provider="auto"
):

    field = detect_field(
        business_idea
    )

    competitor_list = discover_competitors(
        business_idea,
        state,
        field
    )

    competitor_data = []

    for competitor in competitor_list:

        data = research_competitor(
            competitor,
            business_idea,
            state
        )

        score = calculate_score(
            data["signals"],
            len(data["research"])
        )

        logger.info(
            "competitor_score name=%s results=%d signals=%s score=%d",
            data["name"],
            len(data["research"]),
            data["signals"],
            score
        )

        data["strategic_score"] = score
        data["threat_level"] = threat_level(score)

        data["capabilities"] = capability_scores(
            score,
            len(data["signals"])
        )

        competitor_data.append(data)

    target_score = 62

    target_capabilities = {
        "innovation": 60,
        "market": 58,
        "digital": 55,
        "customer": 63
    }

    ai_data = ai_analysis(
        business_idea,
        state,
        field,
        competitor_data,
        provider
    )

    average_score = round(
        sum(
            item["strategic_score"]
            for item in competitor_data
        )
        / max(len(competitor_data), 1)
    )

    average_capabilities = {
        "innovation": round(
            sum(
                x["capabilities"]["innovation"]
                for x in competitor_data
            )
            / max(len(competitor_data), 1)
        ),

        "market": round(
            sum(
                x["capabilities"]["market"]
                for x in competitor_data
            )
            / max(len(competitor_data), 1)
        ),

        "digital": round(
            sum(
                x["capabilities"]["digital"]
                for x in competitor_data
            )
            / max(len(competitor_data), 1)
        ),

        "customer": round(
            sum(
                x["capabilities"]["customer"]
                for x in competitor_data
            )
            / max(len(competitor_data), 1)
        )
    }

    market_gaps = build_market_gaps(
        business_idea,
        competitor_data,
        ai_data.get("market_gaps")
    )

    # Development section
    development = []

    for competitor in competitor_data:

        development.append({
            "competitor": competitor["name"],
            "state": state,
            "development": competitor["development"],
            "signals": competitor["signals"]
        })

    # Strategic signals
    signals = []

    for competitor in competitor_data:

        for signal in competitor["signals"]:

            signals.append({
                "competitor": competitor["name"],
                "type": signal,
                "detail": (
                    f"{competitor['name']} shows "
                    f"activity related to {signal}."
                )
            })

    # Threats
    threats = [
        {
            "title": "Strong competitors",
            "detail": (
                "Established competitors may already "
                "have stronger brand recognition."
            )
        },
        {
            "title": "Pricing pressure",
            "detail": (
                "Competitors may use discounts and "
                "offers to attract customers."
            )
        },
        {
            "title": "Technology gap",
            "detail": (
                "Competitors adopting AI and automation "
                "can create a capability gap."
            )
        }
    ]

    # Opportunities
    opportunities = [
        {
            "title": "Personalization",
            "detail": (
                "Use AI to personalize products, services "
                "and customer interactions."
            )
        },
        {
            "title": "Local market focus",
            "detail": (
                f"Create a strategy specifically designed "
                f"for customers in {state}."
            )
        },
        {
            "title": "Digital improvement",
            "detail": (
                "Improve mobile, website and digital "
                "customer experience."
            )
        }
    ]

    recommendations = []

    for item in ai_data.get(
        "improvements",
        []
    ):
        recommendations.append({
            "title": item,
            "reason": (
                "Recommended based on competitor "
                "capabilities and strategic gaps."
            ),
            "priority": "HIGH"
        })

    if not recommendations:

        recommendations = [
            {
                "title": "Improve personalization",
                "reason": "Competitors increasingly provide tailored experiences.",
                "priority": "HIGH"
            },
            {
                "title": "Improve digital experience",
                "reason": "A stronger digital journey can increase customer engagement.",
                "priority": "HIGH"
            },
            {
                "title": "Monitor competitor pricing",
                "reason": "Pricing can directly influence customer choice.",
                "priority": "MEDIUM"
            }
        ]

    # Capability gap
    capability_gap = {
        "innovation": max(
            0,
            average_capabilities["innovation"]
            - target_capabilities["innovation"]
        ),

        "market": max(
            0,
            average_capabilities["market"]
            - target_capabilities["market"]
        ),

        "digital": max(
            0,
            average_capabilities["digital"]
            - target_capabilities["digital"]
        ),

        "customer": max(
            0,
            average_capabilities["customer"]
            - target_capabilities["customer"]
        )
    }

    largest_gap = max(
        capability_gap,
        key=capability_gap.get
    )

    graph_explanations = {
        "strategic_score": [
            "Step 1: The graph compares the strategic strength of the business and competitors.",
            "Step 2: A higher score means stronger overall competitive capability.",
            "Step 3: Compare the business score with the competitor average.",
            "Step 4: Focus first on areas where competitors have a large advantage."
        ],

        "radar": [
            "Step 1: The radar compares four important capabilities.",
            "Step 2: The outer area represents stronger capability.",
            "Step 3: Compare your business shape with the competitor average shape.",
            "Step 4: Expand the areas where your shape is smaller."
        ],

        "gap": [
            "Step 1: The graph calculates the difference between your business and competitors.",
            "Step 2: A larger gap means a greater improvement opportunity.",
            f"Step 3: The largest current gap is {largest_gap.title()}.",
            "Step 4: Prioritize that capability before making too many changes."
        ]
    }

    swot = {
        "strengths": [
            f"Focused concept in {field}",
            "Can build a specialized customer experience",
            "Can use AI from the beginning"
        ],

        "weaknesses": [
            "New business has lower brand recognition",
            "Smaller initial customer base",
            "Lower strategic score than established competitors"
        ],

        "opportunities": [
            "AI personalization",
            f"State-specific strategy for {state}",
            "Digital customer experience",
            "Partnerships and local expansion"
        ],

        "threats": [
            "Established competitors",
            "Aggressive pricing",
            "Fast competitor innovation",
            "Changing customer expectations"
        ]
    }

    return {
        "business_idea": business_idea,
        "state": state,
        "field": field,

        "summary": ai_data.get(
            "summary",
            ""
        ),

        "market_position": ai_data.get(
            "market_position",
            ""
        ),

        "analysis_provider": ai_data.get("analysis_provider", "Local strategic baseline"),

        "target_score": target_score,

        "target_threat": threat_level(
            target_score
        ),

        "competitor_average": average_score,

        "competitors": competitor_data,

        "development": development,

        "signals": signals[:20],

        "threats": threats,

        "opportunities": opportunities,

        "market_gaps": market_gaps,

        "recommendations": recommendations[:10],

        "swot": swot,

        "target_capabilities": target_capabilities,

        "competitor_capabilities": average_capabilities,

        "capability_gap": capability_gap,

        "graph_explanations": graph_explanations,

        "generated_at": datetime.now().strftime(
            "%d %b %Y, %I:%M %p"
        )
    }


# ============================================================
# PDF REPORT
# ============================================================

def build_pdf_report(data):

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle
    )

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=35,
        leftMargin=35,
        topMargin=35,
        bottomMargin=35
    )

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "AI Autonomous Strategic Competitor Report",
            styles["Title"]
        )
    )

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            f"<b>Business Idea:</b> "
            f"{data.get('business_idea', '')}",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"<b>State:</b> "
            f"{data.get('state', '')}",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Business Field:</b> "
            f"{data.get('field', '')}",
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "<b>Strategic Summary</b>",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            data.get("summary", ""),
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "<b>Competitors</b>",
            styles["Heading2"]
        )
    )

    table_data = [
        [
            "Competitor",
            "Score",
            "Threat"
        ]
    ]

    for item in data.get("competitors", []):

        table_data.append([
            item.get("name", ""),
            str(
                item.get(
                    "strategic_score",
                    ""
                )
            ),
            item.get(
                "threat_level",
                ""
            )
        ])

    table = Table(
        table_data,
        colWidths=[260, 80, 80]
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                7
            )
        ])
    )

    story.append(table)

    story.append(Spacer(1, 18))

    story.append(
        Paragraph(
            "<b>How Competitors Are Developing</b>",
            styles["Heading2"]
        )
    )

    for item in data.get(
        "development",
        []
    ):

        story.append(
            Paragraph(
                f"<b>{item.get('competitor')}</b>: "
                f"{item.get('development')}",
                styles["Normal"]
            )
        )

        story.append(Spacer(1, 6))

    story.append(
        Paragraph(
            "<b>Market Gap Detector</b>",
            styles["Heading2"]
        )
    )

    market_gaps = data.get("market_gaps", [])
    if not market_gaps:
        story.append(
            Paragraph(
                "Not enough competitor data to identify reliable market gaps.",
                styles["Normal"]
            )
        )

    for gap in market_gaps:
        story.append(
            Paragraph(
                f"<b>{gap.get('level', 'Opportunity')}: "
                f"{gap.get('title', '')} ({gap.get('strength', 0)}%)</b>",
                styles["Heading3"]
            )
        )
        story.append(Paragraph(
            f"<b>Why this gap matters:</b> {gap.get('why_matters', '')}",
            styles["Normal"]
        ))
        story.append(Paragraph(
            f"<b>Business opportunity:</b> {gap.get('business_opportunity', '')}",
            styles["Normal"]
        ))
        story.append(Paragraph(
            f"<b>Recommended differentiator:</b> {gap.get('recommended_differentiator', '')}",
            styles["Normal"]
        ))
        story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            "<b>Recommendations</b>",
            styles["Heading2"]
        )
    )

    for item in data.get(
        "recommendations",
        []
    ):

        story.append(
            Paragraph(
                f"• {item.get('title')}: "
                f"{item.get('reason')}",
                styles["Normal"]
            )
        )

        story.append(Spacer(1, 5))

    story.append(
        Paragraph(
            "<b>SWOT Analysis</b>",
            styles["Heading2"]
        )
    )

    swot = data.get(
        "swot",
        {}
    )

    for title, key in [
        ("Strengths", "strengths"),
        ("Weaknesses", "weaknesses"),
        ("Opportunities", "opportunities"),
        ("Threats", "threats")
    ]:

        story.append(
            Paragraph(
                f"<b>{title}</b>",
                styles["Heading3"]
            )
        )

        for item in swot.get(key, []):

            story.append(
                Paragraph(
                    f"• {item}",
                    styles["Normal"]
                )
            )

    document.build(story)

    buffer.seek(0)

    return buffer
