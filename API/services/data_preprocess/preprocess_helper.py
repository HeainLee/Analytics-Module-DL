import os
import logging
import warnings
import numpy as np
import pandas as pd
from django.http import Http404

from .data_summary import DataSummary
from .preprocess_base import PreprocessorBase
from ..utils.custom_decorator import where_exception
from ...models.original_data import OriginalData
from ...models.preprocess_functions import PreprocessFunction
from ...serializers.serializers import OriginalDataSerializer
from ...serializers.serializers import PreprocessFunctionSerializer
from ...config.result_path_config import PATH_CONFIG

warnings.filterwarnings("ignore")
logger = logging.getLogger("collect_log_helper")

PREPROCESSED_DATA_DIR = PATH_CONFIG.PREPROCESSED_DATA
# 'result/preprocessed_data'


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


class InspectUserRequest(PreprocessorBase):
    """
    For inspecting Users' POST request from user's request body

        Attributes:
        -----------
        _key_data_pk (str) : shortcut of 'original_data_sequence_pk'
        _key_func_pk (str) : 'shortcut of preprocess_functions_sequence_pk'
        original_data_id (int) : user requested ID of original Data
        data_saved_path (str) : original data's saved path (eg. ['FILEPATH'] from query)
        pfunction_ids (list) : list of all '_key_func_pk' from user request
        data_loaded (pandas.DataFrame) : user requested Data for Preprocessing
    """

    def __init__(self):
        self._key_data_pk = "original_data_sequence_pk"
        self._key_func_pk = "preprocess_functions_sequence_pk"
        self.original_data_id = None
        self.data_saved_path = None
        self.pfunction_ids = None
        self.data_loaded = None

    @staticmethod
    def _mandatory_key_exists_preprocessed_post(element):
        """
        Check whether mandatory keys are existed

            Parameters:
            -----------
                 element (dict) :
                 raw request information from user's request body

            Returns:
            --------
                 True (bool) :
                 True, if all mandatory keys is satisfied
                 or
                 _key (str) :
                 omitted key (induce 4101)
        """
        mand_key_level_one = ["original_data_sequence_pk", "request_data"]
        mand_key_level_two = ["preprocess_functions_sequence_pk", "field_name"]
        if list(element.keys()) != mand_key_level_one:
            _key = set(mand_key_level_one).difference(list(element.keys()))
            return "".join(_key)
        else:
            for request_info_dict in element["request_data"]:
                for _key in mand_key_level_two:
                    if _key not in request_info_dict.keys():
                        return _key
        return True

    def _check_request_pk(self):
        """
        Check IDs of original data and preprocess function (valid DB)

        check self.original_data_id & self.pfunction_ids
        new value to self.data_loaded & self.data_saved_path is added
        if True is returned

            Returns:
            --------
                 True (bool) : if all IDs are valid
                 or
                 _error_return_dict (dict) :
                 if self.data_saved_path not valid

            Raises:
            -------
                Http404 (django Exception) :
                if IDs are not valid
        """
        all_origin_id = list(
            OriginalData.objects.all().values_list(
                "ORIGINAL_DATA_SEQUENCE_PK", flat=True
            )
        )
        if not int(self.original_data_id) in all_origin_id:
            logger.error(f"{self._key_data_pk}가 잘못 요청되었습니다")
            raise Http404
        else:
            self.data_saved_path = OriginalDataSerializer(
                OriginalData.objects.get(pk=self.original_data_id)
            ).data["FILEPATH"]

            if not os.path.isfile(self.data_saved_path):
                logger.error(f"{self.data_saved_path} 경로가 존재하지 않습니다")
                return _error_return_dict("4004", self.data_saved_path)
            else:
                self.data_loaded = super()._load_data(
                    base_path="ORIGINAL_DATA_DIR",
                    file_name=os.path.split(self.data_saved_path)[1],
                )
        all_pfunc_id = list(
            PreprocessFunction.objects.all().values_list(
                "PREPROCESS_FUNCTIONS_SEQUENCE_PK", flat=True
            )
        )
        is_ids = [True if i in all_pfunc_id else False for i in self.pfunction_ids]
        if not all(is_ids):
            logger.error(f"{self._key_func_pk}가 잘못 요청되었습니다")
            raise Http404
        return True

    # 전처리 데이터 생성 요청에 대한 요청 파라미터 검사하는 함수
    def check_post_mode(self, request_info):
        """
        Checking whether 'request_info' is valid

            Parameters:
            -----------
                 request_info (dict) :
                 request information from user's request body

            Returns:
            --------
                 True (bool) : if valid
                 or
                 _error_return_dict (dict) :
                 specific error info to induce custom error
        """
        logger.warning("[데이터 전처리] Check Request Info")
        # 필수 파라미터 검사 (4101)
        is_keys = self._mandatory_key_exists_preprocessed_post(element=request_info)
        if isinstance(is_keys, str):  # mandatory key name (str)
            return _error_return_dict("4101", is_keys)
        request_all = request_info["request_data"]
        self.original_data_id = request_info[self._key_data_pk]
        self.pfunction_ids = list(map(int, [i[self._key_func_pk] for i in request_all]))

        # 요청한 원본데이터 ID와 전처리 ID가 있는지 검사 (Http404/4004)
        is_valid = self._check_request_pk()
        if isinstance(is_valid, dict):
            return _error_return_dict(is_valid["error_type"], is_valid["error_msg"])

        # 요청한 필드명이 원본 데이터에 있는지 (4102)
        for request_info_dict in request_all:
            field_name = request_info_dict["field_name"]

            if len(field_name.split(",")) != 1:
                field_name_list = list(map(lambda x:x.strip(), field_name.split(",")))
            else:
                field_name_list = [field_name]

            for field_name_ in field_name_list:
                if field_name_ not in list(self.data_loaded.columns):
                    return _error_return_dict("4102", field_name_)
        return True  # 에러 상태가 없으면 True


class PreprocessTask(PreprocessorBase):
    """
    Return data preprocessing result

        Attributes:
        -----------
            pk (int) : PREPROCESSED_DATA_SEQUENCE_PK
            func_query (dict) : preprocess function query info
                                (eg. PreprocessFunctionSerializer)
            file_path (str) : preprocessed data saved path
                              (eg. os.path.join(PREPROCESSED_DATA_DIR, file_name))
            file_name (str) : file name of preprocessed data
                              (eg. 'P_{}.json'.format(self.pk))
            real_final_list (list) : which saved as 'SUMMARY' in PreprocessedData DB
                (eg. info_dict = {"field_name":field_name, "function_name":pfunc_name,
                                  "function_pk":pfunc_pk, "file_name":file_name,
                                  "original_classes":None, "encoded_classes":None})
    """

    def __init__(self):
        self.pk = None
        self.func_query = None
        self.file_path = None
        self.file_name = None
        self.real_final_list = []

    # 전처리된 데이터를(pandas.DataFrame)을 json을 변환하여 저장하는 함수
    def _save_prep_data(self, prep_data, file_name):
        """
        Save preprocessed Data as json

            Parameters:
            -----------
                 prep_data (pandas.DataFrame) :
                 preprocessed data after all preprocessing finished
                 file_name (str) :
                 saved name of preprocessed data
                 (eg. 'P_{}.json'.format(self.pk))

            Returns:
            --------
                 (save 'prep_data' to PREPROCESSED_DATA_DIR)
                 (append new value to self.file_path)
        """
        self.file_path = os.path.join(PREPROCESSED_DATA_DIR, file_name)
        prep_data.to_json(self.file_path, orient="index")

    # TODO 전처리 방법의 동작방식에 따라 조건문
    def _train_data_transformer(self, data, field_name, processor):
        """
        Making 'changed_field' using 'field_name' with 'processor'
        and Overwriting 'data' from original 'field_column' to 'changed_field'
        and Return 'data' (used by the related function `_task_result`)

            Parameters:
            -----------
                 data (pandas.DataFrame) :
                 preprocessed data in progress
                 field_name (str) : one of the column name
                 processor (object) :
                 preprocessor from scikit-learn library

            Returns:
            --------
                 data (pandas.DataFrame) :
                 preprocessed data in progress
                 processor (object) :
                 preprocessor after `fit` and `transform`
                 encoded_info (dict) :
                 saving original and encoded classes or categories
        """
        encoded_info = dict()
        trans_name = type(processor).__name__

        try:
            field_column = data[field_name].astype(float)
        except ValueError:
            field_column = data[field_name]
        except Exception as e:
            where_exception(error_msg=e)
        try:
            changed_field = processor.fit_transform(field_column.values.reshape(-1, 1))
            changed_field = super()._to_array(changed_field)

            # transform 된 데이터와 원본 데이터 통합
            if len(changed_field.shape) == 2 and changed_field.shape[1] == 1:
                # case 04 : 실제로 작동할 수 없는 전처리 기능 Pass
                if trans_name == "Normalizer":
                    logger.warning("Not working in this version!!!")
                else:  # case 01 : 새로운 칼럼이 추가 되지 않음 + 인코딩 아님 (스케일링 등)
                    data[field_name] = changed_field

                    # case 02 : 인코딩 필요한 경우
                    if trans_name == "Binarizer":
                        encoded_info["origin_class"] = np.unique(field_column).tolist()
                        encoded_class = processor.transform(
                            np.unique(field_column).reshape(-1, 1)
                        )
                        encoded_info["encode_class"] = encoded_class.tolist()
                    # case 02 : 인코딩 필요한 경우
                    elif trans_name == "OrdinalEncoder":
                        encoded_info["origin_class"] = list(processor.categories_[0])
                        encoded_class = processor.transform(
                            processor.categories_[0].reshape(-1, 1)
                        )
                        encoded_info["encode_class"] = encoded_class.tolist()
            # case 02 : 새로운 칼럼이 추가 되지 않음 + 인코딩
            elif len(changed_field.shape) == 1:  # LabelEncoder
                encoded_info["origin_class"] = list(processor.classes_)
                encoded_info["encode_class"] = list(np.unique(changed_field))
                data[field_name] = changed_field
            # case 03 : 새로운 칼럼이 추가 됨 + 인코딩
            else:
                # KBinsDiscretizer, LabelBinarizer, MultiLabelBinarizer, OneHotEncoder
                if trans_name == "KBinsDiscretizer":
                    print(changed_field)
                    encoded_info["origin_class"] = processor.bin_edges_[0].tolist()
                    encoded_class = processor.transform(
                        processor.bin_edges_[0].reshape(-1, 1)
                    )
                elif trans_name == "OneHotEncoder":
                    encoded_info["origin_class"] = list(processor.categories_[0])
                    encoded_class = processor.transform(
                        processor.categories_[0].reshape(-1, 1)
                    )
                else:
                    encoded_info["origin_class"] = list(processor.classes_)
                    encoded_class = processor.transform(
                        processor.classes_.reshape(-1, 1)
                    )
                encoded_info["encode_class"] = super()._to_array(encoded_class).tolist()

                col_name = super()._new_columns(
                    field_name=field_name, after_fitted=changed_field
                )
                new_columns = pd.DataFrame(changed_field, columns=col_name)
                data = pd.concat([data, new_columns], axis=1, sort=False)
                data = data.drop(field_name, axis=1)
            return data, processor, encoded_info
        except Exception as e:
            where_exception(error_msg=e)
            return False

    def _task_drop_columns(self, data, request_dict):
        """
        Drop Columns and Return Data without request columns

            Parameters:
            -----------
                 data (pandas.DataFrame) :
                 preprocessed data in progress
                 request_dict (dict) :
                 single request info from user's request body

            Returns:
            --------
                 data (pandas.DataFrame):
                 pandas DataFrame without 'field_name'
                 (append new value to self.real_final_list)
        """
        field_name = request_dict["field_name"]
        pfunc_pk = request_dict["preprocess_functions_sequence_pk"]

        if len(field_name.split(",")) != 1:
            field_name_list = list(map(lambda x:x.strip(), field_name.split(",")))
        else:
            field_name_list = [field_name]
        for single_field_name in field_name_list:
            data = super()._drop_columns(data=data, columns=single_field_name)
            single_result = dict(
                field_name=single_field_name,
                function_name="DropColumns",
                function_pk=pfunc_pk,
                file_name=None,
                original_classes=None,
                encoded_classes=None,
            )

            self.real_final_list.append(single_result)
        return data

    def _task_result(self, data, request_dict, save_n):
        """
        Preparation for calling `_train_data_transformer` and `_save_transformer`
        according to 'request_dict'

            Parameters:
            -----------
                 data (pandas.DataFrame) :
                 preprocessed data in progress
                 request_dict (dict) :
                 single request info from user's request body
                 save_n (int) :
                 incremental Num for naming pickle file of transformer

            Returns:
            --------
                 data (pandas.DataFrame):
                 pandas DataFrame without 'field_name'
                 save_n (int) :
                 incremental Num for naming pickle file of transformer
        """
        field_name = request_dict["field_name"]
        pfunc_pk = request_dict["preprocess_functions_sequence_pk"]
        pfunc_name = self.func_query["PREPROCESS_FUNCTIONS_NAME"]

        transformer = super()._get_base_object(params=self.func_query)

        if "condition" in request_dict.keys():  # 파라미터 수정을 요청한 경우
            request_condition = request_dict["condition"]

            transformer = super()._change_transformer_params(
                transformer=transformer, params_dict=request_condition
            )
            logger.info(
                f"{pfunc_name} run with changed parameter {transformer.get_params()}"
            )
        else:
            logger.info(
                f"{pfunc_name} run with basic parameter {transformer.get_params()}"
            )
        if len(field_name.split(",")) != 1:
            field_name_list = list(map(lambda x:x.strip(), field_name.split(",")))
        else:
            field_name_list = [field_name]
        for single_field_name in field_name_list:

            data, fitted_transformer, encode_info = self._train_data_transformer(
                data=data, field_name=single_field_name, processor=transformer
            )

            save_n += 1
            saved_name = "T_{}_{}.pickle".format(self.pk, save_n)
            logger.info(f'save "{saved_name}" <{pfunc_name} | {single_field_name}> ')

            _ = super()._dump_pickle(
                save_object=fitted_transformer,
                base_path="PREPROCESS_TRANSFORMER_DIR",
                file_name=saved_name,
            )

            info_dict = dict(
                field_name=single_field_name,
                function_name=pfunc_name,
                function_pk=pfunc_pk,
                file_name=saved_name,
                original_classes=None,
                encoded_classes=None,
            )
            if "origin_class" in encode_info.keys():
                info_dict["original_classes"] = encode_info["origin_class"]
                info_dict["encoded_classes"] = encode_info["encode_class"]
            self.real_final_list.append(info_dict)
        return data, save_n

    def task_result(self, data_path, request_info, pk):
        """
        Preparation for calling `_task_drop_columns` and `_task_result`
        according to 'request_info' and saving preprocessed Data

            Parameters:
            -----------
                 data_path (str) :
                 original data saved path
                 request_info (dict) :
                 full request info from user's request body
                 pk (int) :
                 current PreprocessedData ID

            Returns:
            --------
                 final_result (dict):
                 final return value of user's requested
        """
        self.pk = pk
        self.file_name = "P_{}.json".format(self.pk)

        user_request_dict = request_info["request_data"]
        data = super()._load_data(
            base_path="ORIGINAL_DATA_DIR", file_name=os.path.split(data_path)[1]
        )

        save_N = 0

        try:
            for get_request_dict in user_request_dict:
                """
                {'preprocess_functions_sequence_pk': 8, 'field_name': 'temp'}
                {'preprocess_functions_sequence_pk': 10, 'field_name': 'season'}
                {'preprocess_functions_sequence_pk': 14, 'field_name': 'datetime'}
                """
                pfunc_pk = get_request_dict["preprocess_functions_sequence_pk"]

                self.func_query = PreprocessFunctionSerializer(
                    PreprocessFunction.objects.get(pk=pfunc_pk)
                ).data
                func_name = self.func_query["PREPROCESS_FUNCTIONS_NAME"]

                if func_name == "DropColumns":
                    data = self._task_drop_columns(
                        data=data, request_dict=get_request_dict
                    )
                else:
                    data, save_N = self._task_result(
                        data=data, request_dict=get_request_dict, save_n=save_N
                    )
            self._save_prep_data(prep_data=data, file_name=self.file_name)
            data_summary = DataSummary(self.file_path)

            final_result = dict(
                file_path=self.file_path,
                file_name=self.file_name,
                summary=self.real_final_list,
                columns_info=data_summary.columns_info(),
                amount_info=data_summary.size_info(),
                sample_data=data_summary.sample_info(),
                statistics=data_summary.statistics_info(),
            )
            return final_result
        except Exception as e:
            logger.error("전처리 데이터 생성에 실패했습니다")
            where_exception(e)
            return False
