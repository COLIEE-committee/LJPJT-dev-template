import configparser
import random
from pathlib import Path
from typing import Final

from src.models.defendant_claim import DefendantClaim
from src.models.plaintiff_claim import PlaintiffClaim
from src.models.tort import Tort
from src.utils import main

PATH_TO_ROOT: Final[Path] = Path(__file__).parent
PATH_TO_CONF: Final[Path] = PATH_TO_ROOT / "app.ini"

CONFIG: Final[configparser.ConfigParser] = configparser.ConfigParser()
CONFIG.read(PATH_TO_CONF, encoding="utf-8")

TEST_DATA_FILENAME: Final[str] = CONFIG["settings"]["TEST_DATA"]


# TODO: Write your own algorithm
def solve(test_data: list[Tort]) -> list[Tort]:  # pylint: disable=unused-argument
    # print(f"TEST DATA: {TEST_DATA_FILENAME}")
    system_results: list[Tort] = []
    for tort in test_data:
        system_results.append(
            Tort(
                version=tort.version,
                tort_id=tort.tort_id,
                undisputed_facts=tort.undisputed_facts,
                plaintiff_claims=[
                    PlaintiffClaim(id=claim.id, description=claim.description, is_accepted=bool(random.getrandbits(1)))
                    for claim in tort.plaintiff_claims
                ],
                defendant_claims=[
                    DefendantClaim(id=claim.id, description=claim.description, is_accepted=bool(random.getrandbits(1)))
                    for claim in tort.defendant_claims
                ],
                court_decision=bool(random.getrandbits(1)),
            )
        )
    # print("SYSTEM RESULTS:")
    # print(system_results)
    return system_results


if __name__ == "__main__":
    main(solve)
