
from django_filters import rest_framework as django_filter
from datetime import timedelta
import django_filters

from emails.models import MailAccount, MailInbox

class MailAccountFilterSet(django_filter.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    email = django_filters.CharFilter(field_name='email', lookup_expr='icontains')

    class Meta:
        model = MailAccount
        fields = ['name', 'email']

class MailFilterSet(django_filter.FilterSet):

    # email = django_filters.DateFilter(method='user__email', label='Email', input_formats=["%d-%m-%Y"])
    # date_to = django_filters.DateFilter(method='filter_date_to', label='Date To', input_formats=["%d-%m-%Y"])
    email = django_filters.CharFilter(field_name='mail_account__email', lookup_expr='icontains')

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