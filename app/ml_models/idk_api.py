import pandas as pd
from datetime import timedelta

def analyze_similarity_with_recent_data(historical_file, new_file, kpi_column, date_column):
    """
    Compare new data with the most recent matching period in historical data and calculate percent change.

    Args:
    - historical_file (str): Path to the historical data CSV file.
    - new_file (str): Path to the new data CSV file.
    - kpi_column (str): Column name of the KPI to calculate percent change.
    - date_column (str): Column name of the date variable.

    Returns:
    - dict: Results including the matching historical period and percent change for the KPI.
    """
    # Load historical and new data
    historical_data = pd.read_csv(historical_file)
    new_data = pd.read_csv(new_file)

    # Parse the date column as datetime
    historical_data[date_column] = pd.to_datetime(historical_data[date_column], errors="coerce")
    new_data[date_column] = pd.to_datetime(new_data[date_column], errors="coerce")

    # Ensure the KPI column is numeric
    historical_data[kpi_column] = pd.to_numeric(historical_data[kpi_column], errors="coerce")
    new_data[kpi_column] = pd.to_numeric(new_data[kpi_column], errors="coerce")

    # Drop rows with invalid KPI or date values
    historical_data = historical_data.dropna(subset=[kpi_column, date_column])
    new_data = new_data.dropna(subset=[kpi_column, date_column])

    # Detect the time period in new data
    new_data_start = new_data[date_column].min()
    new_data_end = new_data[date_column].max()
    new_data_duration = new_data_end - new_data_start

    # Determine the matching historical period
    historical_end = new_data_start - timedelta(days=1)  # Day before new data starts
    historical_start = historical_end - new_data_duration  # Same duration as new data

    # Filter historical data for the matching period
    historical_matching = historical_data[
        (historical_data[date_column] >= historical_start) &
        (historical_data[date_column] <= historical_end)
    ]

    # Aggregate KPI values for the historical and new periods
    historical_kpi_sum = historical_matching[kpi_column].sum()
    new_kpi_sum = new_data[kpi_column].sum()

    # Calculate percent change
    if historical_kpi_sum == 0:
        percent_change = float('inf') if new_kpi_sum > 0 else float('-inf')
    else:
        percent_change = ((new_kpi_sum - historical_kpi_sum) / historical_kpi_sum) * 100

    # Return results
    results = {
        "New Data Period": (new_data_start, new_data_end),
        "Matching Historical Period": (historical_start, historical_end),
        "New KPI Value": new_kpi_sum,
        "Historical KPI Value": historical_kpi_sum,
        "Percent Change (KPI)": percent_change
    }

    return results
