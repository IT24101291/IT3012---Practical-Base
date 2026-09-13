# test_logic.py

from logic_engine import KnowledgeBase


def test_forward_chaining():

    kb = KnowledgeBase()

    # =====================================================
    # DOMAIN RULES
    # =====================================================

    kb.tell_rule(
        ['TargetVisible', 'HasDust'],
        'SafeToEngage'
    )

    kb.tell_rule(
        ['SafeToEngage', 'BloodseekerMissing'],
        'Retreat'
    )

    # =====================================================
    # TEST CASE 1
    # Safe Engagement
    # =====================================================

    kb.clear_facts()

    kb.tell_fact(
        'TargetVisible'
    )

    kb.tell_fact(
        'HasDust'
    )

    kb.forward_chain()

    assert (
        'SafeToEngage'
        in kb.facts
    ), (
        "Test 1 Failed: "
        "Should deduce SafeToEngage"
    )

    assert (
        'Retreat'
        not in kb.facts
    ), (
        "Test 1 Failed: "
        "Should NOT deduce Retreat"
    )

    # =====================================================
    # TEST CASE 2
    # Unsafe Engagement
    # =====================================================

    kb.clear_facts()

    kb.tell_fact(
        'TargetVisible'
    )

    kb.tell_fact(
        'HasDust'
    )

    kb.tell_fact(
        'BloodseekerMissing'
    )

    kb.forward_chain()

    assert (
        'SafeToEngage'
        in kb.facts
    ), (
        "Test 2 Failed: "
        "Should deduce SafeToEngage"
    )

    assert (
        'Retreat'
        in kb.facts
    ), (
        "Test 2 Failed: "
        "Should deduce Retreat"
    )

    # =====================================================
    # TEST CASE 3
    # Missing Premise
    # =====================================================

    kb.clear_facts()

    kb.tell_fact(
        'TargetVisible'
    )

    kb.forward_chain()

    assert (
        'SafeToEngage'
        not in kb.facts
    ), (
        "Test 3 Failed: "
        "HasDust is missing, so "
        "SafeToEngage must not be inferred"
    )

    print(
        "All Logic Engine Test Cases Passed!"
    )


if __name__ == "__main__":

    test_forward_chaining()