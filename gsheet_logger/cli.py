import os, shutil
import click

TEMPLATE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../config_templates"))

@click.group()
def cli():
    """gsheet-logger 초기화 도구."""
    pass

@cli.command("init")
def init():
    """
    config_templates의 예시 파일을
      .env,
      service_account.json
    로 복사해줍니다.
    """
    examples = [
        (".env.example",       ".env"),
        ("service_account.example.json", "service_account.json"),
    ]
    for src, dst in examples:
        srcp = os.path.join(TEMPLATE_DIR, src)
        if os.path.exists(dst):
            click.echo(f"⚠️  {dst} already exists, skipped.")
        else:
            shutil.copy(srcp, dst)
            click.echo(f"✅  {dst} created.")
    click.echo("\n이제 `.env` 와 `service_account.json` 을 열어 본인 설정으로 채워주세요.")
