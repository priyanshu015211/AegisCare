"""
backend/services/drift_service.py

Dynamic Emergency Drift Detection Engine (T-002)

Tracks symptom progression by category and detects emergency drift:
- NEW_CATEGORY: symptom appears in a new category (e.g. respiratory → cardiac)
- WORSENING: multiple symptoms in the same category
- CRITICAL: any critical symptom → immediate escalation
- COUNT_INCREASE: >3 symptoms → elevated risk
- NONE: no concerning changes

Severity escalation follows a progressive scale:
  GREEN → YELLOW → RED → CRITICAL

This is the core innovation of AegisCare — no competitor continuously
monitors symptom evolution within a session and auto-escalates based
on trajectory.
"""

from typing import Dict, List, Set, Tuple
from backend.core.constants import (
    SeverityLevel,
    RESPIRATORY_SYMPTOMS,
    CARDIAC_SYMPTOMS,
    NEUROLOGICAL_SYMPTOMS,
    CRITICAL_SYMPTOMS,
)
from backend.services.base_service import BaseService


# ------------------------------------------------------------------
# Severity escalation map
# ------------------------------------------------------------------
_SEVERITY_ORDER = [
    SeverityLevel.GREEN.value,
    SeverityLevel.YELLOW.value,
    SeverityLevel.RED.value,
    SeverityLevel.CRITICAL.value,
]

_SEVERITY_INDEX = {s: i for i, s in enumerate(_SEVERITY_ORDER)}


def _escalate(severity: str) -> str:
    """Escalate severity one level up.  CRITICAL stays CRITICAL."""
    idx = _SEVERITY_INDEX.get(severity, 0)
    return _SEVERITY_ORDER[min(idx + 1, len(_SEVERITY_ORDER) - 1)]


def _max_severity(a: str, b: str) -> str:
    """Return the more severe of two severity strings."""
    ia = _SEVERITY_INDEX.get(a, 0)
    ib = _SEVERITY_INDEX.get(b, 0)
    return a if ia >= ib else b


# ------------------------------------------------------------------
# Symptom → category mapping
# ------------------------------------------------------------------

# Build a reverse lookup: symptom → category name
_CATEGORY_MAP: Dict[str, str] = {}

for _s in RESPIRATORY_SYMPTOMS:
    _CATEGORY_MAP[_s] = "respiratory"
for _s in CARDIAC_SYMPTOMS:
    _CATEGORY_MAP[_s] = "cardiac"
for _s in NEUROLOGICAL_SYMPTOMS:
    _CATEGORY_MAP[_s] = "neurological"

# CRITICAL set includes cardiac + neurological, but we track the
# "pure" critical symptoms separately for clarity.
_CRITICAL_ONLY = frozenset({
    "not breathing", "no pulse", "unresponsive",
    "severe bleeding", "anaphylaxis",
})
for _s in _CRITICAL_ONLY:
    _CATEGORY_MAP[_s] = "critical"

# Catch-all for symptoms not in any category
_GENERAL = frozenset({
    "fever", "fatigue", "headache", "nausea", "vomiting",
    "diarrhea", "body aches", "sore throat", "runny nose",
    "chills", "loss of appetite", "abdominal pain",
    "muscle pain", "joint pain", "skin rash", "swelling", "bleeding",
    "dizziness",
})
for _s in _GENERAL:
    _CATEGORY_MAP.setdefault(_s, "general")


def _categorise(symptom: str) -> str:
    """Return the category for a symptom, or 'general' if unknown."""
    return _CATEGORY_MAP.get(symptom.lower().strip(), "general")


# ------------------------------------------------------------------
# DriftDetectionEngine (replaces placeholder)
# ------------------------------------------------------------------

class DriftDetectionService(BaseService):
    """
    Real drift detection engine.

    Call `detect_drift(symptoms_history, previous_severity)` after every
    symptom addition to determine whether the patient's condition is
    worsening.

    Returns a dict with:
        drift_detected, drift_type, escalation_risk,
        previous_severity, new_severity, reason,
        symptom_count, categories_involved
    """

    def __init__(self):
        super().__init__()

    async def process(self, *args, **kwargs) -> Dict:
        return await self.detect_drift(*args, **kwargs)

    async def detect_drift(
        self,
        symptoms_history: List[str],
        previous_severity: str = "green",
        **kwargs,
    ) -> Dict:
        """
        Analyse a list of symptoms (in chronological order) and detect
        whether the patient's condition has drifted from their previous
        severity level.

        Parameters
        ----------
        symptoms_history : list[str]
            All symptoms in chronological order (oldest first).
        previous_severity : str
            The patient's severity at the last check point.

        Returns
        -------
        dict with keys:
            drift_detected     : bool
            drift_type         : str  (new_category | worsening | critical | count_increase | none)
            escalation_risk    : str  (low | medium | high | critical)
            previous_severity  : str
            new_severity       : str
            reason             : str  (human-readable)
            symptom_count      : int
            categories_involved: list[str]
        """
        if not symptoms_history:
            return self._no_drift(previous_severity, "No symptoms reported.")

        normalised = [s.lower().strip() for s in symptoms_history]
        unique_symptoms = list(dict.fromkeys(normalised))  # preserve order, dedupe

        # ---- Categorise all symptoms ----
        categories_present: Dict[str, List[str]] = {}
        for s in unique_symptoms:
            cat = _categorise(s)
            categories_present.setdefault(cat, []).append(s)

        # ---- Check 1: TRULY CRITICAL symptom → immediate escalation ----
        # Only the life-threatening set triggers immediate critical.
        # Cardiac/neurological symptoms are high-risk but handled by
        # the category-based checks below (new_category / worsening).
        critical_found = [
            s for s in unique_symptoms
            if s in _CRITICAL_ONLY
        ]
        if critical_found:
            new_sev = SeverityLevel.CRITICAL.value
            return self._build_result(
                drift_detected=True,
                drift_type="critical",
                escalation_risk="critical",
                previous_severity=previous_severity,
                new_severity=new_sev,
                reason=(
                    f"Critical symptom(s) detected: {', '.join(critical_found)}. "
                    f"Immediate escalation required."
                ),
                symptom_count=len(unique_symptoms),
                categories=list(categories_present.keys()),
            )

        # ---- Check 2: NEW_CATEGORY — symptom in a category not seen before ----
        # Split the history into "before" (first half) and "after" (second half)
        # to detect category *introduction* during the session.
        mid = max(len(unique_symptoms) // 2, 1)
        first_half = unique_symptoms[:mid]
        second_half = unique_symptoms[mid:]

        cats_first = {_categorise(s) for s in first_half}
        cats_second = {_categorise(s) for s in second_half}

        new_cats = (cats_second - cats_first) - {"general"}
        if new_cats:
            # Determine the severity impact of the new category
            new_sev = _escalate(previous_severity)
            # Cardiac/neurological in a new category is especially dangerous
            high_risk_cats = {"cardiac", "neurological"}
            if new_cats & high_risk_cats:
                new_sev = _max_severity(new_sev, SeverityLevel.RED.value)
                risk = "high"
            else:
                risk = "medium"

            return self._build_result(
                drift_detected=True,
                drift_type="new_category",
                escalation_risk=risk,
                previous_severity=previous_severity,
                new_severity=new_sev,
                reason=(
                    f"New symptom category detected: {', '.join(sorted(new_cats))}. "
                    f"Patient previously only had {', '.join(sorted(cats_first - {'general'}))} symptoms."
                ),
                symptom_count=len(unique_symptoms),
                categories=list(categories_present.keys()),
            )

        # ---- Check 3: WORSENING — multiple symptoms in the same category ----
        for cat, syms in categories_present.items():
            if cat in ("general", "critical"):
                continue
            if len(syms) >= 2:
                new_sev = _escalate(previous_severity)
                return self._build_result(
                    drift_detected=True,
                    drift_type="worsening",
                    escalation_risk="medium",
                    previous_severity=previous_severity,
                    new_severity=new_sev,
                    reason=(
                        f"Worsening in {cat} category: {len(syms)} symptoms reported "
                        f"({', '.join(syms)})."
                    ),
                    symptom_count=len(unique_symptoms),
                    categories=list(categories_present.keys()),
                )

        # ---- Check 4: COUNT_INCREASE — more than 3 symptoms ----
        if len(unique_symptoms) > 3:
            new_sev = _escalate(previous_severity)
            return self._build_result(
                drift_detected=True,
                drift_type="count_increase",
                escalation_risk="medium",
                previous_severity=previous_severity,
                new_severity=new_sev,
                reason=(
                    f"Symptom count increased to {len(unique_symptoms)} "
                    f"(threshold: 3). Risk elevated."
                ),
                symptom_count=len(unique_symptoms),
                categories=list(categories_present.keys()),
            )

        # ---- No drift ----
        return self._no_drift(
            previous_severity,
            f"Stable. {len(unique_symptoms)} symptom(s) across "
            f"{len(categories_present)} categor{'y' if len(categories_present) == 1 else 'ies'}.",
            symptom_count=len(unique_symptoms),
            categories=list(categories_present.keys()),
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_result(
        drift_detected: bool,
        drift_type: str,
        escalation_risk: str,
        previous_severity: str,
        new_severity: str,
        reason: str,
        symptom_count: int,
        categories: List[str],
    ) -> Dict:
        return {
            "drift_detected": drift_detected,
            "drift_type": drift_type,
            "escalation_risk": escalation_risk,
            "previous_severity": previous_severity,
            "new_severity": new_severity,
            "reason": reason,
            "symptom_count": symptom_count,
            "categories_involved": categories,
        }

    @staticmethod
    def _no_drift(
        previous_severity: str,
        reason: str,
        symptom_count: int = 0,
        categories: List[str] = None,
    ) -> Dict:
        return {
            "drift_detected": False,
            "drift_type": "none",
            "escalation_risk": "low",
            "previous_severity": previous_severity,
            "new_severity": previous_severity,
            "reason": reason,
            "symptom_count": symptom_count,
            "categories_involved": categories or [],
        }
