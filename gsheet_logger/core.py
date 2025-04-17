from __future__ import annotations
import json, os, warnings, smtplib
from datetime import datetime
from typing import List, Dict, Optional
from zoneinfo import ZoneInfo
from email.message import EmailMessage
import pathlib
import gspread
from dotenv import load_dotenv

load_dotenv()  # allow user‑provided .env

_CFG_DIR  = os.path.join(os.path.expanduser("~"), ".config", "gsheet_logger")
_CFG_PATH = os.path.join(_CFG_DIR, "config.json")


def _load_cfg() -> Dict[str, str]:
    if os.path.exists(_CFG_PATH):
        with open(_CFG_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_cfg(cfg: Dict[str, str]) -> None:
    os.makedirs(_CFG_DIR, exist_ok=True)
    with open(_CFG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


class GSheetLogger:
    """
    Lightweight Google‑Sheet logger with optional Gmail alerts.

    * No hard singleton; id‑based registry only warns on duplicates.
    * URL supplied  →  **not persisted** in config (explicit beats implicit).
    * URL absent    →  id‑lookup -> auto‑create -> persist.
    """

    _registry: Dict[str, "GSheetLogger"] = {}

    # ―――――――――――――――――――――――――――――――――――――――――――――――――
    def __init__(
        self,
        *,
        sheet_url: str | None = None,
        logger_id: str | None = None,
        sheet_name: str = "Logs",
        smtp_user: str | None = os.getenv("SMTP_USER"),
        smtp_password: str | None = os.getenv("SMTP_PASSWORD"),
        email_recipients: List[str] | None = None,
        email_levels: List[str] | None = None,
        service_account_file: str = "service_account.json",
        persist: bool = True,
    ) -> None:
        explicit_url      = sheet_url is not None
        logger_id         = logger_id or ("_explicit_" if explicit_url else "default")
        self.email_levels = {lvl.upper() for lvl in (email_levels or [])}
        self.email_recipients = email_recipients or []
        self.smtp_user, self.smtp_password = smtp_user, smtp_password

        # warn on duplicate id in same process
        if logger_id in self._registry:
            warnings.warn(f"GSheetLogger '{logger_id}' already exists.", UserWarning)
        self._registry[logger_id] = self

        # config lookup / persist
        cfg = _load_cfg()
        if explicit_url:
            # do not overwrite config with explicit value
            persist = False
            if logger_id in cfg and cfg[logger_id] != sheet_url:
                warnings.warn(
                    f"logger_id '{logger_id}' had different stored URL – "
                    "running with explicit URL (not persisted).",
                    UserWarning,
                )
        else:
            sheet_url = cfg.get(logger_id)

        # open or create sheet -------------------------------------------------
        key_path = pathlib.Path(service_account_file).expanduser()

        if not key_path.is_file():
            raise FileNotFoundError(
                f"\n✖  Service‑account key file not found:  {key_path}\n"
                "   · Go to **Google Cloud Console → IAM & Admin → Service Accounts**\n"
                "   · Create / pick a service account → Keys → “Create key” (JSON)\n"
                "   · Save the JSON next to your script, or anywhere, e.g.  ~/.secrets/key.json\n"
                "   · Then run again with either\n"
                "       GSheetLogger(service_account_file='/full/path/key.json')\n"
                "     or\n"
                "       export GSHEET_LOGGER_KEY=/full/path/key.json   # in .env / shell\n"
            )

        # keep the filename the rest of the code expects
        service_account_file = str(key_path)
        
        self.gc = gspread.service_account(filename=service_account_file)
        if sheet_url:
            sh = self.gc.open_by_url(sheet_url)
        else:
            sh = self.gc.create(sheet_name)
            sheet_url = sh.url
            if persist:
                cfg[logger_id] = sheet_url
                _save_cfg(cfg)

        # share (only once, harmless if already shared)
        for rec in self.email_recipients:
            try:
                sh.share(rec, perm_type="user", role="writer", notify=False)
            except Exception:
                pass

        # worksheet ------------------------------------------------------------
        try:
            self.ws = sh.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            self.ws = sh.add_worksheet(title=sheet_name, rows=1000, cols=4)

        if not self.ws.get_all_values():
            self.ws.append_row(["Timestamp", "Level", "Message", "Context"])

        self._cleanup_once()

    def _cleanup_once(self) -> None:
        rows = self.ws.get_all_values()
        if len(rows) < 2:
            return
        hdr, data = rows[0], rows[1:]
        now = datetime.now(ZoneInfo("Asia/Seoul"))
        keep = []
        for r in data:
            try:
                ts = datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S")
            except Exception:
                continue
            days = (now - ts).days
            lvl  = (r[1] or "").upper()
            if days >= 14 or (lvl == "INFO" and days >= 3):
                continue
            keep.append(r)
        self.ws.clear()
        self.ws.update("A1", [hdr] + keep)

    def _mail(self, lvl: str, msg: str, ctx: str) -> None:
        if not (self.smtp_user and self.smtp_password and self.email_recipients):
            return
        m = EmailMessage()
        m["Subject"] = f"[{lvl}] Log Notification"
        m["From"] = self.smtp_user
        m["To"] = ",".join(self.email_recipients)
        m.set_content(f"Level: {lvl}\nMessage: {msg}\nContext: {ctx}")
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as s:
                s.starttls()
                s.login(self.smtp_user, self.smtp_password)
                s.send_message(m)
        except Exception as e:
            warnings.warn(f"Email send failed: {e}", RuntimeWarning)

    def log(self, level: str, message: str, context: dict | None = None) -> None:
        ts  = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")
        lvl = level.upper()
        ctx = json.dumps(context or {}, ensure_ascii=False)
        try:
            self.ws.append_row([ts, lvl, message, ctx])
        except Exception as e:
            warnings.warn(f"Sheet append failed: {e}", RuntimeWarning)
        if lvl in self.email_levels:
            self._mail(lvl, message, ctx)

    # optional getter
    @property
    def url(self) -> str:
        return self.ws.spreadsheet.url
