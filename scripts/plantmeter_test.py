#!/usr/bin/env python

import os
import datetime
import pytz
from plantmeter.mongotimecurve import MongoTimeCurve,parseLocalTime
from yamlns import namespace as ns

import unittest

def isodatetime(string):
    return datetime.datetime.strptime(string, "%Y-%m-%d")

def localTime(string):
    isSummer = string.endswith("S")
    if isSummer: string=string[:-1]
    return parseLocalTime(string, isSummer)

def datespan(startDate, endDate, delta=datetime.timedelta(hours=1)):
    currentDate = startDate
    while currentDate < endDate:
        yield currentDate
        currentDate += delta

class GenerationkwhProductionAggregator_Test(unittest.TestCase):
    def setUp(self):
        import erppeek
        import dbconfig
        import pymongo
        import tempfile

        self.database = dbconfig.pymongo['database']
        self.collection = 'generationkwh.production.measurement'

        self.c = erppeek.Client(**dbconfig.erppeek)
        self.m = pymongo.Connection()
        self.mdb = self.m[self.database]
        self.mdc = self.mdb[self.collection]
        self.curveProvider = MongoTimeCurve(self.mdb, self.collection)
        self.clearAggregator()
        self.clearMeasurements()
        self.tempdir = tempfile.mkdtemp()
        
    def tearDown(self):
        import os

        self.clearAggregator()
        self.clearMeasurements()
        self.clearTemp()

    def clearAggregator(self):
        aggr_obj = self.c.model('generationkwh.production.aggregator')
        plant_obj = self.c.model('generationkwh.production.plant')
        meter_obj = self.c.model('generationkwh.production.meter')
        meter_obj.unlink(meter_obj.search([]))
        plant_obj.unlink(plant_obj.search([]))
        aggr_obj.unlink(aggr_obj.search([]))

    def clearMeasurements(self):
        self.mdc.delete_many({})

    def clearTemp(self):
        for filename in os.listdir(self.tempdir):
            os.remove(os.path.join(self.tempdir, filename))
        os.removedirs(self.tempdir)

    def setupPlant(self, aggr_id, plant):
        plant_obj = self.c.model('generationkwh.production.plant')
        return plant_obj.create(dict(
            aggr_id=aggr_id,
            name='myplant%d' % plant,
            description='myplant%d' % plant,
            enabled=True))

    def setupMeter(self, plant_id, plant, meter):
        meter_obj = self.c.model('generationkwh.production.meter')
        return meter_obj.create(dict(
            plant_id=plant_id,
            name='mymeter%d%d' % (plant, meter),
            description='mymeter%d%d' % (plant, meter),
            uri='csv://%s/mymeter%d%d' % (self.tempdir, plant, meter),
            enabled=True))

    def setupAggregator(self, nplants, nmeters):
        aggr_obj = self.c.model('generationkwh.production.aggregator')
        aggr = aggr_obj.create(dict(
            name='myaggr',
            description='myaggr',
            enabled=True))

        for plant in range(nplants):
            plant_id = self.setupPlant(aggr, plant)
            for meter in range(nmeters):
                self.setupMeter(plant_id, plant, meter)
        return aggr

    def setupPointsByDay(self, points):

        for meter, start, end, values in points:
            daterange = datespan(isodatetime(start), isodatetime(end)+datetime.timedelta(days=1))
            for date, value in zip(daterange, values):
                self.curveProvider.fillPoint(
                    datetime=localTime(str(date)),
                    name=meter,
                    ae=value)

    def setupPointsByHour(self, points):
        for meter, date, value in points:
            self.curveProvider.fillPoint(
                datetime=localTime(date),
                name=meter,
                ae=value)

    def setupLocalMeter(self, filename, points):
        import csv
        def toStr(date):
            return date.strftime('%Y-%m-%d %H:%M')

        with open(filename, 'w') as tmpfile:
            writer = csv.writer(tmpfile, delimiter=';')
            writer.writerows([[toStr(date),summer,value,0,0]
                for start, end, summer, values in points
                for date,value in zip(datespan(isodatetime(start),
                    isodatetime(end)+datetime.timedelta(days=1)), values)])

    def test_GenerationkwhProductionAggregator_getwh_onePlant_withNoPoints(self):
        aggr_id = self.setupAggregator(
                nplants=1,
                nmeters=1).read(['id'])['id']

        self.setupPointsByDay([
            ('mymeter00', '2015-08-16', '2015-08-16', 24*[10])
            ])
        production = self.c.GenerationkwhProductionAggregator.getWh(
                aggr_id, '2015-08-17', '2015-08-17')
        self.assertEqual(production, 25*[0])

    def test_GenerationkwhProductionAggregator_getwh_onePlant_winter(self):
        aggr_id = self.setupAggregator(
                nplants=1,
                nmeters=1).read(['id'])['id']

        self.setupPointsByDay([
            ('mymeter00', '2015-03-16', '2015-03-16', 24*[10])
            ])
        production = self.c.GenerationkwhProductionAggregator.getWh(
                aggr_id, '2015-03-16', '2015-03-16')
        self.assertEqual(production, [0]+24*[10])

    def test_GenerationkwhProductionAggregator_getwh_onePlant_winterToSummer(self):
        aggr_id = self.setupAggregator(
                nplants=1,
                nmeters=1).read(['id'])['id']

        self.setupPointsByHour([
            ('mymeter00', '2015-03-29 00:00:00', 1),
            ('mymeter00', '2015-03-29 01:00:00', 2),
            ('mymeter00', '2015-03-29 03:00:00', 3),
            ('mymeter00', '2015-03-29 23:00:00', 4)
            ])
        production = self.c.GenerationkwhProductionAggregator.getWh(
                aggr_id, '2015-03-29', '2015-03-29')
        self.assertEqual(production, [0,1,2,3]+19*[0]+[4,0])

    def test_GenerationkwhProductionAggregator_getwh_onePlant_summer(self):
        aggr_id = self.setupAggregator(
                nplants=1,
                nmeters=1).read(['id'])['id']

        self.setupPointsByDay([
            ('mymeter00', '2015-08-16', '2015-08-16', 24*[10])
            ])
        production = self.c.GenerationkwhProductionAggregator.getWh(
                aggr_id, '2015-08-16', '2015-08-16')
        self.assertEqual(production, 24*[10]+[0])

    def test_GenerationkwhProductionAggregator_getwh_onePlant_summerToWinter(self):
        aggr_id = self.setupAggregator(
                nplants=1,
                nmeters=1).read(['id'])['id']

        self.setupPointsByHour([
            ('mymeter00','2015-10-25 00:00:00', 1),
            ('mymeter00','2015-10-25 02:00:00S', 2),
            ('mymeter00','2015-10-25 02:00:00', 3),
            ('mymeter00','2015-10-25 23:00:00', 4)
            ])
        production = self.c.GenerationkwhProductionAggregator.getWh(
                aggr_id, '2015-10-25', '2015-10-25')
        self.assertEqual(production, [1,0,2,3]+20*[0]+[4])

    def test_GenerationkwhProductionAggregator_getwh_twoPlant_withNoPoints(self):
        aggr_id = self.setupAggregator(
                nplants=2,
                nmeters=1).read(['id'])['id']

        production = self.c.GenerationkwhProductionAggregator.getWh(
                aggr_id, '2015-08-17', '2015-08-17')
        self.assertEqual(production, 25*[0])

    def test_GenerationkwhProductionAggregator_getwh_twoPlant_winter(self):
        aggr_id = self.setupAggregator(
                nplants=2,
                nmeters=1).read(['id'])['id']

        self.setupPointsByDay([
            ('mymeter00', '2015-03-16', '2015-03-16', 24*[10]),
            ('mymeter10', '2015-03-16', '2015-03-16', 24*[10])
            ])
        production = self.c.GenerationkwhProductionAggregator.getWh(
                aggr_id, '2015-03-16', '2015-03-16')
        self.assertEqual(production, [0]+24*[20])

    def test_GenerationkwhProductionAggregator_getwh_twoPlant_winterToSummer(self):
        aggr_id = self.setupAggregator(
                nplants=2,
                nmeters=1).read(['id'])['id']

        self.setupPointsByHour([
            ('mymeter00', '2015-03-29 00:00:00', 1),
            ('mymeter00', '2015-03-29 01:00:00', 2),
            ('mymeter00', '2015-03-29 03:00:00', 3),
            ('mymeter00', '2015-03-29 23:00:00', 4),
            ('mymeter10', '2015-03-29 00:00:00', 1),
            ('mymeter10', '2015-03-29 01:00:00', 2),
            ('mymeter10', '2015-03-29 03:00:00', 3),
            ('mymeter10', '2015-03-29 23:00:00', 4)
            ])
        production = self.c.GenerationkwhProductionAggregator.getWh(
                aggr_id, '2015-03-29', '2015-03-29')
        self.assertEqual(production, [0,2,4,6]+19*[0]+[8,0])

    def _test_GenerationkwhProductionAggregator_getwh_twoPlant_summer(self):
        aggr_id = self.setupAggregator(
                nplants=2,
                nmeters=1).read(['id'])['id']

        self.setupPointsByDay([
            ('mymeter00', '2015-08-16', '2015-08-16', 24*[10]),
            ('mymeter10', '2015-08-16', '2015-08-16', 24*[10])
            ])
        production = self.c.GenerationkwhProductionAggregator.getWh(
                aggr_id, '2015-08-16', '2015-08-16')
        self.assertEqual(production, 24*[20]+[0])

    def test_GenerationkwhProductionAggregator_getwh_twoPlant_summerToWinter(self):
        aggr_id = self.setupAggregator(
                nplants=2,
                nmeters=1).read(['id'])['id']

        self.setupPointsByHour([
            ('mymeter00','2015-10-25 00:00:00', 1),
            ('mymeter00','2015-10-25 02:00:00S', 2),
            ('mymeter00','2015-10-25 02:00:00', 3),
            ('mymeter00','2015-10-25 23:00:00', 4),
            ('mymeter10','2015-10-25 00:00:00', 1),
            ('mymeter10','2015-10-25 02:00:00S', 2),
            ('mymeter10','2015-10-25 02:00:00', 3),
            ('mymeter10','2015-10-25 23:00:00', 4)
            ])
        production = self.c.GenerationkwhProductionAggregator.getWh(
                aggr_id, '2015-10-25', '2015-10-25')
        self.assertEqual(production, [2,0,4,6]+20*[0]+[8])

    def test_GenerationkwhProductionAggregator_getwh_twoDays(self):
        aggr_id = self.setupAggregator(
                nplants=1,
                nmeters=1).read(['id'])['id']

        self.setupPointsByDay([
            ('mymeter00', '2015-03-16', '2015-03-17', 48*[10])
            ])
        production = self.c.GenerationkwhProductionAggregator.getWh(
                aggr_id, '2015-03-16', '2015-03-17')
        self.assertEqual(production, [0]+24*[10]+[0]+24*[10])

    def test_GenerationkwhProductionAggregator_updatewh_withNoPoints(self):
            aggr_id = self.setupAggregator(
                    nplants=1,
                    nmeters=1).read(['id'])['id']
            self.setupLocalMeter(os.path.join(self.tempdir,'mymeter00'),[
                ])

            self.c.GenerationkwhProductionAggregator.updateWh(
                    aggr_id, '2015-08-16', '2015-08-16')
            production = self.c.GenerationkwhProductionAggregator.getWh(
                    aggr_id, '2015-08-16', '2015-08-16')
            self.assertEqual(production, 25*[0])

    def test_GenerationkwhProductionAggregator_updatewh_onePlant(self):
            aggr_id = self.setupAggregator(
                    nplants=1,
                    nmeters=1).read(['id'])['id']
            self.setupLocalMeter(os.path.join(self.tempdir,'mymeter00'),[
                ('2015-08-16', '2015-08-16', 'S', 10*[0]+14*[10])
                ])

            self.c.GenerationkwhProductionAggregator.updateWh(
                    aggr_id, '2015-08-16', '2015-08-16')
            production = self.c.GenerationkwhProductionAggregator.getWh(
                    aggr_id, '2015-08-16', '2015-08-16')
            self.assertEqual(production, 10*[0]+14*[10]+[0])

    def test_GenerationkwhProductionAggregator_updatewh_twoPlant_sameDay(self):
            aggr_id = self.setupAggregator(
                    nplants=2,
                    nmeters=1).read(['id'])['id']
            self.setupLocalMeter(os.path.join(self.tempdir,'mymeter00'),[
                ('2015-08-16', '2015-08-16', 'S', 10*[0]+14*[10])
                ])
            self.setupLocalMeter(os.path.join(self.tempdir,'mymeter10'),[
                ('2015-08-16', '2015-08-16', 'S', 10*[0]+14*[20])
                ])

            self.c.GenerationkwhProductionAggregator.updateWh(
                    aggr_id, '2015-08-16', '2015-08-16')
            production = self.c.GenerationkwhProductionAggregator.getWh(
                    aggr_id, '2015-08-16', '2015-08-16')
            self.assertEqual(production, 10*[0]+14*[30]+[0])

    def test_GenerationkwhProductionAggregator_updatewh_twoPlant_differentDays(self):
            aggr_id = self.setupAggregator(
                    nplants=2,
                    nmeters=1).read(['id'])['id']
            self.setupLocalMeter(os.path.join(self.tempdir,'mymeter00'),[
                ('2015-08-16', '2015-08-16', 'S', 10*[0]+14*[10])
                ])
            self.setupLocalMeter(os.path.join(self.tempdir,'mymeter10'),[
                ('2015-08-17', '2015-08-17', 'S', 10*[0]+14*[20])
                ])

            self.c.GenerationkwhProductionAggregator.updateWh(
                    aggr_id, '2015-08-16', '2015-08-17')
            production = self.c.GenerationkwhProductionAggregator.getWh(
                    aggr_id, '2015-08-16', '2015-08-17')
            self.assertEqual(production, 10*[0]+14*[10]+[0]+10*[0]+14*[20]+[0])

    def test_GenerationkwhProductionAggregator_firstMeasurementDate_nonePoint(self):
            aggr_id = self.setupAggregator(
                    nplants=1,
                    nmeters=1).read(['id'])['id']
            self.setupLocalMeter(os.path.join(self.tempdir,'mymeter00'),[
                ])

            date = self.c.GenerationkwhProductionAggregator.firstMeasurementDate(aggr_id)
            self.assertEqual(date, '')

    def _test_GenerationkwhProductionAggregator_firstMeasurementDate_onePlant(self):
            aggr_id = self.setupAggregator(
                    nplants=1,
                    nmeters=1).read(['id'])['id']
            self.setupLocalMeter(os.path.join(self.tempdir,'mymeter00'),[
                ('2015-08-16', '2015-08-16', 'S', 10*[0]+14*[10])
                ])
            self.c.GenerationkwhProductionAggregator.updateWh(
                    aggr_id, '2015-08-16', '2015-08-16')

            date = self.c.GenerationkwhProductionAggregator.firstMeasurementDate(aggr_id)
            self.assertEqual(date, '2015-08-16')
# vim: et ts=4 sw=4
