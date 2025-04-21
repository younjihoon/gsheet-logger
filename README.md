# gsheet‑logger

[🇬🇧 English](#english) | [🇰🇷 한국어](#한국어)

---

## English

**Tiny Gmail‑alerting Google‑Sheet logger**

A lightweight Python logger that appends rows to a Google Sheet and (optionally) sends Gmail alerts for specified levels.

### Features

- Append timestamped logs to a Google Sheet  
- Auto‑create spreadsheet / worksheet if not exists  
- Retain recent rows only (INFO → 3 days, others → 14 days)  
- Optional Gmail alerts on ERROR/CRITICAL (configurable levels)  
- Persists default sheet URLs per `logger_id` under `~/.config/gsheet_logger/config.json`  
- No hard singleton—multiple loggers by `logger_id` with a warning on duplicates  

### Installation

```bash
# from PyPI
pip install gsheet-logger

# or directly from GitHub
pip install git+https://github.com/younjihoon/gsheet-logger.git
```

### Prerequisites

1. **Google service account key** (JSON)  
   - Create in Google Cloud Console → IAM & Admin → Service Accounts → Keys → “Create key” (JSON)  
   - Save it locally, e.g. `~/.secrets/gsheet-key.json`  
   - Point to it via env var or argument (see “Configuration”)

2. **Environment variables** (in `.env` or shell):

   ```dotenv
   # path to your service account JSON
   GSHEET_LOGGER_KEY=~/.secrets/gsheet-key.json

   # for Gmail alerts (optional)
   SMTP_USER=your.email@gmail.com
   SMTP_PASSWORD=your_app_password
   ```

### Quickstart

```python
from gsheet_logger import GSheetLogger

# 1) use a default spreadsheet (will auto‑create and persist URL)
logger = GSheetLogger(
    logger_id="default",               # identifier for this logger
    sheet_name="MyLogs",               # worksheet title
    email_recipients=["ops@domain.com"], 
    email_levels=["ERROR", "CRITICAL"] # which levels trigger Gmail alerts
)

# 2) or supply an explicit sheet URL (not persisted)
logger2 = GSheetLogger(
    sheet_url="https://docs.google.com/…",
    sheet_name="Alerts",
)

# 3) log messages
logger.log("INFO", "Startup complete", {"version": "0.1"})
logger.log("ERROR", "Exception occurred", {"error": "ValueError"})

# 4) inspect spreadsheet URL
print("Logging to:", logger.url)
```

### Configuration details

| Parameter              | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| `sheet_url`            | Full URL to existing sheet (explicit, not saved).                           |
| `logger_id`            | Unique key for default sheet lookup/persistence (`default` if omitted).     |
| `sheet_name`           | Worksheet title inside the spreadsheet (defaults to `"Logs"`).              |
| `email_recipients`     | List of Gmail addresses to share sheet & receive alerts.                    |
| `email_levels`         | Log levels (e.g. `["ERROR"]`) that trigger `_mail()` notifications.         |
| `service_account_file` | Path to Google service account JSON (env `GSHEET_LOGGER_KEY` overrides).    |

Config is auto‑saved under:
```
~/.config/gsheet_logger/config.json
```

### Cleanup policy

- INFO rows older than 3 days → purged
- All other levels older than 14 days → purged  
Executed once on initialization.

---

## 한국어

**작고 가벼운 Gmail 알림 기능이 포함된 Google Sheet 로거**

Google Sheet에 로그를 추가하고, 지정한 레벨에 대해 Gmail로 알림을 보내는 파이썬 로거입니다.

### 주요 기능

- Google Sheet에 타임스탬프 로그 행 추가  
- 시트/워크시트가 없으면 자동 생성  
- 최근 로그만 보관 (INFO → 3일, 기타 → 14일)  
- ERROR/CRITICAL 레벨에 한해 Gmail 알림 전송(레벨 설정 가능)  
- `logger_id`별 기본 시트 URL을 `~/.config/gsheet_logger/config.json`에 저장  
- 강제 싱글톤이 아니며, 중복 생성 시 경고만 발생  

### 설치 방법

```bash
# PyPI에서 설치
pip install gsheet-logger

# GitHub에서 바로 설치
pip install git+https://github.com/younjihoon/gsheet-logger.git
```

### 사전 준비

1. **Google 서비스 계정 키** (JSON)  
   - Google Cloud Console → IAM & Admin → Service Accounts → Keys → “Create key” (JSON)  
   - 로컬에 저장 (예: `~/.secrets/gsheet-key.json`)  
   - 환경 변수 또는 인자로 경로 지정

2. **환경 변수** (`.env` 파일 또는 셸 설정):

   ```dotenv
   # 서비스 계정 JSON 경로
   GSHEET_LOGGER_KEY=~/.secrets/gsheet-key.json

   # Gmail 알림용 (선택)
   SMTP_USER=your.email@gmail.com
   SMTP_PASSWORD=your_app_password
   ```

### 빠른 시작 예제

```python
from gsheet_logger import GSheetLogger

# 1) 기본 시트 사용 (자동 생성 및 URL 저장)
logger = GSheetLogger(
    logger_id="default",               # 로거 식별자
    sheet_name="MyLogs",               # 워크시트 제목
    email_recipients=["ops@domain.com"], 
    email_levels=["ERROR", "CRITICAL"] # 알림을 보낼 레벨
)

# 2) 명시적 시트 URL 사용 (저장되지 않음)
logger2 = GSheetLogger(
    sheet_url="https://docs.google.com/…",
    sheet_name="Alerts",
)

# 3) 로그 기록
logger.log("INFO", "앱 시작 완료", {"version": "0.1"})
logger.log("ERROR", "예외 발생", {"error": "ValueError"})

# 4) 시트 URL 확인
print("로그 저장 URL:", logger.url)
```

### 설정 파라미터

| 파라미터                   | 설명                                                                 |
|----------------------------|----------------------------------------------------------------------|
| `sheet_url`                | 기존 스프레드시트 URL (명시적, 저장되지 않음)                         |
| `logger_id`                | 기본 시트 조회/저장용 고유 키 (`default` 기본값)                    |
| `sheet_name`               | 워크시트 제목 (기본 `"Logs"`)                                        |
| `email_recipients`         | 시트를 공유하고 알림을 받을 Gmail 주소 리스트                         |
| `email_levels`             | 어떤 레벨에서 `_mail()` 알림을 보낼지 설정 (예: `["ERROR"]`)         |
| `service_account_file`     | 서비스 계정 JSON 경로 (환경 변수 `GSHEET_LOGGER_KEY` 우선)           |

설정 파일 위치:
```
~/.config/gsheet_logger/config.json
```

### 로그 정리 정책

- INFO 레벨 로그: 3일 경과 시 삭제  
- 그 외 레벨 로그: 14일 경과 시 삭제  
- 초기화 시 한 번 실행하여 불필요한 행 정리  

---

© 2025 Yun jihun  
MIT License  
