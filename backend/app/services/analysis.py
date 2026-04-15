from __future__ import annotations

import random


class AnalysisService:
    """Analyse marketing video content and produce scores.

    In production this would call an LLM or custom model. Here we use
    deterministic-ish heuristics seeded by the content so demo runs are
    reproducible yet realistic.
    """

    @staticmethod
    def score_content(
        transcript_text: str = "",
        duration: float = 0.0,
        has_cta: bool | None = None,
    ) -> dict:
        rng = random.Random(hash(transcript_text) & 0xFFFFFFFF)
        words = transcript_text.lower().split()
        word_count = len(words)

        hook_keywords = {"hey", "stop", "wait", "watch", "incredible", "amazing", "secret"}
        hook_hits = sum(1 for w in words[:15] if w.strip(",.!?") in hook_keywords)
        hook_score = min(100.0, 50 + hook_hits * 12 + rng.uniform(0, 10))

        cta_keywords = {"link", "bio", "shop", "buy", "grab", "order", "click", "subscribe", "comment"}
        cta_hits = sum(1 for w in words if w.strip(",.!?") in cta_keywords)
        if has_cta is True:
            cta_hits += 3
        cta_score = min(100.0, 30 + cta_hits * 15 + rng.uniform(0, 8))

        ideal_pace = 150
        words_per_min = (word_count / max(duration, 1)) * 60 if duration else 140
        pace_diff = abs(words_per_min - ideal_pace) / ideal_pace
        pacing_score = max(20.0, 95 - pace_diff * 100 + rng.uniform(-5, 5))
        pacing_score = min(100.0, pacing_score)

        is_short = duration <= 60
        platform_fit_score = min(100.0, (85 if is_short else 65) + rng.uniform(0, 12))

        engagement_score = round(
            hook_score * 0.3 + cta_score * 0.2 + pacing_score * 0.25 + platform_fit_score * 0.25,
            1,
        )

        return {
            "hook_score": round(hook_score, 1),
            "cta_score": round(cta_score, 1),
            "pacing_score": round(pacing_score, 1),
            "platform_fit_score": round(platform_fit_score, 1),
            "engagement_score": round(engagement_score, 1),
        }

    @staticmethod
    def explain_scores(scores: dict) -> str:
        parts = []
        hook = scores.get("hook_score", 0)
        if hook >= 80:
            parts.append("Strong opening hook — the first 3 seconds grab attention effectively.")
        elif hook >= 60:
            parts.append("Decent hook but could be punchier. Try leading with a bold claim or question.")
        else:
            parts.append("Weak hook — consider starting with a surprising stat or emotional statement.")

        cta = scores.get("cta_score", 0)
        if cta >= 75:
            parts.append("Clear call-to-action present. Viewers know what to do next.")
        else:
            parts.append("CTA is missing or unclear. Add a direct instruction like 'Link in bio' or 'Comment below'.")

        pacing = scores.get("pacing_score", 0)
        if pacing >= 80:
            parts.append("Pacing feels natural and keeps energy up throughout.")
        else:
            parts.append("Pacing could be tightened — cut dead air and keep cuts under 3 seconds.")

        platform = scores.get("platform_fit_score", 0)
        if platform >= 80:
            parts.append("Well-suited for short-form platforms (Reels, TikTok, Shorts).")
        else:
            parts.append("Consider trimming to under 60s and using vertical framing for better platform fit.")

        return " ".join(parts)

    @staticmethod
    def platform_recommendations(scores: dict, duration: float = 0.0) -> dict:
        recs: dict = {
            "tiktok": {"suitable": duration <= 60, "notes": "Keep under 60s for maximum reach."},
            "instagram_reels": {"suitable": duration <= 90, "notes": "90s max. Use trending audio."},
            "youtube_shorts": {"suitable": duration <= 60, "notes": "Vertical 9:16. Strong first frame."},
            "youtube_long": {"suitable": duration > 60, "notes": "Add chapters and end screen."},
        }
        return recs
