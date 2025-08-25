# ERP_CORE/sales/ai_predictor.py

import pandas as pd
from sklearn.linear_model import LinearRegression
from .models import Sale

def predict_future_sales(model_name, months_ahead=3):
    sales = Sale.objects.filter(product__model_name=model_name).order_by('date')
    if not sales.exists():
        return None

    data = pd.DataFrame.from_records(sales.values('date', 'quantity'))
    data['month'] = data['date'].dt.to_period('M').astype(str)
    monthly = data.groupby('month').sum().reset_index()
    monthly['month_index'] = range(len(monthly))

    X = monthly[['month_index']]
    y = monthly['quantity']
    model = LinearRegression()
    model.fit(X, y)

    future = pd.DataFrame({'month_index': range(len(monthly), len(monthly) + months_ahead)})
    predictions = model.predict(future)

    future['predicted_quantity'] = predictions
    return future[['month_index', 'predicted_quantity']]
