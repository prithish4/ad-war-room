from __future__ import annotations

import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(title="Ad Intelligence API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# SQLite setup
# ---------------------------------------------------------------------------

DB_PATH = Path(__file__).parent / "ads.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS competitor_ads (
    id                  TEXT PRIMARY KEY,
    ad_id               TEXT UNIQUE NOT NULL,
    competitor_name     TEXT,
    competitor_page_id  TEXT,
    brand               TEXT,
    vertical            TEXT,
    ad_format           TEXT,
    message_theme       TEXT,
    emotional_tone      TEXT,
    headline            TEXT,
    body_text           TEXT,
    cta                 TEXT,
    platform            TEXT,
    estimated_spend_min INTEGER,
    estimated_spend_max INTEGER,
    start_date          TEXT,
    end_date            TEXT,
    is_active           INTEGER DEFAULT 1,
    days_running        INTEGER DEFAULT 0,
    num_cards           INTEGER,
    country             TEXT,
    source              TEXT DEFAULT 'mock',
    created_at          TEXT DEFAULT (datetime('now'))
);
"""

CREATE_INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_brand           ON competitor_ads(brand);",
    "CREATE INDEX IF NOT EXISTS idx_competitor_name ON competitor_ads(competitor_name);",
    "CREATE INDEX IF NOT EXISTS idx_message_theme   ON competitor_ads(message_theme);",
    "CREATE INDEX IF NOT EXISTS idx_is_active       ON competitor_ads(is_active);",
    "CREATE INDEX IF NOT EXISTS idx_start_date      ON competitor_ads(start_date);",
]

CREATE_BRIEFS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS weekly_briefs (
    id            TEXT PRIMARY KEY,
    brand         TEXT NOT NULL,
    markdown      TEXT NOT NULL,
    stats_json    TEXT,
    generated_at  TEXT DEFAULT (datetime('now'))
);
"""

CREATE_BRIEFS_INDEX_SQL = (
    "CREATE INDEX IF NOT EXISTS idx_briefs_brand ON weekly_briefs(brand);"
)

# ---------------------------------------------------------------------------
# Brand / theme constants
# ---------------------------------------------------------------------------

BRAND_LABELS: dict[str, str] = {
    "bebodywise":  "Bebodywise",
    "man_matters": "Man Matters",
    "little_joys": "Little Joys",
}

VALID_BRANDS = set(BRAND_LABELS.keys())

# Themes each brand competes across — used to detect creative gaps
BRAND_THEMES: dict[str, list[str]] = {
    "bebodywise":  ["weight", "immunity", "energy", "confidence"],
    "man_matters": ["hair_loss", "performance", "energy", "confidence"],
    "little_joys": ["immunity", "parenting", "safety", "energy"],
}


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    try:
        yield conn
    finally:
        conn.close()


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    # SQLite stores booleans as 0/1 — convert back for JSON consumers
    d["is_active"] = bool(d["is_active"])
    return d


@app.on_event("startup")
def init_db() -> None:
    with get_db() as conn:
        conn.execute(CREATE_TABLE_SQL)
        for sql in CREATE_INDEXES_SQL:
            conn.execute(sql)
        conn.execute(CREATE_BRIEFS_TABLE_SQL)
        conn.execute(CREATE_BRIEFS_INDEX_SQL)
        conn.commit()

        row_count = conn.execute(
            "SELECT COUNT(*) FROM competitor_ads;"
        ).fetchone()[0]

    if row_count == 0:
        _seed_database()


def _seed_database() -> None:
    """Insert all mock records. Called on startup when the table is empty."""
    from scraper.mock_data import generate_mock_ads

    records = generate_mock_ads()
    with get_db() as conn:
        for rec in records:
            conn.execute(
                """
                INSERT INTO competitor_ads (
                    id, ad_id, competitor_name, competitor_page_id,
                    brand, vertical, ad_format, message_theme, emotional_tone,
                    headline, body_text, cta, platform,
                    estimated_spend_min, estimated_spend_max,
                    start_date, end_date, is_active, days_running,
                    num_cards, country, source
                ) VALUES (
                    :id, :ad_id, :competitor_name, :competitor_page_id,
                    :brand, :vertical, :ad_format, :message_theme, :emotional_tone,
                    :headline, :body_text, :cta, :platform,
                    :estimated_spend_min, :estimated_spend_max,
                    :start_date, :end_date, :is_active, :days_running,
                    :num_cards, :country, :source
                )
                ON CONFLICT(ad_id) DO NOTHING;
                """,
                rec,
            )
        conn.commit()


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# POST /api/seed-mock-data
# ---------------------------------------------------------------------------

@app.post("/api/seed-mock-data")
def seed_mock_data(clear_existing: bool = False) -> dict[str, Any]:
    """
    Populate competitor_ads with realistic mock data for all 15 competitors
    across Bebodywise, Man Matters, and Little Joys.

    ?clear_existing=true  — wipes previous mock rows before inserting.
    """
    from scraper.mock_data import generate_mock_ads

    records = generate_mock_ads()

    with get_db() as conn:
        if clear_existing:
            conn.execute("DELETE FROM competitor_ads WHERE source = 'mock';")

        inserted = 0
        for rec in records:
            # UPSERT: if ad_id already exists, overwrite all fields
            conn.execute(
                """
                INSERT INTO competitor_ads (
                    id, ad_id, competitor_name, competitor_page_id,
                    brand, vertical, ad_format, message_theme, emotional_tone,
                    headline, body_text, cta, platform,
                    estimated_spend_min, estimated_spend_max,
                    start_date, end_date, is_active, days_running,
                    num_cards, country, source
                ) VALUES (
                    :id, :ad_id, :competitor_name, :competitor_page_id,
                    :brand, :vertical, :ad_format, :message_theme, :emotional_tone,
                    :headline, :body_text, :cta, :platform,
                    :estimated_spend_min, :estimated_spend_max,
                    :start_date, :end_date, :is_active, :days_running,
                    :num_cards, :country, :source
                )
                ON CONFLICT(ad_id) DO UPDATE SET
                    competitor_name     = excluded.competitor_name,
                    brand               = excluded.brand,
                    ad_format           = excluded.ad_format,
                    message_theme       = excluded.message_theme,
                    emotional_tone      = excluded.emotional_tone,
                    headline            = excluded.headline,
                    body_text           = excluded.body_text,
                    estimated_spend_min = excluded.estimated_spend_min,
                    estimated_spend_max = excluded.estimated_spend_max,
                    start_date          = excluded.start_date,
                    end_date            = excluded.end_date,
                    is_active           = excluded.is_active,
                    days_running        = excluded.days_running;
                """,
                rec,
            )
            inserted += 1

        conn.commit()

    # Summary breakdowns computed from the generated records (no extra DB query)
    brand_counts: dict[str, int] = {}
    competitor_counts: dict[str, int] = {}
    for rec in records:
        brand_counts[rec["brand"]] = brand_counts.get(rec["brand"], 0) + 1
        competitor_counts[rec["competitor_name"]] = (
            competitor_counts.get(rec["competitor_name"], 0) + 1
        )

    return {
        "status": "success",
        "total_records": len(records),
        "upserted_count": inserted,
        "active_ads": sum(1 for r in records if r["is_active"]),
        "ads_60_plus_days": sum(1 for r in records if r["days_running"] >= 60),
        "by_brand": brand_counts,
        "by_competitor": competitor_counts,
    }


# ---------------------------------------------------------------------------
# GET /api/ads
# ---------------------------------------------------------------------------

@app.get("/api/ads")
def list_ads(
    brand: str | None = None,
    competitor: str | None = None,
    theme: str | None = None,
    tone: str | None = None,
    ad_format: str | None = None,
    is_active: bool | None = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
) -> dict[str, Any]:
    """
    Paginated, filtered ad listing. All filters are AND-combined.
    """
    conditions: list[str] = []
    params: list[Any] = []

    if brand:
        conditions.append("brand = ?")
        params.append(brand)
    if competitor:
        conditions.append("competitor_name = ?")
        params.append(competitor)
    if theme:
        conditions.append("message_theme = ?")
        params.append(theme)
    if tone:
        conditions.append("emotional_tone = ?")
        params.append(tone)
    if ad_format:
        conditions.append("ad_format = ?")
        params.append(ad_format)
    if is_active is not None:
        conditions.append("is_active = ?")
        params.append(1 if is_active else 0)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    with get_db() as conn:
        total = conn.execute(
            f"SELECT COUNT(*) FROM competitor_ads {where};", params
        ).fetchone()[0]

        rows = conn.execute(
            f"SELECT * FROM competitor_ads {where} "
            f"ORDER BY start_date DESC LIMIT ? OFFSET ?;",
            [*params, limit, offset],
        ).fetchall()

    return {
        "data": [_row_to_dict(r) for r in rows],
        "total": total,
        "count": len(rows),
        "limit": limit,
        "offset": offset,
    }


# ---------------------------------------------------------------------------
# GET /api/competitors
# ---------------------------------------------------------------------------

@app.get("/api/competitors")
def list_competitors(brand: str | None = None) -> dict[str, Any]:
    """
    Returns each competitor with aggregated stats:
    total ads, active ads, average daily spend, top message theme.
    """
    where = "WHERE brand = ?" if brand else ""
    params = [brand] if brand else []

    sql = f"""
        SELECT
            competitor_name,
            brand,
            vertical,
            COUNT(*)                                        AS total_ads,
            SUM(is_active)                                  AS active_ads,
            ROUND(AVG((estimated_spend_min + estimated_spend_max) / 2.0), 0)
                                                            AS avg_spend,
            MAX(days_running)                               AS max_days_running
        FROM competitor_ads
        {where}
        GROUP BY competitor_name, brand, vertical
        ORDER BY total_ads DESC;
    """

    top_theme_sql = f"""
        SELECT competitor_name, message_theme
        FROM (
            SELECT competitor_name, message_theme,
                   COUNT(*) AS cnt,
                   ROW_NUMBER() OVER (
                       PARTITION BY competitor_name ORDER BY COUNT(*) DESC
                   ) AS rn
            FROM competitor_ads
            {where}
            GROUP BY competitor_name, message_theme
        )
        WHERE rn = 1;
    """

    with get_db() as conn:
        rows = conn.execute(sql, params).fetchall()
        theme_rows = conn.execute(top_theme_sql, params).fetchall()

    top_theme_map = {r["competitor_name"]: r["message_theme"] for r in theme_rows}

    data = []
    for r in rows:
        d = dict(r)
        d["top_theme"] = top_theme_map.get(d["competitor_name"])
        data.append(d)

    return {"data": data, "count": len(data)}


# ---------------------------------------------------------------------------
# GET /api/trends
# ---------------------------------------------------------------------------

@app.get("/api/trends")
def get_trends(brand: str | None = None) -> dict[str, Any]:
    """
    Returns chart-ready trend data:
    - weekly_spend: estimated spend aggregated by ISO week
    - theme_distribution: ad count per message theme
    - format_distribution: ad count per format
    - tone_distribution: ad count per emotional tone
    - longevity_buckets: ads grouped by days_running ranges
    """
    where = "WHERE brand = ?" if brand else ""
    params = [brand] if brand else []

    with get_db() as conn:
        # Weekly spend (use start_date truncated to Monday of that week)
        weekly = conn.execute(
            f"""
            SELECT
                strftime('%Y-W%W', start_date)              AS week,
                ROUND(SUM((estimated_spend_min + estimated_spend_max) / 2.0), 0)
                                                            AS total_spend,
                COUNT(*)                                    AS ad_count
            FROM competitor_ads
            {where}
            GROUP BY week
            ORDER BY week ASC;
            """,
            params,
        ).fetchall()

        theme_dist = conn.execute(
            f"""
            SELECT message_theme AS name, COUNT(*) AS value
            FROM competitor_ads {where}
            GROUP BY message_theme ORDER BY value DESC;
            """,
            params,
        ).fetchall()

        format_dist = conn.execute(
            f"""
            SELECT ad_format AS name, COUNT(*) AS value
            FROM competitor_ads {where}
            GROUP BY ad_format ORDER BY value DESC;
            """,
            params,
        ).fetchall()

        tone_dist = conn.execute(
            f"""
            SELECT emotional_tone AS name, COUNT(*) AS value
            FROM competitor_ads {where}
            GROUP BY emotional_tone ORDER BY value DESC;
            """,
            params,
        ).fetchall()

        longevity = conn.execute(
            f"""
            SELECT
                CASE
                    WHEN days_running < 7   THEN '0-6 days'
                    WHEN days_running < 14  THEN '7-13 days'
                    WHEN days_running < 30  THEN '14-29 days'
                    WHEN days_running < 60  THEN '30-59 days'
                    ELSE '60+ days'
                END AS bucket,
                COUNT(*) AS count
            FROM competitor_ads {where}
            GROUP BY bucket
            ORDER BY MIN(days_running) ASC;
            """,
            params,
        ).fetchall()

        # Top spenders by competitor
        top_spenders = conn.execute(
            f"""
            SELECT
                competitor_name,
                brand,
                ROUND(SUM((estimated_spend_min + estimated_spend_max) / 2.0), 0)
                    AS total_spend
            FROM competitor_ads {where}
            GROUP BY competitor_name, brand
            ORDER BY total_spend DESC
            LIMIT 10;
            """,
            params,
        ).fetchall()

    return {
        "weekly_spend": [dict(r) for r in weekly],
        "theme_distribution": [dict(r) for r in theme_dist],
        "format_distribution": [dict(r) for r in format_dist],
        "tone_distribution": [dict(r) for r in tone_dist],
        "longevity_buckets": [dict(r) for r in longevity],
        "top_spenders": [dict(r) for r in top_spenders],
    }


# ---------------------------------------------------------------------------
# GET /api/brief
# ---------------------------------------------------------------------------

@app.get("/api/brief")
def get_brief(brand: str | None = None) -> dict[str, Any]:
    """
    Returns a structured competitive intelligence brief.
    If ANTHROPIC_API_KEY is set, the summary field is AI-generated.
    Otherwise, a rule-based summary is returned so the endpoint always works.
    """
    where = "WHERE brand = ?" if brand else ""
    params = [brand] if brand else []

    with get_db() as conn:
        totals = conn.execute(
            f"""
            SELECT
                COUNT(*)                     AS total_ads,
                SUM(is_active)               AS active_ads,
                COUNT(DISTINCT competitor_name) AS competitor_count,
                ROUND(AVG(days_running), 1)  AS avg_days_running,
                ROUND(SUM((estimated_spend_min + estimated_spend_max) / 2.0), 0)
                                             AS total_est_spend
            FROM competitor_ads {where};
            """,
            params,
        ).fetchone()

        top_theme = conn.execute(
            f"""
            SELECT message_theme, COUNT(*) AS cnt
            FROM competitor_ads {where}
            GROUP BY message_theme ORDER BY cnt DESC LIMIT 1;
            """,
            params,
        ).fetchone()

        top_tone = conn.execute(
            f"""
            SELECT emotional_tone, COUNT(*) AS cnt
            FROM competitor_ads {where}
            GROUP BY emotional_tone ORDER BY cnt DESC LIMIT 1;
            """,
            params,
        ).fetchone()

        longest_running = conn.execute(
            f"""
            SELECT competitor_name, headline, days_running, message_theme
            FROM competitor_ads {where}
            ORDER BY days_running DESC LIMIT 3;
            """,
            params,
        ).fetchall()

        high_spend = conn.execute(
            f"""
            SELECT competitor_name, headline, estimated_spend_max, ad_format
            FROM competitor_ads {where}
            ORDER BY estimated_spend_max DESC LIMIT 3;
            """,
            params,
        ).fetchall()

    totals_d = dict(totals)
    brand_label = brand.replace("_", " ").title() if brand else "all brands"

    # Rule-based summary (always available)
    rule_summary = (
        f"Across {brand_label}, {totals_d['competitor_count']} competitors are running "
        f"{totals_d['total_ads']} tracked ads ({totals_d['active_ads']} currently active). "
        f"The dominant message theme is '{top_theme['message_theme'] if top_theme else 'N/A'}' "
        f"and the most-used emotional tone is '{top_tone['emotional_tone'] if top_tone else 'N/A'}'. "
        f"Ads run for an average of {totals_d['avg_days_running']} days, "
        f"with estimated cumulative spend of ₹{totals_d['total_est_spend']:,.0f}."
    )

    ai_summary: str | None = None
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if anthropic_key:
        try:
            import anthropic  # type: ignore

            client = anthropic.Anthropic(api_key=anthropic_key)
            prompt = (
                f"You are a competitive intelligence analyst. "
                f"Write a 3-bullet strategic brief for {brand_label} based on this data:\n\n"
                f"- Competitors tracked: {totals_d['competitor_count']}\n"
                f"- Total ads: {totals_d['total_ads']} ({totals_d['active_ads']} active)\n"
                f"- Top message theme: {top_theme['message_theme'] if top_theme else 'N/A'}\n"
                f"- Top emotional tone: {top_tone['emotional_tone'] if top_tone else 'N/A'}\n"
                f"- Avg ad lifespan: {totals_d['avg_days_running']} days\n"
                f"- Longest-running ads: {[dict(r) for r in longest_running]}\n"
                f"- Highest-spend ads: {[dict(r) for r in high_spend]}\n\n"
                f"Be concise and actionable."
            )
            msg = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}],
            )
            ai_summary = msg.content[0].text
        except Exception:
            pass  # Fall through to rule-based summary

    return {
        "brand": brand,
        "summary": ai_summary or rule_summary,
        "ai_generated": ai_summary is not None,
        "stats": totals_d,
        "top_theme": dict(top_theme) if top_theme else None,
        "top_tone": dict(top_tone) if top_tone else None,
        "longest_running_ads": [dict(r) for r in longest_running],
        "highest_spend_ads": [dict(r) for r in high_spend],
    }


# ---------------------------------------------------------------------------
# POST /api/brief/generate/{brand}
# ---------------------------------------------------------------------------

@app.post("/api/brief/generate/{brand}")
def generate_brief(brand: str) -> dict[str, Any]:
    """
    Queries the DB for all ads of that brand, builds a rich data payload,
    calls claude-sonnet-4-6 to write a 400-word markdown brief, then
    stores the result in weekly_briefs and returns it.
    """
    if brand not in VALID_BRANDS:
        raise HTTPException(status_code=404, detail=f"Unknown brand '{brand}'.")

    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="ANTHROPIC_API_KEY is not configured. Add it to backend/.env and restart.",
        )

    brand_label = BRAND_LABELS[brand]

    with get_db() as conn:
        # -- aggregate totals ------------------------------------------------
        totals = conn.execute(
            """
            SELECT COUNT(*) AS total_ads,
                   SUM(is_active) AS active_ads,
                   COUNT(DISTINCT competitor_name) AS competitor_count,
                   ROUND(AVG(days_running), 1) AS avg_days_running
            FROM competitor_ads WHERE brand = ?;
            """,
            [brand],
        ).fetchone()

        if not totals or totals["total_ads"] == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No ad data found for '{brand}'. Seed the database first.",
            )

        # -- format distribution with percentages ----------------------------
        format_dist = conn.execute(
            """
            SELECT ad_format,
                   COUNT(*) AS count,
                   ROUND(COUNT(*) * 100.0 /
                         (SELECT COUNT(*) FROM competitor_ads WHERE brand = ?), 1) AS pct
            FROM competitor_ads WHERE brand = ?
            GROUP BY ad_format ORDER BY count DESC;
            """,
            [brand, brand],
        ).fetchall()

        # -- top 5 longest-running ads ---------------------------------------
        longest = conn.execute(
            """
            SELECT competitor_name, headline, days_running,
                   message_theme, emotional_tone, ad_format
            FROM competitor_ads WHERE brand = ?
            ORDER BY days_running DESC LIMIT 5;
            """,
            [brand],
        ).fetchall()

        # -- theme distribution with percentages -----------------------------
        theme_dist = conn.execute(
            """
            SELECT message_theme,
                   COUNT(*) AS count,
                   ROUND(COUNT(*) * 100.0 /
                         (SELECT COUNT(*) FROM competitor_ads WHERE brand = ?), 1) AS pct
            FROM competitor_ads WHERE brand = ?
            GROUP BY message_theme ORDER BY count DESC;
            """,
            [brand, brand],
        ).fetchall()

        # -- tone distribution with percentages ------------------------------
        tone_dist = conn.execute(
            """
            SELECT emotional_tone,
                   COUNT(*) AS count,
                   ROUND(COUNT(*) * 100.0 /
                         (SELECT COUNT(*) FROM competitor_ads WHERE brand = ?), 1) AS pct
            FROM competitor_ads WHERE brand = ?
            GROUP BY emotional_tone ORDER BY count DESC;
            """,
            [brand, brand],
        ).fetchall()

        # -- distinct competitor names ----------------------------------------
        competitors = conn.execute(
            "SELECT DISTINCT competitor_name FROM competitor_ads WHERE brand = ?;",
            [brand],
        ).fetchall()

    # -- compute creative gaps -----------------------------------------------
    # A gap = a theme in the brand's competitive space with < 15 % share
    theme_pcts = {r["message_theme"]: r["pct"] for r in theme_dist}
    gaps = [
        (t, theme_pcts.get(t, 0.0))
        for t in BRAND_THEMES.get(brand, [])
        if theme_pcts.get(t, 0.0) < 15.0
    ]

    # -- build prompt data strings -------------------------------------------
    competitor_names = [r["competitor_name"] for r in competitors]

    format_lines = "\n".join(
        f"- {r['ad_format'].title()}: {r['pct']}% ({r['count']} ads)"
        for r in format_dist
    )
    longest_lines = "\n".join(
        f"{i + 1}. **{r['competitor_name']}** — \"{r['headline']}\" "
        f"— **{r['days_running']} days** — Theme: {r['message_theme'].replace('_', ' ')}"
        f", Tone: {r['emotional_tone']}"
        for i, r in enumerate(longest)
    )
    theme_lines = "\n".join(
        f"- {r['message_theme'].replace('_', ' ').title()}: {r['pct']}% ({r['count']} ads)"
        for r in theme_dist
    )
    tone_lines = "\n".join(
        f"- {r['emotional_tone'].title()}: {r['pct']}% ({r['count']} ads)"
        for r in tone_dist
    )
    gap_lines = (
        "\n".join(
            f"- {t.replace('_', ' ').title()}: {pct}% coverage (underexploited)"
            for t, pct in gaps
        )
        if gaps
        else "- No significant gaps — all core themes are actively contested."
    )

    prompt = f"""You are a senior competitive intelligence analyst. \
Analyze the following ad library data and write a strategic brief in markdown for {brand_label}'s marketing team.

---

## Input Data

**Brand under analysis:** {brand_label}
**Competitors monitored:** {', '.join(competitor_names)}
**Total ads tracked:** {totals['total_ads']} ({totals['active_ads']} currently active)
**Average ad lifespan:** {totals['avg_days_running']} days

## Ad Format Distribution
{format_lines}

## Top 5 Longest-Running Ads (battle-tested creatives — survived the algorithm longest)
{longest_lines}

## Message Theme Distribution
{theme_lines}

## Emotional Tone Distribution
{tone_lines}

## Creative Gaps (themes with low competitive saturation for {brand_label})
{gap_lines}

---

Write a 400-word competitive intelligence brief using EXACTLY this markdown structure. \
Use real percentages, specific competitor names, and actual headline quotes from the data above. \
Be analytical, specific, and actionable — not generic.

## 🎯 Executive Summary
(2–3 sentences. Include specific numbers: total ads, active ads, competitor count, avg lifespan.)

## 📊 Format Landscape
(What formats dominate, exact percentages, and what this signals for {brand_label}'s creative mix.)

## 🏆 Battle-Tested Creatives
(Name at least 3 specific competitors and quote their longest-running headlines. \
Identify what message pattern makes these creatives survive 60+ days.)

## ⚡ Theme & Tone Dominance
(Which themes are oversaturated with exact percentages? Which emotional tones rule? \
What does the dominance of '{(theme_dist[0]["message_theme"] if theme_dist else "aspiration")}' signal?)

## 🚀 Strategic Recommendations for {brand_label}
- (Specific recommendation tied to a gap or data point above)
- (Specific recommendation tied to format or tone insight above)
- (Specific recommendation tied to a battle-tested creative pattern above)"""

    # -- call Anthropic ------------------------------------------------------
    import anthropic as _anthropic  # type: ignore

    client = _anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1200,
        messages=[{"role": "user", "content": prompt}],
    )
    markdown_content: str = message.content[0].text

    # -- store in DB ---------------------------------------------------------
    stats_payload = {
        "totals": dict(totals),
        "format_distribution": [dict(r) for r in format_dist],
        "theme_distribution": [dict(r) for r in theme_dist],
        "tone_distribution": [dict(r) for r in tone_dist],
        "longest_running": [dict(r) for r in longest],
        "gaps": [{"theme": t, "pct": p} for t, p in gaps],
    }
    brief_id = str(uuid.uuid4())

    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO weekly_briefs (id, brand, markdown, stats_json, generated_at)
            VALUES (?, ?, ?, ?, datetime('now'));
            """,
            [brief_id, brand, markdown_content, json.dumps(stats_payload)],
        )
        generated_at = conn.execute(
            "SELECT generated_at FROM weekly_briefs WHERE id = ?;", [brief_id]
        ).fetchone()["generated_at"]
        conn.commit()

    return {
        "id": brief_id,
        "brand": brand,
        "markdown": markdown_content,
        "generated_at": generated_at,
        "stats": stats_payload,
    }


# ---------------------------------------------------------------------------
# GET /api/brief/{brand}
# ---------------------------------------------------------------------------

@app.get("/api/brief/{brand}")
def get_stored_brief(brand: str) -> dict[str, Any]:
    """
    Returns the most recently generated brief for the given brand.
    Raises 404 if none has been generated yet.
    """
    if brand not in VALID_BRANDS:
        raise HTTPException(status_code=404, detail=f"Unknown brand '{brand}'.")

    with get_db() as conn:
        row = conn.execute(
            """
            SELECT id, brand, markdown, stats_json, generated_at
            FROM weekly_briefs
            WHERE brand = ?
            ORDER BY generated_at DESC
            LIMIT 1;
            """,
            [brand],
        ).fetchone()

    if not row:
        raise HTTPException(
            status_code=404,
            detail=f"No brief found for '{brand}'. Use POST /api/brief/generate/{brand} to create one.",
        )

    result = dict(row)
    if result.get("stats_json"):
        result["stats"] = json.loads(result.pop("stats_json"))

    return result
