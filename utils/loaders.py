import os
import pandas as pd
import geopandas as gpd
from typing import List
from pandas import DataFrame as PandasDataFrame
from geopandas import GeoDataFrame


class GeoLoader:

    def __init__(self, *, path: str, schema: List[str]):
        self.path = path
        self.schema = schema

    def get_files_in_path(self) -> List[str]:
        return [os.path.join(self.path, name) for name in os.listdir(self.path)]

    def load(self):
        raise NotImplementedError


class PandasCsvLoader(GeoLoader):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def load(self) -> PandasDataFrame:
        pdf_list = []
        for file in self.get_files_in_path():
            pdf_list.append(pd.read_csv(file, index_col=None,
                                        names=self.schema))
        return pd.concat(pdf_list, axis=0, ignore_index=True)


class GeoPandasLoader(GeoLoader):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def load(self) -> GeoDataFrame:
        gpdf_list = []
        for file in self.get_files_in_path():
            gpdf_list.append(gpd.read_file(file))
        return GeoDataFrame(pd.concat(gpdf_list))
