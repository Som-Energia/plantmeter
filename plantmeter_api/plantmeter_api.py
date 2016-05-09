# -*- coding: utf-8 -*-

import os
from osv import osv, fields
from mongodb_backend import osv_mongodb
from mongodb_backend.mongodb2 import mdbpool
from .erpwrapper import ErpWrapper

from datetime import datetime
from plantmeter.resource import ProductionAggregator, ProductionPlant, ProductionMeter 
from plantmeter.mongotimecurve import MongoTimeCurve, tz
from plantmeter.isodates import localisodate

class GenerationkwhProductionAggregator(osv.osv):
    '''Implements generationkwh production aggregation '''

    _name = 'generationkwh.production.aggregator'


    def getWh(self, cursor, uid, pid, start, end, context=None):
        '''Get production aggregation'''
   
        if not context:
            context = {}
        if isinstance(pid, list) or isinstance(pid, tuple):
            pid = pid[0]

        aggr = self.browse(cursor, uid, pid, context)
        _aggr = self._createAggregator(aggr, ['id', 'name', 'description', 'enabled'])
        return _aggr.getWh(start, end).tolist()

    def updateWh(self, cursor, uid, pid, start, end, context=None):
        '''Update Wh measurements'''

        notifier = ProductionNotifierProvider(self, cursor, uid, context)
        if start > end: return
        if not context:
            context = {}
        if isinstance(pid, list) or isinstance(pid, tuple):
            pid = pid[0]

        args = ['id', 'name', 'description', 'enabled']
        aggr = self.browse(cursor, uid, pid, context)
        _aggr = self._createAggregator(aggr, args)
        return _aggr.updateWh(start, end, notifier)

    def firstMeasurementDate(self, cursor, uid, pid, context=None):
        '''Get first measurement date'''

        if not context:
            context = {}
        if isinstance(pid, list) or isinstance(pid, tuple):
            pid = pid[0]

        args = ['id', 'name', 'description', 'enabled']
        aggr = self.browse(cursor, uid, pid, context)
        _aggr = self._createAggregator(aggr, args)
        date = _aggr.firstMeasurementDate()
        return date if date else None

    def lastMeasurementDate(self, cursor, uid, pid, context=None):
        '''Get last measurement date'''

        if not context:
            context = {}
        if isinstance(pid, list) or isinstance(pid, tuple):
            pid = pid[0]

        args = ['id', 'name', 'description', 'enabled']
        aggr = self.browse(cursor, uid, pid, context)
        _aggr = self._createAggregator(aggr, args)
        date = _aggr.lastMeasurementDate()
        return date if date else None

    def getNshares(self, cursor, uid, pid, context=None):
        '''Get number of shares'''

        if not context:
            context = {}
        if isinstance(pid, list) or isinstance(pid, tuple):
            pid = pid[0]

        aggr = self.browse(cursor, uid, pid, context)
        return sum([plant.nshares for plant in aggr.plants])

    def _createAggregator(self, aggr, args):
        def obj_to_dict(obj, attrs):
            return {attr: getattr(obj, attr) for attr in attrs}

        curveProvider = MongoTimeCurve(mdbpool.get_db(),
                'generationkwh.production.measurement')

        # TODO: Clean initialization method
        return ProductionAggregator(**dict(obj_to_dict(aggr, args).items() + 
            dict(plants=[ProductionPlant(**dict(obj_to_dict(plant, args).items() +
                dict(meters=[ProductionMeter(**dict(obj_to_dict(meter, args + ['uri']).items() +
                    dict(curveProvider=curveProvider).items())) 
                for meter in plant.meters if meter.enabled]).items()))
            for plant in aggr.plants if plant.enabled]).items()))

    _columns = {
        'name': fields.char('Name', size=50),
        'description': fields.char('Description', size=150),
        'enabled': fields.boolean('Enabled'),
        'plants': fields.one2many('generationkwh.production.plant', 'aggr_id', 'Plants')
    }

    _defaults = {
        'enabled': lambda *a: False
    }
GenerationkwhProductionAggregator()


class GenerationkwhProductionAggregatorTesthelper(osv.osv):
    '''Implements generationkwh production aggregation testhelper '''

    _name = 'generationkwh.production.aggregator.testhelper'
    _auto = False


    def getWh(self, cursor, uid, pid, start, end, context=None):
        production = self.pool.get('generationkwh.production.aggregator')
        return production.getWh(cursor, uid, pid,
                localisodate(start), localisodate(end), context)

    def updateWh(self, cursor, uid, pid, start, end, context=None):
        production = self.pool.get('generationkwh.production.aggregator')
        return production.updateWh(cursor, uid, pid,
                localisodate(start), localisodate(end), context)

    def firstMeasurementDate(self, cursor, uid, pid, context=None):
        production = self.pool.get('generationkwh.production.aggregator')
        return production.firstMeasurementDate(cursor, uid, pid, context)

    def lastMeasurementDate(self, cursor, uid, pid, context=None):
        production = self.pool.get('generationkwh.production.aggregator')
        return production.lastMeasurementDate(cursor, uid, pid, context)

    def getNshares(self, cursor, uid, pid, context=None):
        production = self.pool.get('generationkwh.production.aggregator')
        return production.getNshares(cursor, uid, pid, context)

GenerationkwhProductionAggregatorTesthelper()


class GenerationkwhProductionPlant(osv.osv):

    _name = 'generationkwh.production.plant'
    _columns = {
        'name': fields.char('Name', size=50),
        'description': fields.char('Description', size=150),
        'enabled': fields.boolean('Enabled'),
        'nshares': fields.integer('Number of shares'),
        'aggr_id': fields.many2one('generationkwh.production.aggregator', 'Production aggregator',
                                  required=True),
        'meters': fields.one2many('generationkwh.production.meter', 'plant_id', 'Meters')
    }
    _defaults = {
        'enabled': lambda *a: False,
    }
GenerationkwhProductionPlant()


class GenerationkwhProductionMeter(osv.osv):

    _name = 'generationkwh.production.meter'
    _columns = {
        'name': fields.char('Name', size=50),
        'description': fields.char('Description', size=150),
        'enabled': fields.boolean('Enabled'),
        'plant_id': fields.many2one('generationkwh.production.plant'),
        'uri': fields.char('Host', size=150, required=True),
        }
    _defaults = {
        'enabled': lambda *a: False,
    }
GenerationkwhProductionMeter()


class ProductionNotifierProvider(ErpWrapper):
    def __init__(self, erp, cursor, uid, pid, context=None):
        self.pid = pid
        super(ProductionNotifierProvider, self).__init__(erp, cursor, uid, context)

    def push(self, meter_id, date, status, message):
        notifier=self.erp.pool.get('generationkwh.production.notifier')
        return notifier.create(self.cursor, self.uid, {
            'meter_id': meter_id,
            'date_pull': date,
            'status': status,
            'message': message
            })

class GenerationkwhProductionNotifier(osv.osv):
    _name = 'generationkwh.production.notifier'
    _rec_name = 'contract_id'

    _columns = {
        'meter_id': fields.many2one(
            'generationkwh.production.meter',
            'meter'
        ),
        'date_pull': fields.datetime('Last pull datetime'),
        'status': fields.selection([
            ('failed', 'Failed'),
            ('done', 'Done')]),
        'message': fields.char('Message', size=200)
    }

    _order = 'date_pull desc'
GenerationkwhProductionNotifier()


class GenerationkwhProductionNotifierTesthelper(osv.osv):
    _name = 'generationkwh.production.notifier.testhelper'
    _auto = False

    def push(self, cursor, uid, meter_id, date, status, message, context=None):
        from datetime import datetime

        notifier = ProductionNotifierProvider(self, cursor, uid, context)
        return notifier.push(meter_id, date, status, message) 

GenerationkwhProductionNotifierTesthelper()


class GenerationkwhProductionMeasurement(osv_mongodb.osv_mongodb):

    _name = 'generationkwh.production.measurement'
    _order = 'timestamp desc'

    def search(self, cursor, uid, args, offset=0, limit=0, order=None,
               context=None, count=False):
        '''Exact match for name.
        In mongodb, even when an index exists, not exact
        searches for fields scan all documents in collection
        making it extremely slow. Making name exact search
        reduces dramatically the amount of documents scanned'''

        new_args = []
        for arg in args:
            if not isinstance(arg, (list, tuple)):
                new_args.append(arg)
                continue
            field, operator, value = arg
            if field == 'name' and operator != '=':
                operator = '='
            new_args.append((field, operator, value))
        return super(GenerationkwhProductionMeasurement,
                     self).search(cursor, uid, new_args,
                                  offset=offset, limit=limit,
                                  order=order, context=context,
                                  count=count)

    _columns = {
        'name': fields.integer('Plant identifier'), # NOTE: workaround due mongodb backend
        'create_at': fields.datetime('Create datetime'),
        'datetime': fields.datetime('Exported datetime'),
        'daylight': fields.char('Exported datetime daylight',size=1),
        'ae': fields.float('Exported energy (kWh)')
    }
GenerationkwhProductionMeasurement()

# vim: ts=4 sw=4 et
