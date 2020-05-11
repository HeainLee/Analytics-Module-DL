import os
import json
import logging
import pandas as pd
import numpy as np
import matplotlib # 맥에서 에러 처리용
matplotlib.use("agg") # 맥에서 에러 처리용
import matplotlib.pyplot as plt

from ..utils.custom_decorator import where_exception

logger = logging.getLogger('collect_log_helper')


class DataSummary:

    def __init__(self, path):
        self.data = self.get_data(path)
        self.columns = self.data.columns

    def _categorical(self, col_name):
        col_data = self.data[col_name]
        if len(set(col_data)) == len(col_data):
            return "count", {"elements":"unique",
                             "frequency":[str(len(col_data))], 
                             "additional_info":{"nan":str(len(col_data)-len(col_data.dropna()))}}
        elif len(set(col_data)) < 3:
            dic = dict(col_data.value_counts())
            return "pie", {"elements":list(dic.keys()),
                           "frequency":list(map(str,dic.values())), 
                           "additional_info":{"valid":str(len(col_data.dropna())), 
                                              "nan":str(len(col_data)-len(col_data.dropna()))}}
        else:
            dic = dict(col_data.value_counts())
            return "bar", {"elements":list(dic.keys()),
                           "frequency":list(map(str,dic.values())), 
                           "additional_info":{"valid":str(len(col_data.dropna())), 
                                              "nan":str(len(col_data)-len(col_data.dropna())), 
                                              "most_frequence":str(max(dic, key=lambda k: dic[k]))}}

    def _numerical(self, col_name):
        col_data=self.data[col_name]
        (freq, bins, patches) = plt.hist(col_data)
        bins_means = []
        for i in range(len(bins) - 1):
            bins_means.append(np.mean([bins[i], bins[i + 1]]))
        return "histogram", {"bins_means":list(map(str,np.round(bins_means,decimals=3))),
                             "frequency":list(map(str,np.round(freq,decimals=3))), 
                             "additional_info":{"valid":str(len(col_data.dropna())),
                                                "nan":str(len(col_data)-len(col_data.dropna())), 
                                                "mean" : str(col_data.describe()["mean"]), 
                                                "std" : str(col_data.describe()["std"]), 
                                                "quantiles": dict(col_data.describe()[3:])}}

    def get_data(self, path):
        if os.path.splitext(path)[1] == '.csv':
            df_data = pd.read_csv(path)
        elif os.path.splitext(path)[1] == '.json':
            if 'O' in path:
                df_data = pd.read_json(path, lines=True, encoding='utf-8') \
                    .fillna("None").sort_index()
            elif 'P' in path:
                df_data = pd.read_json(path, orient='index').sort_index()
        return df_data

    def columns_info(self):
        columns_list = list(self.columns)
        return str(columns_list)

    def sample_info(self):
        sample_data = self.data.loc[:4].to_json()
        sample_data = json.loads(sample_data)
        return str(sample_data)

    def size_info(self):
        amount = self.data.shape[0]
        return amount

    def statistics_info(self):
        graph_types = []
        compact_datas = []
        data_statistics = []
        column_dtypes = self.data.dtypes.replace('object', 'string')
        
        for i, j in enumerate(column_dtypes):
            if sum(self.data[self.columns[i]].isna())==len(self.data[self.columns[i]]):
                j="string"
            if list(self.data[self.columns[i]].unique()) in [[0, 1], [1, 0]]:
                j="string"
                
            try:                    
                if j in ["float64", "float32", "int64", "int32"]:  # numerical 일 경우
                    column_dtypes[i] = 'numerical'
                    get_graph_type, get_compact_data = self._numerical(self.columns[i])

                else:  # categorical 일 경우
                    column_dtypes[i] = 'categorical'
                    get_graph_type, get_compact_data = self._categorical(self.columns[i])

                graph_types.append(get_graph_type)
                compact_datas.append(get_compact_data)

            except Exception as e:
                where_exception(e)
                logger.error("Cant Extract Graph Data "+self.columns[i])
                graph_types.append("")
                compact_datas.append({})

        for name, data_type, graph_type, compact_data in zip(
                self.columns, column_dtypes, graph_types, compact_datas):
            single_column_info = {'name': name,
                                  'type': data_type,
                                  'graph_type': graph_type,
                                  'compact_data': compact_data}
            data_statistics.append(single_column_info)

        data_statistics = json.dumps(data_statistics)
        return data_statistics
