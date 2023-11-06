#!/usr/bin/env python

from .mongotimecurve import MongoTimeCurve
from somutils.isodates import localisodate
import os
import pymongo
from datetime import date
from . import testutils
from .resource import (
    ProductionMeter,
    ProductionPlant,
    ProductionAggregator,
    )

import unittest
import pytest

def local_file(filename):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), filename)

class Meter_Test(unittest.TestCase):
    def setUp(self):
        self.databasename = 'generationkwh_test'
        self.collection = 'production'

        self.connection = pymongo.MongoClient()
        self.connection.drop_database(self.databasename)
        self.db = self.connection[self.databasename]
        self.curveProvider = MongoTimeCurve(self.db, self.collection)
        self.row1 = [0,0,0,0,0,0,0,0,3,6,5,4,8,17,34,12,12,5,3,1,0,0,0,0,0,]
        self.row2 = [0,0,0,0,0,0,0,0,4,7,6,5,9,18,35,13,13,6,4,2,0,0,0,0,0,]

    def tearDown(self):
        self.connection.drop_database('generationkwh_test')

    def setupEmptyMeter(self, **kwd):
        return ProductionMeter(
            1,
            'meterName',
            'meterDescription',
            True,
            curveProvider = self.curveProvider,
            **kwd
            )

    def setupMeter(self, **kwd):
        m = self.setupEmptyMeter(**kwd)
        self.curveProvider.update(
            localisodate("2015-09-04"), 'meterName', 'ae',
            self.row1+self.row2)
        return m

    def test__get_kwh__empty(self):
        m = self.setupEmptyMeter()
        self.assertEqual(
            list(m.get_kwh(
                date(2015,9,4),
                date(2015,9,5))),
            2*25*[0]
            )

    def test__get_kwh__filled(self):
        m = self.setupMeter()
        self.assertEqual(
            list(m.get_kwh(
                date(2015,9,4),
                date(2015,9,5))),
            self.row1 + self.row2)

    def test__get_kwh__filled__whenFiltered(self):
        m = self.setupMeter(first_active_date="2015-09-05")
        self.assertEqual(
            list(m.get_kwh(
                date(2015,9,4),
                date(2015,9,5))),
            [0]*25 + self.row2)

    def test__get_kwh__filled__whenFiltered_onStart(self):
        m = self.setupMeter(first_active_date="2015-09-04")
        self.assertEqual(
            list(m.get_kwh(
                date(2015,9,4),
                date(2015,9,5))),
            self.row1 + self.row2)

    def test__get_kwh__filled__whenFiltered_onEnd(self):
        m = self.setupMeter(first_active_date="2015-09-06")
        self.assertEqual(
            list(m.get_kwh(
                date(2015,9,4),
                date(2015,9,5))),
            [0]*50)

    def test_lastDate_empty(self):
        m = self.setupEmptyMeter()
        self.assertEqual(m.lastMeasurementDate(), None)

    def test_lastDate_filled(self):
        m = self.setupMeter()
        self.assertEqual(m.lastMeasurementDate(), date(2015,9,5))

    def test_firstDate_empty(self):
        m = self.setupEmptyMeter()
        self.assertEqual(m.firstMeasurementDate(), None)

    def test_firstDate_filled(self):
        m = self.setupMeter()
        self.assertEqual(m.firstMeasurementDate(), date(2015,9,4))


class Resource_Test(unittest.TestCase):

    def setUp(self):
        self.databasename = 'generationkwh_test'
        self.collection = 'production'

        self.connection = pymongo.MongoClient()
        self.connection.drop_database(self.databasename)
        self.db = self.connection[self.databasename]
        self.curveProvider = MongoTimeCurve(self.db, self.collection)
        self.row1 = [0,0,0,0,0,0,0,0,3,6,5,4,8,17,34,12,12,5,3,1,0,0,0,0,0]
        self.row2 = [0,0,0,0,0,0,0,0,4,7,6,5,9,18,35,13,13,6,4,2,0,0,0,0,0]

    def tearDown(self):
        self.connection.drop_database('generationkwh_test')

    def setupMeter(self, n, name):
        return ProductionMeter(
            id=n,
            name = name,
            description = 'meterDescription{}'.format(n),
            enabled = True,
            curveProvider = self.curveProvider,
            )

    def fillMeter(self, name, start):
        self.curveProvider.update(
            localisodate(start), name, 'ae',
            self.row1+self.row2)


    def test__get_kwh__empty(self):
        m = self.setupMeter(1, 'counter')

        p = ProductionPlant(1,'plantName','plantDescription',True, meters=[m])
        aggr = ProductionAggregator(1,'aggrName','eggrDescription',True, plants=[p])

        self.assertEqual(
            list(aggr.get_kwh(
                date(2015,9,4),
                date(2015,9,5))),
                2*25*[0] 
                )
      
    def test__get_kwh__onePlantOneMeter(self):
        m = self.setupMeter(1, '20150904')

        p = ProductionPlant(1,'plantName','plantDescription',True, meters=[m])
        aggr = ProductionAggregator(1,'aggrName','aggrDescription',True, plants=[p])
        self.fillMeter('20150904', '2015-09-04')

        self.assertEqual(
            list(aggr.get_kwh(
                date(2015,9,4),
                date(2015,9,5))),
            [
                0,0,0,0,0,0,0,0,3,6,5,4,8,17,34,12,12,5,3,1,0,0,0,0,0,
                0,0,0,0,0,0,0,0,4,7,6,5,9,18,35,13,13,6,4,2,0,0,0,0,0,
            ])

    def test__get_kwh__onePlantTwoMeters(self):
        m1 = self.setupMeter(1,'m1')
        self.fillMeter('m1', '2015-09-04')
        m2 = self.setupMeter(2,'m2')
        self.fillMeter('m2', '2015-09-04')

        p = ProductionPlant(1,'plantName','plantDescription',True, meters=[m1,m2])
        aggr = ProductionAggregator(1,'aggrName','aggrDescription',True, plants=[p])

        self.assertEqual(
            list(aggr.get_kwh(
                date(2015,9,4),
                date(2015,9,5))),
            [
                0,0,0,0,0,0,0,0,6,12,10, 8,16,34,68,24,24,10,6,2,0,0,0,0,0,
                0,0,0,0,0,0,0,0,8,14,12,10,18,36,70,26,26,12,8,4,0,0,0,0,0,
            ])

    import sys
    @pytest.mark.skipif(sys.version_info > (2,8), reason="py3 numpy requires same dimensions when sum arrays")
    def test__get_kwh__twoPlantsOneMeter(self):
        m1 = self.setupMeter(1, 'm1')
        self.fillMeter('m1', '2015-09-04')
        p1 = ProductionPlant(1,'plantName1','plantDescription1',True, meters=[m1])
        p2 = ProductionPlant(2,'plantName2','plantDescription2',True)
        aggr = ProductionAggregator(1,'aggrName','aggrDescription',True,plants=[p1,p2])

        self.assertEqual(
            list(aggr.get_kwh(
                date(2015,9,4),
                date(2015,9,5))),
            [
                0,0,0,0,0,0,0,0,3,6,5,4,8,17,34,12,12,5,3,1,0,0,0,0,0,
                0,0,0,0,0,0,0,0,4,7,6,5,9,18,35,13,13,6,4,2,0,0,0,0,0,
            ])

    def test__get_kwh__twoPlantsTwoMeters(self):
        m1 = self.setupMeter(1, 'm1')
        self.fillMeter('m1', '2015-09-04')
        p1 = ProductionPlant(1,'plantName1','plantDescription1',True, meters=[m1])

        m2 = self.setupMeter(2, 'm2')
        self.fillMeter('m2', '2015-09-04')
        p2 = ProductionPlant(2,'plantName2','plantDescription2',True, meters=[m2])

        aggr = ProductionAggregator(1,'aggrName','aggreDescription',True,
            plants=[p1, p2])

        self.assertEqual(
            list(aggr.get_kwh(
                date(2015,9,4),
                date(2015,9,5))),
            [
                0,0,0,0,0,0,0,0,6,12,10, 8,16,34,68,24,24,10,6,2,0,0,0,0,0,
                0,0,0,0,0,0,0,0,8,14,12,10,18,36,70,26,26,12,8,4,0,0,0,0,0,
            ])

    def test_lastDate_empty(self):
        m = self.setupMeter(1, '20150904')
        p = ProductionPlant(1,'plantName','plantDescription',True, meters=[m])
        aggr = ProductionAggregator(1,'aggrName','aggreDescription',True,
            plants=[p])

        self.assertEqual(aggr.lastMeasurementDate(), None)
    
    def test_firstDate_empty(self):
        m = self.setupMeter(1, '20150904')
        p = ProductionPlant(1,'plantName','plantDescription',True, meters=[m])
        aggr = ProductionAggregator(1,'aggrName','aggreDescription',True, plants=[p])

        self.assertEqual(aggr.firstMeasurementDate(), None)

    def test_lastDate_onePlantOneMeter(self):
        m = self.setupMeter(1, 'm1')
        self.fillMeter('m1', '2015-09-04')
        p = ProductionPlant(1,'plantName','plantDescription',True, meters=[m])
        aggr = ProductionAggregator(1,'aggrName','aggreDescription',True, plants=[p])

        self.assertEqual(aggr.lastMeasurementDate(), date(2015,9,5))

    def test_firstDate_onePlantOneMeter(self):
        m = self.setupMeter(1, 'm1')
        self.fillMeter('m1', '2015-09-04')
        p = ProductionPlant(1,'plantName','plantDescription',True, meters=[m])
        aggr = ProductionAggregator(1,'aggrName','aggreDescription',True, plants=[p])

        self.assertEqual(aggr.firstMeasurementDate(), date(2015,9,4))

    def test_lastDate_onePlantTwoMeters(self):
        m1 = self.setupMeter(1, 'm1')
        m2 = self.setupMeter(2, 'm2')
        self.fillMeter('m1', '2015-09-04')
        self.fillMeter('m2', '2015-08-04')

        p = ProductionPlant(1,'plantName','plantDescription',True, meters=[m1,m2])
        aggr = ProductionAggregator(1,'aggrName','aggreDescription',True, plants=[p])

        self.assertEqual(aggr.lastMeasurementDate(), date(2015,8,5))

    def test_firstDate_onePlantTwoMeters(self):
        m1 = self.setupMeter(1, 'm1')
        m2 = self.setupMeter(2, 'm2')
        self.fillMeter('m1', '2015-09-04')
        self.fillMeter('m2', '2015-08-04')

        p = ProductionPlant(1,'plantName','plantDescription',True, meters=[m1,m2])
        aggr = ProductionAggregator(1,'aggrName','aggreDescription',True, plants=[p])

        self.assertEqual(aggr.firstMeasurementDate(), date(2015,8,4))

    def test_lastDate_twoPlantsTwoMeters(self):
        m1 = self.setupMeter(1, 'm1')
        m2 = self.setupMeter(2, 'm2')
        self.fillMeter('m1', '2015-09-04')
        self.fillMeter('m2', '2015-08-04')

        p1 = ProductionPlant(1,'plantName1','plantDescription1',True, meters=[m1])
        p2 = ProductionPlant(2,'plantName2','plantDescription2',True, meters=[m2])
        aggr = ProductionAggregator(1,'aggrName','aggreDescription',True, plants=[p1,p2])

        self.assertEqual(aggr.lastMeasurementDate(), date(2015,8,5))

    def test_firstDate_twoPlantsTwoMeters(self):
        m1 = self.setupMeter(1, 'm1')
        m2 = self.setupMeter(2, 'm2')
        self.fillMeter('m1', '2015-09-04')
        self.fillMeter('m2', '2015-08-04')

        p1 = ProductionPlant(1,'plantName1','plantDescription1',True, meters=[m1])
        p2 = ProductionPlant(2,'plantName2','plantDescription2',True, meters=[m2])
        aggr = ProductionAggregator(1,'aggrName','aggreDescription',True, plants=[p1,p2])

        self.assertEqual(aggr.firstMeasurementDate(), date(2015,8,4))

class Mix_Test(unittest.TestCase):

    def setUp(self):
        self.databasename = 'generationkwh_test'
        self.collection = 'production'

        self.connection = pymongo.MongoClient()
        self.connection.drop_database(self.databasename)
        self.db = self.connection[self.databasename]
        self.curveProvider = MongoTimeCurve(self.db, self.collection)
        self.row1 = [0,0,0,0,0,0,0,0,3,6,5,4,8,17,34,12,12,5,3,1,0,0,0,0,0]
        self.row2 = [0,0,0,0,0,0,0,0,4,7,6,5,9,18,35,13,13,6,4,2,0,0,0,0,0]

    def tearDown(self):
        self.connection.drop_database('generationkwh_test')

    def setupMeter(self, n, name):
        return ProductionMeter(
            id=n,
            name = name,
            description = 'meterDescription{}'.format(n),
            enabled = True,
            curveProvider = self.curveProvider,
            )

    def fillMeter(self, name, start):
        self.curveProvider.update(
            localisodate(start), name, 'ae',
            self.row1+self.row2)


    def test_firstActiveDate_noPlants(self):
        aggr = ProductionAggregator(1,'aggrName','aggreDescription',True, plants=[])

        self.assertEqual(aggr.firstActiveDate(), None)

    def test_firstActiveDate_singlePlant(self):
        m1 = self.setupMeter(1, 'm1')
        p1 = ProductionPlant(1,'plantName1','plantDescription1',True, '2000-01-01', meters=[m1])
        aggr = ProductionAggregator(1,'aggrName','aggreDescription',True, plants=[p1])

        self.assertEqual(aggr.firstActiveDate(), date(2000,1,1))

    def test_firstActiveDate_manyPlants(self):
        m1 = self.setupMeter(1, 'm1')
        m2 = self.setupMeter(2, 'm2')
        p1 = ProductionPlant(1,'plantName1','plantDescription1',True, '2000-01-01', meters=[m1])
        p2 = ProductionPlant(2,'plantName2','plantDescription2',True, '2001-01-01', meters=[m2])
        aggr = ProductionAggregator(1,'aggrName','aggreDescription',True, plants=[p1,p2])

        self.assertEqual(aggr.firstActiveDate(), date(2000,1,1))

        


# vim: et ts=4 sw=4
