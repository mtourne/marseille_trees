import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import unittest
from Treepedia import GreenView_Calculate

class TestGreenViewCalculate(unittest.TestCase):
    def test_get_api_url(self):
        panoID = "0TZEoCxMscKUg5y7BpADBQ"
        heading = 0
        pitch = 0
        key = "MyKey"
        actual_url = GreenView_Calculate.get_api_url(panoID, heading, pitch, key)
        expected_url = "http://maps.googleapis.com/maps/api/streetview?size=400x400&pano=0TZEoCxMscKUg5y7BpADBQ&fov=60&heading=0&pitch=0&sensor=false&key=MyKey&source=outdoor"

        self.assertEqual(actual_url, expected_url)

    def test_get_pano_lists_from_file(self):
        panoIDLst = ["PEMVMfgReaRew_JEsfG9jQ", "N0UDB9H2pkgSptkkhBU7iw"]
        panoDateLst = ["2019-08", "2019-08"]
        panoLonLst = ["-71.099664", "-71.099844"]
        panoLatLst = ["42.373572", "42.373593"]
        greenmonth = ["08"]

        actual = GreenView_Calculate.get_pano_lists_from_file("tests/test_metadata.txt", greenmonth)

        self.assertEqual(actual[0], panoIDLst)
        self.assertEqual(actual[1], panoDateLst)
        self.assertEqual(actual[2], panoLonLst)
        self.assertEqual(actual[3], panoLatLst)


if __name__ == '__main__':
    unittest.main()