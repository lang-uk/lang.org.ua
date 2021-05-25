from django.db import models

from .mongodb import db
from collections import defaultdict

# Create your models here.


class Corpus:
    def get_sources(self):
        grouped = defaultdict(dict)

        for source in db.corpus__sources.find():
            grouped[s["collection"]] = s


        return grouped
