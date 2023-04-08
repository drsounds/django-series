"""
Copyright 2023 Alexander Forselius <drsounds@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from datetime import timedelta
import datetime
from urllib.parse import urlparse
from django.db.models import Sum
from dateutil.relativedelta import relativedelta
from django.utils.module_loading import import_string

from django.conf import settings


class DictObject(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
  
    def __getitem__(self, __key):
        print(__key)
        if hasattr(self, __key):
            return getattr(self, __key)
        return super().__getitem__(__key)

    def __setitem__(self, __key, __value) -> None:
        if hasattr(self, __key):
            setattr(self, __key, __value)
        return super().__setitem__(__key, __value)


class Axis(DictObject):
    field_id = ""
    type = ""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class XAxis(Axis):
    pass


class YAxis(Axis):
    model = ""
    name = ""
    filters = []
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class YAxisFilter(DictObject):
    model : str
    field_id: str
    value = None
    name = ""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class Serie(DictObject):
    values : list 
    slug : str
    name: str
    func: str
    group_by: str

    def __init__(self, values=[], slug=None, name=None, func='sum', group_by='date', *args, **kwargs) -> None:
        self.values = values
        self.name = name
        self.func = func
        self.group_by = group_by
        super().__init__(*args, **kwargs)
  

class Chart(DictObject):
    labels : list
    series : list


def resolve_model(slug):
    return import_string(settings.DJANGO_SERIES_MODELS[slug])


def compile_time_series_chart(
    x_axis,
    y_axises,
    start=None,
    end=None,
    group_by='date',
    func='sum',
    filters=dict()
):
    """Compiles a JSON dictionary representing a chart for the selected query
    
    Parameters
    ---------
    x_axis : dict
        A dictionary object representing the x axis data, with (currently) only one attribute 'column' which determines the x axis
    
    y_axises : list
        A list of dictionary representing the y-axis. Each dict is containing the following attributes:
        uri - The URI to the data to aggregate eg.

        spotlight:<model_identifier>:@:<field_to_compare>
    start : date|any 
        A start date
    end : date|any, optional
        The end date (optional)

    group_by : str, optional
        The date to break down on (date, day, month, week etc.)
    
    func : str, optional
        The function used to aggregate the data ('sum' etc.) (only sum is supported now)    
    """
    x_axis_column_slug = x_axis.get('column')
    if end: 
        if not start:
            if isinstance(end, datetime.datetime):
                start = end - timedelta(days=7) 

    x_objects = []

    if isinstance(start, datetime.datetime) and isinstance(end, datetime.datetime):
        now = start
        while now <= end:
            label = now.strftime('%Y-%m-%d') 
            if group_by == 'week':
                now = now + relativedelta(days=7)
            elif group_by == 'month':
                now = now + relativedelta(days=28)
            elif group_by == 'year':
                now = now + relativedelta(years=28)
            else:
                now = now + relativedelta(days=1)
            x_objects.append(label)

    y_series = []

    default_group_by = group_by
    default_func = func

    for y_axis in y_axises:
        y_axis_column_slug = y_axis.get('field_id')
        y_axis_column_name = y_axis.get('name')
        y_axis_collection_slug = y_axis.get('model')
        
        group_by = y_axis.get('group_by', default_group_by)
        func = y_axis.get('group_by', default_func)

        y_model = resolve_model(y_axis_collection_slug)
        q = y_model.objects 

        q = q.filter(
            **filters
        )

        if end is datetime and start is datetime:
            date_filters = {}
            date_filters[x_axis_column_slug + '__gte'] = start
            date_filters[x_axis_column_slug + '__lte'] = end
            q = q.filter(
                **date_filters
            )

        rows = q.values(x_axis_column_slug + "__" + group_by).order_by(x_axis_column_slug)

        if func == 'sum':
            rows = rows.annotate(sum=Sum(y_axis_column_slug))
        values = []

        for x_object in x_objects:
            found_row = False
            for row in rows:
                x_object_value = x_object
                row_attribute = row[x_axis_column_slug + "__" + group_by]
                if isinstance(row_attribute, datetime.datetime) or isinstance(row_attribute, datetime.date): 
                    row_attribute = row_attribute.strftime("%Y-%m-%d")
                if row_attribute == x_object_value:
                    values.append(row['sum'])
                    found_row = True
                    break
            if not found_row:
                values.append(0)

        y_serie = dict(
            values=values,
            slug=y_axis_column_slug,
            name=y_axis_column_name
        )
        y_series.append(y_serie)

    return dict(
        labels=x_objects,
        series=y_series
    )
