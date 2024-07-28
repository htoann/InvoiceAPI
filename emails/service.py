import datetime
import imaplib
import email
from typing import List

from emails.models import MailInbox
from email.header import decode_header


MAIL_SERVER = 'imap.gmail.com'

class EmailService:
    @classmethod
    def load_inbox(cls, email_param: str, password: str) -> List[dict]:
        # Kết nối và đăng nhập
        mail = imaplib.IMAP4_SSL(MAIL_SERVER)
        mail.login(email_param, password)
        mail.select('inbox')

        # Search for emails in the primary category
        status, data = mail.search(None, 'X-GM-RAW "category:primary"')

        mail_ids = [block.decode() for block in data[0].split()]

        # Sort mail IDs to get the newest emails
        mail_ids = sorted(mail_ids, key=lambda x: int(x), reverse=True)

        # Lấy 10 email đầu tiên
        mail_ids = mail_ids[:10]
        
        inbox_list = []

        for i in mail_ids:
            status, data = mail.fetch(i, '(RFC822)')
            for response_part in data:
                if isinstance(response_part, tuple):
                    message = email.message_from_bytes(response_part[1])

                    # Decode sender
                    sender, encoding = decode_header(message['from'])[0]
                    if isinstance(sender, bytes):
                        sender = sender.decode(encoding if encoding else 'utf-8')
                    
                    # Decode the email subject
                    subject, encoding = decode_header(message['subject'])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else 'utf-8')
                    
                    body = ""

                    if message.is_multipart():
                        for part in message.walk():
                            if part.get_content_type() == 'text/html':
                                payload = part.get_payload(decode=True)
                                if payload:
                                    body += payload.decode()
                    else:
                        payload = message.get_payload(decode=True)
                        if payload:
                            body = payload.decode()

                    # Thêm thông tin email vào danh sách
                    inbox_list.append({
                        "subject": subject, 
                        "sender": sender, 
                        "label": "Test", 
                        "date": datetime.datetime.now(), 
                        "body": body
                    })

        # Đóng kết nối và đăng xuất
        mail.close()
        mail.logout()

        return inbox_list