# gsheet-logger

구글 스프레드시트를 로그 저장소로 사용하고, 지정된 수준 이상의 로그는 이메일로 알림까지 보내주는 Python 로깅 유틸리티입니다.

---

## 📋 주요 기능

- **Google Sheets** 에 로그를 쌓아 언제든지 실시간으로 확인 가능  
- **자동 헤더 생성** 및 **시트 공유**  
- 로그 **자동 정리** (14일 이상 전체 삭제, INFO 로그는 3일 이상 삭제)  
- **다양한 로그 레벨** 지원 (`INFO`, `WARNING`, `ERROR`, `CRITICAL` 등)  
- **이메일 알림**: 지정한 레벨 이상일 때 자동 발송  
- **단일 CLI** 로 예제 환경 `.env` 와 `service_account.json` 생성  

---

## 🔧 요구 사항

- Python 3.9 이상  
- 패키지: `gspread`, `click`, `python-dotenv`  

---

## 🚀 설치

1. **pip** 로 직접 GitHub 레포에서 설치
    ```bash
    pip install git+https://github.com/younjihoon/gsheet-logger.git
    ```
2. 패키지 내부 CLI 등록 확인
    ```bash
    which gsheet-init
    # → gsheet-init 커맨드가 보여야 정상
    ```

---

## ⚙️ 초기 설정

### 1) 예제 파일 복사

```bash
gsheet-init
```

- 프로젝트 루트에 `.env` 와 `service_account.json` 예시 파일이 생성됩니다.

### 2) 환경 변수 설정

`.env` 파일을 열고 아래 값을 본인 환경에 맞춰 수정하세요:

```dotenv
# .env

# 필수: 로그를 기록할 스프레드시트 URL
SPREADSHEET_URL=https://docs.google.com/spreadsheets/d/...

# 필수: 서비스 계정 JSON 경로
SERVICE_ACCOUNT_FILE=service_account.json

# 필수: 이메일 알림을 보낼 SMTP 계정
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# 선택: 알림을 받을 이메일 주소 (콤마로 구분)
EMAIL_RECIPIENTS=alice@example.com,bob@example.com

# 선택: 이메일 발송이 발생할 로그 레벨 (콤마로 구분)
EMAIL_LEVELS=ERROR,CRITICAL
```

- `service_account.json` 안에는 Google 서비스 계정 키를 그대로 복사·붙여넣기 합니다.

---

## 🎉 빠르게 시작하기 (예제)

```python
# your_script.py

from gsheet_logger.config_loader import load_config
from gsheet_logger.sheet_logger import GSheetLogger

# 1) 환경 변수 로드
cfg = load_config()

# 2) 로거 초기화
logger = GSheetLogger(
    sheet_url            = cfg["sheet_url"],
    sheet_name           = "로그",               # 시트 이름 (기본값: 워크북 첫번째 시트)
    smtp_user            = cfg["smtp_user"],
    smtp_password        = cfg["smtp_password"],
    email_recipients     = cfg["email_recipients"],
    email_levels         = cfg["email_levels"],
    service_account_file = cfg["service_account"]
)

# 3) 로그 남기기
logger.log("INFO",    "애플리케이션 시작")
logger.log("WARNING", "디스크 용량이 90% 초과")
logger.log("ERROR",   "데이터베이스 연결 실패", {"host": "db.example.com", "port": 5432})

# ▶ ERROR 레벨 이상은 이메일로 자동 알림이 발송됩니다.
```

---

## 📚 모든 사용 시나리오

### 1. 기본 로깅

```python
logger.log("INFO", "값이 정상 처리되었습니다.")
```

- 스프레드시트에 `[타임스탬프, INFO, "값이 정상 처리되었습니다.", ""]` 행 추가

### 2. 컨텍스트 포함

```python
logger.log("ERROR",
           "파일 읽기 중 예외 발생",
           {"filename": "data.csv", "error": str(e)})
```

- `Context` 열에 JSON 문자열로 `{"filename":"data.csv","error":"..."} ` 저장

### 3. 이메일 알림 커스터마이즈

- `.env` 의 `EMAIL_LEVELS` 값을 `WARNING,ERROR` 로 설정하면  
  `WARNING` 레벨 로그부터 메일 발송

### 4. 시트 이름 변경

- 기본 `sheet_name` 은 첫 번째 워크시트(`sheet1`).  
- `GSheetLogger(..., sheet_name="MyLogs", ...)` 처럼 지정

### 5. 로그 자동 정리

- **14일 초과** 모든 레벨 삭제  
- **3일 초과 INFO** 레벨만 삭제  

### 6. 예외시 디버그

- 구글 인증 실패, 시트 연결 오류 등은 **RuntimeError** 또는 **gspread.exceptions** 로 표시  
- 설치·환경 변수 누락 시 `load_config()` 에서 명확히 예외 발생

---

## 🛠️ CLI 상세

```bash
$ gsheet-init --help
Usage: cli [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  init  .env 및 service_account.json 예시 파일을 생성
```

1. `gsheet-init` :  
   - `config_templates/.env.example` → `./.env`  
   - `config_templates/service_account.example.json` → `./service_account.json`

---

## 🔄 GitHub Actions 연동 예시

```yaml
# .github/workflows/logging.yml
name: Run Script & Log

on:
  schedule:
    - cron: '0 * * * *'  # 매 시간 정각

jobs:
  run-and-log:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with: python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install git+https://github.com/yourname/gsheet-logger.git
          pip install -r requirements.txt
      - name: Initialize config
        run: gsheet-init
      - name: Populate .env
        run: |
          echo "SPREADSHEET_URL=$SPREADSHEET_URL" >> .env
          echo "SERVICE_ACCOUNT_FILE=service_account.json" >> .env
          echo "SMTP_USER=$SMTP_USER" >> .env
          echo "SMTP_PASSWORD=$SMTP_PASSWORD" >> .env
      - name: Run your script
        run: python your_script.py
        env:
          SPREADSHEET_URL: ${{ secrets.SPREADSHEET_URL }}
          SERVICE_ACCOUNT_FILE: service_account.json
          SMTP_USER: ${{ secrets.SMTP_USER }}
          SMTP_PASSWORD: ${{ secrets.SMTP_PASSWORD }}
          EMAIL_RECIPIENTS: ${{ secrets.EMAIL_RECIPIENTS }}
          EMAIL_LEVELS: ${{ secrets.EMAIL_LEVELS }}
```

---

## 🤝 기여 및 라이선스

- PR, Issue 환영합니다!  
- MIT License  

---

이제 **`pip install git+https://github.com/yourname/gsheet-logger.git` → `gsheet-init` → `.env` 수정 → import & `logger.log()`** 로  
모든 로깅/알림 시나리오를 한 번에 해결하세요!





---
---
---

# gsheet-logger

A Python logging utility that writes logs to Google Sheets and sends email alerts for specified log levels.

---

## 🎯 Key Features

- **Google Sheets storage**: Write logs in real time to a shared spreadsheet  
- **Automatic header setup** and **sheet sharing**  
- **Auto-cleanup** of old logs (delete all entries older than 14 days; remove INFO entries older than 3 days)  
- Support for standard **log levels** (INFO, WARNING, ERROR, CRITICAL, etc.)  
- **Email notifications** for logs at specified levels  
- **One-step CLI** to generate example `.env` and service account JSON  

---

## 🛠︎ Requirements

- Python 3.9+  
- Dependencies:
  - `gspread`
  - `click`
  - `python-dotenv`

---

## 🚀 Installation

Install directly from GitHub:

```bash
pip install git+https://github.com/younjihoon/gsheet-logger.git
```

Verify the CLI command was registered:

```bash
which gsheet-init
# Should output the path to the gsheet-init executable
```

---

## ⚙️ Initial Setup

### 1) Generate example config files

```bash
gsheet-init
```

This creates:

- `.env` (environment variable template)  
- `service_account.json` (Google service account template)  

### 2) Populate your `.env`

Open `.env` and fill in your own values:

```dotenv
# .env

# Required: URL of the Google Spreadsheet to log into
SPREADSHEET_URL=https://docs.google.com/spreadsheets/d/...

# Required: Path to service account JSON
SERVICE_ACCOUNT_FILE=service_account.json

# Required: SMTP credentials for email alerts
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Optional: Comma-separated addresses to notify
EMAIL_RECIPIENTS=alice@example.com,bob@example.com

# Optional: Levels that trigger email (comma-separated)
EMAIL_LEVELS=ERROR,CRITICAL
```

Copy your Google service account JSON into `service_account.json`.

---

## 🎉 Quickstart (Example)

```python
# example.py

from gsheet_logger.config_loader import load_config
from gsheet_logger.sheet_logger import GSheetLogger

# 1) Load configuration from env
cfg = load_config()

# 2) Initialize logger
logger = GSheetLogger(
    sheet_url            = cfg["sheet_url"],
    sheet_name           = "Logs",               # defaults to first sheet
    smtp_user            = cfg["smtp_user"],
    smtp_password        = cfg["smtp_password"],
    email_recipients     = cfg["email_recipients"],
    email_levels         = cfg["email_levels"],
    service_account_file = cfg["service_account"]
)

# 3) Log messages
logger.log("INFO",    "Application started")
logger.log("WARNING", "Disk usage at 90%")
logger.log("ERROR",   "Database connection failed", {"host": "db.example.com", "port": 5432})

# ERROR and above will also trigger an email alert automatically.
```

---

## 📚 Usage Scenarios

1. **Basic logging**  
   ```python
   logger.log("INFO", "Operation completed successfully.")
   ```
   Writes a new row: `[timestamp, INFO, "Operation completed successfully.", ""]`

2. **With context payload**  
   ```python
   logger.log("ERROR",
              "Failed to read file",
              {"filename": "data.csv", "error": str(e)})
   ```
   Context column stores `{"filename":"data.csv","error":"…"}`
   
3. **Custom email levels**  
   Set `EMAIL_LEVELS=WARNING,ERROR` in `.env` to receive emails starting at WARNING.

4. **Custom sheet name**  
   ```python
   GSheetLogger(..., sheet_name="MyAppLogs", ...)
   ```

5. **Automatic cleanup**  
   - Deletes any log older than 14 days  
   - Deletes INFO logs older than 3 days  

6. **Error handling**  
   - Missing env vars: raised by `load_config()`  
   - Google API errors: surfaced as `gspread` exceptions  

---

## 💻 CLI Commands

```bash
$ gsheet-init --help
Usage: cli [OPTIONS] COMMAND [ARGS]...

Commands:
  init  Generate example .env and service_account.json files
```

- `gsheet-init` copies:
  - `config_templates/.env.example` → `./.env`
  - `config_templates/service_account.example.json` → `./service_account.json`

---

## 🔄 GitHub Actions Example

```yaml
# .github/workflows/logging.yml
name: Run & Log

on:
  schedule:
    - cron: '0 * * * *'  # every hour

jobs:
  log-job:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with: python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install git+https://github.com/yourname/gsheet-logger.git
      - name: Initialize config
        run: gsheet-init
      - name: Populate .env
        run: |
          echo "SPREADSHEET_URL=${{ secrets.SPREADSHEET_URL }}" >> .env
          echo "SERVICE_ACCOUNT_FILE=service_account.json" >> .env
          echo "SMTP_USER=${{ secrets.SMTP_USER }}" >> .env
          echo "SMTP_PASSWORD=${{ secrets.SMTP_PASSWORD }}" >> .env
      - name: Run script
        run: python example.py
        env:
          SPREADSHEET_URL: ${{ secrets.SPREADSHEET_URL }}
          SERVICE_ACCOUNT_FILE: service_account.json
          SMTP_USER: ${{ secrets.SMTP_USER }}
          SMTP_PASSWORD: ${{ secrets.SMTP_PASSWORD }}
          EMAIL_RECIPIENTS: ${{ secrets.EMAIL_RECIPIENTS }}
          EMAIL_LEVELS: ${{ secrets.EMAIL_LEVELS }}
```

---

## 🤝 Contributing & License

- Contributions welcome via PRs and Issues  
- Licensed under the MIT License  
```