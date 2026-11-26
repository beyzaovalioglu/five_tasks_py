# Five-task learning study

An oTree experiment on how people use examples from another participant. Each participant completes two distinct tasks drawn in random order from a pool of five. Each task lasts ten rounds. The demo uses hypothetical points and placeholders for pre-experiment responses.

## Run the demo

Download and extract the repository. Open a terminal in the folder containing `settings.py`, activate your oTree virtual environment, and run:

```sh
python -m pip install -r requirements.txt
otree devserver
```

Open the local address printed in the terminal and select **Five-task study — random assignment**. To run the participant bots, use `otree test click_demo` from the same project folder. A random demo run can cover only a subset of the 20 possible task orders.

## Assignment and participant flow

The `assignment` app selects the task order, condition (endogenous or exogenous), and treatment (Low, High, or Choice). The target proportions are 50/50 for condition and 25/50/25 for Low, High, and Choice. Condition and assigned treatment carry across both tasks. A Choice participant can buy example access for one task and decline it for the other.

1. **Instructions and example prices.** After the first task’s instructions, everyone completes a multiple price list (MPL) for access to an example in each of its ten rounds. The five prices are 0, 1, 2, 3, and 4 points. Once a participant selects **No example**, all higher prices must also receive **No example**. Accepting all five prices or declining all five is allowed. The exogenous MPL explains that the example comes from an average performer.
2. **Treatment reveal.** High participants receive examples and Low participants proceed without them. For Choice, one MPL row is drawn uniformly. Accepting that row gives access and costs the selected price once for the whole task. Declining gives no access and costs zero. Only Choice participants can incur an MPL cost.
3. **Own-performance forecasts.** Before round 1, participants predict their performance in rounds 5 and 10. After round 5 feedback and before round 6, they update their round 10 forecast. In urns, a forecast is an expected accuracy score from 0 to 2. In the other tasks it is a 0–100% chance of answering the specified round correctly.
4. **Decisions and feedback.** Participants complete one decision per round and receive feedback on their own performance. Example access and condition determine what information appears before each decision, as described below.
5. **Second task and payment.** The second task starts with new instructions. Only Choice participants repeat the MPL, with a fresh binding draw. The same forecast and decision schedule applies. After both tasks finish, participants see a payment summary for each task.

## Tasks and examples

**Two urns.** Each round has two ten-ball urns. The left urn has a red majority and the right a blue majority. Compositions vary by round and are set in `tasks/urns.py`. The computer selects the source urn with equal probability, independently each round, and draws one ball. Participants see illustrations of their own two urns and report a 0–100% probability that the ball came from the left urn.

With equal priors, the correct posterior is L/(L+R), where L and R are the probabilities of drawing the observed colour from the left and right urns. The round score is 2 × (1 − squared error), rounded to two decimal places, using the report and posterior on a 0–1 scale. For example, after a red draw from a pair with 7/10 and 3/10 red balls, the posterior is 0.70. A report of 50% earns 1.92 points. Round feedback shows the participant’s posterior benchmark and score.

**General knowledge.** Enter ten questions in `tasks/data/knowledge.csv`, keeping IDs GK01–GK10 in order. Each row contains the question, options A–D, and the correct option’s letter in `key`. A blank item produces a scored practice prompt, flagged by `practice_item` in the export. After editing the bank, restart the server and create a fresh session.

**Colours, Shapes, and Animals.** These are click tasks for demonstrating the experiment flow. The participant clicks the named option. The option lists live in `tasks/colours.py`, `tasks/shapes.py`, and `tasks/animals.py`.

### What participants see when they have example access

| Task | Endogenous condition | Exogenous condition |
|---|---|---|
| Two urns | Each round, the participant sees the example person’s draw and prediction, then estimates how many red balls were in that person’s red-majority urn. They submit the estimate before their own decision. The example urn compositions stay hidden. | The example panel shows both example urn compositions, the draw, and the example person’s prediction. |
| General knowledge | Once, before seeing **any** example answers, the participant estimates how many of the ten questions the example person answered correctly. They then see the corresponding answer each round. The example person’s total stays hidden. | Each round, the participant sees the example person’s answer and their total correct out of ten. The panel gives no item-level correctness label. |

The demo leaves the example responses and disclosures as placeholders. When real histories are available, use the selected pre-experiment participant’s round-matched data in `ExampleEstimate.html`, `UrnDecision.html`, and `KnowledgeDecision.html`. The urn diagrams on the decision page represent the current participant’s own urns. The two endogenous estimates about another participant are recorded separately from the three own-performance forecasts.

## Payment

After overall round 20, the computer draws **one item per task**. Each of the ten decisions and three own-performance forecasts has a **1/13** chance. The two task draws are independent. The estimates about the example participant are outside this draw.

| Selected item | Bonus for that task |
|---|---|
| Urn decision | The participant earns the selected round’s urn accuracy score directly. |
| Knowledge or click decision | A correct response earns 2 points. An incorrect response earns 0. |
| Own-performance forecast | Accuracy sets the probability of winning a fixed 2-point prize. The participant receives either 2 points or 0. |

For a selected forecast, the probability of winning is **1 − error²**. For knowledge and click tasks, error equals the forecast percentage divided by 100 minus the actual outcome (1 if correct, 0 otherwise). For urns, error equals (forecast score − actual round score)/2. For example, forecasting an 80% chance of a correct knowledge answer and then answering correctly gives a 96% chance of winning the 2-point prize.

**Task payment = 4-point endowment + bonus from the selected item − applicable MPL cost.** A lost forecast lottery gives zero bonus. The endowment and any Choice cost still apply. Total payment is the sum of the two task payments.

## Code and export

| Location | Purpose |
|---|---|
| `settings.py`, `catalog.py` | Session configuration and list of eligible tasks. |
| `assignment/__init__.py` | Assignment of task order, condition, and treatment. |
| `tasks/__init__.py` | Player fields, page order, example access, round setup, and payment draws in `settle_task`. |
| `payment_rules.py` | Payment amounts, urn scoring, and forecast prize probability. |
| `tasks/*.html` | Participant pages, example panels, urn illustration, feedback, and payment summary. |
| `assignment/tests.py`, `tasks/tests.py` | Participant bots for checking assignment, page flow, and payment outcomes. |

In the tasks export, use `task`, `position`, and `task_round` to identify the task and round. Urn records include `left_red`, `right_red`, `ball`, `source_left`, `probability_left` (percent), `posterior` (0–1), and `score`. Knowledge records include `item_id`, `practice_item`, `knowledge_answer`, `answer_key`, and `correct`. The endogenous estimates are `example_left_red_guess` and `example_total_correct_guess`.

Own-performance forecasts `initial_r5` and `initial_r10` are stored on task round 1, and `updated_r10` on task round 5. Task payments are stored on overall rounds 10 and 20. Use `paid_round` or `paid_belief` to identify the selected item, even when the bonus is zero. For a selected forecast, `paid_forecast` and `forecast_target_score` record the prediction and outcome. The realized amounts are in `payment_endowment`, `decision_bonus`, `belief_bonus`, `payment_cost`, and `payoff`.
