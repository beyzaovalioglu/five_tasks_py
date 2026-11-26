import random

from otree.api import *
import payment_rules
from catalog import TASK_NAMES
from . import animals, colours, shapes, urns, knowledge


OPTIONS = {
    'animals': animals.OPTIONS,
    'colours': colours.OPTIONS,
    'shapes': shapes.OPTIONS,
}


class C(BaseConstants):
    MPL_PRICES = [0, 1, 2, 3, 4]
    AVERAGE_INFO_CONDITION = 'exogenous'
    NAME_IN_URL = 'tasks'
    PLAYERS_PER_GROUP = None
    ROUNDS_PER_TASK = 10
    NUM_ROUNDS = 2 * ROUNDS_PER_TASK


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    task = models.StringField()
    position = models.IntegerField()
    task_round = models.IntegerField()
    # MPL rows and the resulting task-level allocation are saved on task round 1.
    row_1 = models.StringField(choices=['Example', 'No example'])
    row_2 = models.StringField(choices=['Example', 'No example'])
    row_3 = models.StringField(choices=['Example', 'No example'])
    row_4 = models.StringField(choices=['Example', 'No example'])
    row_5 = models.StringField(choices=['Example', 'No example'])
    selected_row = models.IntegerField()
    selected_price = models.IntegerField()
    learning_level = models.StringField()
    demo_cost = models.IntegerField(initial=0)
    # Populated only on the final round of each task, after both tasks finish.
    paid_round = models.IntegerField()
    paid_belief = models.StringField()
    paid_forecast = models.FloatField()
    forecast_target_score = models.FloatField()
    paid_round_score = models.FloatField()
    decision_bonus = models.CurrencyField()
    belief_bonus = models.CurrencyField()
    payment_endowment = models.CurrencyField()
    payment_cost = models.CurrencyField()
    target = models.StringField()
    answer = models.StringField()
    correct = models.BooleanField()
    score = models.FloatField()
    left_red = models.IntegerField()
    right_red = models.IntegerField()
    source_left = models.BooleanField()
    ball = models.StringField()
    posterior = models.FloatField()
    probability_left = models.FloatField(min=0, max=100, label='Probability that your ball came from the left (red-majority) urn, in percent')
    example_left_red_guess = models.IntegerField(
        min=6,
        max=10,
        label=(
            'How many of the 10 balls do you think were red '
            'in the example participant’s red-majority urn?'
        ),
    )

    example_total_correct_guess = models.IntegerField(
        min=0,
        max=10,
        label=(
            'How many of the 10 general-knowledge questions '
            'do you think the example participant answered correctly?'
        ),
    )
    item_id = models.StringField()
    practice_item = models.BooleanField()
    question_text = models.StringField()
    answer_key = models.StringField()
    option_a = models.StringField()
    option_b = models.StringField()
    option_c = models.StringField()
    option_d = models.StringField() 
    knowledge_answer = models.StringField(widget=widgets.RadioSelect)
    initial_r5 = models.FloatField(min=0, label='Prediction for round 5')
    initial_r10 = models.FloatField(min=0, label='Prediction for round 10')
    updated_r10 = models.FloatField(min=0, label='Updated prediction for round 10')


def forecast_limit(player):
    return payment_rules.URN_MAX if player.task == 'urns' else 100


initial_r5_max = initial_r10_max = updated_r10_max = forecast_limit


def knowledge_answer_choices(player):
    return [(key, getattr(player, 'option_' + key.lower())) for key in knowledge.OPTIONS]



def creating_session(subsession):
    block, offset = divmod(subsession.round_number - 1, C.ROUNDS_PER_TASK)
    for player in subsession.get_players():
        player.task = player.participant.task_order[block]
        player.position = block + 1
        player.task_round = offset + 1
        if offset == 0 and player.participant.treatment != 'choice':
            player.learning_level = player.participant.treatment
        if player.task == 'urns':
            urns.setup(player)
        elif player.task == 'knowledge':
            knowledge.setup(player)
        else:
            player.target = random.choice(OPTIONS[player.task])


def answer_choices(player):
    return OPTIONS[player.task]


class Instructions(Page):
    @staticmethod
    def is_displayed(player):
        return player.task_round == 1


def requires_mpl(player):
    return player.task_round == 1 and (
        player.position == 1 or player.participant.treatment == 'choice'
    )


def block_start(player):
    return player.in_round(player.round_number - player.task_round + 1)


class MPL(Page):
    form_model = 'player'
    form_fields = ['row_1', 'row_2', 'row_3', 'row_4', 'row_5']
    is_displayed = staticmethod(requires_mpl)

    @staticmethod
    def vars_for_template(player):
        rows = [dict(field=f'row_{i}', price=price)
                for i, price in enumerate(C.MPL_PRICES, start=1)]
        return dict(rows=rows, average_info=player.participant.condition == C.AVERAGE_INFO_CONDITION)

    @staticmethod
    def error_message(player, values):
        declined = False
        for field in MPL.form_fields:
            if values[field] == 'No example':
                declined = True
            elif declined and values[field] == 'Example':
                return 'After choosing no example, you cannot go back to example for a higher price.'
            
    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.participant.treatment == 'choice':
            player.selected_row = random.randint(1, len(C.MPL_PRICES))
            player.selected_price = C.MPL_PRICES[player.selected_row - 1]
            buy = getattr(player, f'row_{player.selected_row}') == 'Example'
            player.learning_level = 'high' if buy else 'low'
            player.demo_cost = player.selected_price if buy else 0


class TreatmentReveal(Page):
    @staticmethod
    def is_displayed(player):
        return player.task_round == 1


class InitialBeliefs(Page):
    template_name = 'tasks/Beliefs.html'
    form_model = 'player'
    form_fields = ['initial_r5', 'initial_r10']

    @staticmethod
    def is_displayed(player):
        return player.task_round == 1


class Decision(Page): #this is the placeholder decision page, delete it when we add tasks
    form_model = 'player'
    form_fields = ['answer']

    @staticmethod
    def is_displayed(player):
        return player.task in OPTIONS

    @staticmethod
    def vars_for_template(player):
        return dict(options=answer_choices(player), high=block_start(player).learning_level == 'high')

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.correct = player.answer == player.target
        player.score = int(player.correct)

class ExampleEstimate(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player):
        if player.participant.condition != 'endogenous':
            return False

        if block_start(player).learning_level != 'high':
            return False

        if player.task == 'knowledge':
            return player.task_round == 1

        return player.task == 'urns'

    @staticmethod
    def get_form_fields(player):
        if player.task == 'knowledge':
            return ['example_total_correct_guess']

        return ['example_left_red_guess']
    
class UrnDecision(Page):
    form_model = 'player'
    form_fields = ['probability_left']

    @staticmethod
    def is_displayed(player):
        return player.task == 'urns'

    @staticmethod
    def vars_for_template(player):
        return dict(
            jars=[
                urns.diagram('Left · red majority', player.left_red),
                urns.diagram('Right · blue majority', player.right_red),
            ],
            high=block_start(player).learning_level == 'high',
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.score = payment_rules.urn_score(
            player.probability_left, player.posterior
        )



class KnowledgeDecision(Page):
    form_model = 'player'
    form_fields = ['knowledge_answer']

    @staticmethod
    def is_displayed(player):
        return player.task == 'knowledge'

    @staticmethod
    def vars_for_template(player):
        return dict(high=block_start(player).learning_level == 'high')

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.correct = player.knowledge_answer == player.answer_key
        player.score = int(player.correct)


# Field name -> (round when reported, round whose click was predicted, display label)
FORECASTS = {
    'initial_r5': (1, 5, 'Initial forecast for round 5'),
    'initial_r10': (1, 10, 'Initial forecast for round 10'),
    'updated_r10': (5, 10, 'Updated forecast for round 10'),
}


def settle_task(rounds):
    last = rounds[-1]

    # If payment for this task was already calculated, keep the original draw.
    if last.field_maybe_none('payment_endowment') is not None:
        return

    # Ten round decisions and three belief reports give thirteen tickets.
    beliefs = list(FORECASTS)
    number_of_rounds = len(rounds)
    ticket = random.randint(1, number_of_rounds + len(beliefs))

    last.decision_bonus = 0
    last.belief_bonus = 0

    if ticket <= number_of_rounds:
        # Tickets 1–10 pay the decision in that round.
        decision = rounds[ticket - 1]
        last.paid_round = decision.task_round
        last.paid_round_score = decision.score

        if decision.task == 'urns':
            last.decision_bonus = decision.score
        else:
            last.decision_bonus = payment_rules.CORRECT_DECISION * decision.score

    else:
        # Tickets 11–13 pay one of the three belief reports.
        belief = beliefs[ticket - number_of_rounds - 1]
        reported_in, target_round, _ = FORECASTS[belief]

        report = getattr(rounds[reported_in - 1], belief)
        target_score = rounds[target_round - 1].score

        last.paid_belief = belief
        last.paid_forecast = report
        last.forecast_target_score = target_score
        win_probability = payment_rules.forecast_win_probability(
            report, target_score, last.task == 'urns'
        )

        if random.random() < win_probability:
            last.belief_bonus = payment_rules.MAX_FORECAST_BONUS
        else:
            last.belief_bonus = 0

    last.payment_endowment = payment_rules.ENDOWMENT
    last.payment_cost = rounds[0].demo_cost
    last.payoff = (
        last.payment_endowment
        + last.decision_bonus
        + last.belief_bonus
        - last.payment_cost
    )

class Feedback(Page):
    @staticmethod
    def vars_for_template(player):
        if player.task == 'urns':
            return dict(posterior_pct=round(100 * player.posterior, 2))
        return {}

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.round_number == C.NUM_ROUNDS:
            records = player.in_all_rounds()
            settle_task(records[:C.ROUNDS_PER_TASK])
            settle_task(records[C.ROUNDS_PER_TASK:])


class UpdatedBelief(Page):
    template_name = 'tasks/Beliefs.html'
    form_model = 'player'
    form_fields = ['updated_r10']

    @staticmethod
    def is_displayed(player):
        return player.task_round == 5


class Summary(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player):
        rows = []

        for last in [player.in_round(C.ROUNDS_PER_TASK), player]:
            start = last.round_number - C.ROUNDS_PER_TASK + 1
            records = player.in_rounds(start, last.round_number)

            paid_round = last.field_maybe_none('paid_round')
            paid_belief = last.field_maybe_none('paid_belief')

            rows.append(dict(
                name=TASK_NAMES[last.task],
                result=last,
                unit=' points' if last.task == 'urns' else '%',
                first=records[0],
                fifth=records[4],
                paid_decision=paid_round is not None,
                forecast=FORECASTS[paid_belief][2] if paid_belief else '',
            ))

        return dict(rows=rows, total=player.participant.payoff)


page_sequence = [
    Instructions,
    MPL,
    TreatmentReveal,
    InitialBeliefs,
    ExampleEstimate,
    UrnDecision,
    KnowledgeDecision,
    Decision,
    Feedback,
    UpdatedBelief,
    Summary,
]