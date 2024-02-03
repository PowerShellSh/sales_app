from django.test import TestCase
from datetime import datetime, timedelta, timezone
from sales.views import SalesAggregateView
from freezegun import freeze_time


class TestSalesAggregateView(TestCase):
    @freeze_time("2024-01-20 12:00:00", tz_offset=9)
    def test_init(self):
        # インスタンスの作成
        view = SalesAggregateView()
        # end_of_day のアサーション
        expected_end_of_day = datetime(2024, 1, 21, 23, 59, 59, tzinfo=timezone(timedelta(hours=9)))
        self.assertEqual(view.end_of_day, expected_end_of_day)

        # start_date_monthly のアサーション
        expected_start_date_monthly = datetime(2023, 11, 1, 0, 0, 0, tzinfo=timezone(timedelta(hours=9)))
        self.assertEqual(view.start_date_monthly, expected_start_date_monthly)

        # start_date_daily のアサーション
        expected_start_date_daily = datetime(2024, 1, 19, 0, 0, 0, tzinfo=timezone(timedelta(hours=9)))
        self.assertEqual(view.start_date_daily, expected_start_date_daily)
