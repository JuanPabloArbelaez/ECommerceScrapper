# from typings import Options
import csv
import json
from datetime import datetime

import pandas as pd


class SaveToDisc:
    _save_format: str = None
    _time: str = None
    _output_dir: str = None

    def __init__(self, output_dir:str, save_format: str) -> None:
        self._output_dir = output_dir
        self._save_format = save_format

    def save_file(self, filename: str, data: object) -> bool:
        self._time = str(datetime.now())[:16]
        if self._save_format == "json":
            return self._save_json(filename, data)
        elif self._save_format == "csv":
            return self._save_csv(filename, data)

    def _save_json(self, filename: str, data: object) -> bool:
        with open(f"{self._output_dir}{filename}_{self._time}.json", "w+") as fin:
            json_data = json.dumps(data, ensure_ascii=False)
            fin.write(json_data)
        return True

    def _save_csv(self, filename: str, data: object) -> bool:
        with open(f"{self._output_dir}/{filename}_{self._time}.csv", "w+") as fin:
            csv_writer = csv.writer(fin)
            if type(data) is list:
                header = data[0].keys()
                csv_writer.writerow(header)
                for d in data:
                    csv_writer.writerow(d.values())

            # recursive write to csv
            df = pd.read_json(json.dumps(data))
            pd_csv = df.to_csv("test.csv")
            print(pd_csv)
            

        return True