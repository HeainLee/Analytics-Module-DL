import sys
import logging
import warnings
import numpy as np
from django.http import Http404
from scipy.sparse import csr_matrix
from pandas.core.common import flatten

from .preprocess_base import PreprocessorBase
from ....utils.custom_decorator import where_exception
from ....common.models.preprocess_function import PreprocessFunction
from ....common.serializers.serializers import PreprocessFunctionSerializer

warnings.filterwarnings("ignore")
logger = logging.getLogger("collect_log_helper")


def _error_return_dict(error_type, error_msg):
    """
    Return common error dictionary type

        Parameters:
        -----------
             error_type (str) : type of error (eg. '4102')
             error_msg (str) : detail message of the error

        Returns:
        --------
             (dict) : common error dictionary
    """
    return dict(error_type=error_type, error_msg=error_msg)


class TestPreprocessor(PreprocessorBase):
    """
    For processing test result of Preprocessor from original Data

        Attributes:
        -----------
            func_query (dict) :
            preprocessFunction Query
            original_data_pk (int) :
            user requested ID of original Data
            test_total_result (list) :
            final return value of user's requested
            about Preprocessor Testing
            test_data (pandas.DataFrame) :
            user requested Data for Preprocessor Testing
    """

    def __init__(self, file_name, pk):
        self.func_query = None
        self.original_data_pk = pk
        self.test_total_result = []
        self.test_data = super()._load_data(
            base_path="ORIGINAL_DATA_DIR", file_name=file_name
        )

    @staticmethod
    def _mandatory_key_exists_original_patch(element):
        """
        Check whether mandatory keys are existed

            Parameters:
            -----------
                 element (dict) :
                 raw request information from user's request body

            Returns:
            --------
                 True (bool) :
                 True, if all mandatory keys satisfied
                 or
                 _key or mand_key_level_one (str) :
                 omitted key
        """
        mand_key_level_one = "request_test"
        mand_key_level_two = ["preprocess_functions_sequence_pk", "field_name"]
        if mand_key_level_one not in element.keys():
            return mand_key_level_one
        else:
            for request_info_dict in element["request_test"]:
                for _key in mand_key_level_two:
                    if _key not in request_info_dict.keys():
                        return _key
        return True

    @staticmethod
    def _convert_to_return_shape(data_shape, after_):
        """
        Convert returning shape of data('after_')
        by data's original shape and type

            Parameters:
            -----------
                 data_shape (tuple) :
                 data shape from numpy.ndarray.shape
                 after_ (numpy.ndarray) :
                 array shape data after specific
                 transformers were applied

            Returns:
            --------
                 changed_field (list) :
                 list of flatten array which element
                is converted to string
        """
        NUM = 5
        changed_field = []

        if isinstance(after_[1], np.ndarray) and data_shape[1] == 1:
            # print('type 1', function_name)
            changed_field = list(flatten(after_[:NUM]))
            changed_field = [
                round(float(i), 4) if str(i)[::-1].find(".") > 4 else i
                for i in changed_field
            ]
            # SimpleImputer, Binarizer, MaxAbsScaler, MinMaxScaler,
            # Normalizer, OrdinalEncoder, RobustScaler, StandardScaler
        elif isinstance(after_[1], (np.int64, np.int32, np.float64, np.float32)):
            # LabelEncoder
            # print('type 2', function_name)
            changed_field = list(map(lambda x: str(x), list(flatten(after_[:NUM]))))
        elif isinstance(after_[1], csr_matrix):
            # KBinsDiscretizer, OneHotEncoder(sparse=True)
            # print('type 3', function_name)
            changed_field = after_.toarray()
            changed_field = list(list(i) for i in changed_field[:NUM])
            changed_field = list(map(lambda x: str(x), changed_field))
        elif isinstance(after_[1], np.ndarray) and data_shape[1] != 1:
            # LabelBinarizer, MultiLabelBinarizer, OneHotEncoder(sparse=False)
            # print('type 4', function_name)
            changed_field = list(list(i) for i in after_[:NUM])
            changed_field = list(map(lambda x: str(x), changed_field))
        return changed_field

    def _test_transformer(self, field, field_name, transformer):
        """
        Perform fit_transform with specific field
        with requested transformer

            Parameters:
            -----------
                 field (pandas.Series) :
                 specific data values selected by field name
                 field_name (str) :
                 field name of field
                 transformer (object) :
                 preprocessor from scikit-learn library

            Returns:
            --------
                 show_changed_field (dict) :
                 converted value of changed_field
                 by '_convert_to_return_shape' function
                 or
                 return_error (dict) :
                 specific error info to induce custom error
        """
        transformer_name = type(transformer).__name__

        try:
            changed_field = transformer.fit_transform(field.values.reshape(-1, 1))

            # 결과를 반환하기 위해 결과 형태 변환
            show_changed_field = self._convert_to_return_shape(
                data_shape=changed_field.shape, after_=changed_field
            )

            show_changed_field = dict(
                zip(range(0, len(show_changed_field)), show_changed_field)
            )
            return show_changed_field
        except Exception as e:
            where_exception(error_msg=e)
            logger.error(f"{transformer_name} 전처리 기능 fit&transform 도중 에러가 발생했습니다")
            error_detail = [field_name, transformer_name, str(sys.exc_info()[1])]
            return_error = dict(
                error_name="PreprocessorTestError", error_detail=error_detail
            )
            return return_error

    def _test_result_drop_columns(self, func_name, name_field):
        """
        Perform Fake Drop Columns with specific field

            Parameters:
            -----------
                 func_name (str) : 'DropColumns'
                 name_field (str) : field name of field

            Returns:
            --------
                 (append new value to self.test_total_result)
        """
        logger.info(f"[전처리 테스트] {name_field} 필드를 제외합니다")
        if len(name_field.split(",")) != 1:
            field_name_list = list(map(lambda x:x.strip(), name_field.split(",")))
        else:
            field_name_list = [name_field]
        for single_field_name in field_name_list:
            self.test_data = super()._drop_columns(
                data=self.test_data, columns=single_field_name
            )
            fake_drop_columns = [" "] * 5
            fake_drop_columns = dict(
                zip(range(0, len(fake_drop_columns)), fake_drop_columns)
            )
            single_result = {
                "field_name": single_field_name,
                "function_name": func_name,
                "function_parameter": None,
                "test_result": fake_drop_columns,
            }
            self.test_total_result.append(single_result)

    def _test_result(self, func_name, name_field, request_detail):
        """
        According to 'request_detail' prepare and
        request '_test_transformer'

            Parameters:
            -----------
                 func_name (str) : transformer name
                 name_field (str) : field name of field
                 request_detail (dict) :
                 request information from user's request body

            Returns:
            --------
                 (append new value to self.test_total_result)
                 or
                 _error_return_dict() (dict) :
                 specific error info to induce custom error
        """
        transformer = super()._get_base_object(params=self.func_query)
        base_param = transformer.get_params()

        if "condition" in request_detail.keys():  # 파라미터 수정을 요청한 경우
            request_condition = request_detail["condition"]

            transformer = super()._change_transformer_params(
                transformer=transformer, params_dict=request_condition
            )

            if isinstance(transformer, dict) and "error_name" in transformer.keys():
                # ParameterSyntaxError
                return _error_return_dict("4102", transformer["error_detail"])
            else:
                logger.info(f"[전처리 테스트] 변경된 파라미터 {transformer.get_params()} 가 적용됩니다")
            base_param.update(request_condition)
        else:
            request_condition = None
            logger.info(f"[전처리 테스트] 기본 파라미터 {transformer.get_params()} 가 적용됩니다")
        full_condition = base_param.copy()
        for k, v in full_condition.items():
            full_condition[k] = str(v)
        if len(name_field.split(",")) != 1:
            field_name_list = list(map(lambda x:x.strip(), name_field.split(",")))
        else:
            field_name_list = [name_field]
        for single_field_name in field_name_list:
            logger.info(f"[전처리 테스트] {single_field_name} 필드의 {func_name} 전처리 수행중...")

            # 요청한 필드명이 원본 데이터에 있는지 검사 (4102)
            if single_field_name not in list(self.test_data.columns):
                return _error_return_dict(
                    "4104", [single_field_name, func_name, "Field Name is Not Exist"]
                )
            try:
                field_column = self.test_data[single_field_name].astype(float)
            except ValueError:
                field_column = self.test_data[single_field_name]
            except Exception as e:
                where_exception(error_msg=e)
            after_changed = self._test_transformer(
                field=field_column,
                field_name=single_field_name,
                transformer=transformer,
            )

            before_changed = field_column.values.reshape(-1, 1)[:5]
            before_changed = list(flatten(before_changed))
            before_changed = dict(zip(range(0, len(before_changed)), before_changed))

            # PreprocessorTestError
            if isinstance(after_changed, dict) and "error_name" in after_changed.keys():
                return _error_return_dict("4104", after_changed["error_detail"])
            else:
                single_result = {
                    "field_name": single_field_name,
                    "function_name": func_name,
                    "function_parameter": request_condition,
                    # 'original': before_changed,
                    "test_result": after_changed,
                }
                self.test_total_result.append(single_result)

    # 전처리 테스트 요청에 대한 요청 파라미터 검사하는 함수
    def check_request_body_original_patch(self, request_info):
        """
        Checking whether 'request_info' is valid

            Parameters:
            -----------
                 request_info (dict) :
                 request information from user's request body

            Returns:
            --------
                 _error_return_dict() (dict) :
                 specific error info to induce custom error
                 or
                 Http404
        """
        logger.info(f"[전처리 테스트] 요청 ID [{self.original_data_pk}]의 필수 파라미터 검사...")
        # 필수 파라미터 검사 (4101)
        is_keys = self._mandatory_key_exists_original_patch(element=request_info)
        if isinstance(is_keys, str):  # mandatory key name (str)
            return _error_return_dict("4101", is_keys)
        request_info_list = request_info["request_test"]
        for request_info_dict in request_info_list:
            # 요청한 전처리 기능이 있는지 검사 (Http404)
            pfunc_id = request_info_dict["preprocess_functions_sequence_pk"]
            if not int(pfunc_id) in list(
                PreprocessFunction.objects.all().values_list(
                    "PREPROCESS_FUNCTIONS_SEQUENCE_PK", flat=True
                )
            ):
                raise Http404
            # 요청한 필드명이 원본 데이터에 있는지 검사 (4102)
            field_name = request_info_dict["field_name"]

            if len(field_name.split(",")) != 1:
                field_name_list = list(map(lambda x:x.strip(), field_name.split(",")))
            else:
                field_name_list = [field_name]

            for field_name_ in field_name_list:
                if field_name_ not in list(self.test_data.columns):
                    return _error_return_dict("4102", field_name_)
        return True

    def test_result(self, request_info):
        """
        According to 'request_info' invoking
        required function and returning result

            Parameters:
            -----------
                 request_info (dict) :
                 request information from user's request body

            Returns:
            --------
                 self.test_total_result (list) :
                 final return value of user's
                 requested about Preprocessor Testing
                 or
                 _error_return_dict() (dict) :
                 specific error info to induce custom error
        """
        logger.info(f"[전처리 테스트] 요청 ID [{self.original_data_pk}]의 테스트 결과 생성 중...")
        user_request_dict = request_info["request_test"]

        for get_request_dict in user_request_dict:
            field_name = get_request_dict["field_name"]  # 전처리 요청한 컬럼명
            self.func_query = PreprocessFunctionSerializer(
                PreprocessFunction.objects.get(
                    pk=get_request_dict["preprocess_functions_sequence_pk"]
                )
            ).data
            func_name = self.func_query["PREPROCESS_FUNCTIONS_NAME"]

            if func_name == "DropColumns":  # self.test_total_result is changed
                self._test_result_drop_columns(
                    func_name=func_name, name_field=field_name
                )
            else:  # return Error or self.test_total_result is changed
                is_error = self._test_result(
                    func_name=func_name,
                    name_field=field_name,
                    request_detail=get_request_dict,
                )

                if isinstance(is_error, dict):
                    return _error_return_dict(
                        is_error["error_type"], is_error["error_msg"]
                    )
        return self.test_total_result
