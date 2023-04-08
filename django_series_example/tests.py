import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_series_project.settings")
from django import setup
setup()

from math import floor
import random
from django.test import TestCase
from faker import Faker
from django_series import XAxis, YAxis, compile_time_series_chart

from dateutil.relativedelta import relativedelta

from datetime import datetime

from django_series_example.models import Video, Stream


class VideoStreamStatisticsTestCase(TestCase):
    def setUp(self):
        fake = Faker()
        self.video = Video.objects.create(name=fake.name())

        self.start = datetime(2022, 12, 1)
        self.end = datetime(2022, 12, 31)
        
        now = start
 
        Stream.objects.create(
            node_type='video',
            node_id=self.video.id,
            qty=28000,
            streamed=datetime(2022, 12, 1)
        )
        Stream.objects.create(
            node_type='video',
            node_id=self.video.id,
            qty=18000,
            streamed=datetime(2022, 12, 2)
        ) 

    def test_compile_chart(self):
        self.chart = compile_time_series_chart(
            x_axis=XAxis(
                field_id="streamed"
            ),
            y_axises=[
                YAxis(
                    field_id='qty',
                    model='stream',
                    id='@',
                    name='Stream',
                    func='sum',
                    group_by='date'
                )
            ],
            start=self.start,
            end=self.end,
            filters=dict(
                node_type='video',
                node_id=self.video.id
            )
        )
