import os
import json
import joblib
import logging
import numpy as np
import pandas as pd

from ..utils.custom_decorator import where_exception
from ...config.result_path_config import PATH_CONFIG

ORIGINAL_DATA_DIR = PATH_CONFIG.ORIGINAL_DATA_DIRECTORY
# 'result/original_data'
PREPROCESSED_DATA_DIR = PATH_CONFIG.PREPROCESSED_DATA
# 'result/preprocessed_data'
PREPROCESS_TRANSFORMER_DIR = PATH_CONFIG.PREPROCESS_TRANSFORMER
# 'result/preprocess_transformer '
MODEL_DIR = PATH_CONFIG.MODEL
# 'result/model'

logger = logging.getLogger("collect_log_utils")


class CallMixin:
    """
    데이터 로드 / 전처리기 로드 또는 저장 / 모델 로드 또는 저장
    """

    @staticmethod
    def _load_data(base_path, file_name):
        """
        Load Data and Return as pd.DataFrame.

        Parameters:
        -----------
             file_name (str) : file name
             (ex. 'P_1.json', 'O_1.csv')

        Returns:
        --------
             get_data (pandas.DataFrame) :
             DataFrame loaded from json or csv file

        파일형식이 json 인 경우,
        1) 데이터 저장 형태가 다음과 같으면
            => dict like {index -> {column -> value}}
            get_data = pd.read_json(get_data, orient='index').sort_index()
        2) 데이터 저장 형태가 다음과 같으면
            => separate by enter {column:value,column:value,…}
            get_data = pd.read_json(file_path, lines=True, encoding='utf-8')
        """
        try:
            if base_path == "ORIGINAL_DATA_DIR":
                base_path = ORIGINAL_DATA_DIR
                if os.path.splitext(file_name)[1] == ".csv":
                    file_path = os.path.join(base_path, file_name)
                    get_data = pd.read_csv(file_path)
                elif os.path.splitext(file_name)[1] == ".json":
                    file_path = os.path.join(base_path, file_name)
                    get_data = pd.read_json(file_path, lines=True, encoding="utf-8")
            elif base_path == "PREPROCESSED_DATA_DIR":
                base_path = PREPROCESSED_DATA_DIR
                file_path = os.path.join(base_path, file_name)
                get_data = pd.read_json(file_path, orient="index").sort_index()
            return get_data
        except Exception as e:
            where_exception(error_msg=e)
            return None

    # 오픈소스 라이브러리에서 base object 로드하는 함수
    @staticmethod
    def _get_base_object(params):
        try:
            module_ = __import__(params["LIBRARY_NAME"])
            class_ = getattr(module_, str(params["LIBRARY_OBJECT_NAME"]))
            base_object_ = getattr(class_, params["LIBRARY_FUNCTION_NAME"])
            base_object = base_object_()
            return base_object
        except AttributeError:
            module_ = __import__(
                params["LIBRARY_NAME"] + "." + params["LIBRARY_OBJECT_NAME"]
            )
            class_ = getattr(module_, params["LIBRARY_OBJECT_NAME"])
            base_object_ = getattr(class_, params["LIBRARY_FUNCTION_NAME"])
            base_object = base_object_()
            return base_object
        except Exception as e:
            where_exception(error_msg=e)

    # .pickle 파일 로드하는 함수
    @staticmethod
    def _load_pickle(base_path, file_name):
        if base_path == "MODEL_DIR":
            base_path = MODEL_DIR
        elif base_path == "PREPROCESS_TRANSFORMER_DIR":
            base_path = PREPROCESS_TRANSFORMER_DIR
        logger.info(f"pickle file loaded from {base_path}/{file_name}")
        file_path = os.path.join(base_path, file_name)
        loaded_object = joblib.load(file_path)
        return loaded_object

    # .pickle 파일 저장하는 함수
    @staticmethod
    def _dump_pickle(save_object, base_path, file_name):
        if base_path == "MODEL_DIR":
            base_path = MODEL_DIR
        elif base_path == "PREPROCESS_TRANSFORMER_DIR":
            base_path = PREPROCESS_TRANSFORMER_DIR
        logger.info(f"pickle file saved to {base_path}/{file_name}")
        file_path = os.path.join(base_path, file_name)
        joblib.dump(save_object, file_path)
        return file_path


class PreprocessUtils:
    @staticmethod
    def _to_array(after_fitted):
        """
        Return value as numpy array type

            Parameters:
            -----------
                 after_fitted (array or csr_matrix) :
                 raw value of preprocessor's 'fit_transform'

            Returns:
            --------
                 after_fitted (array) :
                 value converted to numpy array
        """
        if isinstance(after_fitted, np.ndarray):
            return after_fitted
        else:
            after_fitted = after_fitted.toarray()
            return after_fitted

    @staticmethod
    def _new_columns(field_name, after_fitted):
        """
        Return list of Column name for saving data

            Parameters:
            -----------
                 field_name (str) : one of the column name
                 after_fitted (array) :
                 converted value of preprocessor's 'fit_transform'

            Returns:
            --------
                 name_of_columns (list) :
                 the list of a newly created field name
                 based on the second dimension(shape[1])
                 of after_fitted
        """
        name_of_columns = [
            field_name + "_" + str(i) for i in range(after_fitted.shape[1])
        ]
        return name_of_columns

    @staticmethod
    def _drop_columns(data, columns):
        """
        Drop Columns and Return Data without request columns

            Parameters:
            -----------
                 data (pandas.DataFrame) : pandas DataFrame
                 columns (str) : one single name of data's columns

            Returns:
            --------
                 data (pandas.DataFrame): pandas DataFrame without 'columns'
        """
        logger.info("{} 필드를 데이터에서 제외시킵니다".format(columns))
        data = data.drop(columns=[columns], axis=1)
        return data
