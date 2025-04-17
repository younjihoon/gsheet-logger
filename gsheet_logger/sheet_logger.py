import json
from datetime import datetime
from zoneinfo import ZoneInfo
import gspread
from email.message import EmailMessage
import smtplib

class GSheetLogger:
    def __init__(self,
                 sheet_url: str,
                 sheet_name: str,
                 smtp_user: str,
                 smtp_password: str,
                 email_recipients: list,
                 email_levels: list,
                 service_account_file: str):
        self.sheet_url       = sheet_url
        self.sheet_name      = sheet_name
        self.smtp_user       = smtp_user
        self.smtp_password   = smtp_password
        self.email_recipients= email_recipients
        self.email_levels    = [lvl.upper() for lvl in email_levels]

        # Google Sheets 인증 & 시트 준비
        self.gc = gspread.service_account(filename=service_account_file)
        try:
            sh = self.gc.open_by_url(sheet_url)
            self.ws = sh.worksheet(sheet_name)
        except gspread.exceptions.SpreadsheetNotFound:
            sh = self.gc.create(sheet_name)
            self.ws = sh.sheet1
            self.ws.append_row(["Timestamp","Level","Message","Context"])
            sh.share(self.email_recipients, perm_type="user", role="writer", notify=False)

        # 오래된 로그 자동 정리
        self._cleanup_old_logs()

    def _cleanup_old_logs(self):
        """14일 전체 삭제, INFO는 3일 초과 삭제"""
        rows = self.ws.get_all_values()
        if len(rows) < 2:
            return
        header, data = rows[0], rows[1:]
        now = datetime.now(ZoneInfo("Asia/Seoul"))
        keep = []
        for row in data:
            try:
                ts = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
            except:
                continue
            age = (now - ts).days
            lvl = (row[1] or "").upper()
            if age >= 14 or (lvl == "INFO" and age >= 3):
                continue
            keep.append(row)
        self.ws.clear()
        self.ws.update("A1", [header] + keep)

    def _send_email(self, level, message, context_str):
        msg = EmailMessage()
        msg["Subject"] = f"[{level}] Log Notification"
        msg["From"]    = self.smtp_user
        msg["To"]      = ",".join(self.email_recipients)
        body = f"Level: {level}\nMessage: {message}\nContext: {context_str}"
        msg.set_content(body)
        with smtplib.SMTP("smtp.gmail.com", 587) as s:
            s.starttls()
            s.login(self.smtp_user, self.smtp_password)
            s.send_message(msg)

    def log(self, level: str, message: str, context: dict = None):
        ts = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")
        lvl = level.upper()
        ctx = json.dumps(context) if context else ""
        self.ws.append_row([ts, lvl, message, ctx])
        if lvl in self.email_levels:
            self._send_email(lvl, message, ctx)
