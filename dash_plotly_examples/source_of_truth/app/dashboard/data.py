import typing as typ

import pandas as pd


class DataManager:
    """
    Manage dashboard data using the singleton pattern to coordinate data
    updates across requests
    """

    class __DataManager:
        """
        Singleton instance for the data manager
        """

        def __init__(self):
            self._data = {
                "Insect Control": {
                    "GPA": {
                        "data": {
                            "sample_id": [1, 2, 3, 4, 5],
                            "score_date": [
                                "2022-10-02",
                                "2022-10-03",
                                "2022-10-02",
                                "2022-10-01",
                                "2022-09-15",
                            ],
                            "media": ["agar", "agar", "agar", "agar", "agar"],
                            "number_dead": [100, 80, 90, 60, 70],
                            "total_insects": [205, 202, 203, 208, 205],
                        },
                        "columns": [
                            {
                                "name": "Sample ID",
                                "id": "sample_id",
                                "hideable": False,
                            },
                            {
                                "name": "Score Date",
                                "id": "score_date",
                                "hideable": True,
                            },
                            {
                                "name": "Media",
                                "id": "media",
                                "hideable": True,
                            },
                            {
                                "name": "Number Dead",
                                "id": "number_dead",
                                "hideable": True,
                            },
                            {
                                "name": "Total Insects",
                                "id": "total_insects",
                                "hideable": True,
                            },
                        ],
                        "charts": [
                            {
                                "title": "Number Dead",
                                "x": "sample_id",
                                "y": "number_dead",
                            },
                        ],
                    },
                    "Leps": {
                        "data": {
                            "asm": [1, 2, 3, 4, 5],
                            "score_date": [
                                "2022-10-02",
                                "2022-10-03",
                                "2022-10-02",
                                "2022-10-01",
                                "2022-09-15",
                            ],
                            "notes": ["a", "b", "c", "d", "e"],
                            "total_mice": [205, 202, 203, 208, 205],
                        },
                        "columns": [
                            {
                                "name": "ASM",
                                "id": "asm",
                                "hideable": False,
                            },
                            {
                                "name": "Score Date",
                                "id": "score_date",
                                "hideable": True,
                            },
                            {
                                "name": "Notes",
                                "id": "notes",
                                "hideable": True,
                            },
                            {
                                "name": "Total Mice",
                                "id": "total_mice",
                                "hideable": True,
                            },
                        ],
                        "charts": [
                            {
                                "title": "Total Mice",
                                "x": "asm",
                                "y": "total_mice",
                            },
                        ],
                    },
                },
                "Herbicides": {},
                "Rock Phosphate": {
                    "P-Sol": {
                        "data": {
                            "sample_id": [1, 2, 3, 4, 5],
                            "score_date": [
                                "2022-10-02",
                                "2022-10-03",
                                "2022-10-02",
                                "2022-10-01",
                                "2022-09-15",
                            ],
                            "sample_taken_by": [
                                "april",
                                "april",
                                "april",
                                "april",
                                "april",
                            ],
                            "sample_grams": [98, 95, 89, 96, 92],
                            "success": ["yes", "yes", "yes", "no", "yes"],
                        },
                        "columns": [
                            {
                                "name": "Sample ID",
                                "id": "sample_id",
                                "hideable": False,
                            },
                            {
                                "name": "Score Date",
                                "id": "score_date",
                                "hideable": True,
                            },
                            {
                                "name": "Sample Taken By",
                                "id": "sample_taken_by",
                                "hideable": True,
                            },
                            {
                                "name": "Sample Grams",
                                "id": "sample_grams",
                                "hideable": True,
                            },
                            {
                                "name": "Success",
                                "id": "success",
                                "hideable": True,
                            },
                        ],
                        "charts": [
                            {
                                "title": "Sample Grams",
                                "x": "sample_id",
                                "y": "sample_grams",
                            },
                        ],
                    },
                },
            }

        def projects(self):
            return self._data.keys()

        def assays(
            self, project: typ.Union[str, None] = None
        ) -> typ.List[str] | None:
            if project is None:
                assays = []
                for project in self._data.keys():
                    self_assays = self.assays(project)
                    assays += self_assays

                return sorted(list(set(assays)))

            if project not in self._data:
                return None

            return sorted(list(self._data[project].keys()))

        def charts(self, project: str, assay: str):
            if project not in self._data:
                return None

            if assay not in self._data[project]:
                return None

            if "charts" not in self._data[project][assay]:
                return None

            return self._data[project][assay]["charts"]

        def table_columns(self, project: str, assay: str):
            if project not in self._data:
                return None

            if assay not in self._data[project]:
                return None

            if "columns" not in self._data[project][assay]:
                return None

            return self._data[project][assay]["columns"]

        def table_data(self, project: str, assay: str) -> pd.DataFrame | None:
            """Retrieve dashboard table data

            If data has not been initialized, it will be loaded from redis
            """
            if project not in self._data:
                return None

            if assay not in self._data[project]:
                return None

            if "data" not in self._data[project][assay]:
                return None

            return pd.DataFrame(data=self._data[project][assay]["data"])

        def update_data(self):
            """
            Refresh data table from the cache
            """

            self._table_data = None

    instance = None

    def __new__(cls):  # __new__ always a class method
        if not DataManager.instance:
            DataManager.instance = DataManager.__DataManager()
        return DataManager.instance

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __setattr__(self, name, value):
        return setattr(self.instance, name, value)
