from os import environ

SESSION_CONFIGS = [
    dict(name='click_demo', display_name='Five-task study — random assignment',
         app_sequence=['assignment', 'tasks'], num_demo_participants=10),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = ['task_order', 'condition', 'treatment']
SESSION_FIELDS = []

#ROOMS = [
#    dict(name='learning_study', display_name='Learning study'),
#]

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = True
POINTS_DECIMAL_PLACES = 2

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '7222042702994'
