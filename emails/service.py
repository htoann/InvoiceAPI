import datetime
import imaplib
import email
from typing import List

from emails.models import MailInbox


MAIL_SERVER = 'imap.gmail.com'

class EmailService:
  @classmethod
  def load_inbox(self, email_param: str, password: str) -> List[dict]:
      # Kết nối và đăng nhập
      mail = imaplib.IMAP4_SSL(MAIL_SERVER)
      mail.login(email_param, password)
      mail.select('inbox')

      status, data = mail.search(None, 'X-GM-RAW "category:primary"')

      mail_ids = [block.decode() for block in data[0].split()]

      # Lấy 10 email đầu tiên
      mail_ids = mail_ids[:10]
      
      inbox_list = []

      for i in mail_ids:
          status, data = mail.fetch(i, '(RFC822)')
          for response_part in data:
              if isinstance(response_part, tuple):
                  message = email.message_from_bytes(response_part[1])
                  mail_from = message['from']
                  mail_subject = message['subject']
                  mail_content = ""
                  
                  if message.is_multipart():
                    for part in message.get_payload():
                        if part.get_content_type() == 'text/plain':
                            payload = part.get_payload(decode=True)
                            if payload:
                                mail_content += payload.decode(part.get_content_charset(), errors='ignore')
                    else:
                        payload = message.get_payload(decode=True)
                        if payload:
                            mail_content = payload.decode(message.get_content_charset(), errors='ignore')

                  # Thêm thông tin email vào danh sách
                  inbox_list.append({"subject": mail_subject, "sender": mail_from, "label": "Test", "date": datetime.datetime.now(), "body": mail_content})

      # Đóng kết nối và đăng xuất
      mail.close()
      mail.logout()

      return inbox_list