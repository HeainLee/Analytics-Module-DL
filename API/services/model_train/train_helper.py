import os
import copy
import inspect
import logging
import warnings
import numpy as np
import pandas as pd
from distutils import util
from ast import literal_eval
from django.http import Http404
from sklearn import base
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn.utils.estimator_checks import check_estimators_dtypes
from lightgbm.basic import LightGBMError

from ..utils.custom_decorator import where_exception
from ..utils.custom_call import CallMixin
from ...models.algorithm import Algorithm
from ...models.original_data import OriginalData
from ...models.preprocessed_data import PreprocessedData
from ...serializers.serializers import ALGOSerializer
from ...serializers.serializers import OriginalDataSerializer
from ...serializers.serializers import PreprocessedDataSerializer

warnings.filterwarnings("ignore")
logger = logging.getLogger("collect_log_helper")


class PrepareModelTrain(CallMixin):
    """
    For preparing data, inspect data, get estimator, change parameters

    """

    # 요청한 데이터의 변수 타입이 수치형인지 검사하는 함수
    @staticmethod
    def _inspect_data(sample):
        sample_data = pd.DataFrame.from_dict(sample)
        for data_type in sample_data.dtypes:
            if data_type == "object":
                return False
            else:
                pass
        return True

    # 요청된 모델 조건에 맞게 파라미터 값 변경
    @staticmethod
    def _change_params(model, param):
        """
        @type model: object
        @type param: dict
        @type model: object
        @param model: training model
        @param param: model parameters
        @return: training model with changed model parameters
                 or training model with default model parameters
        """
        try:
            for k, v in param.items():
                if not isinstance(v, str):
                    v = str(v)
                # v = v.lower()
                logger.warning(f"[Change Parameter] {k} = {v}")
                if "." in v:
                    if v.replace(".", "").isdigit():  # float 인 경우
                        v = float(v)
                        setattr(model, k, v)
                    else:
                        setattr(model, k, v)
                elif v.isdigit():  # int 인 경우
                    v = int(v)
                    setattr(model, k, v)
                elif v.startswith("-"):  # neg int 인 경우
                    v = int(v)
                    setattr(model, k, v)
                elif v.lower() == "none":  # None 인 경우
                    setattr(model, k, None)
                elif v.lower() == "true" or v.lower() == "false":  # boolean 인 경우
                    v = bool(util.strtobool(v))
                    setattr(model, k, v)
                elif v.startswith("{"):  # dict 인 경우
                    v = literal_eval(v)
                    setattr(model, k, v)
                else:
                    setattr(model, k, v) # str 인 경우(대소문 중요!!)
            return model
        except Exception as e:
            where_exception(error_msg=e)
            return model


class InspectUserRequest(PrepareModelTrain):
    """
    For inspecting Users' POST or PATCH request

    """

    def __init__(self):
        self.req_info_algorithm_seq_pk = None
        self.req_info_train_data_id = None
        self.req_info_train_data_type = None
        self.req_info_model_param = None
        self.req_info_train_param = None

        self.clf = None
        self.library_name = None
        self.function_usage = None
        self.model_param = None
        self.train_param = None
        self.train_data_dict = None
        self.train_data_type = None
        self.train_data_columns = None

    # 공통 에러 형식
    @staticmethod
    def _error_return_dict(error_type, error_msg):
        """
        @type error_type: str
        @type error_msg: str
        @param error_type: error type represented by '0000' or str
        @param error_msg:  error message (str)
        @return:
        """
        return dict(error_type=error_type, error_msg=error_msg)

    # 필수 파라미터 검사 (4101)
    @staticmethod
    def _mandatory_key_exists_models_post(element):
        """
        @type element: dict
        @type Boolean(True) or str
        @param element: request_info (user request param(json) from django's views.py (request.data))
        @return: True (if element is valid)
                 key (if not)
        """
        mand_key = ["algorithms_sequence_pk", "train_data", "train_parameters"]
        for key in mand_key:
            if key not in element.keys():
                return key
            if key == "train_data":
                get_train_data_info = element["train_data"].keys()
                is_original_data = bool(
                    "original_data_sequence_pk" in get_train_data_info
                )
                is_preprocessed_data = bool(
                    "preprocessed_data_sequence_pk" in get_train_data_info
                )
                if is_original_data == False and is_preprocessed_data == False:
                    return key
        return True

    # 요청한 알고리즘 ID와 데이터 ID가 있는지 검사 (Http404/4004)
    def _check_request_pk(self, algo_id, data_id, data_type):
        """
        check algorithm and data primary key (valid DB)
        if valid, save self.library_name, self.function_usage, self.clf,
                  self.train_data_type, self.train_data_dict and self.train_data

        @type algo_id: int
        @type data_id: int
        @type data_type: str
        @param algo_id: algorithm's database saved id
        @param data_id: data's database saved id (Original or Preprocessed)
        @param data_type: data type (Original or Preprocessed)
        @return: True (if all params are valid)
                 False (if algo_id or data_id is not valid)
                 self._error_return_dict ; dict (if data_path from data_id not valid)
        """
        if not int(algo_id) in list(
            Algorithm.objects.all().values_list("ALGORITHM_SEQUENCE_PK", flat=True)
        ):
            return False
        else:
            # USAGE 확인(regression, classification)
            user_request_algorithm = ALGOSerializer(
                Algorithm.objects.get(pk=algo_id)
            ).data
            self.library_name = user_request_algorithm["LIBRARY_NAME"]
            self.function_usage = user_request_algorithm["LIBRARY_FUNCTION_USAGE"]
            self.clf = super()._get_base_object(params=user_request_algorithm)

        if data_type == "original_data_sequence_pk":
            self.train_data_type = "original"
            if not int(data_id) in list(
                OriginalData.objects.all().values_list(
                    "ORIGINAL_DATA_SEQUENCE_PK", flat=True
                )
            ):
                return False
            else:
                self.train_data_dict = OriginalDataSerializer(
                    OriginalData.objects.get(pk=data_id)
                ).data
                data_path = self.train_data_dict["FILEPATH"]
                if not os.path.isfile(data_path):
                    logger.error(f"{data_path} 경로가 존재하지 않습니다")
                    return self._error_return_dict("4004", data_path)
                else:
                    self.train_data_columns = literal_eval(self.train_data_dict["COLUMNS"])

        elif data_type == "preprocessed_data_sequence_pk":
            self.train_data_type = "preprocessed"
            if not int(data_id) in list(
                PreprocessedData.objects.all().values_list(
                    "PREPROCESSED_DATA_SEQUENCE_PK", flat=True
                )
            ):
                return False
            else:
                self.train_data_dict = PreprocessedDataSerializer(
                    PreprocessedData.objects.get(pk=data_id)
                ).data
                data_path = self.train_data_dict["FILEPATH"]
                if not os.path.isfile(data_path):
                    logger.error(f"{data_path} 경로가 존재하지 않습니다")
                    return self._error_return_dict("4004", data_path)
                else:
                    self.train_data_columns = literal_eval(self.train_data_dict["COLUMNS"])
        return True

    # model_parameters 검사 (4012/4000)
    # 예) {"max_features": "log2", "min_samples_split":3}
    def _check_model_parameters(self, model_param_dict):
        """
        check model_param_dict is valid
        to check model_param_dict being applied with self.clf call _change_param func
        if valid, save self.model_param

        @type model_param_dict: dict or False
        @param model_param_dict: user request 'model_parameter' (request_info['model_parameters'])
        @return: True (if model_param_dict is valid)
                 self._error_return_dict ; dict (if     )
        """
        self.model_param = self.clf.get_params()

        if model_param_dict:  # model_parameters 가 있는 경우
            model_param_list = list(model_param_dict.keys())
            self.model_param.update(model_param_dict)
            logger.info(f"사용자가 변경을 요청한 모델 파라미터 {model_param_list}")

            for name in model_param_list:
                if not hasattr(self.clf, name):
                    logger.error(f"{name}는 요청 가능한 모델 파라미터가 아닙니다")
                    return self._error_return_dict("4102", name)
            try:
                self.clf = super()._change_params(
                    model=self.clf, param=model_param_dict
                )
                check_estimators_dtypes(
                    name=type(self.clf).__name__, estimator_orig=self.clf
                )
                # logger.info('모델 파라미터 적용 결과 {}'.format(self.clf.get_params()))
            except ValueError as e:
                where_exception(error_msg=e)
                return self._error_return_dict("4103", str(e))
            except LightGBMError as e:
                where_exception(error_msg=e)
                return self._error_return_dict("4103", str(e))
            except Exception as e:
                where_exception(error_msg=e)
                return self._error_return_dict("4103", str(e))
        else:  # model_parameters 가 없는 경우
            logger.info("모델 파라미터를 요청하지 않았으므로, 모델의 기본 파라미터가 적용됩니다")
            # self.model_param = self.clf.get_params()
        for k, v in self.model_param.items():
            if isinstance(v, bool) or isinstance(v, type(None)):
                self.model_param[k] = str(v)
        return True

    # train_parameters 검사 (4101, 4102)
    # 예)  "y": "target"
    def _check_train_parameters(self, train_param_dict):
        """
        check train_param_dict is valid
        if valid, save self.train_param

        @type train_param_dict: dict
        @param train_param_dict: user request 'train_parameter' (request_info['train_parameters'])
        @return: True (if train_param_dict is valid)
                 self._error_return_dict ; dict (if    )
        """
        # if train_param_dict:  # train_parameters 가 있는 경우
        train_param_list = list(train_param_dict.keys())
        logger.info(f"사용자가 요청한 학습 파라미터 {train_param_list}")
        for name in train_param_list:
            if name not in inspect.getfullargspec(self.clf.fit).args:
                logger.error(f"{name}는 요청 가능한 학습 파라미터가 아닙니다")
                return self._error_return_dict("4102", name)
        # 지도학습에서 train_parameter 에 y 값이 있는지 검사 (4101)
        if (self.library_name == "sklearn" or "lightgbm") and (
            self.function_usage == "regression" or "classification"
        ):
            if "y" not in train_param_list:
                logger.error("지도학습에서 y 학습 파라미터는 필수입니다")
                return self._error_return_dict("4101", "y")

        # 지도학습에서 요청한 train_parameter 의 y 값이 유휴한 값인지 검사 (4102)
        if train_param_dict["y"] not in self.train_data_columns:
            logger.error(f"{train_param_dict['y']}는 유효한 값이 아닙니다")
            return self._error_return_dict("4102", train_param_dict["y"])
        self.train_param = {}  # Command 필드에 저정할 train_parameters 정보 생성
        for k, v in inspect.signature(self.clf.fit).parameters.items():
            if v.default is not inspect.Parameter.empty:
                self.train_param[k] = v.default
            else:
                self.train_param[k] = None
        self.train_param.update(train_param_dict)
        for k, v in self.train_param.items():
            if isinstance(v, bool) or isinstance(v, type(None)):
                self.train_param[k] = str(v)
        return True

    # 모델 학습 요청에 대한 요청 파라미터 검사하는 함수
    def check_request_body_models_post(self, request_info, pk):
        """
        @type request_info: dict
        @type pk: int
        @param request_info: user request param(json) from django's views.py (request.data)
        @param pk: TrainInfo.objects.latest('MODEL_SEQUENCE_PK').pk + 1
        @return: True (if request_info is valid)
                 self._error_return_dict ; dict (if not)
        """

        logger.info(f"Model Train Request ID [{pk}] - Check Request Info")

        # 필수 파라미터 검사 (4101)
        is_keys = self._mandatory_key_exists_models_post(element=request_info)
        if isinstance(is_keys, str):  # mandatory key name (str)
            return self._error_return_dict("4101", is_keys)
        self.req_info_algorithm_seq_pk = request_info["algorithms_sequence_pk"]
        self.req_info_train_data_id = list(request_info["train_data"].values())[0]
        self.req_info_train_data_type = list(request_info["train_data"].keys())[0]
        self.req_info_model_param = (
            request_info["model_parameters"]
            if "model_parameters" in list(request_info.keys())
            else False
        )
        self.req_info_train_param = request_info["train_parameters"]

        # 요청한 알고리즘 ID와 데이터 ID가 있는지 검사 (Http404/4004)
        is_valid = self._check_request_pk(
            algo_id=self.req_info_algorithm_seq_pk,
            data_id=self.req_info_train_data_id,
            data_type=self.req_info_train_data_type,
        )
        if isinstance(is_valid, dict):
            if is_valid["error_type"] == "4004":
                return self._error_return_dict(
                    is_valid["error_type"], is_valid["error_msg"]
                )
                # file_not_found
        elif not is_valid:
            raise Http404
            # algorithm 또는 data ID가 없는 경우 -- resource_not_found
        # model_parameters 검사 (4012/4013)
        is_valid = self._check_model_parameters(
            model_param_dict=self.req_info_model_param
        )
        if isinstance(is_valid, dict):
            return self._error_return_dict(
                is_valid["error_type"], is_valid["error_msg"]
            )
        # train_parameters 검사 (4101/4102)
        is_valid = self._check_train_parameters(
            train_param_dict=self.req_info_train_param
        )
        if isinstance(is_valid, dict):
            return self._error_return_dict(
                is_valid["error_type"], is_valid["error_msg"]
            )
            # invalid train parameter name 또는 'y' not found
        # 요청한 데이터의 변수 타입이 수치형인지 검사 (4022)
        sample_data=literal_eval(self.train_data_dict["SAMPLE_DATA"])
        if not super()._inspect_data(sample=sample_data):
            logger.error("Train Data's dtype must be numeric not object")
            error_msg = "Data is not suitable for the algorithm"
            return self._error_return_dict("4022", error_msg)
        return True

    # 모델 중지/재시작/테스트 요청 필수 파라미터 검사하는 함수
    def check_patch_mode(self, request_info):
        valid_patch_mode = ["STOP", "TEST", "RESTART"]  # 'LOAD', 'UNLOAD'
        # 필수 body parameters 인 mode 를 요청하지 않은 경우
        if "mode" not in request_info.keys():
            return self._error_return_dict("4101", "mode")
        # mode 가 valid_patch_mode 가 아닌 경우
        if request_info["mode"] not in valid_patch_mode:
            return self._error_return_dict("4102", request_info["mode"])
        # mode 가 TEST 인데 test_data_path 를 요청하지 않은 경우
        if request_info["mode"] == "TEST":
            if "test_data_path" not in request_info.keys():
                return self._error_return_dict("4101", "test_data_path")
            # test_parameters(target, test_type) 를 요청하지 않은 경우
            # if 'test_parameters' not in request_info.keys():
            #     return dict(error_type='4101', error_msg='test_parameters')
            # if 'target' not in request_info['test_parameters'].keys():
            #     return dict(error_type='4101', error_msg='target')
        return True


class MachineLearningTask(PrepareModelTrain):
    """
    For executing Machine Learning Model Train (SKlearn and LightGBM)

    """

    @staticmethod
    def _train_sklearn_model(estimator, data_set, train_columns, target_column):
        x_data = data_set[train_columns]
        y_data = data_set[target_column]
        train_columns = list(x_data.columns.values)
        clf = copy.deepcopy(estimator)

        # 교차검증
        kfold = KFold(n_splits=5, shuffle=True, random_state=2019)
        cv_scores = cross_val_score(clf, X=x_data, y=y_data, cv=kfold)
        cv_scores = np.around(cv_scores, 8).tolist()

        # 홀드아웃 검증
        x_train, x_valid, y_train, y_valid = train_test_split(
            x_data, y_data, test_size=0.3, random_state=2019
        )
        clf_ = clf.fit(X=x_train, y=y_train)
        holdout_score = np.around(clf_.score(x_valid, y_valid), 8)

        # Final Model
        final_model = estimator.fit(X=x_data, y=y_data)
        return final_model, train_columns, cv_scores, holdout_score

    @staticmethod
    def _train_lightgbm_model(estimator, data_set, train_columns, target_column):
        x_data = data_set[train_columns]
        y_data = data_set[target_column]
        train_columns = list(x_data.columns.values)
        # 홀드아웃 검증 + Final Model
        x_train, x_valid, y_train, y_valid = train_test_split(
            x_data, y_data, test_size=0.3, random_state=2020
        )
        final_model = estimator.fit(
            X=x_train,
            y=y_train,
            eval_set=[(x_valid, y_valid)],
            early_stopping_rounds=5,
            eval_metric=None,
            verbose=10,
        )
        holdout_score = np.around(estimator.score(x_valid, y_valid), 8)
        return final_model, train_columns, holdout_score

    # RESTART 모드에서 command 검사
    def check_params(self, params_dict):
        valid_params = {}
        for param_key, param_value in params_dict.items():
            if isinstance(param_value, str):
                param_value = param_value.lower()
                if param_value == "true" or param_value == "false":
                    param_value = bool(util.strtobool(param_value))
                elif param_value == "None":
                    param_value = None
            valid_params[param_key] = param_value
        return valid_params

    def model_task_result(self, algo_pk, data_path, model_param, train_param, pk):
        final_result = dict()

        if "preprocessed_data" in data_path:
            data = super()._load_data(
                base_path="PREPROCESSED_DATA_DIR", file_name=os.path.split(data_path)[1]
            )
        elif "original_data" in data_path:
            data = super()._load_data(
                base_path="ORIGINAL_DATA_DIR", file_name=os.path.split(data_path)[1]
            )
        logger.info(f"[{data_path}] 경로에서 학습 데이터를 로드했습니다")

        # 학습에 사용될 알고리즘 불러오기
        algo = ALGOSerializer(Algorithm.objects.get(pk=algo_pk)).data
        clf = super()._get_base_object(params=algo)
        model_name = type(clf).__name__

        # 사용자 요청에 따라 모델 파라미터 변경
        if model_param is not None:
            clf = super()._change_params(model=clf, param=model_param)
        if "LGBM" in model_name:  # LightGBM 알고리즘
            final_model, train_columns, holdout_score = \
                self._train_lightgbm_model(
                    estimator=clf, 
                    data_set=data, 
                    train_columns=train_param['X'],
                    target_column=train_param["y"]
            )

            saved_name = "M_{}.pickle".format(pk)
            file_path = super()._dump_pickle(
                save_object=final_model, base_path="MODEL_DIR", file_name=saved_name
            )
            logger.info(f"요청 ID [{pk}]의 학습된 모델 저장 => M_{pk}.pickle")

            lgbm_train_param = dict(
                early_stopping_rounds=5, 
                eval_metric="default", 
                validation_data_rate=0.3
            )
            final_result = dict(
                file_path=file_path,
                file_name=saved_name,
                model_info=dict(
                    model_name=algo["ALGORITHM_NAME"],
                    model_param=clf.get_params(),
                    model_train_columns=train_columns,
                    train_param=lgbm_train_param,
                ),
                validation_info=dict(holdout_score=holdout_score),
            )
        else:  # 사이킷런 알고리즘
            if base.is_regressor(clf) == True or base.is_classifier(clf) == True:
                final_model, train_columns, cv_score, holdout_score = \
                    self._train_sklearn_model(
                        estimator=clf, 
                        data_set=data, 
                        train_columns= train_param['X'],
                        target_column=train_param['y']
                    )

                saved_name = "M_{}.pickle".format(pk)
                file_path = super()._dump_pickle(
                    save_object=final_model, base_path="MODEL_DIR", file_name=saved_name
                )
                logger.info(f"요청 ID [{pk}]의 학습된 모델 저장 => M_{pk}.pickle")

                final_result = dict(
                    file_path=file_path,
                    file_name=saved_name,
                    model_info=dict(
                        model_name=algo["ALGORITHM_NAME"],
                        model_param=clf.get_params(),
                        model_train_columns=train_columns,
                    ),
                    validation_info=dict(
                        cv_score=cv_score, holdout_score=holdout_score
                    ),
                )
        return final_result
