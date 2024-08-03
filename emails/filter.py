
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
    email = django_filters.CharFilter(field_name='mail_account__email', lookup_expr='icontains')

    class Meta:
        model = MailInbox
        fields = ['email', 'sender']
