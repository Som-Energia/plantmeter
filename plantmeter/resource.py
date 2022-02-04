import numpy as np

from somutils.isodates import (
    isodate,
    dateToLocal,
    assertDate,
    )
import datetime

"""
TODOs
+ Ordre
- Duplicats
- Gaps
+ Padding
"""

class Resource(object):
    id = None 
    name = None
    description = None
    enabled = None

    def __init__(self, id, name, description, enabled):
        self.id = id 
        self.name = name
        self.description = description
        self.enabled = enabled

class ParentResource(Resource):

    def __init__(self, id, name, description, enabled, children=[]):
        super(ParentResource, self).__init__(id, name, description, enabled)
        self.children = children

    def get_kwh(self, start, end):

        assertDate('start', start)
        assertDate('end', end)

        return np.sum([
            child.get_kwh(start, end)
            for child in self.children
            if child.enabled
            ], axis=0)

    def firstMeasurementDate(self):
        return min([
            child.firstMeasurementDate()
            for child in self.children
            if child.enabled
            ])

    def lastMeasurementDate(self):
        return min([
            child.lastMeasurementDate()
            for child in self.children
            if child.enabled
            ])

class ProductionAggregator(ParentResource):
    def __init__(self, id, name, description, enabled, plants=[]):
        super(ProductionAggregator, self).__init__(
            id, name, description, enabled, children=plants)

    def firstActiveDate(self):
        if not self.children: return None
        return isodate(min(plant.first_active_date for plant in self.children))

class ProductionPlant(ParentResource):
    def __init__(self, id, name, description, enabled, first_active_date=None, last_active_date=None, meters=[]):
        super(ProductionPlant, self).__init__(
            id, name, description, enabled, children=meters)
        self.first_active_date = first_active_date

class ProductionMeter(Resource):
    def __init__(self, *args, **kwargs):
        self.first_active_date = kwargs.pop('first_active_date', None)
        self.first_active_date = self.first_active_date and isodate(self.first_active_date)
        self.curveProvider = kwargs.pop('curveProvider', None)
        super(ProductionMeter, self).__init__(*args, **kwargs)

    def get_kwh(self, start, end):

        assertDate('start', start)
        assertDate('end', end)

        data = self.curveProvider.get(
            start=dateToLocal(start),
            stop=dateToLocal(end),
            filter=self.name,
            field='ae',
            )

        if self.first_active_date and self.first_active_date >= start:
            nbins= (self.first_active_date-start).days * 25
            data[:nbins] = 0

        return data

    def lastMeasurementDate(self):
        result = self.curveProvider.lastFullDate(self.name)
        return result and result.date()
    
    def firstMeasurementDate(self):
        result = self.curveProvider.firstFullDate(self.name)
        return result and result.date()

# vim: et ts=4 sw=4
