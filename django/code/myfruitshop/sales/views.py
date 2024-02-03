from decimal import Decimal
from datetime import datetime, timedelta, timezone as dt_timezone
from typing import List, Tuple, Dict, Any, Union
from collections import defaultdict
import csv
import logging
from io import TextIOWrapper

from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, DeleteView, View
from django.db import models

from .models import Fruit, Sale
from .forms import SaleCombinedForm, SaleAddForm, FruitForm, BulkSaleForm, SaleEditForm


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FruitListView(LoginRequiredMixin, ListView):
    model: models.Model = Fruit
    template_name: str = 'fruit_list.html'
    context_object_name: str = 'fruits'
    ordering: List[str] = ['-created_at']
    queryset: models.QuerySet = Fruit.objects.filter(is_active=True)


class DeleteFruitView(LoginRequiredMixin, DeleteView):
    model: models.Model = Fruit
    success_url: str = reverse_lazy('fruit')
    template_name: str = 'fruit_confirm_delete.html'

    def delete(self, request, *args, **kwargs) -> redirect:
        self.object: models.Model = self.get_object()
        success_url: str = self.get_success_url()
        self.object.is_active = False
        self.object.save()

        return redirect(success_url)

    def get(self, request, *args, **kwargs) -> redirect:
        return self.delete(request, *args, **kwargs)


class EditFruitView(LoginRequiredMixin, UpdateView):
    model: models.Model = Fruit
    template_name: str = 'edit_fruit.html'
    form_class: models.Model = FruitForm
    success_url: str = reverse_lazy('fruit')
    http_method_names: List[str] = ['get', 'post', ]

    def get_object(self, queryset=None) -> models.Model:
        logger.info('This is an info message in get_object method.')
        return super().get_object(queryset)

    def form_valid(self, form) -> super:
        logger.info('This is an info message in form_valid method.')
        # フォームのバリデーションが成功した場合の処理
        return super().form_valid(form)

    def get_context_data(self, **kwargs) -> dict:
        context: dict = super().get_context_data(**kwargs)
        context['fruit_id'] = self.kwargs['pk']
        return context


class AddFruitView(LoginRequiredMixin, View):
    template_name: str = 'add_fruit.html'

    def get(self, request) -> render:
        form: models.Model = FruitForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request) -> render:
        form: models.Model = FruitForm(request.POST)

        if form.is_valid():
            fruit_name: str = form.cleaned_data['name']
            existing_fruit: models.Model = Fruit.objects.filter(
                name=fruit_name).first()

            if existing_fruit:
                # 既に同じ名前の果物が存在する場合
                existing_fruit.is_active = True
                existing_fruit.price = form.cleaned_data['price']
                existing_fruit.created_at = timezone.now()
                existing_fruit.updated_at = timezone.now()
                existing_fruit.save()
            else:
                # 同じ名前の果物が存在しない場合
                form.save()

            return redirect('fruit')

        return render(request, self.template_name, {'form': form})


class SaleCombinedView(LoginRequiredMixin, View):
    template_name: str = 'sales_list_combined.html'
    paginate_by: int = 10  # ページあたりのアイテム数

    def get(self, request) -> render:
        sales: models.Model = Sale.objects.select_related('fruit').filter(
            is_active=True).order_by('-sale_date')

        paginator: Paginator = Paginator(sales, self.paginate_by)
        page: int = request.GET.get('page')
        sales: models.Model = paginator.get_page(page)

        form_sale: models.Model = SaleCombinedForm()
        form_bulk_sale: models.Model = BulkSaleForm()

        return render(request, self.template_name, {'sales': sales, 'form_sale': form_sale, 'form_bulk_sale': form_bulk_sale})

    def post(self, request, *args, **kwargs) -> render:
        form_bulk_sale: models.Model = BulkSaleForm(
            request.POST, request.FILES)

        if form_bulk_sale.is_valid():
            csv_file: TextIOWrapper = TextIOWrapper(
                request.FILES['csv_file'].file, encoding='utf-8')
            reader: csv.reader = csv.reader(csv_file)
            for row in reader:
                if len(row) != 4:
                    # 期待される数の値が含まれていない場合の処理
                    continue

                fruit_name, quantity, total_amount, sale_date = row

                try:
                    fruit: models.Model = Fruit.objects.filter(name=fruit_name, is_active=True).get()
                except Fruit.DoesNotExist:
                    continue

                current_price: int = fruit.price
                expected_total_amount: int = int(quantity) * current_price

                try:
                    # 日付の形式が正しくない場合はValidationErrorが発生
                    datetime.strptime(sale_date, "%Y-%m-%d %H:%M")
                except ValueError:
                    continue

                if int(total_amount) != expected_total_amount:
                    continue

                Sale.objects.create(
                    fruit=fruit,
                    quantity=int(quantity),
                    total_amount=int(total_amount),
                    sale_date=sale_date
                )

        return self.get(request, *args, **kwargs)


class AddSaleView(LoginRequiredMixin, View):
    template_name: str = 'add_sales.html'

    def get(self, request) -> render:
        form: models.Model = SaleAddForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs) -> render:
        form_sale: models.Model = SaleAddForm(request.POST)

        if form_sale.is_valid():
            sale: models.Model = form_sale.save(commit=False)
            fruit_name: str = form_sale.cleaned_data.get('fruit')
            quantity: int = form_sale.cleaned_data.get('quantity')

            # Fruitが存在するか確認
            try:
                fruit: models.Model = Fruit.objects.get(name=fruit_name)
            except Fruit.DoesNotExist:
                form_sale.add_error('fruit', '選択した果物は存在しません。')
                return render(request, self.template_name, {'form': form_sale})

            # SaleCombinedViewでのバリデーション
            current_price: int = fruit.price
            total_amount: Decimal = quantity * current_price

            # 計算結果をsaleオブジェクトのtotal_amountフィールドに代入
            sale.total_amount = Decimal(total_amount)

            sale.save()
            logger.info('This is an info message in get_object AddSaleView.')
            return redirect('sales_combined')  # 保存後、販売情報管理画面にリダイレクト

        return render(request, self.template_name, {'form': form_sale})


class EditSaleView(LoginRequiredMixin, View):
    template_name: str = 'edit_sales.html'

    def get(self, request, pk) -> render:
        sale: models.Model = get_object_or_404(Sale, pk=pk)
        form: models.Model = SaleEditForm(instance=sale)
        return render(request, self.template_name, {'form': form, 'sale_id': pk})

    def post(self, request, pk) -> render:
        sale: models.Model = get_object_or_404(Sale, pk=pk)
        form: models.Model = SaleEditForm(request.POST, instance=sale)

        if form.is_valid():
            sale: models.Model = form.save(commit=False)
            fruit_name: str = form.cleaned_data.get('fruit')
            quantity: int = form.cleaned_data.get('quantity')
            try:
                fruit: models.Model = Fruit.objects.get(
                    name__iexact=fruit_name)
            except Fruit.DoesNotExist:
                form.add_error('fruit', '選択した果物は存在しません。')
                return render(request, self.template_name, {'form': form})

            current_price: int = fruit.price
            total_amount: Decimal = quantity * current_price

            # 計算結果をsaleオブジェクトのtotal_amountフィールドに代入
            sale.total_amount = Decimal(total_amount)
            form.save()
            return redirect('sales_combined')

        return render(request, self.template_name, {'form': form, 'sale_id': pk})


class DeleteSaleView(LoginRequiredMixin, DeleteView):
    model: models.Model = Sale
    success_url: str = reverse_lazy('sales_combined')
    template_name: str = 'sale_confirm_delete.html'

    def delete(self, request, *args, **kwargs) -> Any:
        self.object: models.Model = self.get_object()
        success_url: str = self.get_success_url()
        self.object.is_active = False
        self.object.save()

        return redirect(success_url)

    def get(self, request, *args, **kwargs) -> Any:
        return self.delete(request, *args, **kwargs)


class SalesAggregateView(LoginRequiredMixin, View):
    template_name: str = 'sales_aggregate.html'

    def __init__(self, *args, **kwargs):

        # 現在時刻を取得
        current_time = datetime.now(timezone.utc)
        # 日本時間に変換
        current_time_jp = current_time.astimezone(
            dt_timezone(timedelta(hours=9)))
        self.end_of_day = current_time_jp.replace(second=59, minute=59, hour=23)
        # 月次集計の開始日（当日を含めた3ヶ月）
        start_year = current_time_jp.year - 1 if (current_time_jp.month - 2) <= 0 else current_time_jp.year
        self.start_date_monthly = datetime(
            start_year, (current_time_jp.month - 2) % 12, 1, 0, 0, 0, tzinfo=dt_timezone(timedelta(hours=9)))
        # 日次集計の開始日（当日を含めた3日）
        # 日数の補正
        adjusted_day = current_time_jp.day - 2
        adjusted_month = current_time_jp.month
        adjusted_year = current_time_jp.year

        while adjusted_day < 1:
            # 日が1未満の場合は前月の末日を取得し、補正する
            current_time_jp = (current_time_jp.replace(day=1) - timedelta(days=1)).replace(day=1)
            adjusted_day += current_time_jp.day
            adjusted_month = current_time_jp.month

            # 年がまたがる場合の補正
            if adjusted_month == 12:
                adjusted_year -= 1

        self.start_date_daily = datetime(
            adjusted_year, adjusted_month, adjusted_day, 0, 0, 0, tzinfo=dt_timezone(timedelta(hours=9)))

    def format_data(
        self, sales_data: List[models.Model], is_monthly: bool = True
    ) -> List[Tuple[Tuple[Any, ...], Dict[str, Union[int, List[Dict[str, Union[str, Decimal, int]]]]]]]:
        formatted_data: Dict[Tuple[Any, ...], Dict[str, Union[int, List[Dict[str, Union[str, Decimal, int]]]]]] = defaultdict(
            lambda: {'total': 0, 'details': {}}
        )

        if is_monthly:
            # 月次集計の開始日（当月を含めた三ヶ月）
            start_date = self.start_date_monthly
        else:
            # 日次集計の開始日（当日を含めた3日）
            start_date = self.start_date_daily

        for sale in sales_data:
            # 指定された期間内のデータのみ処理
            if start_date <= sale.sale_date <= self.end_of_day and sale.is_active:
                key: Tuple[Any, ...] = (
                    sale.sale_date.year,
                    sale.sale_date.month
                ) if is_monthly else (
                    sale.sale_date.year,
                    sale.sale_date.month,
                    sale.sale_date.day
                )
                total_amount: Decimal = sale.total_amount

                # 新しいデータを作成する場合
                if key not in formatted_data:
                    formatted_data[key] = {'total': 0, 'details': {}}

                details: Dict[str, Union[str, Decimal, int]] = formatted_data[key]['details'].get(
                    sale.fruit.name
                )

                # すでに同じ果物のデータがある場合は合算する
                if details:
                    details['amount'] += total_amount
                    details['quantity'] += sale.quantity
                else:
                    details = {
                        'fruit': sale.fruit.name,
                        'amount': total_amount,
                        'quantity': sale.quantity,
                    }

                formatted_data[key]['details'][sale.fruit.name] = details
                formatted_data[key]['total'] += total_amount

        # 期間の部分をソート
        sorted_data: List[Tuple[Tuple[Any, ...], Dict[str, Union[int, List[Dict[str, Union[str, Decimal, int]]]]]]] = sorted(
            formatted_data.items(), key=lambda x: x[0]
        )

        # 一番古いデータを削除(4ヶ月前 OR 4日前のデータ)
        if sorted_data and len(sorted_data) > 3:
            oldest_data: Tuple[Any, ...] = sorted_data[0]
            del formatted_data[oldest_data[0]]

        return formatted_data.items()

    def get(self, request, *args, **kwargs) -> Any:
        # Get all sales data
        all_sales: List[models.Model] = Sale.objects.all()

        # 累計
        total_sales: Decimal = sum(
            sale.total_amount for sale in all_sales if sale.is_active
        )
        # UTC+9:00のオフセットを取得
        jst_offset = timedelta(hours=9)

        # monthly_sales_data の各要素の sale_date を日本時間に変換
        for sale in all_sales:
            sale.sale_date = sale.sale_date + jst_offset

        # 月別集計
        # Filter sales data for the specified conditions
        monthly_sales_data: List[models.Model] = [
            sale
            for sale in all_sales
            if self.start_date_monthly <= sale.sale_date <= self.end_of_day and sale.is_active
        ]
        monthly_data: List[Tuple[Tuple[Any, ...], Dict[str, Union[int, List[Dict[str, Union[str, Decimal, int]]]]]]] = self.format_data(
            monthly_sales_data
        )
        sorted_monthly_data: List[Tuple[Tuple[Any, ...], Dict[str, Union[int, List[Dict[str, Union[str, Decimal, int]]]]]]] = sorted(
            monthly_data, key=lambda x: x[0], reverse=True
        )

        # 日別集計
        daily_sales_data: List[models.Model] = [
            sale
            for sale in all_sales
            if self.start_date_daily <= sale.sale_date <= self.end_of_day and sale.is_active
        ]
        daily_data: List[Tuple[Tuple[Any, ...], Dict[str, Union[int, List[Dict[str, Union[str, Decimal, int]]]]]]] = self.format_data(
            daily_sales_data, is_monthly=False
        )
        sorted_daily_data: List[Tuple[Tuple[Any, ...], Dict[str, Union[int, List[Dict[str, Union[str, Decimal, int]]]]]]] = sorted(
            daily_data, key=lambda x: x[0], reverse=True
        )

        context = {
            'total_sales': total_sales,
            'monthly_data': sorted_monthly_data,
            'daily_data': sorted_daily_data,
        }

        return render(request, self.template_name, context)
