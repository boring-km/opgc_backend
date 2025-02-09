import json
from contextlib import contextmanager
from typing import Optional

from rest_framework import status

from apps.githubs.models import GithubUser
from apps.reservations.models import UpdateUserQueue


# 204: 컨텐츠 제공안함
# 451: 저작권
PASSING_RESPONSE_STATUS = [status.HTTP_204_NO_CONTENT, status.HTTP_405_METHOD_NOT_ALLOWED]
REASON_RATE_LIMIT = 'rate limit exceeded'
REASON_FORBIDDEN = 'Forbidden'
PASSING_STATUS = 'pass'


class GitHubUserDoesNotExist(Exception):
    def __str__(self):
        return "not exists github user."


class RateLimit(Exception):
    def __str__(self):
        return "github api rate limited."


def manage_api_call_fail(
    github_user: GithubUser,
    status_code: int,
    reason: str = None
) -> Optional[str]:

    if not github_user:
        return None

    if status_code == status.HTTP_403_FORBIDDEN and reason == REASON_RATE_LIMIT:
        raise RateLimit()
    elif status_code == status.HTTP_403_FORBIDDEN and reason == REASON_FORBIDDEN:
        return REASON_FORBIDDEN
    elif status_code in PASSING_RESPONSE_STATUS:
        return PASSING_STATUS

    github_user.status = GithubUser.FAIL
    github_user.save(update_fields=['status'])
    insert_queue(github_user.username)

    return None


def insert_queue(username: str):
    # 큐에 저장해서 30분만다 실행되는 스크립트에서 업데이트
    if not UpdateUserQueue.objects.filter(username=username).exists():
        UpdateUserQueue.objects.create(
            username=username,
            status=UpdateUserQueue.READY
        )


@contextmanager
def json_handler_manager():
    try:
        yield 1
    except json.JSONDecodeError:
        pass
