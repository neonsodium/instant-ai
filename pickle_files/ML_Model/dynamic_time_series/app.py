import matplotlib
matplotlib.use('agg')  # Set the backend before importing pyplot
import matplotlib.pyplot as plt
import pickle
import io
import plotly.graph_objs as go
from datetime import datetime
import pandas as pd
from flask import Flask, render_template, request, send_file
from dynamic_time_series_test import create_future_df, adjust_for_weekend_effect, generate_forecast  # Importing the function

app = Flask(__name__)

def load_model_and_data(pickle_file):
    with open(pickle_file, 'rb') as file:
        data = pickle.load(file)
        return data['model'], data['historical_data']

def create_future_forecast(model, historical_data, regressors, start_date, end_date):
    future_df = create_future_df(start_date, end_date, historical_data, regressors)
    future_df = adjust_for_weekend_effect(future_df, regressors)
    return generate_forecast(model, future_df)

def generate_matplotlib_plot(model, forecast):
    fig, ax = plt.subplots(figsize=(10, 6))
    model.plot_components(forecast)
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close(fig)
    return img

def generate_plotly_plot(forecast):
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', 
                             name='Forecast', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], fill=None, 
                             mode='lines', line_color='red', line=dict(dash='dash'), 
                             name='Upper Bound'))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], fill='tonexty', 
                             mode='lines', line_color='red', line=dict(dash='dash'), 
                             name='Lower Bound'))

    fig.update_layout(
        title='Forecasted Values with Prophet',
        xaxis_title='Date',
        yaxis_title='Forecasted Value',
        legend_title='Legend'
    )
    
    return fig.to_html(full_html=False)

@app.route('/')
def index():
    regressors = [
        'over_due_adjustment_amount', 
        'security_deposit', 
        'Percentage_Share',
        'Coupon_Discount', 
        'reading_fee_paid', 
        'Number_of_Months'
    ]

    pickle_file = 'prophet_model_and_data.pkl'
    model, historical_data = load_model_and_data(pickle_file)

    # Get start_date and end_date from query parameters
    start_date_str = request.args.get('start_date', '2024-08-15')
    end_date_str = request.args.get('end_date', '2024-10-31')

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD.", 400

    forecast = create_future_forecast(model, historical_data, regressors, start_date, end_date)

    plotly_plot = generate_plotly_plot(forecast)
    return render_template('dynamic_time_series.html', plotly_plot=plotly_plot)

@app.route('/plot.png')
def plot_png():
    regressors = [
        'over_due_adjustment_amount', 
        'security_deposit', 
        'Percentage_Share',
        'Coupon_Discount', 
        'reading_fee_paid', 
        'Number_of_Months'
    ]

    pickle_file = 'prophet_model_and_data.pkl'
    model, historical_data = load_model_and_data(pickle_file)

    # Get start_date and end_date from query parameters
    start_date_str = request.args.get('start_date', '2024-08-15')
    end_date_str = request.args.get('end_date', '2024-10-31')

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD.", 400

    forecast = create_future_forecast(model, historical_data, regressors, start_date, end_date)

    img = generate_matplotlib_plot(model, forecast)
    return send_file(img, mimetype='image/png')

if __name__ == "__main__":
    app.run(debug=True)