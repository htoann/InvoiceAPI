
from django_filters import rest_framework as django_filter
from datetime import timedelta
import django_filters

from emails.models import MailInbox

class MailFilterSet(django_filter.FilterSet):

    # email = django_filters.DateFilter(method='user__email', label='Email', input_formats=["%d-%m-%Y"])
    # date_to = django_filters.DateFilter(method='filter_date_to', label='Date To', input_formats=["%d-%m-%Y"])
    email = django_filters.CharFilter(field_name='mail_account__email', lookup_expr='exact')

    # def filter_date_from(self, queryset, name, value):
    #     if value:
    #         return queryset.filter(ntao__gte=value)
        
    #     return queryset

    # def filter_date_to(self, queryset, name, value):
    #     if value:
    #         value += timedelta(days=1)
    #         queryset = queryset.filter(ntao__lt=value)
        
    #     return queryset

    class Meta:
        model = MailInbox
        fields = ['email', 'sender']