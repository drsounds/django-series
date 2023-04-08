"""
Copyright 2023 Alexander Forselius <drsounds@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from dateutil import parser

import graphene

from django_series import YAxis, YAxisFilter, parse_uri
from django_series import compile_time_series_chart


class SerieNode(graphene.ObjectType):
    values = graphene.List(
        graphene.Float
    )
    slug = graphene.Field(
        graphene.String
    )
    name = graphene.Field(
        graphene.String
    )


class ChartNode(graphene.ObjectType):
    series = graphene.List(
        SerieNode
    )
    labels = graphene.List(
        graphene.String
    )


class ChartQueryFilterInputType(graphene.InputObjectType):
    field_id = graphene.String(required=True)
    field_value = graphene.String()
    operator = graphene.String()


class ChartQueryInputType(graphene.InputObjectType):
    type = graphene.String(required=True)
    id = graphene.String(required=True)
    field_id = graphene.String(required=True)
    name = graphene.String(required=True)
    group_by = graphene.String(required=False)
    filters = graphene.List(
        ChartQueryFilterInputType,
        required=False
    )


class Query(graphene.ObjectType):
    chart = graphene.Field(
        ChartNode,
        x_axis_column_slug=graphene.String(required=False),
        objects=graphene.List(ChartQueryInputType, required=True),
        start=graphene.String(required=False),
        end=graphene.String(required=False),
        filters=graphene.List(ChartQueryFilterInputType, required=False),
        group_by=graphene.String(required=False),
        func=graphene.String(required=False),
    )

    def resolve_chart(
        self,
        info,
        x_axis_column_slug=None,
        objects=None,
        start=None,
        end=None,
        filters=None,
        group_by='date',
        func='sum'
    ):
        if not info.context.user.is_superuser:
            raise Exception("Not authorized")

        query_filters = {}
        for filter in filters:
            value = filter.field_value
            try:
                date_value = parser.parse(value)
                query_filters[filter.field_id] = date_value
            except:
                try:
                    float_value = float(value)
                    query_filters[filter.field_id] = float_value
                except:
                    query_filters[filter.field_id] = value

        try:
            end = parser.parse(end)
        except:
            pass
        
        try:
            start = parser.parse(start)
        except:
            pass
        

        y_axises = []

        for object in objects:

            y_axis = YAxis(
                model=object.get('model'),
                field_id=object.get('field_id'),
                name=object.get('field_id'),
                group_by=object.get('group_by', 'date'),
                func=object.get('func', 'sum'),
                filters = [
                    
                ]
            )
            for filter in object.get('filters', []):
                y_axis['filters'].append(
                    YAxisFilter(
                        field_id=filter.get('field_id'),
                        value=filter.get('value')
                    )
                )
                
            y_axises.append(y_axis)
        chart = compile_time_series_chart(
            x_axis=dict(
                column=x_axis_column_slug
            ),
            y_axises=y_axises,
            start=start,
            end=end,
            group_by=group_by,
            func=func,
            filters=query_filters
        )
        return ChartNode(
            series=[
                SerieNode(
                    values=serie.get('values'),
                    name=serie.get('name')
                )
                for
                serie
                in
                chart.get('series')
            ],
            labels=chart.get('labels')
        )

