import read, copy
from util import *
from logical_classes import *

verbose = 0

class KnowledgeBase(object):
    def __init__(self, facts=[], rules=[]):
        self.facts = facts
        self.rules = rules
        self.ie = InferenceEngine()

    def __repr__(self):
        return 'KnowledgeBase({!r}, {!r})'.format(self.facts, self.rules)

    def __str__(self):
        string = "Knowledge Base: \n"
        string += "\n".join((str(fact) for fact in self.facts)) + "\n"
        string += "\n".join((str(rule) for rule in self.rules))
        return string

    def _get_fact(self, fact):
        """INTERNAL USE ONLY
        Get the fact in the KB that is the same as the fact argument

        Args:
            fact (Fact): Fact we're searching for

        Returns:
            Fact: matching fact
        """
        for kbfact in self.facts:
            if fact == kbfact:
                return kbfact

    def _get_rule(self, rule):
        """INTERNAL USE ONLY
        Get the rule in the KB that is the same as the rule argument

        Args:
            rule (Rule): Rule we're searching for

        Returns:
            Rule: matching rule
        """
        for kbrule in self.rules:
            if rule == kbrule:
                return kbrule

    def kb_add(self, fact_rule):
        """Add a fact or rule to the KB
        Args:
            fact_rule (Fact|Rule) - the fact or rule to be added
        Returns:
            None
        """
        printv("Adding {!r}", 1, verbose, [fact_rule])
        if isinstance(fact_rule, Fact):
            if fact_rule not in self.facts:
                self.facts.append(fact_rule)
                for rule in self.rules:
                    self.ie.fc_infer(fact_rule, rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.facts.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.facts[ind].supported_by.append(f)
                else:
                    ind = self.facts.index(fact_rule)
                    self.facts[ind].asserted = True
        elif isinstance(fact_rule, Rule):
            if fact_rule not in self.rules:
                self.rules.append(fact_rule)
                for fact in self.facts:
                    self.ie.fc_infer(fact, fact_rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.rules.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.rules[ind].supported_by.append(f)
                else:
                    ind = self.rules.index(fact_rule)
                    self.rules[ind].asserted = True

    def kb_assert(self, fact_rule):
        """Assert a fact or rule into the KB

        Args:
            fact_rule (Fact or Rule): Fact or Rule we're asserting
        """
        printv("Asserting {!r}", 0, verbose, [fact_rule])
        self.kb_add(fact_rule)

    def kb_ask(self, fact):
        """Ask if a fact is in the KB

        Args:
            fact (Fact) - Statement to be asked (will be converted into a Fact)

        Returns:
            listof Bindings|False - list of Bindings if result found, False otherwise
        """
        print("Asking {!r}".format(fact))
        if factq(fact):
            f = Fact(fact.statement)
            bindings_lst = ListOfBindings()
            # ask matched facts
            for fact in self.facts:
                binding = match(f.statement, fact.statement)
                if binding:
                    bindings_lst.add_bindings(binding, [fact])

            return bindings_lst if bindings_lst.list_of_bindings else []

        else:
            print("Invalid ask:", fact.statement)
            return []

    def kb_retract(self, fact_or_rule):
        """Retract a fact from the KB

        Args:
            fact (Fact) - Fact to be retracted

        Returns:
            None
        """
        printv("Retracting {!r}", 0, verbose, [fact_or_rule])
        ####################################################
        # Student code goes here
        if isinstance(fact_or_rule, Fact):
            # print(fact_or_rule.statement)
            # print(fact_or_rule.supported_by == [])
            real_fact = fact_or_rule
            # print("WOWOWOWOW")
            # print(fact_or_rule)
            for f in self.facts:
                if (f.statement == fact_or_rule.statement):
                    real_fact = f

            if ( (real_fact.supported_by) == [] ):
                # print(fact_or_rule.statement)

                supported_facts = real_fact.supports_facts
                supported_rules = real_fact.supports_rules

                self.facts.remove(real_fact)

                for f in supported_facts:
                    for s in f.supported_by:
                        if s[0] == real_fact:
                            f.supported_by.remove(s)
                    self.kb_retract(f)


class InferenceEngine(object):
    def fc_infer(self, fact, rule, kb):
        # """Forward-chaining to infer new facts and rules
        #
        # Args:
        #     fact (Fact) - A fact from the KnowledgeBase
        #     rule (Rule) - A rule from the KnowledgeBase
        #     kb (KnowledgeBase) - A KnowledgeBase
        #
        # Returns:
        #     Nothing
        # """
        printv('Attempting to infer from {!r} and {!r} => {!r}', 1, verbose,
            [fact.statement, rule.lhs, rule.rhs])
        ####################################################
        # Student code goes here
        bindings = match(fact.statement, rule.lhs[0])

        if ( bindings != False ):

            # If there are more than one, create a new rule
            if (len(rule.lhs) > 1):
                rules = [[],rule.rhs]
                for r in rule.lhs:
                    if ( not factq(instantiate(r, bindings)) ):
                        rules[0].append(instantiate(r, bindings))
                rules[1] = instantiate(rule.rhs, bindings)

                # Delete any lhs that are fully bound
                for r in rules[0]:
                    count = 0
                    for t in r.terms:
                        if is_var(t):
                            count+=1
                    if (count == 0):
                        rules[0].remove(r)

                new_rule = Rule(rules, [])

                if (new_rule in kb.rules):
                    return
                else:
                    new_rule.supported_by.append([fact, rule])
                    rule.supports_rules.append(new_rule)
                    fact.supports_rules.append(new_rule)

                    kb.kb_add(new_rule)

                # Use this rule to infer with other facts
                for f in kb.facts:
                    self.fc_infer(f, new_rule, kb)
            # Otherwise, this is a new fact
            else:
                new_rule = instantiate(rule.rhs, bindings)
                new_fact = Fact(new_rule, [])

                if (new_fact in kb.facts):
                    return
                else:
                    # print(fact.statement)
                    # if (str(fact.statement) == "(motherof ada bing)"):

                        # for f in fact.supports_facts:
                        #     print ("HERE")
                        #     print(f.statement)
                            # print(rule)
                        # print (fact.supports_facts)

                    # print("NEW FACT" + str(new_fact.statement))
                    new_fact.supported_by.append([fact, rule])
                    rule.supports_facts.append(new_fact)
                    fact.supports_facts.append(new_fact)

                    # if (str(fact.statement) == "(motherof ada bing)"):
                    #     print ("HERE")
                    #     for f in fact.supports_facts:
                    #         print(f.statement)
                        # print (fact.supports_f

                    kb.kb_add(new_fact)
