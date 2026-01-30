from fastmcp import FastMCP
import pandas as pd
import os
import requests
from dotenv import load_dotenv
import tabulate
load_dotenv() # Load variables from .env
import matplotlib.pyplot as plt
import io
from statsmodels.tsa.seasonal import seasonal_decompose
from prophet import Prophet

mcp = FastMCP("Timeseries server")
# Instructions help clients understand how to interact with the server
mcp_with_instructions = FastMCP(
    name="Timeseries Analysis server",
    instructions="""
        Provide tools for plotting timeseries charts, breakdown components and forecasts.
    """
)

@mcp.tool(
    name="Plot Chart",
    description="Plot a line chart Value against Date from the provided dataframe."
)
def plot_chart(series_id: str) -> str:
    """
        Plot a line chart with title 'title' and axis value vs date from markdown_table.
        Inputs: 
            series_id: series name to plot from the resoruces folder.
        Output: None. Shows the plot in a window.

    """
    try:
        df = pd.read_csv(f"resources/{series_id}.csv")
    except:
        return "Data not found in resources folder."
    df = df.sort_values(by='date')
    df['date'] = pd.to_datetime(df['date'])
    df = df.dropna()
    df['value'] = df['value'].astype(float)

    plt.plot(df['date'], df['value'])
    plt.title(series_id)
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.show()
    return f"Plotted line chart of {series_id}"

@mcp.tool(
    name="Plot Components",
    description="plot trend, seasonal and residual components",
)
def plot_components(series_id: str) -> str:
    """
        Provide the STL decomposition of the timeseries.
        Plot the trend seasonal and residual components.
        Input: series_id - FRED series ID name to plot from the resources folder.
    """
    try:
        df = pd.read_csv(f"resources/{series_id}.csv")
    except:
        return "Data not found in resources folder."
    df['index'] = pd.to_datetime(df['date'])
    decomposition = seasonal_decompose(df['value'], model='additive', period=12) 

    # Plot the decomposed components
    fig = decomposition.plot()
    fig.set_size_inches(10, 8)
    plt.show()
    return f"Plotted 12 month seasonal decomposition of {series_id}"

@mcp.tool(
    name="Forecast",
    description="Forecast the next x years for the timeseries"
)
def forecast(series_id: str, period: int) -> str:
    """
        Forecast the next 24 steps in the timeseries.
        Inputs:
            series_id - series id in resources to forecast.
            period - number of years into the future to forecast.
        Output: None. Shows the plot in a window.    
    """
    try:
        df = pd.read_csv(f"resources/{series_id}.csv")
    except:
        return "Data not found in resources folder."
    model = Prophet()
    prophet_train_df = df.rename(columns={'date': 'ds', 'value': 'y'})
    model.fit(prophet_train_df)
    future = model.make_future_dataframe(periods=365*period, freq='D')
    forecast = model.predict(future)
    fig = model.plot(forecast)
    plt.show()
    return f"Plotted forecast of {series_id}"


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8001)