#!/usr/bin/env python
import os
import sys
from django.conf import settings
from dasolution.celery import checkIfProcessRunning

if __name__ == '__main__':
    print(f'[{__file__}]  장고 manage.py 실행')

    check_version = checkIfProcessRunning('manage.py')
    if check_version:
        full_cmd = ' '.join(check_version)
        print(f'[{__file__}]  장고 실행 명령어입니다.', full_cmd)
        if 'dasolution.production' in full_cmd:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dasolution.production')
            print(f'[{__file__}]  장고 환경을 "배포(production.py)" 버전으로 실행했습니다. \n')
        elif 'dasolution.settings' in full_cmd:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dasolution.settings')
            print(f'[{__file__}]  장고 환경을 "기본(settings.py)" 버전으로 실행했습니다. \n')
        elif 'dasolution.locals' in full_cmd:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dasolution.locals')
            print(f'[{__file__}]  장고 환경을 "로컬(locals.py)" 버전으로 실행했습니다. \n')
        else:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dasolution.settings')
            print(f'[{__file__}]  장고 환경을 명시하지 않았습니다. "기본(settings.py)" 버전의 환경을 임포트합니다. \n')
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dasolution.settings')
        print(f'[{__file__}]  \n manage.py 명령어가 실행되지 않았습니다. "기본(settings.py)" 버전의 환경을 임포트합니다. \n')

    db_config = settings.DATABASES['default']
    res = dict((k, db_config[k]) for k in ['ENGINE', 'NAME', 'HOST'] if k in db_config) 
    print('(중요) 데이터베이스 정보를 확인해주세요!!', res)

    # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dasolution.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
