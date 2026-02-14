# LJPJT System Development Template Repository
This repository is a template repository for system development of the shared task LJPJT. By clicking the `Use this template` button on GitHub, you can copy and use this repository.

Website: https://ljpjt26.coliee.org/  
Contact: Kotaro Sakamoto [@ktr-skmt](https://github.com/ktr-skmt) ( sakamoto.ljpjt@besna.institute )  
## Setting up the development environment

We **recommend** development using [VSCode](https://azure.microsoft.com/ja-jp/products/visual-studio-code/).
[VSCode Insiders](https://code.visualstudio.com/insiders/), which is not a stable version, is not recommended.

You can set up the development environment by following the steps below.

### Installation

- [VSCode](https://azure.microsoft.com/ja-jp/products/visual-studio-code/)
- [Docker](https://docs.docker.com/get-docker/)

### Setting up VSCode

Launch VSCode and install the [Visual Studio Code Remote Containers](https://code.visualstudio.com/docs/remote/containers) extension.

Open the [Command Palette](https://code.visualstudio.com/docs/getstarted/userinterface#_command-palette) and select:
```
Remote-Containers: Reopen in Container
```

## System Development

### Overview of Directory Structure
```plaintext
├── dataset  # Location for storing test data
├── evaluation_results
│   └── development  # Location for saving evaluation results
├── scripts
│   └── generate_lockfile.sh  # Script for generating requirements.txt
├── submissions
│   └── development  # Location for saving solver execution results
├── app.ini  # Configuration file
├── README.md  # This file
├── requirements.in  # List of dependency packages
├── requirements.txt  # Fixed version list of dependency packages
├── schema.yaml  # Data schema
└── solver.py  # Implementation of the solver
```

### Preparing the Configuration File
Set the `TEAM_NAME` and `AFFILIATION` in `app.ini` to the team name and affiliation submitted during registration (note: hyphens "-" are not allowed for either).  
Set the system name in `SYSTEM_NAME` (note: hyphens "-" are not allowed).  

Set the API key specific to each team in `API_KEY`. The API key will be provided upon the completion of registration.  

Set the file name of the test data specified by the organizers in `TEST_DATA`

Set `MODE` to either `development` or `leaderboard`. In `development` mode, evaluation results can be received without being reflected on the leaderboard. In `leaderboard` mode, the received evaluation results will be reflected on the leaderboard.

```toml
[system]
TEAM_NAME = Team1
AFFILIATION = Affiliation2
SYSTEM_NAME = System3

[settings]
API_KEY = your-api-key-here
TEST_DATA = LJPJT26-test001.jsonl
MODE = development
```

### Implementation of the Solver

#### Data Schema
The input and output data of the solver follow the [data schema](schema.yaml).

#### Input Data (Test Data)
The input data is a list of `Tort`. The input data has `null` values for `is_accepted` of `PlaintiffClaim`, `is_accepted` of `DefendantClaim`, and `court_decision` of `Tort`. The solver fills in boolean values for the `null` positions.
```python
test_data: list[Tort] = [
    Tort(
        version="LJPJT26-test001.jsonl",
        tort_id="0",
        undisputed_facts=[
            UndisputedFact(
                id="0",
                description="本件報道の報道時間は全体で約三分間であり、原告の動画像と実名の字幕が報道されたのは約六秒間であった。",
            )
        ],
        plaintiff_claims=[
            PlaintiffClaim(
                id="0",
                description="社会的活動に対する評価の資料として前科の公表が是認される余地はない。",
                is_accepted=null,
            )
        ],
        defendant_claims=[
            DefendantClaim(
                id="0",
                description="本件報道は、その報道手段においても、前記の報道目的を達成させる上で、必要最小限の相当な方法であった。",
                is_accepted=null,
            )
        ],
        court_decision=null,
    ),
    Tort(...),
    Tort(...),
    ...
]
```
#### Output Data
The output data is also a list of `Tort`. As a result of the solver's processing, boolean values are filled in for the `null` positions in the input data.

* The participation requirement for the Tort Prediction task is that all `court_decision` fields of `Tort` are filled with boolean values. If there is any `null`, the Tort Prediction task is disqualified.
* Additionally, the participation requirement for the Rationale Extraction task is that all `is_accepted` fields of both `PlaintiffClaim` and `DefendantClaim` are filled with boolean values. If there is any `null`, the Rationale Extraction task is disqualified.

```python
return [
    Tort(
        version="LJPJT26-test001.jsonl",
        tort_id="0",
        undisputed_facts=[
            UndisputedFact(
                id="0",
                description="本件報道の報道時間は全体で約三分間であり、原告の動画像と実名の字幕が報道されたのは約六秒間であった。",
            )
        ],
        plaintiff_claims=[
            PlaintiffClaim(
                id="0",
                description="社会的活動に対する評価の資料として前科の公表が是認される余地はない。",
                is_accepted=False,
            )
        ],
        defendant_claims=[
            DefendantClaim(
                id="0",
                description="本件報道は、その報道手段においても、前記の報道目的を達成させる上で、必要最小限の相当な方法であった。",
                is_accepted=True,
            )
        ],
        court_decision=False,
    ),
    Tort(...),
    Tort(...),
    ...
]
```

#### Algorithm Creation
The objectives of the Tort Prediction task and the Rationale Extraction task are described on their respective introduction pages. Here, concerning implementation, as explained in the descriptions of the input and output data above, an algorithm will be created to fill the `null` values in the input data with boolean values. This algorithm should be implemented in the `solve` function in `solver.py`, located in the project root. The contents of the `solve` function can be freely modified.

```python
# TODO: Write your own algorithm
def solve(test_data: list[Tort]) -> list[Tort]:
    system_result: list[Tort] = [algorithm(tort) for tort in test_data]
    return system_result
```

### Running the Solver
In the terminal of VSCode's Remote Container, execute the following command. This will download and load the test data file specified in `TEST_DATA` in `app.ini`, and run the `solve` function. Evaluation results will also be output to standard output.

```bash
python -m solver
```

#### Error message caused by a cold start

If an error message like the one below is displayed in the standard output, rerunning the process after approximately one minute will resolve the error message, and the evaluation results will be displayed in the standard output (this is due to the cold start of the evaluation system).

```bash
$ python -m solver
EVALUATION RESULT: evaluation_results/development/test001_your-team-name-here_your-affiliation-here_your-system-name-here_20241213185310.jsonl
---
Tort prediction task
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/workspaces/LJPJT-dev-template/solver.py", line 48, in <module>
    main(solve)
  File "/workspaces/LJPJT-dev-template/src/utils.py", line 152, in main
    pipeline(submission)
  File "/workspaces/LJPJT-dev-template/src/utils.py", line 143, in pipeline
    filename_with_timestamp, evaluation_result = evaluate(filename)
                                                 ^^^^^^^^^^^^^^^^^^
  File "/workspaces/LJPJT-dev-template/src/utils.py", line 97, in evaluate
    print(f"Accuracy: \t{evaluation_result['tort_prediction_task']['accuracy']}")
                         ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
TypeError: 'NoneType' object is not subscriptable
```

### Checking Logs
There are two types of logs: solver execution results and evaluation results.

#### Solver Execution Results
The execution results of the `solve` function are saved in `submissions/{MODE}/` (`submissions/development/` or `submissions/leaderboard/`). The filename is determined by `TEST_DATA`, `SYSTEM_NAME`, `AFFILIATION`, `TEAM_NAME`, and a timestamp set in `app.ini`. If `TEST_DATA` is `test.jsonl`, the filename will be `test_{SYSTEM_NAME}_{AFFILIATION}_{TEAM_NAME}_{timestamp}.jsonl`. The content of the file is the execution results of the `solve` function.

#### Evaluation Results
Evaluation results are saved in `evaluation_results/{MODE}/` (`evaluation_results/development/` or `evaluation_results/leaderboard/`). The filename is determined by `TEST_DATA`, `SYSTEM_NAME`, `AFFILIATION`, `TEAM_NAME`, and a timestamp set in `app.ini`. If `TEST_DATA` is `test.jsonl`, the filename will be `test_{SYSTEM_NAME}_{AFFILIATION}_{TEAM_NAME}_{timestamp}.jsonl`. The content of the file is the evaluation results for the execution results of the `solve` function.

## Managing Python Dependency Packages

### Updating requirements.in

- Always update manually.
- Only list directly dependent packages.
- Only list packages available on [PyPI](https://pypi.org/).

Example) If you want to update the version of flake8 to 1.2.X: `flake8~=1.2.3`
Reference: https://www.python.org/dev/peps/pep-0440/#version-specifiers

Updating using the following commands is prohibited
```bash
pip freeze > requirements.in
pip freeze >> requirements.in
```

### Updating requirement.txt

Instead of updating requirements.txt manually, execute the following command
```bash
rm requirements.txt
./scripts/generate_lockfile.sh
```
