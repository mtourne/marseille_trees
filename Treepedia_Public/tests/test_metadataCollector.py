import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import unittest
from collections import OrderedDict
from Treepedia import metadataCollector


class TestMetadataCollector(unittest.TestCase):

    def test_get_pano_items(self):
        # Boston
        test_data_1 = OrderedDict([('@image_width', '16384'), ('@image_height', '8192'), ('@tile_width', '512'), ('@tile_height', '512'), ('@image_date', '2019-08'), ('@pano_id', 'Z12uXTZKc7-CkGZI27rzjw'), ('@imagery_type', '1'), ('@num_zoom_levels', '5'), ('@lat', '42.400560'), ('@lng', '-71.151165'), ('@original_lat', '42.400584'), ('@original_lng', '-71.151152'), ('@elevation_wgs84_m', '-27.212080'), ('@best_view_direction_deg', '164.39876'), ('@elevation_egm96_m', '1.335211'), ('copyright', '© 2020 Google'), ('text', 'MA-2'), ('region', 'Cambridge, Massachusetts'), ('country', 'United States')])
        panoDate, panoId, panoLat, panoLon = metadataCollector.getPanoItems(test_data_1)
        
        self.assertEqual(panoDate, '2019-08')
        self.assertEqual(panoId, 'Z12uXTZKc7-CkGZI27rzjw')
        self.assertEqual(panoLat, '42.400560')
        self.assertEqual(panoLon, '-71.151165')

        # Shibuya
        test_data_2 = OrderedDict([('@image_width', '16384'), ('@image_height', '8192'), ('@tile_width', '512'), ('@tile_height', '512'), ('@image_date', '2020-01'), ('@pano_id', 'Hgpbe7YandLTAkTt191Hfw'), ('@imagery_type', '1'), ('@num_zoom_levels', '5'), ('@lat', '35.661628'), ('@lng', '139.708112'), ('@original_lat', '35.661685'), ('@original_lng', '139.708116'), ('@elevation_wgs84_m', '71.271167'), ('@best_view_direction_deg', '119.61822'), ('@elevation_egm96_m', '34.677269'), ('copyright', '© 2020 Google'), ('text', 'Aoyama-dori Ave'), ('region', 'Shibuya City, Tokyo'), ('country', 'Japan')])
        panoDate, panoId, panoLat, panoLon = metadataCollector.getPanoItems(test_data_2)
        
        self.assertEqual(panoDate, '2020-01')
        self.assertEqual(panoId, 'Hgpbe7YandLTAkTt191Hfw')
        self.assertEqual(panoLat, '35.661628')
        self.assertEqual(panoLon, '139.708112')

        # Shibuya, with different data format
        test_data_3 = OrderedDict([('@image_width', '13312'), ('@image_height', '6656'), ('@tile_width', '512'), ('@tile_height', '512'), ('@image_date', '2018-05'), ('@pano_id', 'Y37nf692NCU2nEAn7OFqmw'), ('@scene', '1'), ('@imagery_type', '5'), ('@level_id', '7137976d59905955'), ('@num_zoom_levels', '5'), ('@lat', '35.669549'), ('@lng', '139.702947'), ('@original_lat', '35.669549'), ('@original_lng', '139.702947'), ('@elevation_wgs84_m', '1.193989'), ('@best_view_direction_deg', '41.73935'), ('@elevation_egm96_m', '-35.458862'), ('copyright', '© 2020 Google'), ('text', None), ('country', 'Japan'), ('attribution_name', None)])
        panoDate, panoId, panoLat, panoLon = metadataCollector.getPanoItems(test_data_3)
        
        self.assertEqual(panoDate, '2018-05')
        self.assertEqual(panoId, 'Y37nf692NCU2nEAn7OFqmw')
        self.assertEqual(panoLat, '35.669549')
        self.assertEqual(panoLon, '139.702947')


    def test_check_pano_month_in_greenmonth(self):
        # case 1, in greenmonth
        greenmonth = ["08"]
        panoDate1 = "2019-08"
        self.assertEqual(True, metadataCollector.check_pano_month_in_greenmonth(panoDate1, greenmonth))

        # case 2, not in greenmonth
        panoDate2 = "2019-07"
        self.assertEqual(False, metadataCollector.check_pano_month_in_greenmonth(panoDate2, greenmonth))


    def test_sort_pano_list_by_date(self):
        pano_list = [   
            {   'lat': 42.37277274422208,
                'lon': -71.08278311276163,
                'month': 7,
                'panoid': 'nsrTpG-J2x5xL-SPE8x1xw',
                'year': 2007},
            {   'lat': 42.37279881264624,
                'lon': -71.08279280296806,
                'month': 8,
                'panoid': 'kFEbzO11yCR-XrQKEjM87g',
                'year': 2011},
            {   'lat': 42.37278743408569,
                'lon': -71.08280824468974,
                'month': 7,
                'panoid': 'DWd8HToF5fZMV7Fjnh3COw',
                'year': 2014},
            {   'lat': 42.3727815168744,
                'lon': -71.08279476123815,
                'month': 9,
                'panoid': 'P32D4tE8PDMCwXwquHDbFA',
                'year': 2018},
            {   'lat': 42.37280035166095,
                'lon': -71.0827322522328,
                'panoid': 'WusqZvc_h-rOYGtBRTnciA'},
            {   'lat': 42.37266257978233,
                'lon': -71.08283965867031,
                'panoid': 'S87dfypNal44x8VxW95u5Q'}
        ]
        actual = metadataCollector.sort_pano_list_by_date(pano_list)
        expected = [   
            {   'lat': 42.3727815168744,
                'lon': -71.08279476123815,
                'month': 9,
                'panoid': 'P32D4tE8PDMCwXwquHDbFA',
                'year': 2018},
            {   'lat': 42.37278743408569,
                'lon': -71.08280824468974,
                'month': 7,
                'panoid': 'DWd8HToF5fZMV7Fjnh3COw',
                'year': 2014},
            {   'lat': 42.37279881264624,
                'lon': -71.08279280296806,
                'month': 8,
                'panoid': 'kFEbzO11yCR-XrQKEjM87g',
                'year': 2011},
            {   'lat': 42.37277274422208,
                'lon': -71.08278311276163,
                'month': 7,
                'panoid': 'nsrTpG-J2x5xL-SPE8x1xw',
                'year': 2007},
            {   'lat': 42.37280035166095,
                'lon': -71.0827322522328,
                'panoid': 'WusqZvc_h-rOYGtBRTnciA'},
            {   'lat': 42.37266257978233,
                'lon': -71.08283965867031,
                'panoid': 'S87dfypNal44x8VxW95u5Q'}
        ]
        self.assertListEqual(expected, actual)


    def test_get_next_pano_in_greenmonth(self):
        pano_list = [   
            {   'lat': 42.3727815168744,
                'lon': -71.08279476123815,
                'month': 9,
                'panoid': 'P32D4tE8PDMCwXwquHDbFA',
                'year': 2018},
            {   'lat': 42.37278743408569,
                'lon': -71.08280824468974,
                'month': 7,
                'panoid': 'DWd8HToF5fZMV7Fjnh3COw',
                'year': 2014},
            {   'lat': 42.37279881264624,
                'lon': -71.08279280296806,
                'month': 8,
                'panoid': 'kFEbzO11yCR-XrQKEjM87g',
                'year': 2011},
            {   'lat': 42.37277274422208,
                'lon': -71.08278311276163,
                'month': 7,
                'panoid': 'nsrTpG-J2x5xL-SPE8x1xw',
                'year': 2007},
            {   'lat': 42.37280035166095,
                'lon': -71.0827322522328,
                'panoid': 'WusqZvc_h-rOYGtBRTnciA'},
            {   'lat': 42.37266257978233,
                'lon': -71.08283965867031,
                'panoid': 'S87dfypNal44x8VxW95u5Q'}
        ]

        # case 1: pano is next pano (second in list)
        greenmonth = ["07", "08"]
        year = 2014
        actual = metadataCollector.get_next_pano_in_greenmonth(pano_list, greenmonth, year)
        expected_panoDate = "2014-07"
        expected_panoId = 'DWd8HToF5fZMV7Fjnh3COw'
        expected_panoLat = 42.37278743408569
        expected_panoLon = -71.08280824468974

        self.assertEqual(expected_panoDate, actual[0])
        self.assertEqual(expected_panoId, actual[1])
        self.assertEqual(expected_panoLat, actual[2])
        self.assertEqual(expected_panoLon, actual[3])

        # case 2: pano is third in list as second pano is not in greenmonth
        greenmonth = ["08"]
        year = 2014
        actual = metadataCollector.get_next_pano_in_greenmonth(pano_list, greenmonth, year)
        expected_panoDate = "2011-08"
        expected_panoId = 'kFEbzO11yCR-XrQKEjM87g'
        expected_panoLat = 42.37279881264624
        expected_panoLon = -71.08279280296806

        self.assertEqual(expected_panoDate, actual[0])
        self.assertEqual(expected_panoId, actual[1])
        self.assertEqual(expected_panoLat, actual[2])
        self.assertEqual(expected_panoLon, actual[3])

        # case 3: no other panos in greenmonth
        greenmonth = ["04"]
        year = 2014
        actual = metadataCollector.get_next_pano_in_greenmonth(pano_list, greenmonth, year)
        expected_panoDate = "2018-09"
        expected_panoId = 'P32D4tE8PDMCwXwquHDbFA'
        expected_panoLat = 42.3727815168744
        expected_panoLon = -71.08279476123815

        self.assertEqual(expected_panoDate, actual[0])
        self.assertEqual(expected_panoId, actual[1])
        self.assertEqual(expected_panoLat, actual[2])
        self.assertEqual(expected_panoLon, actual[3])


        # case 4: year is unspecified ("")
        # should return latest pano in greenmonth
        greenmonth = ["07"]
        year = ""
        actual = metadataCollector.get_next_pano_in_greenmonth(pano_list, greenmonth, year)
        expected_panoDate = "2014-07"
        expected_panoId = 'DWd8HToF5fZMV7Fjnh3COw'
        expected_panoLat = 42.37278743408569
        expected_panoLon = -71.08280824468974

        self.assertEqual(expected_panoDate, actual[0])
        self.assertEqual(expected_panoId, actual[1])
        self.assertEqual(expected_panoLat, actual[2])
        self.assertEqual(expected_panoLon, actual[3])


        # case 5: year is given
        # should return pano in greenmonth older than specified year
        greenmonth = ["07", "08"]
        year = 2013
        actual = metadataCollector.get_next_pano_in_greenmonth(pano_list, greenmonth, year)
        expected_panoDate = "2011-08"
        expected_panoId = 'kFEbzO11yCR-XrQKEjM87g'
        expected_panoLat = 42.37279881264624
        expected_panoLon = -71.08279280296806

        self.assertEqual(expected_panoDate, actual[0])
        self.assertEqual(expected_panoId, actual[1])
        self.assertEqual(expected_panoLat, actual[2])
        self.assertEqual(expected_panoLon, actual[3])


    def test_get_pano_date_str(self):
        # case 1, month < 10
        month1 = 9
        year = 2020
        actual = metadataCollector.get_pano_date_str(month1, year)
        self.assertEqual(actual, "2020-09")

        # case 2, month > 10
        month2 = 11
        year = 2019
        actual = metadataCollector.get_pano_date_str(month2, year)
        self.assertEqual(actual, "2019-11")


if __name__ == '__main__':
    unittest.main()