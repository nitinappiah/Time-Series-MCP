from fastmcp import FastMCP
import pandas as pd
import os
import requests
from dotenv import load_dotenv
import tabulate
load_dotenv() # Load variables from .env
import matplotlib.pyplot as plt

FRED_API_KEY = os.getenv("FRED_API_KEY")

mcp = FastMCP("FRED MCP server")
# Instructions help clients understand how to interact with the server
mcp_with_instructions = FastMCP(
    name="FRED MCP server",
    instructions="""
        This server provides data from the Frederal Reserve Economic Data (FRED) API.
        Data series can be queried/ searched by name.
        Data series by date and value can be pulled by series ID.
    """
)


@mcp.tool(
    name="Search FRED series",     # Custom name
    description="Search the FRED database and provide the series that match with their series ID.", # Custom description
)
def search_series(keyword: str) -> str:
    """
        Search economic data series by name using the FRED API.
        Input: keyword - search string
        Output: Pandas dataframe with the following fields - id, realtime_start, realtime_end, title, observation_start, observation_end, frequency, frequency_short, units, units_short, seasonal_adjustment, seasonal_adjustment_short, last_updated, popularity, group_popularity, notes
    """
    keyword_search = '+'.join(keyword.split(' '))
    url = f"https://api.stlouisfed.org/fred/series/search?search_text={keyword_search}&api_key={FRED_API_KEY}&file_type=json"
    response = requests.get(url)
    df = None
    if response.status_code == 200:
        json_data = response.json()
        df = pd.DataFrame(json_data['seriess'])
    else:
        df = pd.DataFrame()
    return df.to_markdown(index=False)


@mcp.tool(
    name="Get FRED series data",     # Custom name
    description="Get the timeseries dataset date, value for the provided dataseries from FRED API"
)
def get_series_data(series_id: str) -> str:
    """
        Get the series timeseries data by date and value.
        Input: series_id - FRED series ID
        Output: String - Save the retrieved dataframe as csv in resources folder.
    """
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json"
    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
        df = pd.DataFrame(json_data['observations'])[['date', 'value']]
        df = df.sort_values(by='date')
        df['date'] = pd.to_datetime(df['date'])
        df = df.dropna()
        df['value'] = df['value'].astype(float)
        df.to_csv(f'resources/{series_id}.csv', index=False)

        return f"Series saved to resources folder with the name {series_id}.csv"
    else:
        df = pd.DataFrame({'data': 'No data found'})
        return "No data found - API call failed"


@mcp.prompt(
        name="General Analysis", 
        description="Provide a general analysis about the timeseries dataset provided"
)
def general_analysis(markdown_df: str) -> str:
    """
        Analyze the provided dataframe. 
    """
    prompt = f"""
        Provide a summary in words about the data timeseries.
        Provide details on the trend, highs and dips in terms of date.
        Here is the timeseries data with the schema of date: Date, value: float64.\n
        {markdown_df}
        """
    return prompt

if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8000)