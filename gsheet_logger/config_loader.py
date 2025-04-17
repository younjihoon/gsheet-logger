import os

def load_config():
    """
    필수 환경변수:
      - SPREADSHEET_URL
      - SERVICE_ACCOUNT_FILE
      - SMTP_USER
      - SMTP_PASSWORD
    선택 환경변수:
      - EMAIL_RECIPIENTS (콤마 구분)
      - EMAIL_LEVELS     (콤마 구분)
    """
    cfg = {
        "sheet_url":       os.getenv("SPREADSHEET_URL"),
        "service_account": os.getenv("SERVICE_ACCOUNT_FILE"),
        "smtp_user":       os.getenv("SMTP_USER"),
        "smtp_password":   os.getenv("SMTP_PASSWORD"),
        "email_recipients": os.getenv("EMAIL_RECIPIENTS", "").split(","),
        "email_levels":     os.getenv("EMAIL_LEVELS", "ERROR,CRITICAL").split(","),
    }
    missing = [k for k in ("sheet_url","service_account","smtp_user","smtp_password")
               if not cfg[k]]
    if missing:
        raise RuntimeError(f"[gsheet-logger] Missing env vars: {', '.join(missing)}")
    return cfg
