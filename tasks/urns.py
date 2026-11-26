import random

# (red balls in the left urn, red balls in the right urn); 10 balls per urn.
RED_COUNTS = [(7, 3), (8, 4), (6, 2), (9, 3), (7, 1),
              (8, 2), (6, 4), (9, 1), (7, 4), (8, 3)]
SIZE = 10


def setup(player):
    left, right = RED_COUNTS[player.task_round - 1]
    player.left_red = left
    player.right_red = right
    player.source_left = random.choice([True, False])
    red_count = left if player.source_left else right
    player.ball = 'Red' if random.randrange(SIZE) < red_count else 'Blue'
    left_likelihood, right_likelihood = (left, right) if player.ball == 'Red' else (SIZE-left, SIZE-right)
    player.posterior = left_likelihood / (left_likelihood + right_likelihood)


def diagram(label, red):
    # Fixed positions let the drawing show the exact count, including on narrow screens.
    points = [(41, 58), (64, 58), (87, 58), (30, 82), (53, 82), (76, 82),
              (99, 82), (41, 106), (64, 106), (87, 106)]
    balls = [dict(x=x, y=y, red=i < red) for i, (x, y) in enumerate(points)]
    return dict(label=label, red=red, blue=SIZE-red, balls=balls)
