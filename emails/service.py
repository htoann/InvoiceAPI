import os
import datetime
import imaplib
import email
from typing import List
from email.header import decode_header

MAIL_SERVER = 'imap.gmail.com'
ATTACHMENTS_DIR = 'attachments'  # Định nghĩa thư mục lưu trữ tệp đính kèm

class EmailService:
    @classmethod
    def load_inbox(cls, email_param: str, password: str) -> List[dict]:
        mail = cls.connect_and_login(email_param, password)
        mail_ids = cls.fetch_mail_ids(mail)
        inbox_list = cls.fetch_emails(mail, mail_ids)
        mail.close()
        mail.logout()
        return inbox_list

    @staticmethod
    def connect_and_login(email_param: str, password: str):
        mail = imaplib.IMAP4_SSL(MAIL_SERVER)
        mail.login(email_param, password)
        mail.select('inbox')
        return mail

    @staticmethod
    def fetch_mail_ids(mail) -> List[str]:
        status, data = mail.search(None, 'X-GM-RAW "category:primary"')
        mail_ids = [block.decode() for block in data[0].split()]
        mail_ids = sorted(mail_ids, key=lambda x: int(x), reverse=True)
        return mail_ids[:10]

    @classmethod
    def fetch_emails(cls, mail, mail_ids: List[str]) -> List[dict]:
        """
        Lấy thông tin chi tiết của các email từ danh sách ID.

        Args:
            mail (imaplib.IMAP4_SSL): Đối tượng kết nối IMAP.
            mail_ids (List[str]): Danh sách các ID email.

        Returns:
            List[dict]: Danh sách thông tin chi tiết của các email.
        """
        inbox_list = []
        if not os.path.exists(ATTACHMENTS_DIR):
            os.makedirs(ATTACHMENTS_DIR)

        for i in mail_ids:
            status, data = mail.fetch(i, '(RFC822)')
            for response_part in data:
                if isinstance(response_part, tuple):
                    message = email.message_from_bytes(response_part[1])
                    sender = cls.decode_header(message['from'])
                    subject = cls.decode_header(message['subject'])
                    body, attachments = cls.extract_body_and_attachments(message)
                    
                    # Thêm thông tin email vào danh sách
                    inbox_list.append({
                        "subject": subject,
                        "sender": sender,
                        "label": "Test",
                        "date": datetime.datetime.now(),
                        "body": body,
                        # "attachments": attachments  # Include attachments information
                    })

        return inbox_list

    @staticmethod
    def decode_header(header_value: str) -> str:
        value, encoding = decode_header(header_value)[0]
        if isinstance(value, bytes):
            value = value.decode(encoding if encoding else 'utf-8')
        return value

    @staticmethod
    def extract_body_and_attachments(message) -> (str, List[str]): # type: ignore
        """
        Trích xuất nội dung và tệp đính kèm từ email.

        Args:
            message (email.message.Message): Đối tượng email.

        Returns:
            Tuple[str, List[str]]: Nội dung email và danh sách đường dẫn tệp đính kèm.
        """
        body = ""
        attachments = []

        if message.is_multipart():
            for part in message.walk():
                content_type = part.get_content_type()
                content_disposition = part.get('Content-Disposition', '')
                
                if content_type == 'text/html' and 'attachment' not in content_disposition:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body += payload.decode()

                if 'attachment' in content_disposition:
                    filepath = EmailService.save_attachment(part)
                    if filepath:
                        attachments.append(filepath)
        else:
            payload = message.get_payload(decode=True)
            if payload:
                body = payload.decode()

        return body, attachments

    @staticmethod
    def save_attachment(part) -> str:
        """
        Lưu tệp đính kèm từ một phần của email.

        Args:
            part (email.message.Message): Phần chứa tệp đính kèm.

        Returns:
            str: Đường dẫn đến tệp đính kèm đã được lưu hoặc None nếu không lưu được.
        """
        filename = part.get_filename()
        if filename:
            decoded_filename, encoding = decode_header(filename)[0]
            if isinstance(decoded_filename, bytes):
                filename = decoded_filename.decode(encoding if encoding else 'utf-8')

            filepath = os.path.join(ATTACHMENTS_DIR, filename)
            with open(filepath, 'wb') as f:
                f.write(part.get_payload(decode=True))
            return filepath
        return None
