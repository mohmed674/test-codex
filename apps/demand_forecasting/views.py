from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.sales.models import SaleItem  # تم تعديل هنا

from .forms import ForecastForm
from .models import Forecast


@login_required
def forecast_list(request):
    forecasts = Forecast.objects.all().order_by("-forecast_month")
    return render(
        request, "demand_forecasting/forecast_list.html", {"forecasts": forecasts}
    )


@login_required
def forecast_generate(request):
    form = ForecastForm(request.POST or None)
    if form.is_valid():
        forecast = form.save(commit=False)
        product = forecast.product
        month = forecast.forecast_month

        # تحديد آخر 3 شهور
        three_months_ago = month.replace(day=1) - timezone.timedelta(days=90)

        # تجميع كميات البيع للمنتج
        total_sold = (
            SaleItem.objects.filter(
                product=product,
                invoice__date__gte=three_months_ago,
                invoice__date__lt=month,
            ).aggregate(qty=Sum("quantity"))["qty"]
            or 0
        )

        forecast.predicted_quantity = round(total_sold / 3)  # متوسط شهري
        forecast.save()
        return redirect("demand_forecasting:forecast_list")

    return render(request, "demand_forecasting/forecast_form.html", {"form": form})


def index(request):
    return render(request, "demand_forecasting/index.html")


def app_home(request):
    return render(
        request, "apps/demand_forecasting/home.html", {"app": "demand_forecasting"}
    )
