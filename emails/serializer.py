from rest_framework import serializers

from emails.models import MailAccount, MailInbox
from emails.service import EmailService

class EmailAccountSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'email', 'password')
        model = MailAccount

    def create(self, validated_data):
        mail_account = MailAccount.objects.create(**validated_data)
        
        inboxes = EmailService.load_inbox(validated_data['email'], validated_data['password'])
        for inbox in inboxes:
            MailInbox.objects.create(mail_account=mail_account, **inbox)
        return mail_account

class MailSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = MailInbox