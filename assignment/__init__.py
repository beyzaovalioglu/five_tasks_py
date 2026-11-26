import random
from itertools import permutations

from otree.api import *
import payment_rules
from catalog import TASK_NAMES


class C(BaseConstants):
    NAME_IN_URL = 'assignment'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


def creating_session(subsession):
    tasks = list(TASK_NAMES)

    for player in subsession.get_players():
        participant = player.participant

        # Draw two distinct tasks in the order this participant will see them.
        participant.task_order = random.sample(tasks, 2)

        # Assign the condition with equal probability.
        participant.condition = random.choice(['endogenous', 'exogenous'])

        # Assign Low, High, or Choice with probabilities 25%, 50%, and 25%.
        participant.treatment = random.choices(
            ['low', 'high', 'choice'],
            weights=[1, 2, 1],
        )[0]

# def creating_session(subsession):
#     tasks = list(TASK_NAMES)
#     assignment_block = []
#
#     players = sorted(subsession.get_players(), key=lambda p: p.id_in_subsession)
#     for player in players:
#         participant = player.participant
#
#         # Each participant independently gets two tasks in random order.
#         participant.task_order = random.sample(tasks, 2)
#
#         # Prepare eight assignments whenever the previous block runs out.
#         if not assignment_block:
#             assignment_block = [
#                 ('endogenous', 'low'),
#                 ('endogenous', 'high'),
#                 ('endogenous', 'high'),
#                 ('endogenous', 'choice'),
#                 ('exogenous', 'low'),
#                 ('exogenous', 'high'),
#                 ('exogenous', 'high'),
#                 ('exogenous', 'choice'),
#             ]
#             random.shuffle(assignment_block)
#
#         # Take one pair and remove it from the block.
#         participant.condition, participant.treatment = assignment_block.pop()


class Welcome(Page):
    @staticmethod
    def vars_for_template(player):
        first, second = player.participant.task_order
        return dict(first=TASK_NAMES[first], second=TASK_NAMES[second],
                    endowment=payment_rules.ENDOWMENT, click=payment_rules.CORRECT_DECISION,
                    forecast=payment_rules.MAX_FORECAST_BONUS)


page_sequence = [Welcome]
