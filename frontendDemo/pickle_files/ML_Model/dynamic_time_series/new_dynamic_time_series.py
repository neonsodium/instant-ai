import plotly.graph_objects as go

# Create the figure
fig = go.Figure()

# Add forecast line
fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Forecast', line=dict(color='red')))

# Add uncertainty interval (optional)
fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], fill=None, mode='lines', line_color='red', line=dict(dash='dash'), name='Upper Bound'))
fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], fill='tonexty', mode='lines', line_color='red', line=dict(dash='dash'), name='Lower Bound'))

# Update layout
fig.update_layout(title='Forecasted Values with Prophet',
                  xaxis_title='Date',
                  yaxis_title='Forecasted Value',
                  legend_title='Legend')
fig.show()