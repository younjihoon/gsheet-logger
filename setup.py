from setuptools import setup, find_packages

setup(
    name="gsheet-logger",
    version="0.1.0",
    description="Google Sheets 기반 로깅 & 알림 유틸리티",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "gspread",
        "python-dotenv",
        "click",
    ],
    entry_points={
        "console_scripts": [
            "gsheet-init = gsheet_logger.cli:cli",
        ]
    },
    python_requires=">=3.9",
)
