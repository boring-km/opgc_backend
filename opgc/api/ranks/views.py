from rest_framework import mixins, viewsets, exceptions
from rest_framework.response import Response

from api.paginations import ScoreOrderingPagination, UserRankOrderingPagination
from api.ranks.serializers import RankSerializer, TierSerializer
from apps.githubs.models import GithubUser
from apps.ranks.models import UserRank


class RankViewSet(mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """
    endpoint : ranks/
    """

    queryset = UserRank.objects.prefetch_related('github_user').all()
    pagination_class = ScoreOrderingPagination
    serializer_class = RankSerializer

    def list(self, request, *args, **kwargs):
        rank_type = self.request.query_params.get('type')

        if not rank_type:
            raise exceptions.ValidationError

        queryset = self.filter_queryset(self.get_queryset()).filter(type=rank_type)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class OverallRankViewSet(mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    """
    endpoint : ranks/overall/
    """

    queryset = GithubUser.objects.filter(user_rank__isnull=False)
    serializer_class = TierSerializer
    pagination_class = UserRankOrderingPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        response = self.get_paginated_response(serializer.data)
        response.data['total_users'] = self.queryset.count()
        return response
