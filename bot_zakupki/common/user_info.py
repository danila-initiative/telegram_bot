import datetime
from typing import Optional

from bot_zakupki.common import models


def get_trial_period_state(
        user: models.User,
        date: Optional[datetime.datetime],
) -> models.TrialPeriodState:
    if date is None:
        date = datetime.datetime.now().replace(microsecond=0)

    if user.trial_start_date is None:
        return models.TrialPeriodState.TRIAL_PERIOD_HAS_NOT_STARTED
    elif user.trial_start_date <= date <= user.trial_end_date:
        return models.TrialPeriodState.TRIAL_PERIOD

    return models.TrialPeriodState.TRIAL_PERIOD_IS_OVER
