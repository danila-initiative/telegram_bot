import datetime

from loguru import logger

from bot_zakupki.common import models


def get_trial_period_state(
    user: models.User, date: datetime.datetime
) -> models.TrialPeriodState:
    logger.debug(
        f"user id: {user.user_id}; "
        f"now: {date}; "
        f"trial_start_date: {user.trial_start_date}; "
        f"trial_end_date: {user.trial_end_date}"
    )

    if user.trial_start_date is None:
        return models.TrialPeriodState.TRIAL_PERIOD_HAS_NOT_STARTED
    elif user.trial_start_date <= date <= user.trial_end_date:
        return models.TrialPeriodState.TRIAL_PERIOD

    return models.TrialPeriodState.TRIAL_PERIOD_IS_OVER
