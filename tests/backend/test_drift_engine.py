"""Headless validation for T-002 Drift Detection Engine."""
import asyncio
from backend.services.drift_service import DriftDetectionService


async def run_drift_tests():
    svc = DriftDetectionService()
    print("=== Drift Detection Engine Tests ===\n")

    # Test 1: No drift - single symptom
    r = await svc.detect_drift(["cough"], previous_severity="green")
    print("Test 1 (no drift, single symptom):")
    print(f"  drift_detected={r['drift_detected']}, type={r['drift_type']}, sev={r['new_severity']}")
    assert r["drift_detected"] == False
    assert r["new_severity"] == "green"

    # Test 2: Same-category worsening - 2 respiratory symptoms
    r = await svc.detect_drift(["cough", "wheezing"], previous_severity="green")
    print("\nTest 2 (same-category worsening):")
    print(f"  drift_detected={r['drift_detected']}, type={r['drift_type']}, sev={r['new_severity']}")
    assert r["drift_detected"] == True
    assert r["drift_type"] == "worsening"
    assert r["new_severity"] == "yellow"

    # Test 3: Cross-category drift - respiratory then general
    # (dizziness is neurological but not in CRITICAL set)
    r = await svc.detect_drift(["cough", "fever", "dizziness"], previous_severity="green")
    print("\nTest 3 (cross-category: respiratory -> neurological):")
    print(f"  drift_detected={r['drift_detected']}, type={r['drift_type']}, risk={r['escalation_risk']}")
    print(f"  sev: {r['previous_severity']} -> {r['new_severity']}")
    assert r["drift_detected"] == True
    assert r["drift_type"] == "new_category"
    assert r["new_severity"] in ("yellow", "red")

    # Test 4: Critical symptom - immediate CRITICAL
    r = await svc.detect_drift(["cough", "not breathing"], previous_severity="green")
    print("\nTest 4 (critical symptom):")
    print(f"  drift_detected={r['drift_detected']}, type={r['drift_type']}, sev={r['new_severity']}")
    assert r["drift_detected"] == True
    assert r["drift_type"] == "critical"
    assert r["new_severity"] == "critical"

    # Test 5: Symptom count increase (>3)
    r = await svc.detect_drift(["cough", "fever", "fatigue", "headache"], previous_severity="green")
    print("\nTest 5 (count increase, 4 symptoms):")
    print(f"  drift_detected={r['drift_detected']}, type={r['drift_type']}, sev={r['new_severity']}")
    assert r["drift_detected"] == True
    assert r["drift_type"] == "count_increase"
    assert r["new_severity"] == "yellow"

    # Test 6: Progressive escalation - RED previous goes to CRITICAL
    r = await svc.detect_drift(["chest pain", "palpitations"], previous_severity="red")
    print("\nTest 6 (progressive escalation from RED):")
    print(f"  sev: {r['previous_severity']} -> {r['new_severity']}")
    assert r["new_severity"] == "critical"

    # Test 7: Human-readable reason
    r = await svc.detect_drift(["cough", "wheezing"], previous_severity="green")
    print("\nTest 7 (reason string):")
    print(f"  reason: {r['reason']}")
    assert len(r["reason"]) > 10
    assert "respiratory" in r["reason"].lower()

    # Test 8: Dict shape validation
    required = {
        "drift_detected", "drift_type", "escalation_risk",
        "previous_severity", "new_severity", "reason",
        "symptom_count", "categories_involved",
    }
    assert set(r.keys()) == required, f"Missing: {required - set(r.keys())}"
    print("\nTest 8 (dict shape): OK")

    # Test 9: No symptoms
    r = await svc.detect_drift([], previous_severity="green")
    print("\nTest 9 (empty symptoms):")
    print(f"  drift_detected={r['drift_detected']}, reason={r['reason']}")
    assert r["drift_detected"] == False
    assert r["new_severity"] == "green"

    # Test 10: Cardiac symptom with other symptoms triggers new_category
    # (single chest pain alone is baseline, not drift — handled by risk scorer)
    r = await svc.detect_drift(["fever", "chest pain"], previous_severity="green")
    print("\nTest 10 (general -> cardiac = new_category):")
    print(f"  type={r['drift_type']}, sev={r['new_severity']}, risk={r['escalation_risk']}")
    assert r["drift_detected"] == True
    assert r["drift_type"] == "new_category"
    assert r["escalation_risk"] == "high"

    print("\n=== All 10 tests PASSED ===")


if __name__ == "__main__":
    asyncio.run(run_drift_tests())
