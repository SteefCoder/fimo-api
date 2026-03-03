from enum import Enum
from functools import partial

from dacite import Config, from_dict

from ..domain.models import GameList, Player
from ..repository import RatingRepository
from .exc import VerificationError
from .models import GameList as GameListIn


def validate_player(player: dict[str, int], repo: RatingRepository) -> Player:
    knsb_id = player.get("knsb_id")
    fide_id = player.get("fide_id")

    if knsb_id:
        knsb = repo.get_knsb(knsb_id)
        if not fide_id:
            fide_id = knsb.fide_id
        elif fide_id != knsb.fide_id:
            raise VerificationError(f"Geen match tussen gegeven KNSB ID {knsb_id} en FIDE ID {fide_id}.")
    
    elif fide_id:
        # fide just for verification of existence
        _ = repo.get_fide(fide_id)
        knsb = repo.get_knsb_from_fide(fide_id)
        if knsb:
            knsb_id = knsb.knsb_id

    return Player(knsb_id, fide_id)


def validate_game_list(game_list: GameListIn, repo: RatingRepository) -> GameList:
    validate = partial(validate_player, repo=repo)

    config = Config(cast=[Enum], type_hooks={Player: validate})
    domain_list = from_dict(GameList, game_list.model_dump(), config=config)
    for game in domain_list.games:
        if game.opponent == domain_list.player:
            raise VerificationError("Een player kan niet tegen zichzelf spelen.")
    return domain_list
