from unittest import TestCase
from unittest.mock import patch
from nose.tools import assert_list_equal
from .. import util as module


class TestModule(TestCase):
    def test_get_filtered_cwd__blacklist_ok(self):
        with patch('lib.util.glob') as p:
            whitelist = ['foo.txt']
            blacklist = [
                'lib',
                'LICENSE',
                'README.md',
                'SRM_Assay_Optimization.ipynb']
            p.return_value = whitelist + blacklist

            files = module.get_filtered_cwd()
            assert_list_equal(whitelist, files)
