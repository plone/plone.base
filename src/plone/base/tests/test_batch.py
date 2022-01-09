from ZTUtils.Lazy import LazyMap

import unittest


class TestBatch(unittest.TestCase):
    def test_batch_no_lazy(self):
        from plone.base.batch import Batch

        batch = Batch(range(100), size=10, start=10)
        self.assertEqual([b for b in batch], [10, 11, 12, 13, 14, 15, 16, 17, 18, 19])

    def test_batch_lazy_map(self):
        from plone.base.batch import Batch

        def get(key):
            return key

        sequence = LazyMap(get, range(80, 90), actual_result_count=95)
        batch = Batch(sequence, size=10, start=80)
        self.assertEqual([b for b in batch], [80, 81, 82, 83, 84, 85, 86, 87, 88, 89])

        self.assertEqual(batch.numpages, 10)
        self.assertEqual(batch.pagenumber, 9)
        self.assertEqual(batch.navlist, range(6, 11))
        self.assertEqual(batch.leapback, [])
        self.assertEqual(batch.prevlist, range(6, 9))
        self.assertEqual(batch.previous.length, 10)
        self.assertEqual(batch.next.length, 5)
        self.assertEqual(batch.pageurl({}), "b_start:int=80")
        self.assertListEqual(
            list(batch.prevurls({})),
            [
                (6, "b_start:int=50"),
                (7, "b_start:int=60"),
                (8, "b_start:int=70"),
            ],
        )
        self.assertListEqual(
            list(batch.nexturls({})),
            [(10, "b_start:int=90")],
        )
