import time
import os, sys
import logging
import traceback
from functools import wraps

logger = logging.getLogger('collect_log_utils')


def call_deco(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        errors = traceback.extract_stack()
        func_script = str(errors[0]).split('FrameSummary file ')[1].split('.')[0].split('/')[-1]
        call_flow = []
        for i in range(len(errors)):
            if 'wrapper' not in str(errors[i]):
                call_func_name = str(errors[i]).split('in ')[1].replace('>', '').replace('<', '')
                call_flow.insert(0, call_func_name)

        if func_script == 'train_helper_test':
            log_sub_title = '[TRAIN MODEL FUNC]'
        else:
            log_sub_title = '[N/A]'

        logger.warning('[@wrapper] {} function "{}" is called by {}' \
                       .format(log_sub_title, func.__name__, call_flow))
        # logger.info(('kwargs {}'.format(kwargs)))
        return func(*args, **kwargs)

    return wrapper


def my_timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        t1 = time.time()
        result = func(*args, **kwargs)
        t2 = time.time() - t1
        print('{} 함수가 실행된 총 시간: {} 초'.format(func.__name__, t2))
        return result

    return wrapper


def where_exception(error_msg):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logger.error('[@wrapper] [WHERE EXCEPTION] {}, {}, {}'.format(exc_type, fname, exc_tb.tb_lineno))
    logger.error('[@wrapper] [WHERE EXCEPTION] Error Message = {}'.format(error_msg))
