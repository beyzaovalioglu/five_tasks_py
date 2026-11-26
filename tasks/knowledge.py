import csv
from pathlib import Path

OPTIONS = ['A', 'B', 'C', 'D']


def load_questions():
    path = Path(__file__).with_name('data') / 'knowledge.csv'
    with path.open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 10 or [row['id'] for row in rows] != [f'GK{i:02d}' for i in range(1, 11)]:
        raise ValueError('Expected exactly GK01 through GK10 in knowledge.csv.')
    for row in rows:
        if any(row[field] for field in ['question', *OPTIONS, 'key']):
            if not all(row[field].strip() for field in ['question', *OPTIONS]) or row['key'] not in OPTIONS:
                raise ValueError(f"Incomplete question or invalid answer key: {row['id']}")
    return rows


QUESTIONS = load_questions()


def setup(player):
    row = QUESTIONS[player.task_round - 1]
    player.item_id = row['id']
    player.practice_item = not bool(row['question'])
    player.question_text = row['question'] or 'Practice item: select option A to test the response form.'
    player.answer_key = row['key'] or 'A'
    for key in OPTIONS:
        setattr(player, 'option_' + key.lower(), row[key] or f'Option {key}')
