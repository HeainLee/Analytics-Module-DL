#데이터 적용 테스트에서 필요한 함수 (train_model_view.py)
#모델이 전처리된 데이터로 학습된경우, SUMMARY 정보를 받아와서 동일하게 테스트 데이터도 전처리를 수행하는 함수

import logging
import numbers
import numpy as np
import pandas as pd
from ast import literal_eval
from django.shortcuts import get_object_or_404

from ...services.data_preprocess.preprocess_base import PreprocessorBase
from ...models.preprocessed_data import PreprocessedData
from ...serializers.serializers import PreprocessedDataSerializer
from ....utils.custom_decorator import where_exception

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


class ModelPerformance(PreprocessorBase):
    """
    Return model test result

        Attributes:
        -----------
            model_info (dict) : Model query info (eg. TrainModelSerializer)
            test_data_path (str) : real test data saved path
            model_train_command (str) : model query 'COMMAND'
            x_data (list) : columns' name model trained 
            y_data (str) : target name of data
    """
    def __init__(self, model_info, test_data_path, y_data=None):
        self.model_info = model_info
        self.test_data_path = test_data_path
        self.model_train_command = literal_eval(model_info['COMMAND'])
        self.x_data = self.model_train_command['train_parameters']['X']
        self.y_data = self.model_train_command['train_parameters']['y']
        self.y_data_transformer = None
        # self.model_session = model_session

    # Train Data와 동일한 변환기로 Test Data에 전처리를 수행하는 함수
    def _test_data_transformer(self, data_set, pdata_summary):
        test_data_columns = list(data_set.columns.values)
        train_pdata_summary = literal_eval(pdata_summary) # str => list

        # 학습된 데이터의 전처리 정보를 읽어서 차례대로 동일하게 수행하는 코드
        for preprocess_info_dict in train_pdata_summary:
            field_name = preprocess_info_dict["field_name"]
            func_name = preprocess_info_dict["function_name"]
            file_name = preprocess_info_dict["file_name"]
            logger.info(f"[모델 테스트] {func_name} applied to {field_name}")

            if field_name not in test_data_columns:
                return False
            else:
                if func_name == "DropColumns":
                    data_set = super()._drop_columns(data_set, field_name)
                else:
                    transformer = super()._load_pickle(
                        base_path="PREPROCESS_TRANSFORMER_DIR", file_name=file_name
                    )

                    if field_name == self.y_data:
                        self.y_data_transformer = transformer

                    changed_field = transformer.transform(
                        data_set[field_name].values.reshape(-1, 1)
                    )
                    changed_field = super()._to_array(changed_field)

                    # transform 된 데이터와 원본 데이터 통합(NEW) - preprocess_helper.py 참고
                    if len(changed_field.shape) == 2 and changed_field.shape[1] == 1:
                        if func_name == "Normalizer":
                            logger.warning("Not working in this version!!!")
                        else:
                            data_set[field_name] = changed_field
                    elif len(changed_field.shape) == 1:  # LabelEncoder
                        data_set[field_name] = changed_field
                    else:
                        col_name = super()._new_columns(
                            field_name=field_name, after_fitted=changed_field
                        )
                        new_columns = pd.DataFrame(changed_field, columns=col_name)
                        data_set = pd.concat(
                            [data_set, new_columns], axis=1, sort=False
                        )
                        data_set = data_set.drop(field_name, axis=1)
        return data_set

    # 예측값 또는 스코어를 출력하는 함수
    def get_test_result(self):
        try:
            pk = self.model_info["MODEL_SEQUENCE_PK"]
            if self.test_data_path.endswith(".csv"):
                test_data = pd.read_csv(self.test_data_path)
            elif self.test_data_path.endswith(".json"):
                test_data = pd.read_json(
                    self.test_data_path, lines=True, encoding="utf-8"
                )
            logger.info(f"[모델 테스트] Model ID [{pk}] Data Load!")

            pdata_info = get_object_or_404(
                PreprocessedData, pk=self.model_info["PREPROCESSED_DATA_SEQUENCE_FK2"]
            )
            pdata_serial = PreprocessedDataSerializer(pdata_info).data
            pdata_test = self._test_data_transformer(
                data_set=test_data, pdata_summary=pdata_serial["SUMMARY"]
            )

            if isinstance(pdata_test, bool): # 오류 발생시 False 반환
                logger.error(f"[모델 테스트] Model ID [{pk}] Check Columns Name")
                return _error_return_dict("4022", "Data is not suitable for the model")

            try:
                X_ = pdata_test[self.x_data]
                y_ = pdata_test[self.y_data]
            except Exception as e:
                logger.error(f"[모델 테스트] Model ID [{pk}] Check Columns Name")
                return _error_return_dict("4022", "Data is not suitable for the model")

            model_load = super()._load_pickle(
                base_path="MODEL_DIR", file_name=self.model_info["FILENAME"]
            )
            score_ = model_load.score(X=X_, y=y_)
            predict_ = model_load.predict(X=X_)

            if self.y_data_transformer != None:
                try:
                    y_ = self.y_data_transformer.inverse_transform(y_)
                    predict_ = self.y_data_transformer.inverse_transform(predict_)
                except ValueError:
                    y_ = self.y_data_transformer.inverse_transform(np.array(y_).reshape(-1,1))
                    predict_ = self.y_data_transformer.inverse_transform(np.array(predict_).reshape(-1,1))
                    y_ = np.concatenate(y_).ravel().tolist()
                    predict_ = np.concatenate(predict_).ravel().tolist()
                except Exception as e:
                    where_exception(error_msg=e)

            if isinstance(predict_[0], numbers.Integral):
                result_response = {"score": "%.3f" % score_, "predict": predict_, "real_value": y_}
                return result_response
            else:
                # result_response = ["%.3f" % elem for elem in predict_]
                result_response = {"score": "%.3f" % score_, "predict": predict_, "real_value": y_}
                return result_response
        except Exception as e:
            where_exception(error_msg=e)
