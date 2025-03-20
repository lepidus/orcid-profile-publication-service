class PublicationDataRetrieval:
    def __init__(self, work_data):
        self.work_data = work_data

    def get_publication_title(self):
        return self.work_data["title"]["title"]["value"]

    def get_journal_title(self):
        return self.work_data["journal-title"]["value"]