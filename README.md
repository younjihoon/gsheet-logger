## English
# gsheet‑logger

[🇬🇧 English](#english) | [🇰🇷 한국어](#한국어)

---


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

# GSheetLogger

## 개요
GSheetLogger는 Python 애플리케이션에서 Google Sheets를 로그 저장소로 사용하고, 선택적으로 Gmail 알림을 보낼 수 있는 경량 로거입니다. 기본적으로 동기(synchronous) 방식으로 동작하며, 설정이 간편합니다.

## 주요 기능
- **Google Sheets 기록**: Timestamp, Level, Message, Context 네 가지 컬럼으로 로그 기록
- **버퍼링**: 지정된 `buffer_size`만큼 로그가 쌓이면 일괄 전송(기본값: 100)
- **이메일 알림**: `ERROR`/`CRITICAL` 레벨 또는 `email_levels`에 지정된 레벨에 대해 Gmail 알림 전송
- **자동 시트 생성 및 설정 지속화**: `logger_id`별 URL을 config.json에 저장
- **자동 정리**: 14일 이상된 로그(또는 INFO 레벨 3일 이상된 로그) 자동 삭제

## 요구사항
- Python 3.9 이상
- 의존 패키지:
  - `gspread`
  - `google-auth`
  - `python-dotenv`

## 설치
```bash
pip install gspread google-auth python-dotenv
```
또는
```bash
pip install git+https://github.com/younjihoon/gsheet-logger.git
```

## 설정
1. **Google Cloud Console**에서 서비스 계정 생성 및 JSON 키 파일 다운로드
2. 프로젝트 루트에 `.env` 파일 생성 후 다음 설정 추가:
   ```ini
   GSHEET_LOGGER_KEY=/full/path/to/service_account.json
   SMTP_USER=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   EMAIL_RECIPIENTS=recipient1@gmail.com,recipient2@example.com
   ```
3. `.env`는 스크립트 실행 디렉터리에 두거나, 기본적으로 `$HOME/.config/gsheet_logger/config.json`에 설정이 저장됩니다.

## 사용법
```python
from your_module import GSheetLogger

# 1) 기본 인스턴스 생성 (persist=True일 경우 config.json에 URL 저장)
logger = GSheetLogger(
    sheet_name="Logs",
    logger_id="default",
    email_levels=["ERROR", "WARNING"],  # 알림 보낼 레벨
)

# 2) 로그 기록
logger.log("INFO", "작업 시작", {"task": "daily_job"})
logger.log("ERROR", "오류 발생", {"error": str(exception)})

# 3) 버퍼에 남은 로그 강제 전송
logger.flush()

# 4) 스프레드시트 URL 확인
print("로그 시트 URL:", logger.url)
```

### Explicit URL 지정
```python
logger2 = GSheetLogger(
    sheet_url="https://docs.google.com/spreadsheets/...",
    sheet_name="MyLogs",
    persist=False  # 명시적 URL은 config에 저장되지 않음
)
```

## 메서드 설명
- `__init__(...)` : 인스턴스 생성, config 로드·저장, 시트(또는 워크시트) 생성
- `log(level: str, message: str, context: dict | None)` : 단일 로그 기록 (버퍼링 혹은 즉시 전송)
- `flush()` : 버퍼에 쌓인 로그를 한 번에 전송
- `url` (프로퍼티) : 현재 스프레드시트 URL 반환

## 동시성 고려사항
GSheetLogger는 **동기** 방식으로 구현되어 있어, **단일 스레드/프로세스** 환경에서는 안전하게 동작합니다. 그러나 멀티스레드, 멀티프로세스 또는 비동기(asyncio) 환경에서 동시에 `log()`를 호출할 경우 내부 버퍼(`self.buffer`)와 워크시트(`self.ws`) 접근에서 **경쟁 상태(race condition)**가 발생할 수 있습니다.

- **멀티스레드**: `threading.Lock`으로 `logger.log()` 및 `flush()` 호출을 보호하세요.
- **멀티프로세스**: 프로세스별로 별도 인스턴스를 사용하거나, IPC를 통해 단일 로거에 접근하세요.
- **asyncio**: `asyncio.to_thread(logger.log, ...)` 혹은 `run_in_executor`로 동기 호출하거나, gspread-async 같은 라이브러리 사용을 고려하세요.

## FAQ
**Q: Gmail 알림을 비활성화하고 싶어요.**  
A: `email_levels`를 빈 리스트로 지정하거나, `email_recipients`를 설정하지 않으면 알림이 전송되지 않습니다.

**Q: config.json 위치는 어디인가요?**  
A: 기본적으로 `$HOME/.config/gsheet_logger/config.json`이며, `logger_id`별로 시트 URL을 저장합니다.

## 라이선스
MIT License

