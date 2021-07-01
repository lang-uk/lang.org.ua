from collections import defaultdict
from django.db import models

from .mongodb import db


class Corpus:
    @staticmethod
    def get_sources():
        grouped = defaultdict(list)

        for source in db.corpus__sources.find():
            try:
                grouped[source["collection"]].append(source)
            except KeyError:
                pass

        return grouped

    @staticmethod
    def get_source(collection, _id):

        return db.corpus__sources.find_one({"collection": collection, "_id": _id})

    @staticmethod
    def get_sample(source, slug):
        if slug not in source["sampling_results"]:
            return None

        sample = source["sampling_results"][slug]
        samples = [i["_id"] for i in sample["ids"]]

        documents = list(db[source["collection"]].find({"_id": {"$in": samples}}))
        documents.sort(key=lambda doc: samples.index(doc["_id"]))

        sample["documents"] = documents

        return sample
