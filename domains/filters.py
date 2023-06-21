from django_filters import rest_framework as filters

from domains.models import AccessLogs

class LogFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name='created_at__date', lookup_expr='gte', )
    end_date = filters.DateFilter(field_name='created_at__date', lookup_expr='lte')

    class Meta:
        model = AccessLogs
        fields = ('domain', 'start_date', 'end_date')