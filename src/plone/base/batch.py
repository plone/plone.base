from plone.batching.batch import QuantumBatch
from plone.batching.utils import calculate_pagerange
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union
from zope.deprecation import deprecate
from ZTUtils import make_query
from ZTUtils.Lazy import LazyMap


class Batch(QuantumBatch):
    b_start_str = "b_start"

    def __init__(
        self,
        sequence: Union[range, LazyMap],
        size: int,
        start: int = 0,
        end: int = 0,
        orphan: int = 0,
        overlap: int = 0,
        pagerange: int = 7,
        quantumleap: int = 0,
        b_start_str: str = "b_start",
    ):
        super().__init__(
            sequence, size, start, end, orphan, overlap, pagerange, quantumleap
        )
        self.b_start_str = b_start_str

    @deprecate("Use length attribute instead of __len__")
    def __len__(self):
        # Note: Using len() was deprecated for several years.
        # It was recommended to explicitly either use the `length` attribute
        # for the size of the current page, which is what we return now,
        # or use the `sequence_length` attribute for the size of the
        # entire sequence.
        # But the deprecation was reverted for Plone 5.2.3,
        # because core code in Products.PageTemplates called `len`
        # on batches, making the deprecation warning unavoidable
        # and thus unnecessary.
        # See https://github.com/plone/Products.CMFPlone/issues/3176
        return self.length

    def __bool__(self):
        # Without __bool__ a bool(self) would call len(self), which
        # gives a deprecation warning.
        return bool(self.length)

    # For Python 2 compatibility:
    __nonzero__ = __bool__

    def initialize(self, start: int, end: int, size: int):
        super().initialize(start, end, size)
        self.pagerange, self.pagerangestart, self.pagerangeend = calculate_pagerange(
            self.pagenumber, self.numpages, self.pagerange  # type: ignore[has-type]
        )

    def pageurl(self, formvariables: Dict[Any, Any], pagenumber: int = -1) -> str:
        # Makes the url for a given page.
        if pagenumber == -1:
            pagenumber = self.pagenumber
        b_start = pagenumber * (self.pagesize - self.overlap) - self.pagesize
        return make_query(formvariables, {self.b_start_str: b_start})

    def navurls(
        self, formvariables: Dict[Any, Any], navlist: Optional[range] = None
    ) -> map:
        # Returns the page number and url for the navigation quick links.
        if navlist is None:
            navlist = range(0)
        if not navlist:
            navlist = self.navlist
        return map(
            lambda x, formvariables=formvariables: (x, self.pageurl(formvariables, x)),
            navlist,
        )

    def prevurls(self, formvariables: Dict[Any, Any]) -> map:
        # Helper method to get prev navigation list from templates.
        return self.navurls(formvariables, self.previous_pages)

    def nexturls(self, formvariables: Dict[Any, Any]) -> map:
        # Helper method to get next navigation list from templates.
        return self.navurls(formvariables, self.next_pages)

    prevlist = QuantumBatch.previous_pages
    nextlist = QuantumBatch.next_pages
