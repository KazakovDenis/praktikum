class DataExtractor:
    """A class to extract data from source"""


class DataFilter:
    """A filter class to prepare data to upload"""


class DataLoader:
    """A class to load data to a target service"""


class ETL:
    """An ETL process"""

    def __init__(self, name):
        self.name = name
        self.extractor = DataExtractor()
        self.filter = DataFilter()
        self.loader = DataLoader()

    def run(self):
        """Update data in the target service"""
        pass
