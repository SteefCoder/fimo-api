from dataclasses import asdict

from ..domain.rules import calculate
from ..repository import RatingRepository
from .models import GameList, ListCalculation
from .verify import validate_game_list


def calculate_new_rating(game_list: GameList, repo: RatingRepository) -> ListCalculation:
    domain_list = validate_game_list(game_list, repo)
    calculation = calculate.calculate_new_rating(domain_list, repo)
    return ListCalculation.model_validate(asdict(calculation))
