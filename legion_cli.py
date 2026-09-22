import click
import os

@click.group()
def cli():
    """🦔 РОБОТ-ЁЖИК CLI: Управление портами Бронепоезда Miroha Monolith"""
    pass

@cli.command()
def status():
    """📊 Показать шеренгу активных портов в LISTEN ОЗУ"""
    os.system("ss -tlnp | grep -E '5432|9000|8000|5000|:80'")

@cli.command()
def restart():
    """🔄 Экстренная ОЗУ-перезагрузка всех трех микросервисов синдиката"""
    os.system("pkill -f 'manage.py' ; pkill -f 'flask' ; pkill -f 'fastapi' || true")
    os.system("nohup /root/app/hello/bin/python3 /root/app/manage.py runserver 0.0.0.0:8000 --noreload --nostatic > /root/app/django_vancouver.log 2>&1 &")
    click.echo("✅ ИТР-Команда перезапуска отправлена в шину ОЗУ!")

if __name__ == '__main__':
    cli()
