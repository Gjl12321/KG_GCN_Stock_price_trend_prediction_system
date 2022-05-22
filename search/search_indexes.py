from haystack import indexes
from stock.models import Stock, HotConcept, Holder, Concept, Industry


class StockIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Stock

    def index_queryset(self, using=None):
        return self.get_model().objects.all()



