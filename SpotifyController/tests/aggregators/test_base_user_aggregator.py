import logging

from unittest.mock import Mock

import pytest

from SpotifyController.services.aggregator.aggregator_base import BaseUserAggregator
from SpotifyController.services.aggregator.aggregator_base import UserDataProcessor

from typing import List
from User.models import CustomUser

logger = logging.getLogger("test")

def test_run_services_for_each_user_with_mocks(users):
    logger.info("[START] test_run_services_for_each_user_with_mocks")

    aggregator = BaseUserAggregator(users=users)

    service_instance_mock = Mock(spec=UserDataProcessor)
    service_class_mock = Mock(return_value=service_instance_mock)

    aggregator.run_services_for_each_user(service_class_mock)

    # проверяем, что сервис создается для каждого пользователя
    assert service_class_mock.call_count == len(users)
    for user in users:
        service_class_mock.assert_any_call(parent=aggregator, user=user)

    # проверяем, что run() вызвался у каждого экземпляра
    assert service_instance_mock.run.call_count == len(users)

    logger.info("[END] test_run_services_for_each_user_with_mocks")

def test_run_services_for_each_user_with_empty_list():
    logger.info("[START] test_run_services_for_each_user_with_empty_list")

    aggregator = BaseUserAggregator(users=[])

    with pytest.raises(Exception):
        aggregator.run_services_for_each_user(Mock(spec=UserDataProcessor))

        logger.info("[END] test_run_services_for_each_user_with_empty_list")