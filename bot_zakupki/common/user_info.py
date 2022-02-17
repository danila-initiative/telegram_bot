import dataclasses
import datetime
import typing

from loguru import logger

from bot_zakupki.bot.handlers import messages
from bot_zakupki.common import consts
from bot_zakupki.common import dates
from bot_zakupki.common import db
from bot_zakupki.common import models


class NoUserWithUserId(Exception):
    pass


class UnexpectedTrialState(Exception):
    pass


@dataclasses.dataclass
class UserInfo:
    user_id: str
    user: typing.Optional[models.User] = None
    trial_state: typing.Optional[models.TrialPeriodState] = None
    can_add_request: bool = False
    reason_message: str = ""  # почему нельзя добавить еще запрос
    _exists: bool = False
    _active: bool = False

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.user = db.get_user_by_user_id(user_id=self.user_id)
        self._set_trial_period_state()
        self._set_can_add_request()
        self._set_reason_message()

    def _is_exists_active(self):
        if self.user:
            self._exists = True
            self._active = self.user.bot_is_active

    def create_or_mark_active(self):
        self._is_exists_active()

        if not self._exists:
            db.insert_new_user(user_id=self.user_id)
            return

        if not self._active:
            logger.info(f"user {self.user_id} was not active")
            now = dates.get_now_without_ms()
            data = {
                consts.USER_BOT_START_DATE: now,
                consts.USER_BOT_IS_ACTIVE: 1,
            }
            db.update_user_by_user_id(user_id=self.user_id, column_values=data)
            return

    def _set_trial_period_state(self):
        if not self.user:
            return

        date = dates.get_now_without_ms().date()

        if self.user.subscription_last_day is None:
            self.trial_state = models.TrialPeriodState.HAS_NOT_STARTED
        elif (
            date <= self.user.subscription_last_day.date()
            and self.user.payment_last_day is None
        ):
            self.trial_state = models.TrialPeriodState.TRIAL_PERIOD
        else:
            self.trial_state = models.TrialPeriodState.IS_OVER

    def _set_can_add_request(self):
        if not self.user:
            return
        now = datetime.datetime.now().replace(microsecond=0)

        search_queries = db.get_all_search_queries_by_user_id(
            user_id=self.user_id
        )

        logger.debug(
            f"user id: {self.user_id}; "
            f"date: {now}; "
            f"subscription_last_day: {self.user.subscription_last_day}; "
            f"payment_last_day: {self.user.payment_last_day}; "
            f"trial_period_state: {self.trial_state}; "
            f"search_queries: {len(search_queries)}"
        )

        config = models.Config()
        max_queries_in_common_period = (
            config.query_limits.max_queries_in_common_period
        )
        max_queries_in_trial_period = (
            config.query_limits.max_queries_in_trial_period
        )

        if self.trial_state == models.TrialPeriodState.HAS_NOT_STARTED:
            self.can_add_request = True
        elif self.trial_state == models.TrialPeriodState.TRIAL_PERIOD:
            if len(search_queries) < max_queries_in_trial_period:
                self.can_add_request = True
        elif (
            self.trial_state == models.TrialPeriodState.IS_OVER
            and len(search_queries) < max_queries_in_common_period
        ):
            self.can_add_request = True

    def _set_reason_message(self):
        if not self.user:
            return

        if self.can_add_request:
            return

        if self.trial_state == models.TrialPeriodState.TRIAL_PERIOD:
            self.reason_message = (
                messages.CannotAddMoreQueries.TRIAL_PERIOD_LIMIT
            )
        elif self.trial_state == models.TrialPeriodState.IS_OVER:
            self.reason_message = (
                messages.CannotAddMoreQueries.COMMON_PERIOD_LIMIT
            )
