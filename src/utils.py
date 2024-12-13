# pylint: disable=duplicate-code
import configparser
import json
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any, Final

import requests

from src.models.tort import Tort

PATH_TO_ROOT: Final[Path] = Path(__file__).parent.parent
PATH_TO_CONF: Final[Path] = PATH_TO_ROOT / "app.ini"

CONFIG: Final[configparser.ConfigParser] = configparser.ConfigParser()
CONFIG.read(PATH_TO_CONF, encoding="utf-8")

API_KEY: Final[str] = CONFIG["settings"]["API_KEY"]
TEAM: Final[str] = CONFIG["system"]["TEAM_NAME"]
AFFILIATION: Final[str] = CONFIG["system"]["AFFILIATION"]
SYSTEM: Final[str] = CONFIG["system"]["SYSTEM_NAME"]

PATH_TO_DATASET: Final[Path] = PATH_TO_ROOT / "dataset"


BASE_URL: Final[str] = "https://asia-northeast1-ljpjt-412809.cloudfunctions.net/"


def create_url(endpoint: str) -> str:
    return f"{BASE_URL}{endpoint}?key={API_KEY}"


EVALUATION_RESULT_URL: Final[str] = create_url("evaluation_result")
RESULT_UPLOADER_URL: Final[str] = create_url("result_uploader")
DISTRIBUTION_DOWNLOADER_URL: Final[str] = create_url("distribution_downloader")

TEST_DATA_FILENAME: Final[str] = CONFIG["settings"]["TEST_DATA"]
MODE: Final[str] = CONFIG["settings"]["MODE"]
PATH_TO_EVALUATION_RESULTS: Final[Path] = PATH_TO_ROOT / "evaluation_results" / MODE
PATH_TO_SUBMISSIONS: Final[Path] = PATH_TO_ROOT / "submissions" / MODE


def submission_filename() -> str:
    tokens: list[str] = TEST_DATA_FILENAME.split(".")
    return f"{tokens[0]}_{TEAM}_{AFFILIATION}_{SYSTEM}.{tokens[-1]}"


def _log_submission(submission: list[Tort], filename: str) -> None:
    with open(PATH_TO_SUBMISSIONS / filename, mode="w", encoding="utf-8") as f:
        for tort in submission:
            f.write(json.dumps(tort.to_dict(), ensure_ascii=False) + "\n")


def _log_evaluation_results(evaluation_result: dict[str, Any], filename: str) -> None:
    with open(PATH_TO_EVALUATION_RESULTS / filename, mode="w", encoding="utf-8") as f:
        f.write(json.dumps(evaluation_result, ensure_ascii=False) + "\n")


def _download_testdata() -> list[Tort]:
    response = requests.post(
        DISTRIBUTION_DOWNLOADER_URL, data=TEST_DATA_FILENAME, headers={"Content-Type": "text/plain"}, timeout=(3.0, 7.5)
    )
    jsonl: str = response.text
    with open(PATH_TO_DATASET / TEST_DATA_FILENAME, mode="w", encoding="utf-8") as f:
        f.write(jsonl)
    return [Tort.from_dict(json.loads(line)) for line in jsonl.split("\n")]


def _submit(submission: list[Tort], filename: str) -> None:
    json_data: dict[str, Any] = {
        "api_key": API_KEY,
        "filename": filename,
        "mode": MODE,
        "body": [tort.to_dict() for tort in submission],
    }
    text_data: str = json.dumps(json_data)
    requests.post(RESULT_UPLOADER_URL, data=text_data, headers={"Content-Type": "application/json"}, timeout=(3.0, 7.5))


def evaluate(filename: str) -> tuple[str, dict[str, Any]]:
    data: str = f"{MODE}/{filename}"
    response = requests.post(
        EVALUATION_RESULT_URL, data=data, headers={"Content-Type": "text/plain"}, timeout=(3.0, 7.5)
    )
    evaluation_result: dict[str, Any] = {}
    if response.status_code == 200:
        evaluation_result = response.json()

    tokens: list[str] = filename.split(".")
    now: str = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{tokens[0]}_{now}.{tokens[-1]}"

    print(f"EVALUATION RESULT: evaluation_results/{MODE}/{filename}")
    print("---")
    print("Tort prediction task")
    print(f"Accuracy: \t{evaluation_result['tort_prediction_task']['accuracy']}")
    print(f"The number of correct answers: \t{evaluation_result['tort_prediction_task']['num_of_correct_answers']}")
    print(f"The number of torts: \t{evaluation_result['tort_prediction_task']['num_of_topics']}")
    print(f"The number of evaluated answers: \t{evaluation_result['tort_prediction_task']['num_of_evaluated_answers']}")
    print("---")
    print("Rationale extraction task")
    print(f"F1 score (all): \t{evaluation_result['rationale_extraction_task']['binary_all_f1']}")
    print(f"Recall (all): \t{evaluation_result['rationale_extraction_task']['binary_all_recall']}")
    print(f"Precision (all): \t{evaluation_result['rationale_extraction_task']['binary_all_precision']}")
    print(f"F1 score (plaintiff): \t{evaluation_result['rationale_extraction_task']['binary_p_f1']}")
    print(f"Recall (plaintiff): \t{evaluation_result['rationale_extraction_task']['binary_p_recall']}")
    print(f"Precision (plaintiff): \t{evaluation_result['rationale_extraction_task']['binary_p_precision']}")
    print(f"F1 score (defendant): \t{evaluation_result['rationale_extraction_task']['binary_d_f1']}")
    print(f"Recall (defendant): \t{evaluation_result['rationale_extraction_task']['binary_d_recall']}")
    print(f"Precision (defendant): \t{evaluation_result['rationale_extraction_task']['binary_d_precision']}")
    print(
        f"The number of correct_answers (all): \t{evaluation_result['rationale_extraction_task']['num_of_all_correct_answers']}"  # noqa: E501
    )
    print(f"The number of claims (all): \t{evaluation_result['rationale_extraction_task']['num_of_all_topics']}")
    print(
        f"The number of evaluated answers (all): \t{evaluation_result['rationale_extraction_task']['num_of_all_evaluated_answers']}"  # noqa: E501
    )
    print(
        f"The number of correct_answers (plaintiff): \t{evaluation_result['rationale_extraction_task']['num_of_p_correct_answers']}"  # noqa: E501
    )
    print(f"The number of claims (plaintiff): \t{evaluation_result['rationale_extraction_task']['num_of_p_topics']}")
    print(
        f"The number of evaluated answers (plaintiff): \t{evaluation_result['rationale_extraction_task']['num_of_p_evaluated_answers']}"  # noqa: E501
    )
    print(
        f"The number of correct_answers (defendant): \t{evaluation_result['rationale_extraction_task']['num_of_d_correct_answers']}"  # noqa: E501
    )
    print(f"The number of claims (defendant): \t{evaluation_result['rationale_extraction_task']['num_of_d_topics']}")
    print(
        f"The number of evaluated answers (defendant): \t{evaluation_result['rationale_extraction_task']['num_of_d_evaluated_answers']}"  # noqa: E501
    )
    return filename, evaluation_result


def pipeline(submission: list[Tort]) -> None:
    filename: str = submission_filename()

    _submit(submission, filename)

    filename_with_timestamp: str
    evaluation_result: dict[str, Any]
    filename_with_timestamp, evaluation_result = evaluate(filename)

    _log_submission(submission, filename_with_timestamp)

    _log_evaluation_results(evaluation_result, filename_with_timestamp)


def main(solve: Callable[[list[Tort]], list[Tort]]) -> None:
    submission: list[Tort] = solve(_download_testdata())
    pipeline(submission)
