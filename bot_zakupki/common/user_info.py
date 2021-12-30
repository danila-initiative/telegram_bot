import datetime

from loguru import logger

from bot_zakupki.bot.handlers import messages
from bot_zakupki.common import consts
from bot_zakupki.common import db
from bot_zakupki.common import models


class NoUserWithUserId(Exception):
    pass


class UnexpectedTrialState(Exception):
    pass


def is_user_exists_and_active(user_id: str) -> tuple[bool, bool]:
    user = db.get_user_by_user_id(user_id=user_id)
    if not user:
        return False, False

    return True, user.bot_is_active


def create_user_or_mark_active(user_id: str):
    user_exists, user_active = is_user_exists_and_active(user_id=user_id)

    if not user_exists:
        db.insert_new_user(user_id=user_id)
        return

    if not user_active:
        logger.info(f"user {user_id} was not active")
        now = datetime.datetime.now().replace(microsecond=0)
        data = {db.USER_BOT_START_DATE: now, db.USER_BOT_IS_ACTIVE: 1}
        db.update_user_by_user_id(user_id=user_id, column_values=data)
        return


def get_trial_period_state(
    user: models.User, date: datetime.datetime
) -> models.TrialPeriodState:
    if user.subscription_last_day is None:
        return models.TrialPeriodState.HAS_NOT_STARTED

    if date <= user.subscription_last_day and user.payment_last_day is None:
        return models.TrialPeriodState.TRIAL_PERIOD

    return models.TrialPeriodState.IS_OVER


def can_add_request(user_id: str) -> tuple[bool, models.TrialPeriodState]:
    user = db.get_user_by_user_id(user_id=user_id)
    if user is None:
        raise NoUserWithUserId
    now = datetime.datetime.now().replace(microsecond=0)

    trial_period_state = get_trial_period_state(user=user, date=now)
    search_queries = db.get_all_search_queries_by_user_id(user_id=user_id)

    logger.debug(
        f"user id: {user.user_id}; "
        f"date: {now}; "
        f"subscription_last_day: {user.subscription_last_day}; "
        f"payment_last_day: {user.payment_last_day}; "
        f"trial_period_state: {trial_period_state}; "
        f"search_queries: {len(search_queries)}"
    )

    if trial_period_state == models.TrialPeriodState.HAS_NOT_STARTED:
        return True, trial_period_state

    if trial_period_state == models.TrialPeriodState.TRIAL_PERIOD:
        if len(search_queries) < consts.MAX_QUERIES_IN_TRIAL_PERIOD:
            return True, trial_period_state
        return False, trial_period_state

    if (
        trial_period_state == models.TrialPeriodState.IS_OVER
        and len(search_queries) < consts.MAX_QUERIES_IN_COMMON_PERIOD
    ):
        return True, trial_period_state

    return False, trial_period_state


def get_message_cannot_add_query(trial_period_state: str) -> str:
    if trial_period_state == models.TrialPeriodState.TRIAL_PERIOD:
        return messages.CannotAddMoreQueries.TRIAL_PERIOD_LIMIT

    if trial_period_state == models.TrialPeriodState.IS_OVER:
        return messages.CannotAddMoreQueries.COMMON_PERIOD_LIMIT

    raise UnexpectedTrialState
