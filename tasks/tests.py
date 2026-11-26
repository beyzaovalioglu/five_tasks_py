from otree.api import Bot, SubmissionMustFail
from . import (Instructions, MPL, TreatmentReveal, InitialBeliefs, UrnDecision,
               KnowledgeDecision, Decision, Feedback, UpdatedBelief, Summary, OPTIONS, ExampleEstimate
            )
from otree.api import Bot, SubmissionMustFail
import payment_rules

class PlayerBot(Bot):
    def play_round(self):
        p = self.player
        block, offset = divmod(p.round_number - 1, 10)
        arm = p.participant.treatment
        high = arm == 'high' or (arm == 'choice' and block == 0)
        assert p.task == p.participant.task_order[block] and p.task_round == offset + 1
        is_urn = p.task == 'urns'
        if offset == 0:
            yield Instructions
            if block == 0 or arm == 'choice':
                assert ('from an average performer' in self.html) == (p.participant.condition == 'exogenous')
                selection = 'Example' if block == 0 else 'No example'
                yield MPL, {f'row_{i}': selection for i in range(1, 6)}
            yield TreatmentReveal
            yield SubmissionMustFail(InitialBeliefs, {'initial_r5': 3 if is_urn else 101, 'initial_r10': 1})
            yield InitialBeliefs, dict(initial_r5=1.4 if is_urn else 50, initial_r10=1.8 if is_urn else 70)
        if high and p.participant.condition == 'endogenous':
            if p.task == 'urns':
                yield ExampleEstimate, dict(example_left_red_guess=7)
            elif p.task == 'knowledge' and p.task_round == 1:
                assert 'Example participant’s answer:' not in self.html
                yield ExampleEstimate, dict(example_total_correct_guess=6)

        assert ('Pre-experiment example' in self.html) == high

        show_example_details = high and p.participant.condition == 'exogenous'

        if p.task == 'urns':
            assert ('Example left urn:' in self.html) == show_example_details
            assert ('Example right urn:' in self.html) == show_example_details
        elif p.task == 'knowledge':
            assert ('Example participant’s answer:' in self.html) == high
            assert ('Across all 10 questions' in self.html) == show_example_details
        if is_urn:
            assert self.html.count('<circle ') == 20
            fields = dict(probability_left=50)
            yield SubmissionMustFail(UrnDecision, dict(fields, probability_left=101))
            yield UrnDecision, fields
            assert 'Accuracy score' in self.html
        elif p.task == 'knowledge':
            yield KnowledgeDecision, dict(knowledge_answer='B' if offset == 0 else 'A')
        else:
            yield Decision, dict(answer=p.target)
        yield Feedback
        if offset == 4:
            yield UpdatedBelief, dict(updated_r10=1.7 if is_urn else 80)
        if p.round_number == 20:
            for last in [p.in_round(10), p.in_round(20)]:
                paid_decision = last.field_maybe_none('paid_round') is not None
                paid_belief = last.field_maybe_none('paid_belief') is not None
                assert paid_decision != paid_belief
                if paid_belief:
                    assert last.belief_bonus in (0, payment_rules.MAX_FORECAST_BONUS)
            assert (
                self.html.count('Selected decision:')
                + self.html.count('Selected forecast:')
            ) == 2
            yield Summary
