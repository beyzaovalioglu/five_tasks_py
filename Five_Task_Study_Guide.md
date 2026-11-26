# Five task study maintainer guide

This guide follows one participant through the main experiment, then shows how to replace a click task with inventory, change assignment, and revise payment. File paths start in the project folder containing `settings.py`.

**Version.** The reference project is `five_task_study.zip`. Its settings include a two-person demo and an optional `check_orders` test configuration. The later settings shared for the study use a ten-person demo and omit that test configuration. Both use the same app sequence. The assignment rules below describe the supplied Python code. Balanced assignment is a separate option described below.

## 1. The participant’s path and the files behind it

Suppose a participant draws knowledge first and urns second. Overall rounds 1–10 are knowledge rounds 1–10. Overall rounds 11–20 are urn rounds 1–10. Each person has one stored task order, condition, and assigned treatment. Each round has its own decision and score.

| When | What happens |
|---|---|
| Entry | Assignment selects two tasks in order, a condition, and Low, High, or Choice treatment. Welcome names the two tasks. |
| Before the first task | Everyone sees that task’s instructions, completes the five-row MPL, learns their assigned treatment and access to examples, then predicts performance in rounds 5 and 10. Only exogenous participants see the average-performer sentence on the MPL. |
| Each decision | High learning shows the corresponding pre-experiment round before the participant answers. Low learning omits the example. The demo contains placeholders. Participants receive feedback on their own answer after each round. |
| Immediately after round 5 feedback | The participant updates their prediction for round 10, then proceeds to round 6. |
| Before the second task | Everyone sees the new instructions, reveal, and initial beliefs. Only Choice completes another MPL, with a fresh binding price draw before the reveal. The second task repeats the ten decisions and the round 5 belief update. |
| After round 20 feedback | The program draws one decision and one forecast report from each task. The summary shows both task payments and their sum. |

**Belief measure to confirm.** The current knowledge and click pages ask for the probability of being correct on a particular round (0–100%). The urn pages ask for that round’s accuracy score (0–2). If the study protocol calls for a cumulative number correct or a total accuracy score, change the question, bounds, scoring target, and payment rule together. Changing the wording alone would pay participants against a different outcome from the one they predicted.

### Project folder and assignment app

| File | Role in the study |
|---|---|
| `settings.py` | Runs the assignment app followed by the tasks app. Declares the participant fields that carry across rounds, the demo size, currency conversion, and participation fee. |
| `catalog.py` | Maps each eligible task identifier to its display name. Assignment samples from these identifiers. |
| `payment_rules.py` | Defines the endowment, bonuses, urn score, and forecast scoring formula. |
| `assignment/__init__.py` | Assigns the task order, condition, and treatment in `creating_session`. Supplies the Welcome page with task names and payment amounts. |
| `assignment/Welcome.html` | Tells participants their task order and explains the payment draws before they start. |
| `assignment/tests.py` | Simulates a participant entering the study. Checks that the two tasks are distinct and that task, condition, and treatment values are allowed. It does not test realized proportions. |

### Python files inside tasks

| File | Role in the study |
|---|---|
| `tasks/__init__.py` | Coordinates the 20 rounds. Defines per-round Player fields, prepares each exercise, routes participants to pages, records MPL and belief responses, scores decisions, and settles payment. Read its final line, `page_sequence`, to see the page order. |
| `tasks/urns.py` | Sets each round’s two urn compositions, draws the source urn and ball, calculates the correct posterior, and prepares the counts and positions for the illustration. |
| `tasks/knowledge.py` | Loads and validates the knowledge CSV. Copies the round’s question, four options, and key onto the participant’s record. Flags placeholder questions. |
| `tasks/animals.py` | Defines the available options for the animal click task. |
| `tasks/colours.py` | Defines the available options for the colour click task. |
| `tasks/shapes.py` | Defines the available options for the shape click task. |
| `tasks/tests.py` | Plays through both tasks as a bot. Checks page timing, inputs, example visibility, and the final summary. Update its decision branch when adding a task. |

**Question editing.** For new general-knowledge questions, edit only `tasks/data/knowledge.csv`. Keep IDs GK01–GK10 in order, enter the four answers in A–D, and enter the correct letter in `key`. Restart the app to reload the question bank and create a fresh test session. An empty question row produces a scored practice prompt that is eligible for payment.

### HTML files inside tasks

| File | What the participant sees |
|---|---|
| `tasks/Instructions.html` | Instructions for the current task at the beginning of its ten rounds. The final fallback describes a click task. |
| `tasks/MPL.html` | Five example prices, with Example or No example at each price. The optional average-performer sentence depends on the condition. |
| `tasks/TreatmentReveal.html` | Assigned condition and treatment, access to examples, and, for Choice, the drawn price and actual cost. |
| `tasks/Beliefs.html` | Both initial and updated belief forms. The wording and units depend on the task. |
| `tasks/Decision.html` | The generic click decision. Displays the named target and clickable answers. |
| `tasks/UrnDecision.html` | The two urns, observed ball, and probability input. High learning adds the example’s own compositions, draw and choice, plus a usefulness rating. |
| `tasks/UrnDiagram.html` | Draws one illustrated urn with the specified red and blue counts. Included twice by the urn decision page. |
| `tasks/KnowledgeDecision.html` | The question and four radio options. High learning also displays placeholders for the earlier participant’s answer and total score across ten questions. |
| `tasks/AssignmentLine.html` | A small shared template used by the click page to display “Task 1 of 2” or “Task 2 of 2”. |
| `tasks/Feedback.html` | The participant’s own result for the round. Urns show the posterior and accuracy score. Other tasks currently show correct or incorrect. |
| `tasks/Summary.html` | The forecasts, selected decision and belief, bonuses, cost, and total payment after both tasks finish. |

## 2. Replacing a click placeholder with inventory

The following example replaces shapes so the pool stays at five. Participants still complete two tasks. Inventory runs inside the existing tasks app, so keep `app_sequence=['assignment', 'tasks']`.

1. **Give inventory a place in the draw.** In `catalog.py`, replace the shapes entry with `'inventory': 'Inventory ordering'`. In `tasks/__init__.py`, remove shapes from the imports and click-task `OPTIONS` mapping, and import `inventory`. Keep only generic click tasks in that mapping.
2. **Prepare each inventory case.** Create `tasks/inventory.py`. Adapt the pre-experiment case data and write `setup(player)` to select the case using `player.task_round` (1–10). Save the case ID, purchase cost, selling price, salvage value, and demand distribution. This also works when inventory is the second task and its opening round is overall round 11.
3. **Declare what to store.** In `class Player` in `tasks/__init__.py`, add fields for the inventory case, order quantity, realized demand and profit, and the expected-profit-maximizing order. Reuse the existing `correct` and `score` fields if performance means choosing the expected-profit-maximizing quantity. Store realized profit separately so a lucky demand draw cannot change which choice you classify as optimal.
4. **Connect the setup.** Inside `creating_session` in that same file, insert this branch immediately before the final click-task `else`:

   ```python
   elif player.task == 'inventory':
       inventory.setup(player)
   ```

5. **Collect the decision.** In `tasks/__init__.py`, add an `InventoryDecision(Page)` class. Its `is_displayed` returns `player.task == 'inventory'`. Set `form_model = 'player'` and `form_fields = ['order_quantity']`. For case-specific quantities, define `order_quantity_choices(player)` to return that case’s options. Pass the template `high=block_start(player).learning_level == 'high'`. In `before_next_page`, resolve demand, calculate profit, and store the round score. Insert `InventoryDecision` in `page_sequence` before `Feedback`.
6. **Write the participant pages.** Create `tasks/InventoryDecision.html` to show the prices, demand probabilities, and order form. Show the pre-experiment panel only when `high` is true and keep its content a placeholder until real records exist. Add an inventory branch in `tasks/Instructions.html` before the click fallback. Add an inventory branch in `tasks/Feedback.html` if you want participants to see demand or profit. Add wording in `tasks/Beliefs.html` defining “correct” as choosing the order that maximizes expected profit if you use that criterion.
7. **Check beliefs and payment against the intended measure.** With binary optimality, the current percentage forecast and binary bonus can be reused. With profit forecasts or profit-based payment, update `forecast_limit`, `settle_task`, `payment_rules.py`, the summary units, and the Welcome, belief, feedback and summary text. Keep the common MPL and reveal pages for both task positions.
8. **Test both positions.** Add an inventory submission to `tasks/tests.py` before its click fallback. Exercise inventory as the first and second task, with and without example access. Verify the chosen quantity and profit are stored, the updated belief comes after round 5 feedback, and the final summary still has two payments. Run `otree test click_demo` from the project folder. A small random demo may miss inventory, so use a test-only fixed order or the archive’s optional order-testing configuration for coverage.

## 3. How assignment works and how to change it

| Draw | Current rule | Where to change it |
|---|---|---|
| Tasks and order | `random.sample(tasks, 2)` selects two different tasks in order. With five tasks there are 20 possible ordered pairs. | Edit the pool in `catalog.py` or the sampler in `assignment/__init__.py`. The optional archive test cycles through ordered pairs. |
| Treatment | Low, High, Choice have weights 1, 2, 1 (25%, 50%, 25%). | Edit `random.choices(..., weights=[1, 2, 1])` in `assignment/__init__.py`. |
| Condition | A separate fair draw assigns endogenous or exogenous within every treatment, including Low. | Edit `participant.condition` assignment in the same function. |
| Example access | Fixed Low and High keep their assigned access across both tasks. Choice draws one of five MPL rows uniformly per task. Its answer at that price determines access for all ten rounds of that task. | Edit `MPL.before_next_page` in `tasks/__init__.py`. Change `requires_mpl` only if changing who sees the elicitation. |
| Round material | Knowledge follows CSV order. Urns follow the listed compositions, with a fresh 50/50 source and random ball each round. Click targets are randomly selected each round. | Edit `tasks/knowledge.py`, `tasks/urns.py`, or the click branch of `creating_session`, respectively. |

### Example change for Low

First decide what Low participants should read. Low participants still complete the first MPL, before learning that they will have no example access. Changing their condition can therefore change their willingness-to-pay responses.

**If Low should have no condition**, replace the two independent treatment and condition assignment lines inside the participant loop in `assignment/__init__.py` with the following. Keep the task-order assignment above them.

```python
participant.treatment = random.choices(
    ['low', 'high', 'choice'], weights=[1, 2, 1]
)[0]
if participant.treatment == 'low':
    participant.condition = 'not_applicable'
else:
    participant.condition = random.choice(['endogenous', 'exogenous'])
```

The existing MPL condition check automatically omits the average-performer sentence for Low. In `TreatmentReveal.html`, wrap the condition label and value in `{{ if participant.condition != 'not_applicable' }} ... {{ endif }}` so the internal label stays out of the participant display. In `assignment/tests.py`, allow `not_applicable` for Low and require endogenous or exogenous for High and Choice. In `tasks/tests.py`, check that Low still completes the first MPL without the sentence, receives no example, and incurs no cost.

**If Low should always receive one specific version**, use `'exogenous'` or `'endogenous'` in the Low branch instead. Exogenous gives all Low participants the average-performer sentence. Endogenous gives none of them that sentence. The 50/50 condition target then applies within High and Choice. The overall condition shares depend on which version Low receives.

### Exact balance during rolling enrollment

The supplied code makes independent draws when oTree creates participant slots. The weights give assignment probabilities. They do not guarantee realized counts. For exact ratios at completed blocks, create the joint treatment–condition assignments below, shuffle each block, and use each slot once.

| Treatment | Original design per 8 | If Low has no condition, per 8 |
|---|---|---|
| Low | 1 endogenous + 1 exogenous | 2 not applicable |
| High | 2 endogenous + 2 exogenous | 2 endogenous + 2 exogenous |
| Choice | 1 endogenous + 1 exogenous | 1 endogenous + 1 exogenous |

For one long-running oTree session, assign the shuffled slots in the order participant places will be filled. For multiple sessions feeding one continuous recruitment stream, retain the remaining allocations across sessions. If allocating on arrival, reserve the next slot atomically and keep that assignment when the same participant returns. A room provides an entry link. The allocation code provides the balance. Exact ratios apply to completed blocks of allocated slots. A partially filled block and the subset of participants who finish can have different proportions.

## 4. How payment works and where to change it

After the participant submits feedback for overall round 20, `Feedback.before_next_page` passes the first and second sets of ten records separately to `settle_task`. For each task it draws one of ten decisions and, independently, one of three forecast reports. It saves the result on the final record of that task (overall round 10 or 20). A stored paid-round value prevents a second settlement from drawing again.

| Component per task | Current calculation |
|---|---|
| Endowment | 4 points per task, giving 8 points over both tasks before bonuses and costs. |
| Selected click or knowledge decision | 2 points for a correct answer, 0 for an incorrect answer. |
| Selected urn decision | 2 × (1 − (reported probability − correct posterior)²), rounded to two decimals. Both probabilities use 0–1 units in the formula. |
| Selected belief | Uniformly draw the initial round 5 forecast, initial round 10 forecast, or updated round 10 forecast. Compare it with the outcome of the round that report predicted. Thus two of three eligible reports concern round 10. |
| Belief bonus | 2 × (1 − error²), rounded to two decimals. For binary tasks, error = forecast percentage / 100 − actual outcome (0 or 1). For urns, error = (forecast score − actual score) / 2. |
| MPL cost | Only Choice can incur a cost. Deduct the selected price once for that task if the binding answer is Example. No example costs 0. Low and High always pay 0. |

**Worked example.** A Choice participant buys knowledge examples for 3 points. The selected decision is round 3 and is correct, earning 2 points. The selected belief is their updated round 10 forecast of 80%. Their round 10 answer is correct, so the belief bonus is 2 × (1 − (0.8 − 1)²) = 1.92. The knowledge task pays **4 + 2 + 1.92 − 3 = 4.92 points**. The urn task is settled separately and added to that amount.

| Desired change | Edit |
|---|---|
| Change bonus amounts or score formulas | Edit `ENDOWMENT`, `CORRECT_DECISION`, `MAX_FORECAST_BONUS`, `URN_MAX`, `urn_score`, or `forecast_bonus` in `payment_rules.py`. Changing `URN_MAX` also changes the urn forecast limit and error normalization. Update hard-coded score limits in instructions, beliefs, feedback, Welcome and tests. |
| Change the five MPL prices | Edit `C.MPL_PRICES` in `tasks/__init__.py`. Row labels read from this list. If changing the number of rows, also change Player’s row fields, `MPL.form_fields`, and the bot submissions. For fractional prices, change the integer price and cost fields to a suitable numeric type. |
| Change who pays or when a price binds | Edit `MPL.before_next_page` for the draw and recorded cost, and `settle_task` for the deduction. Revise `MPL.html`, `TreatmentReveal.html`, and `Welcome.html` to explain the new rule. |
| Change eligible paid decisions or beliefs | Edit `settle_task` in `tasks/__init__.py`. Edit `FORECASTS` to change eligible reports, where they were entered, or the target round. For cumulative performance, compute the target across the relevant round records. Update inputs, bonus scaling, `Beliefs.html`, `Welcome.html`, and `Summary.html` to use those same units. |
| Change euros per point or participation fee | Edit `real_world_currency_per_point` and `participation_fee` in `settings.py`. The supplied demo uses €1 per point and zero fee, describes points as hypothetical, and shows a points total. For real payments, align the participant wording and final cash display with the intended conversion and fee. |

**Project sources.** [Reference project](https://chatgpt.com/library?file_id=libfile_16607269469c8191941583926199812b&account_id=personal) · [Shared tasks module](https://chatgpt.com/library?file_id=libfile_784a710e583c819181e7fb475e2b2ba7&account_id=personal)
