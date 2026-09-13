# logic_engine.py


class KnowledgeBase:
    """
    Stores facts and Horn-clause rules
    and performs forward chaining.
    """

    def __init__(self):

        # Unique known facts
        self.facts = set()

        # Each rule is stored as:
        # (premises, conclusion)
        self.rules = []

    # =====================================================
    # ADD FACT
    # =====================================================
    def tell_fact(self, fact_string):

        self.facts.add(fact_string)

    # =====================================================
    # ADD RULE
    # =====================================================
    def tell_rule(self, premise_list, conclusion_string):

        self.rules.append(
            (
                premise_list,
                conclusion_string
            )
        )

    # =====================================================
    # CLEAR CURRENT FACTS
    # =====================================================
    def clear_facts(self):

        self.facts.clear()

    # =====================================================
    # FORWARD CHAINING
    # =====================================================
    def forward_chain(self):

        new_facts_added = True

        while new_facts_added:

            new_facts_added = False

            for premises, conclusion in self.rules:

                # Only infer the conclusion
                # if it is not already known.
                if conclusion not in self.facts:

                    # Modus Ponens:
                    # All premises must already be true.
                    if all(
                        premise in self.facts
                        for premise in premises
                    ):

                        self.facts.add(
                            conclusion
                        )

                        new_facts_added = True