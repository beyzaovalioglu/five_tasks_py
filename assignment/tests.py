from otree.api import Bot
from catalog import TASK_NAMES
from . import Welcome


class PlayerBot(Bot):
    def play_round(self):
        assignment = self.player.participant
        assert len(set(assignment.task_order)) == 2
        assert set(assignment.task_order) <= set(TASK_NAMES)
        assert assignment.treatment in ['low', 'high', 'choice']
        assert assignment.condition in ['endogenous', 'exogenous']
        yield Welcome
