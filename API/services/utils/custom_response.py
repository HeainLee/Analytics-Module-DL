import logging
from django.urls import Resolver404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.decorators import api_view


ERROR_CASE_01 = dict(ERROR_CASE_01='GET 메소드에서 Resource Not Found(HTTP_404_NOT_FOUND/4004) 에러 발생')
ERROR_CASE_02_1 = dict(ERROR_CASE_02_1='GET 메소드에서 URL Not Found(HTTP_404_NOT_FOUND/4004) 에러 발생')
ERROR_CASE_02_2 = dict(ERROR_CASE_02_2='GET 이외의 메소드에서 URL Not Found(HTTP_404_NOT_FOUND/4004) 에러 발생')
ERROR_CASE_03 = dict(ERROR_CASE_03='File Not Found(HTTP_404_NOT_FOUND/4004) 에러 발생')
ERROR_CASE_04 = dict(ERROR_CASE_04='Method Not Allowed(HTTP_405_METHOD_NOT_ALLOWED/4005) 에러 발생')
ERROR_CASE_05 = dict(ERROR_CASE_05='Not Acceptable(HTTP_406_NOT_ACCEPTABLE/4006) 에러 발생')
ERROR_CASE_06 = dict(ERROR_CASE_06='Unsupported Media Type(HTTP_415_UNSUPPORTED_MEDIA_TYPE/4015) 에러 발생')
ERROR_CASE_07 = dict(ERROR_CASE_07='Mandatory Parameter Missing(HTTP_400_BAD_REQUEST/4101) 에러 발생')
ERROR_CASE_08 = dict(ERROR_CASE_08='Invalid Parameter Type(HTTP_400_BAD_REQUEST/4102) 에러 발생')
ERROR_CASE_09 = dict(ERROR_CASE_09='Conflict(HTTP_409_CONFLICT/4009) 에러 발생')
ERROR_CASE_10 = dict(ERROR_CASE_10='Unprocessable Entity(HTTP_422_UNPROCESSABLE_ENTITY/4022) 에러 발생')
ERROR_CASE_11 = dict(ERROR_CASE_11='Invalid Model Parameter(HTTP_400_BAD_REQUEST/4103) 에러 발생')
ERROR_CASE_12 = dict(ERROR_CASE_12='Invalid_Preprocess_Condition(HTTP_400_BAD_REQUEST/4104) 에러 발생')
ERROR_CASE_13 = dict(ERROR_CASE_13='NOT INITIATED RESOURCE(HTTP_451_Unavailable For Legal Reasons/4051) 에러 발생')





'''
[핸들러 에러 설정 방법]
############### 함수 custom404는 smartcity/urls.py에 handler404 설정
############### 함수 custom_exception_handler는 settings.py에 전역변수 설정 --> EXCEPTION_HANDLER

[핸들러 에러 종류]
# ERROR_CASE_01. GET 메소드에서 Resource Not Found(4004)인 경우 (?또는 POST/PATCH 메소드에서 body 파라미터 검사하는 경우에도 해당)
# ERROR_CASE_02-1. GET 메소드에서 URL Not Found(4004)인 경우
# ERROR_CASE_02-2. POST/DELETE/PATCH 메소드에서 URL Not Found(4004)인 경우
# ERROR_CASE_03. body로 요청한 파일 경로(data_path 또는 test_data_path)가 존재하지 않는 경우 or 로컬 저장 경로(result/..)에 파일이 없는 경우(4004)
# ERROR_CASE_04. 메소드가 허용되지 않는 경우(4005)
############### GET이 아닌 다른 메소드에서 URL이 잘못되면(not found) 디폴트로 404가 아니라 405에러가 발생 
############### custom404가 아닌 method not allowed로 들어오기 때문에 이를 구분해서 if-else문으로 처리함
# ERROR_CASE_05. 요청 Accept 미디어 타입을 지원하지 않는 경우(4006)
# ERROR_CASE_06. 요청 Content Type 미디어 타입을 지원하지 않는 경우(4015)
# ERROR_CASE_07. 필수 파라미터가 누락된 경우(4101)
# ERROR_CASE_08. 파라미터의 값이 규격에 명시된 타입과 다를 경우(4102)
# ERROR_CASE_09. 해당 리소스의 현재 상태와 요청이 충돌하는 경우(4009)
############### STOP 요청인데, progress_state가 이미 success 또는 fail인 경우 / ongoing인 경우만 ok 
############### RESTART 요청에서는 progress_state에 상관없이 재시작 가능하게 해도 되나?
############### TEST 요청인데, progress_state가 아직 success 아닌 경우 
############### download 요청인데, delete_flag가 TRUE인 경우
############### 모델 변경 요청(PATCH)인데 delete_flag가 True인 경우
# ERROR_CASE_10. 요청된 지시를 따를 수 없는 경우(4022)
############### 학습 데이터가 numeric이 아닌 경우 (모델생성)
############### 컬럼이 일치하지 않는 경우 (모델적용)
############### unseen 컬럼이 있는 경우 (모델적용)
# ERROR_CASE_11. 모델 생성 요청시 model_parameters로 전달한 값으로 모델 파라미터를 변경할 수 없는 경우(4103)
# ERROR_CASE_12. 전처리 테스트 도중 발생하는 에러(4104)
# ERROR_CASE_13. 초기화 되지 않아서 정상작동하지 않는 경우(4051)
'''

logger = logging.getLogger('collect_log_utils')

@api_view()
def custom404(request, exception):
    logger.error('{}'.format(ERROR_CASE_02_1))
    response = {'type': "4004", 
                'title': 'URL Not Found',
                'detail': 'The requested URL not found'}
    return Response(response, status=status.HTTP_404_NOT_FOUND)

def custom_exception_handler(exc, context):
    logger.error(exc)
    logger.error(context)
    response = exception_handler(exc, context)
    response_data = {}
    try:
        logger.error('{} ===> {}'.format('디폴트 에러', response))
        # logger.error('{} ===> {}'.format('디폴트 에러', response.data))
        if response is not None:
            if getattr(response.data['detail'], 'code') == 'not_found':
                logger.error('{}'.format(ERROR_CASE_01))
                response_data['type'] = '4004'
                response_data['title'] = 'Resource Not Found'
                response_data['detail'] = 'The requested resource not found'
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)

            elif getattr(response.data['detail'], 'code') == 'method_not_allowed':
                if 'exception' in context['kwargs'] and isinstance(context['kwargs']['exception'], Resolver404):
                    logger.error('{}'.format(ERROR_CASE_02_2))
                    response_data['type'] = '4004'
                    response_data['title'] = 'URL Not Found'
                    response_data['detail'] = 'The requested URL not found'
                    return Response(response_data, status=status.HTTP_404_NOT_FOUND)

                else:
                    logger.error('{}'.format(ERROR_CASE_04))
                    response_data['type'] = '4005'
                    response_data['title'] = 'Method Not Allowed'
                    wrong_method = response.data['detail'].split('"')[1]
                    response_data['detail'] = "Method '{}' not allowed".format(wrong_method)
                    return Response(response_data, status=status.HTTP_405_METHOD_NOT_ALLOWED)

            elif getattr(response.data['detail'], 'code') == 'not_acceptable':
                logger.error('{}'.format(ERROR_CASE_05))
                response_data['type'] = "4006"
                response_data['title'] = 'Not Acceptable'
                response_data['detail'] = "Could not satisfy the request Accept header"
                return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)

            elif getattr(response.data['detail'], 'code') == 'unsupported_media_type':
                logger.error('{}'.format(ERROR_CASE_06))
                response_data['type'] = "4015"
                response_data['title'] = 'Unsupported Media Type'
                wrong_type = response.data['detail'].split('"')[1]
                response_data['detail'] = "Unsupported media type '{}' in request".format(wrong_type)
                return Response(response_data, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        else:
            response_data['type'] = '5000'
            response_data['title'] = 'Internal Server Error'
            response_data['detail'] = 'Internal Server Error'
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except:
        logger.error('{} & {}'.format(response, response.status_code))
        response_data['type'] = '4000'
        response_data['title'] = 'check log message'
        response_data['detail'] = 'Some error occurs but not be defined in Error Handler'
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class CustomErrorCode:
    def FILE_NOT_FOUND_4004(self, path_info=None):
        logger.error('{}'.format(ERROR_CASE_03))
        response = {'type': '4004', 'title': 'File Not Found',
                    'detail': "Cannot found file from path '{}'".format(path_info)}
        return response

    def MANDATORY_PARAMETER_MISSING_4101(self, error_msg):
        logger.error('{}'.format(ERROR_CASE_07))
        response = {'type': '4101', 'title': 'Mandatory Parameter Missing',
                    'detail': "'{}' Field is mandatory but missing".format(error_msg)}
        return response

    def INVALID_PARAMETER_TYPE_4102(self, error_msg):
        logger.error('{}'.format(ERROR_CASE_08))
        response = {'type': '4102', 'title': 'Invalid Parameter Type',
                    'detail': "'{}' is not valid data".format(error_msg)}
        return response

    def CONFLICT_4009(self, mode, error_msg):
        logger.error('{}'.format(ERROR_CASE_09))
        if mode == 'STOP':
            response = {'type': '4009', 'title': 'Conflict',
                        'detail': "Confilct with the current state of the Resource being '{}'".format(error_msg)}
        elif mode == 'TEST':
            response = {'type': '4009', 'title': 'Conflict',
                        'detail': "Confilct with the current state of the Resource being '{}'".format(error_msg)}
        elif mode == 'DELETE':
            response = {'type': '4009', 'title': 'Conflict',
                        'detail': "Confilct with the current state of the Resource being '{}'".format(error_msg)}
        elif mode == 'BATCH':
            response = {'type': '4009', 'title': 'Conflict',
                        'detail': "Conflict with the current state of the Train Model Resource being '{}'".format(error_msg)}
        return response

    def UNPROCESSABLE_ENTITY_4022(self, error_msg):
        logger.error('{}'.format(ERROR_CASE_10))
        response = {'type': '4022', 'title': 'Unprocessable Entity',
                    'detail': '{}'.format(error_msg)}
        return response

    def INVALID_MODEL_PARAMETER_4103(self, error_msg):
        logger.error('{}'.format(ERROR_CASE_11))
        response = {'type': '4103', 'title': 'Invalid Model Parameter',
                    'detail': str(error_msg)}
        return response

    def INVALID_PREPROCESS_CONDITION_4104(self, error_msg):
        logger.error('{}'.format(ERROR_CASE_12))
        response = {'type': '4104', 'title': 'Invalid Preprocess Condition',
                    'detail': f"Cannot apply field name '{error_msg[0]}' with function '{error_msg[1]}'"
                              f" [System Message Detail : {error_msg[2]}]"}
        return response

    def RESOURCE_NOT_INITIATED_4051(self, error_msg):
        logger.error('{}'.format(ERROR_CASE_13))
        response = {'type': '4051', 'title': 'Resource not initiated',
                    'detail': "'{}'".format(error_msg)}
        return response

    def UNSUPPORTED_MEDIA_TYPE_4015(self, error_msg):
        logger.error('{}'.format(ERROR_CASE_06))
        response = {'type': '4015', 'title': 'Media type is not supported',
                    'detail': "'{}' is not proper file type.".format(error_msg)}
        return response


    # print('default status_code', response.status_code)
    # print(response.data['detail'])
    # print(getattr(response.data['detail'], 'code'))