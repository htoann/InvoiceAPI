from rest_framework import serializers

from emails.models import MailAccount, MailInbox

class EmailAccountSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'email')
        model = MailAccount

class MailSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = MailInbox