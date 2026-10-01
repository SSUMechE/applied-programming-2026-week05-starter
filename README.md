# Week 5 Assignment: Parametric Path Evaluation

Use this [Week 5 template](https://github.com/SSUMechE/applied-programming-2026-week05-starter) to create your own private repository.
Read [Week 5 Reading](docs/week_05_reading.pdf), including its final Assignment
section, and follow the setup and submission steps below.

## 1. Purpose and files to edit

Evaluate a supplied path with named settings. Use metre-based inputs, validate
types and ranges, call provided calculations, and return metrics and constraint
margins with a decision. Explain controlled comparisons of candidate paths, acceptance limits and checking
methods with independent tests. Signed margins and sampled-check interpretation
are the new focus. Functions, objects and input validation reuse Weeks 1–4.
You do not write a planner, collision-geometry algorithm or simulator.

Edit only these two files:

| File | Required work |
|---|---|
| `src/ap_week05/model.py` | TODOs 1–3: settings, problem validation and evaluation |
| `tests/test_student.py` | TODO 4: own tests covering the three stated behaviors |

Keep provided interfaces, input objects, functions, published tests and environment
pins unchanged. The completed `to_plot_data()` method is provided and protected.
Practice files and `artifacts/` are ignored local inspection work.

The completed `Configuration`, `ConfigurationBounds`, `Path` and `Obstacle`
classes keep the Week 3–4 fields and normal uses. Use the copies supplied in
this Week 5 package. No previous assignment answers or package installation
are needed. `Configuration.dimension` reads the coordinate count as a property.
`Path.length()` requests a calculation and returns the length.
`PROVENANCE.md` records the source and the additional overflow guards.

This week adds `PlanningSettings` for four checking settings and
`ParametricPlanningProblem` to combine those settings with the supplied path
and scene. It is a new class built from the familiar objects.
`EvaluationResult` stores measurements, margins and the decision.
The earlier `PlanResult.succeeded` records whether a path was supplied.
Here `feasible` records whether both checked limits are met: an existing path
can have `feasible=False`. Reading Section 3 explains this distinction.

The Week 2 interpolation function accepted a point count for one segment.
Here `sample_path` accepts a maximum spacing in metres for the whole path.
The length formula is unchanged. The Week 5 evaluation additionally rejects
consecutive equal positions because a zero-length segment has no direction
for the turning calculation. The reusable `Path` class itself is unchanged.

## 2. Prepare the repository and environment

Click **Use this template → Create a new repository**, choose **Private**, and name it
`applied-programming-w05-YOUR-STUDENT-ID`. Use the existing Week 1–4 GitHub template
and browser sign-in procedure. Invite `SSUMechE` when submitting through LMS.
Never put a credential in a URL, file or LMS record.

Open **Anaconda Prompt** on Windows. Replace the parent folder, GitHub account and
student ID with your own values. Clone your private repository, not the public template.

```bat
cd /d "C:\your-course-folder"
git clone https://github.com/YOUR-GITHUB-ID/applied-programming-w05-YOUR-STUDENT-ID.git
cd applied-programming-w05-YOUR-STUDENT-ID
git remote -v
```

Both origin addresses must identify your private repository. Run the following
in its root, the directory containing this README. Create the Week 5 environment
once. If it already exists, skip creation and activate it. Keep working earlier
environments unchanged.

```bat
set PYTHONUTF8=1
conda --no-plugins env create --solver classic --file environment.yml
conda activate applied-programming-w05
python -m pip install -r requirements.txt
python -m pip install -e . --no-build-isolation
python scripts/verify_environment.py
```

Expect `ENVIRONMENT PASS`. This checks Python, installed versions and package
imports. It does not check unfinished TODOs. Stop and read any setup error.
This core route needs no GPU, simulator, graphics package or additional environment
manager. The first installation needs internet. On a new Prompt, return to the
repository, run `set PYTHONUTF8=1`, then activate `applied-programming-w05`.
Do not recreate the environment after each edit. On macOS/Linux use the Week 2
folder syntax and omit the Windows `set` line in a Conda-initialized terminal.

## 3. Connect each concept to a supplied comparison

The files below are already in your repository. You do not create or complete
them before using the Reading examples:

- `examples/compare_evaluations.py`: complete comparison program with five choices.
- `examples/inspect_path.py`: complete one-path calculation and printing program.
- `src/ap_week05/provided.py`: complete `sample_path`, `path_metrics` and
  `constraint_margins` functions used by both examples.
- `src/ap_week05/domain.py` and `cases.py`: complete objects and the shared input data.

All these examples run before any Assignment TODO is completed. The separate
`src/ap_week05/__main__.py` demo uses your model and runs after TODOs 1–3.

Follow Reading Sections 2 and 4 after setup. In the command
`python examples/compare_evaluations.py metrics`, `python` starts Python,
the file path selects the existing program, and the final word `metrics`
selects which comparison it performs. It is not another file to write.
From the repository root, run each choice when its concept is introduced:

```bat
python examples/compare_evaluations.py metrics
python examples/compare_evaluations.py method
python examples/compare_evaluations.py resolution
python examples/compare_evaluations.py limits
python examples/compare_evaluations.py paths
```

These commands use the completed functions in `provided.py`.
Keep the supplied scripts unchanged. The detour is `(0,0) → (0,2) → (4,2) → (4,0)`
metres around a disk at `(2,0)` of radius `0.5` m. The direct path joins the
same endpoints. Measurements precede margins and decisions in the Reading.

- `metrics`: detour length `8`, clearance `1.5`, turning `pi`, 17 samples.
- `method`: direct path, same length `4`, clearance `1.5` with two waypoint
  checks versus `-0.5` with nine interpolated checks. The path does not change.
- `resolution`: direct path, interpolation spacing `1.0` versus `0.5` gives
  five versus nine samples. Both include the disk centre and report `-0.5`.
- `limits`: fixed detour and checking. Maximum lengths `9`, `8`, `7` give
  length margins `1`, `0`, `-1`. Minimum clearance stays `0.5`, so its margin
  stays `1`. Only the requirement changes.
- `paths`: same scene, limits and checking for direct and detour. Direct
  fails clearance. Detour satisfies both limits. This compares geometry
  without changing the rules to make one result pass.

The Reading shows the relevant calculation code next to each comparison.
For example, `metrics = path_metrics(case["path"], samples, case["obstacle"])`
gives a path, selected positions and an obstacle to the function. It runs the
calculation and returns a dictionary. The `=` gives that dictionary the name
`metrics`. Reading `metrics["length_m"]` gets `8.0` for the detour.
Only a later `print(...)` displays the value in the terminal.

Section 4 follows how `examples/inspect_path.py` passes those measurements to
the limits calculation and prints the results. Create its practice copy once:

```bat
copy examples\inspect_path.py practice\inspect_path.py
```

Reopen an existing copy instead of overwriting it. Keep `MIN_CLEARANCE_M = 0.5`
and change only `MAX_LENGTH_M` to `8.0`. Save and run:

```bat
python practice/inspect_path.py
```

Length margin is `0`, clearance margin is `1`, and the decision is `True`.
Change only maximum length to `7.999`, save, and rerun. Length margin becomes
`-0.001` and the decision becomes `False`. Measurements stay unchanged.
Keep this ungraded practice file for your boundary test. It is not submitted.

## 4. Implement and check

First inspect the untouched baseline:

```bat
python -m pytest tests/public tests/test_student.py -q
```

Unfinished model bodies raise `NotImplementedError`. The one skipped student-test
placeholder is deliberate and must be replaced. The untouched baseline is
`69 failed, 2 passed, 1 skipped`. Import errors,
missing packages and failed installation are not expected TODO failures.

Open `src/ap_week05/model.py`. Work in the following order, replacing only the
unfinished method bodies. Save before each focused check. Reading Section 5.3
gives the complete implementation rules.

**TODO 1 — `PlanningSettings.__post_init__`**

Validate the settings against Reading Section 1.2, store accepted numbers as floats, and
raise `PlanningModelError` for an invalid setting.

```bat
python -m pytest tests/public/test_settings.py -q
```

Expected summary after TODO 1: `36 passed`. Later model tests can still fail.

**TODO 2 — `ParametricPlanningProblem.__post_init__`**

Check the connected objects, 2-D values, 2–32 waypoints, matching endpoints,
inclusive bounds and absence of equal consecutive positions. Reject inconsistent
input rather than repairing it. Use the complete checks in Reading Section 5.3.

```bat
python -m pytest tests/public/test_problem.py -q
```

Expected summary after TODOs 1–2: `20 passed`.

**TODO 3 — `ParametricPlanningProblem.evaluate`**

Call `sample_path`, `path_metrics` and `constraint_margins`. Return the supplied
`EvaluationResult` with its measurements, margins, decision, method and sample
count. Both raw margins must be nonnegative for `feasible=True`. Do not round
them before deciding, print, write files or change the inputs.

```bat
python -m pytest tests/public/test_evaluation.py -q
```

Expected summary after TODOs 1–3: `9 passed`. A validly constructed path may
return `feasible=False`. That is an evaluated result, not an input exception.

**TODO 4 — `tests/test_student.py`**

For TODO 4, replace the placeholder with your own `test_...` functions.
Use small inputs and hand-derived expected values to cover these three behaviors:

1. Compare direct and detour with the same default scene, limits and checking
   settings. Check lengths
   `4`/`8`, clearances `-0.5`/`1.5`, margins and `False`/`True` decisions.
2. Compare the detour at maximum length `8.0` and `7.999`, with minimum clearance
   `0.5`. Check unchanged measurements, length margins `0`/`-0.001` and
   `True`/`False`. Only the acceptance limit changes.
3. Compare the same direct path under waypoint and interpolated checking with
   resolution `0.5` and default limits. Check sample counts `2`/`9`, unchanged
   length, clearances `1.5`/`-0.5`, clearance margins `1`/`-1` and `True`/`False`.

Do not copy or rename public tests. The instructor reviews the assertions.
These are three behavior checks, not a separate function-count grading rule.
The supplied tests also check invalid inputs, ownership and display data.
Then run:

```bat
python -m pytest tests/public tests/test_student.py -q
python -m ap_week05
```

The completed reference reports **`74 passed` = 71 provided tests + 3 own cases**.
This is an example total, not a number to match. Your count may differ with
parametrization or extra tests. Cover all three required behaviors, pass the
full suite and leave no skipped placeholder. The demo prints the result without
generating a file. Passing tests confirms the cases run, not every possible
input or completion of GitHub/LMS submission.

## 5. Submit this week's work

Submit the completed model and test file in the intact private repository.
No separate report, engineering note, wheel or generated picture is required.

Use Anaconda Prompt in the repository root:

```bat
git diff
git status --short
git add src/ap_week05/model.py tests/test_student.py
git diff --staged
git commit -m "Complete Week 5 parametric evaluation"
git push origin main
git status --short
git rev-parse HEAD
git ls-remote origin refs/heads/main
```

Press `q` to leave a diff pager. Check that local and remote full commit IDs match
and the final status is empty. Keep the repository private. At LMS submission,
invite `SSUMechE` through Settings → Collaborators if neither active access nor a
correct pending invitation already exists. Report the actual state honestly.

Submit these same three LMS fields within one week of the Week 5 lab, using
the exact date and time announced in LMS:

1. Your private `applied-programming-w05-<student-id>` repository URL.
2. The full 40-character commit ID of the pushed revision.
3. Confirmation of private visibility, actual `SSUMechE` access state and the
   revision to be graded.

Fictional format example. Replace the account, student ID and commit with your own:

```text
Private repository URL:
https://github.com/example-student/applied-programming-w05-20260000
Full commit ID:
0123456789abcdef0123456789abcdef01234567
Confirmation:
Private. SSUMechE invitation sent on time and pending acceptance.
Grade the full commit ID recorded above.
```

If access is accepted, report active access instead of pending. Do not submit
a public template URL, local path, branch name, `latest`, short hash, unpushed
commit or credential.

A correctly addressed invitation sent on time and awaiting only instructor
acceptance is not a student omission. GitHub upload alone is not submission.
Later pushes do not replace the submitted revision. Week 6–7 continuity does
not postpone this Week 5 submission. No separate LMS attachment is required.
Follow the designated repository, file and LMS formats. Missing mandatory
submission conditions by the deadline results in zero, with the pending-access
exception above. A numerical test failure alone is not an automatic zero for the
entire assignment.

## 6. Optional path views and 3D replay

The optional reference in Reading Section 5.6 may be used at its stated TODO
checkpoints. It is not a step required after LMS submission.

### Optional: view the path and checked points — not submitted

After TODOs 1 and 2, you may run:

```bat
python scripts/render_preview.py
```

It writes `artifacts/path_preview.svg`. Open it in a browser to see the path,
sampled points and disk. This file is ignored by Git and is not submitted.
If it cannot be displayed, continue with numerical results and tests.
No graphics package installation is needed.

### Optional: compare the same path in 3D — not submitted

Complete model TODOs 1–3 first. This supplied renderer calls your `evaluate()`
and the completed `to_plot_data()`. It does not contain replacement answers.
Run it unchanged to visualize the CPU method comparison from Reading Section 2.2. No movie,
report, screenshot or extra test is required for submission.

Use the existing **`applied-programming-cuda`** environment after the checks in the
separate [CUDA/Genesis setup guide](https://github.com/SSUMechE/applied-programming-2026-week05-starter/releases/download/week05-v1-reading-v10/cuda_genesis_gpu_setup_v6.pdf) pass.
Download its [setup files](https://github.com/SSUMechE/applied-programming-2026-week05-starter/releases/download/week05-v1-reading-v10/cuda_genesis_gpu_setup_files_v6.zip) and
[copyable commands TXT](https://github.com/SSUMechE/applied-programming-2026-week05-starter/releases/download/week05-v1-reading-v10/cuda_genesis_gpu_setup_commands_v6.txt). In **Anaconda Prompt**, in this
same Week 5 repository root:

```bat
set PYTHONUTF8=1
conda activate applied-programming-cuda
python -m pip install -e . --no-deps --no-build-isolation
python scripts/preview_genesis.py --case direct --method waypoints
python scripts/preview_genesis.py --case direct --method interpolated
```

Install only the local package here. Do not rerun core requirements or install
Week 4 CPU PyTorch in the CUDA environment. No new environment is needed.

Open the printed `index.html` in your browser. Default comparison pages are:

- `artifacts/genesis/direct_waypoints_L9_low/index.html`
- `artifacts/genesis/direct_interpolated_L9_low/index.html`

The first correct result checks 2 endpoints, reports clearance `1.5 m` and
`feasible=True`. The second checks 9 points on exactly the same direct path,
reports clearance `-0.5 m` and `feasible=False`. The path still crosses the disk
in both animations. The checking locations changed, not the path or its safety.
Your actual model result is displayed even if it differs from these expected values.

The cylinder represents the obstacle footprint, fixed dots mark distance-check positions,
and the moving marker represents a mathematical point. Height and marker size
are display-only. This is **Genesis geometric replay**, not a robot controller,
learned world model or contact/physical-safety experiment.

Default `low` profile: one small scene, 640×480, 10 fps, 40 frames (4 seconds),
rasterization. It is a conservative trial setting for 6 GB GPUs, not a guarantee
for every PC. Initial compilation may take longer. CUDA checks and graphics
output are different. If rendering fails, use the saved numerical result or SVG.
Do not change security settings or reinstall drivers for this optional activity.
All output stays under ignored `artifacts/`. No generated file is submitted.

Return to the core environment for required tests and submission:

```bat
conda activate applied-programming-w05
python -m pytest tests/public tests/test_student.py -q
```

