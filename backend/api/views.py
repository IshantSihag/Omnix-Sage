from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
import pandas as pd
import statistics
from bs4 import BeautifulSoup
import websocket
from websocket import create_connection
import json
import random
import string
import re
import logging
from typing import List, Iterator, Literal
import requests
import pandas as pd
import numpy as np
from typing import Optional, Dict, List, Any
import datetime
import pytz
from io import StringIO
import time
import asyncio
import aiohttp
from asgiref.sync import async_to_sync

# Create your views here.




def calculate_cagr(net_profits):
    initial_value = net_profits[0]
    final_value = net_profits[-1]
    n = len(net_profits) - 1  # number of intervals
    if initial_value == 0 or n<2:  # Avoid division by zero
        return -1  # Return an invalid CAGR to indicate an error
    cagr = (final_value / initial_value) ** (1 / n) - 1
    if isinstance(cagr, complex):
        return -1
    return cagr

def calculate_yoy_growth(net_profits):
    yoy_growth = []
    for i in range(1, len(net_profits)):
        growth = (net_profits[i] - net_profits[i - 1]) / (net_profits[i - 1] + 10**(-10))
        yoy_growth.append(growth)
    return yoy_growth

def calculate_volatility(yoy_growth):
    return np.std(yoy_growth)  # Standard deviation of YoY growth rates

def rate_graph(net_profits, growth_weight=0.8, consistency_weight=0.2, growth_percent = 0.2):
    # Calculate CAGR-based score
    # consider only positive net_profits
    net_profits = [profit for profit in net_profits if profit and profit > 0]
    if len(net_profits) < 2:
        return 0  # If no positive net profits, return 0
    cagr = calculate_cagr(net_profits)
    if cagr < 0:
        cagr_score = 0  # If there's negative growth, score 0
    elif cagr >= growth_percent:
        cagr_score = 10  # If CAGR is 20% or more, score 10
    else:
        cagr_score = round((cagr / growth_percent) * 10, 2)  # Scale score linearly for CAGR < 20%

    # Calculate YoY growth rates and consistency score
    yoy_growth = calculate_yoy_growth(net_profits)
    volatility = calculate_volatility(yoy_growth)

    # Scale consistency score (lower volatility = higher consistency score)
    # For simplicity, we can say if volatility > 0.2, score 0; if volatility is 0, score 10
    consistency_score = max(0, 10 - (volatility * 50))  # Adjust scaling factor as necessary

    # Combine the growth and consistency scores
    final_score = round((growth_weight * cagr_score) + (consistency_weight * consistency_score))
    return final_score

def rate_graph_anchor(data, anchor, growth_positive=True, weight_anchor=0.7, weight_growth=0.3):
    # Step 1: Calculate the average nearness to the anchor
    deviations = [abs(value - anchor) for value in data if value != None]
    avg_deviation = sum(deviations) / len(deviations)
    
    # Scale the anchor score: The smaller the deviation, the higher the score
    # Assuming 10 is the perfect score for being close to the anchor, we scale accordingly
    anchor_score = max(0, 10 - (avg_deviation / (anchor+(10**(-10))) * 10))  # Adjust scaling factor as necessary
    
    # Step 2: Calculate the growth trend and final difference
    initial_value = data[0]
    for i in range(len(data)):
        if data[i] != None:
            initial_value = data[i]
            break

    final_value = data[-1]
    for i in range(len(data)-1, -1, -1):
        if data[i] != None:
            final_value = data[i]
            break
    final_difference = final_value - initial_value
    
    # Determine the growth trend score
    if (final_difference > 0 and growth_positive) or (final_difference < 0 and not growth_positive):
        growth_score = min(10, abs(final_difference / (initial_value+10**-10) * 10))  # Scale based on relative growth
    else:
        growth_score = max(0, 10 - abs(final_difference / (initial_value+10**-10) * 10))  # Penalize for undesired direction

    # Step 3: Combine the scores with respective weights
    final_score = round((weight_anchor * anchor_score) + (weight_growth * growth_score), 2)
    return final_score


AvailableTimeFrame = Literal[
    "1",
    "3",
    "5",
    "15",
    "45",
    "1h",
    "2h",
    "3h",
    "4h",
    "1D",
    "1W",
    "1M",
    "3M",
    "6M",
    "12M",
]


class SESSION_ENUM:
    """
    Description:
        Session constants
    """

    WEBSOCKET: bool = False
    CHART: bool = True


headers = json.dumps(
    {
        "Origin": "https://data.tradingview.com",
    }
)


def generate_sesssion(session) -> str:
    """
    Description:
        Get {session prefix}_{random string}
    Args:
        session (bool)
            True: for websocket
            False: for chart
    Returns:
        (str) web socket session
    """
    string_length = 12
    letters = string.ascii_lowercase
    random_string = "".join(
        random.choice(letters) for i in range(string_length)
    )
    prefix = "cs" if session else "qs"
    return f"{prefix}_{random_string}"


def prepend_header(sentences: str) -> str:
    """
    Description:
        format data into websocket message:
    Args:
        sentence
            (str) contructed message
    Returns:
        (str) An added prefix message
    Example:
        ~m~54~m~{"m":"set_auth_token","p":["unauthorized_user_token"]}
    """
    return f"~m~{len(sentences)}~m~{sentences}"


def construct_message(function_name: str, parameters: List[str]) -> str:
    """
    Args:
        function_name
            (str) Function to summit into websocket
        parameters:
            List[str]: list paramaters to input into the function
    Returns:
        (str) a message as a JSON format join without space
    Example:
        {"m":"set_auth_token","p":["unauthorized_user_token"]}
    """
    transformed_params = []
    for parameter in parameters:
        if isinstance(parameter, str):
            transformed_params.append(parameter)
        elif isinstance(parameter, dict):
            transformed_params.append(json.dumps(parameter).replace("/", ""))
        else:
            transformed_params.append(parameter)
    return json.dumps(
        {"m": function_name, "p": transformed_params}, separators=(",", ":")
    )  # .replace('"(', '{').replace('}"', '}')


def create_message(function_name: str, parameters: List[str]) -> str:
    """
    Description:
        Integration of a created message function
    Args:
        function_name:
            (str) Function to summit into websocket
        parameters:
            List[str]: list paramaters to input into the function
    Returns:
        (str) message as websocket message format
    Example:
        ~m~54~m~{"m":"set_auth_token","p":["unauthorized_user_token"]}
    """
    output = prepend_header(construct_message(function_name, parameters))
    return output


def send_message(
    ws: websocket._core.WebSocket, func: str, args: List[str]
) -> None:
    """
    Description:
        Send formatted message
    Params:
        ws:
            (websocket._core.WebSocket) web socket sesssoin
        func:
            (str) Function to summit into websocket
        args:
            List[str]: list paramaters to input into the function
    """

    ws.send(create_message(func, args))


def get_pe_ratio_template():
    headers = {
        "authority": "pine-facade.tradingview.com",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "en-GB,en;q=0.9",
        # 'if-none-match': 'W/"rscUUmqLJOxhFguZvk588Rqfz37Es9R6f9UjLoBPJrgOHvnMmnx3/MwXZrOCaitLpw8ogsgzOhaGQ4ALxt7xnA=="', # noqa
        "origin": "https://www.tradingview.com",
        "referer": "https://www.tradingview.com/",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',  # noqa
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",  # noqa
    }

    response = requests.get(
        "https://pine-facade.tradingview.com/pine-facade/translate/STD%3BFund_price_earnings/38.0/",  # noqa
        headers=headers,
    )
    return response.json()["result"]["ilTemplate"]


def get_pe_ratio_message(
    chart_session, chart_session_name, study_name="pe_ratio"
):
    text = get_pe_ratio_template()
    parameters = json.dumps(
        {
            "text": text,
            "pineId": "STD;Fund_price_earnings",
            "pineVersion": "38.0",
            "in_0": {"v": "", "f": True, "t": "symbol"},
            "__user_pro_plan": {"v": "", "f": True, "t": "usertype"},
        }
    )

    message = (
        '{"m":"create_study","p":["'
        + chart_session
        + f'","{study_name}","st1","{chart_session_name}","Internal@tv-scripting-101!",'  # noqa
        + parameters
        + "]}"
    )

    message = f"~m~{len(message)}~m~{message}"
    return message


def request_data(
    symbol: str,
    time_frame: str,
    look_back_bars: int,
    websocket_session,
    chart_session,
):
    # look_back_bars = 365 * 10

    resolve_symbol = json.dumps({"symbol": symbol, "adjustment": "splits"})

    # Set up session
    chart_session_name = "price"
    ws = create_connection(
        "wss://data.tradingview.com/socket.io/websocket", headers=headers
    )

    send_message(ws, "set_auth_token", ["unauthorized_user_token"])
    send_message(ws, "chart_create_session", [chart_session, ""])
    send_message(ws, "quote_create_session", [websocket_session])

    send_message(
        ws,
        "quote_add_symbols",
        [websocket_session, symbol, {"flags": ["force_permission"]}],
    )

    send_message(
        ws, "resolve_symbol", [chart_session, "symbol_1", f"={resolve_symbol}"]
    )
    logging.debug(f"Time frame {time_frame}")
    send_message(
        ws,
        "create_series",
        [
            chart_session,
            chart_session_name,
            chart_session_name,
            "symbol_1",
            time_frame,
            look_back_bars,
        ],
    )
    return ws


def listen(
    symbol: str, look_back_bars: int, time_frame: AvailableTimeFrame
) -> Iterator[dict]:
    """
    Open a websocket channel and wait for return.


    Args:
        symbol (str): Target symbol
        look_back_bars (int): Number of bar to look back
        time_frame (str)

    Yields:
        Iterator[dict]: Yield dictionary until it found stop
            the stop condition.
    """
    websocket_session = generate_sesssion(SESSION_ENUM.WEBSOCKET)
    logging.debug(f"Web socket session generated: {websocket_session}")

    chart_session = generate_sesssion(SESSION_ENUM.CHART)
    chart_session_name = "price"
    # chart_session = "cs_j11Xz8aCaxfT"
    logging.debug(f"Chart session generated: {chart_session}")

    ws = request_data(
        symbol, time_frame, look_back_bars, websocket_session, chart_session
    )
    ws.send(get_pe_ratio_message(chart_session, chart_session_name))
    while True:
        try:
            results: str = ws.recv()
            logging.debug(results)
            pattern = re.compile("~m~\d+~m~~h~\d+$")  # noqa

            if pattern.match(results):
                # Send heart beat to keep connection alive
                ws.recv()
                ws.send(results)

            for r in results.split("~m~"):
                try:
                    r = json.loads(r)
                    if not isinstance(r, dict):
                        continue
                    message = r.get("m")
                    if (
                        message == "timescale_update"
                        or message == "du"
                        or message == "study_error"
                    ):
                        yield r
                        # return r
                except json.JSONDecodeError:
                    pass
        except KeyboardInterrupt:
            logging.debug("End")
            break


def load_raw_data(
    symbol: str, look_back_bars: int, time_frame: AvailableTimeFrame
) -> dict:
    """Load price as raw data.

    Args:
        symbol (str): Target symbol
        look_back_bars (int): Number of look bars
        time_frame (AvailableTimeFrame): Observing timeframe

    Returns:
        dict: Raw chart data
    """
    chart = {}

    for res in listen(symbol, look_back_bars, time_frame):
        m = res["m"]
        if m == "study_error":
            break
        p = res["p"]
        data = [element for element in p if isinstance(element, dict)][0]
        if not (("price" in chart) and ("price" in data)):
            chart = {**chart, **data}
        if "pe_ratio" in chart:
            break
    return chart


def extract_price(chart: dict) -> pd.DataFrame:
    """Extract ohlcv chart.

    Args:
        chart (dict): Raw chart data.

    Returns:
        pd.DataFrame: Result dataframe
    """
    return pd.DataFrame(
        [st["v"] for st in chart["price"]["s"]],
    ).rename(
        columns={
            0: "time",
            1: "open",
            2: "high",
            3: "low",
            4: "close",
            5: "volume",
        }
    )


def extract_pe_ratio(chart: dict) -> Optional[pd.DataFrame]:
    """Extracting PE ratio from RAW chart

    Args:
        chart (dict): raw chart data

    Returns:
        Optional[pd.DataFrame]:
         - None if pe_ratio not found in the chart data
         - Dataframe if from
    """
    if "pe_ratio" not in chart:
        return None
    df = pd.DataFrame(
        [st["v"] for st in chart["pe_ratio"]["st"]],
        columns=["time", "pe_ratio"],
    )
    df["pe_ratio"] = df["pe_ratio"].astype(np.float64)
    return df


def aggregate_to_dataframe(
    chart: dict, timezone: Optional[pytz.timezone] = None
) -> pd.DataFrame:
    """Aggregate raw chart data in a Pandas dataframe.

    Args:
        chart (dict): Raw chart data
        timezone (Optional[pytz.timezone], optional):
            Operating timezone. Defaults to None.

    Returns:
        pd.DataFrame: Return as a dataframe
    """
    if timezone is None:
        timezone = pytz.timezone("Asia/Bangkok")
    ohlcv = extract_price(chart)
    logging.debug(ohlcv)
    pe_ratio = extract_pe_ratio(chart)
    if pe_ratio is not None:
        ohlcv = pd.concat(
            [ohlcv.set_index("time"), pe_ratio.set_index("time")], axis=1
        ).reset_index()

    # print(ohlcv) Sihag
    def convert_timestamp(timestamp, timezone):
        try:
            # For negative timestamps, handle manually
            if timestamp < 0:
                base_datetime = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
                dt_utc = base_datetime + datetime.timedelta(seconds=timestamp)
            else:
                # Convert timestamp to naive datetime in UTC for positive timestamps
                dt_utc = datetime.datetime.utcfromtimestamp(timestamp)
                dt_utc = dt_utc.replace(tzinfo=datetime.timezone.utc)
            
            # Convert to the desired timezone
            dt_localized = dt_utc.astimezone(timezone)
            return dt_localized
        except (OSError, ValueError) as e:
            print(f"Error converting timestamp {timestamp}: {e}")
            return None  # Or handle the error as needed

    # Apply the conversion function to the 'time' column
    ohlcv['time'] = ohlcv['time'].apply(lambda timestamp: convert_timestamp(timestamp, timezone))

    # ohlcv.time = ohlcv.time.apply(
    #     lambda timestamp: datetime.datetime.fromtimestamp(
    #         timestamp, tz=timezone
    #     )
    # ) Sihag
    
    ohlcv = ohlcv.dropna(subset=["open", "high", "low", "close"])
    ohlcv[["open", "high", "low", "close"]] = ohlcv[
        ["open", "high", "low", "close"]
    ].astype(np.float64)
    return ohlcv


# async def load_asset_price(
#     symbol: str,
#     look_back_bars: int,
#     time_frame: AvailableTimeFrame,
#     timezone: Optional[pytz.timezone] = None,
# ) -> pd.DataFrame:
#     """Run full process to scrape TradingView data

#     Args:
#         symbol (str): Asset symbol
#         look_back_bars (int): Number of look back bars
#         time_frame (AvailableTimeFrame): Time frame
#         timezone (Optional[pytz.timezone], optional): Timezone.
#             Defaults to None.

#     Returns:
#         pd.DataFrame: return as a dataframe
#     """
#     chart = load_raw_data(symbol, look_back_bars, time_frame)
#     return aggregate_to_dataframe(chart, timezone)





#########################################################SIHAG##############################################################################################################









async def async_listen(ws: aiohttp.ClientWebSocketResponse) -> Dict[str, Any]:
    chart = {}
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            data = msg.data
            if data.startswith("~m~"):
                parts = data.split("~m~")
                for part in parts:
                    if part and not part.isdigit():
                        try:
                            r = json.loads(part)
                            if isinstance(r, dict):
                                message = r.get("m")
                                if message in ["timescale_update", "du", "study_error"]:
                                    if message == "study_error":
                                        return chart
                                    p = r["p"]
                                    data = next((element for element in p if isinstance(element, dict)), None)
                                    if data:
                                        if not (("price" in chart) and ("price" in data)):
                                            chart.update(data)
                                    if "pe_ratio" in chart:
                                        return chart
                        except:
                            pass
            elif data == "~h~":
                await ws.send_str(data)
    return chart

async def async_load_raw_data(symbol: str, look_back_bars: int, time_frame: str) -> Dict[str, Any]:
    websocket_session = generate_sesssion(SESSION_ENUM.WEBSOCKET)
    chart_session = generate_sesssion(SESSION_ENUM.CHART)
    chart_session_name = "price"

    async with aiohttp.ClientSession() as session:
        async with session.ws_connect("wss://data.tradingview.com/socket.io/websocket", headers=json.loads(headers)) as ws:
            await ws.send_str(create_message("set_auth_token", ["unauthorized_user_token"]))
            await ws.send_str(create_message("chart_create_session", [chart_session, ""]))
            await ws.send_str(create_message("quote_create_session", [websocket_session]))
            await ws.send_str(create_message("quote_add_symbols", [websocket_session, symbol, {"flags": ["force_permission"]}]))
            await ws.send_str(create_message("resolve_symbol", [chart_session, "symbol_1", f"={json.dumps({'symbol': symbol, 'adjustment': 'splits'})}"]))
            await ws.send_str(create_message("create_series", [chart_session, chart_session_name, chart_session_name, "symbol_1", time_frame, look_back_bars]))
            await ws.send_str(get_pe_ratio_message(chart_session, chart_session_name))

            return await async_listen(ws)

async def load_asset_price(
    symbol: str,
    look_back_bars: int,
    time_frame: str,
    timezone: Optional[pytz.timezone] = None,
) -> pd.DataFrame:
    """Run full process to scrape TradingView data asynchronously

    Args:
        symbol (str): Asset symbol
        look_back_bars (int): Number of look back bars
        time_frame (str): Time frame
        timezone (Optional[pytz.timezone], optional): Timezone.
            Defaults to None.

    Returns:
        pd.DataFrame: return as a dataframe
    """
    chart = await async_load_raw_data(symbol, look_back_bars, time_frame)
    return aggregate_to_dataframe(chart, timezone)






#########################################################SIHAG##############################################################################################################



class SearchView(APIView):
    def get(self, request):
        company = request.query_params.get('company')
        seach_url = f'https://www.screener.in/api/company/search/?q={company}'
        content = requests.get(seach_url).json()
        return Response(content)

class AnalysisView(APIView):
    @async_to_sync
    async def get(self, request):




        start_time = time.time()
        company = request.query_params.get('company')
        company = company.replace('/company/', '')
        company_name = company.split('/')[0]
        try:
            isConsolidated = True if company.split('/')[1] == 'consolidated' else False
        except:
            isConsolidated = False
        data = {'company': company, 'company_name': company_name, 'isConsolidated': isConsolidated}
        screener_url = f'https://www.screener.in/company/{company_name}/' + ('consolidated/' if isConsolidated else '')
        screener_resp = requests.get(screener_url).content
        soup = BeautifulSoup(screener_resp, 'html.parser')
        table = soup.find_all('table')
        company_id = int(soup.find('div', {'id': 'company-info'})['data-company-id'])
        financial_statement = pd.read_html(StringIO(str(table)))
        df = financial_statement[1]
        data = df.to_dict()
        years = len(list(data)) - 1

        auth_token = 'csrftoken=z3xipDqGzOxQRUzga9bhfnLwLDhH8tRc; sessionid=orif6946g0lk5byu3zvjizx4bxqxado4'
        headers = {
            'authority': 'www.screener.in',
        'method':'GET',
        'path':f'/wiki/company/{company_id}/commentary/v2/',
        'scheme':'https',
        'accept':'*/*',
        'accept-encoding':'gzip, deflate, br, zstd',
        'accept-language':'en-US,en;q=0.9',
        'cookie':auth_token,
        'priority':'u=1, i',
        # 'referer':'https://www.screener.in/company/TATAELXSI/',
        'sec-ch-ua':'"Not)A;Brand";v="99", "Microsoft Edge";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile':'?0',
        'sec-ch-ua-platform':'"Windows"',
        'sec-fetch-dest':'empty',
        'sec-fetch-mode':'cors',
        'sec-fetch-site':'same-origin',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/',
        'x-requested-with':'XMLHttpRequest'
        }

        # expenses_url = f'https://www.screener.in/api/company/{company_id}/schedules/?parent=Expenses&section=profit-loss'+ ('&consolidated=' if isConsolidated else '')
        # expenses_url_resp = requests.get(expenses_url).json()
        # other_assests_url = f'https://www.screener.in/api/company/{company_id}/schedules/?parent=Other+Assets&section=balance-sheet' + ('&consolidated=' if isConsolidated else '')
        # other_assests_url_resp = requests.get(other_assests_url).json()
        # cash_from_investing_url = f'https://www.screener.in/api/company/{company_id}/schedules/?parent=Cash+from+Investing+Activity&section=cash-flow' + ('&consolidated=' if isConsolidated else '')        
        # cash_from_investing = requests.get(cash_from_investing_url).json()
        # key_insights_url = f'https://www.screener.in/wiki/company/{company_id}/commentary/v2/'
        # key_insights_resp = requests.get(key_insights_url, headers=headers)
        # soup_key_insights = BeautifulSoup(key_insights_resp.content, 'html.parser')
        # pe_url = f'https://www.screener.in/api/company/{company_id}/chart/?q=Price+to+Earning-Median+PE-EPS&days=10000' + ('&consolidated=true' if isConsolidated else '')
        # pe_resp = requests.get(pe_url).json()
        # dma_url = f'https://www.screener.in/api/company/{company_id}/chart/?q=Price-DMA50-DMA200-Volume&days=10000' + ('&consolidated=true' if isConsolidated else '')
        # dma_resp = requests.get(dma_url).json()











        async with aiohttp.ClientSession() as session:
            # Fetch screener data
            async with session.get(screener_url) as response:
                screener_resp = await response.text()

            soup = BeautifulSoup(screener_resp, 'html.parser')
            table = soup.find_all('table')
            company_id = int(soup.find('div', {'id': 'company-info'})['data-company-id'])
            financial_statement = pd.read_html(StringIO(str(table)))
            df = financial_statement[1]
            data = df.to_dict()
            years = len(list(data)) - 1

            # Define all URLs
            urls = {
                'expenses': f'https://www.screener.in/api/company/{company_id}/schedules/?parent=Expenses&section=profit-loss' + ('&consolidated=' if isConsolidated else ''),
                'other_assets': f'https://www.screener.in/api/company/{company_id}/schedules/?parent=Other+Assets&section=balance-sheet' + ('&consolidated=' if isConsolidated else ''),
                'cash_from_investing': f'https://www.screener.in/api/company/{company_id}/schedules/?parent=Cash+from+Investing+Activity&section=cash-flow' + ('&consolidated=' if isConsolidated else ''),
                'key_insights': f'https://www.screener.in/wiki/company/{company_id}/commentary/v2/',
                'pe': f'https://www.screener.in/api/company/{company_id}/chart/?q=Price+to+Earning-Median+PE-EPS&days=10000' + ('&consolidated=true' if isConsolidated else ''),
                'dma': f'https://www.screener.in/api/company/{company_id}/chart/?q=Price-DMA50-DMA200-Volume&days=10000' + ('&consolidated=true' if isConsolidated else '')
            }

            # Create tasks for all requests
            tasks = []
            for key, url in urls.items():
                if key == 'key_insights':
                    tasks.append(asyncio.ensure_future(session.get(url, headers=headers)))
                else:
                    tasks.append(asyncio.ensure_future(session.get(url)))

            # Wait for all requests to complete
            responses = await asyncio.gather(*tasks)

            # Process responses
            results = {}
            for key, response in zip(urls.keys(), responses):
                if key in ['expenses', 'other_assets', 'cash_from_investing', 'pe', 'dma']:
                    results[key] = await response.json()
                elif key == 'key_insights':
                    key_insights_content = await response.text()
                    results[key] = BeautifulSoup(key_insights_content, 'html.parser')

        expenses_url_resp = results['expenses']
        other_assests_url_resp = results['other_assets']
        cash_from_investing = results['cash_from_investing']
        soup_key_insights = results['key_insights']
        pe_resp = results['pe']
        dma_resp = results['dma']

















        if list(data)[-1] == 'TTM':
            years -= 1
        if years < 1:
            return Response({'error': 'Data not available'})
        # find first non zero value of list
        first_non_zero_sales = None
        cagr_years = None
        for i in range(1, years+1):
            if data[list(data)[i]][0] != 0:
                first_non_zero_sales = float(data[list(data)[i]][0])
                cagr_years = years - i + 1
                break
                
        compunded_sales_growth = None
        if cagr_years:
            try:
                compunded_sales_growth = (float(data[list(data)[-2]][0]) / first_non_zero_sales) ** (1/cagr_years) - 1
                compunded_sales_growth *= 100
            except:
                pass
        
        
        sales_list = []
        for i in range(1, years+1):
            try:
                sales_list.append(float(data[list(data)[i]][0]))
            except:
                sales_list.append(None)
            if sales_list[-1] != sales_list[-1]:
                sales_list[-1] = None
        expenses_list = []
        for i in range(1, years+1):
            try:
                expenses_list.append(float(data[list(data)[i]][1]))
            except:
                expenses_list.append(None)
            if expenses_list[-1] != expenses_list[-1]:
                expenses_list[-1] = None

        opm_percent_list = []
        for i in range(1, years+1):
            try:
                opm_percent_list.append(float(data[list(data)[i]][3][:-1].replace(',','')))
            except:
                opm_percent_list.append(None)
            if opm_percent_list[-1] != opm_percent_list[-1]:
                opm_percent_list[-1] = None

        interest_list = []
        for i in range(1, years+1):
            try:
                interest_list.append(float(data[list(data)[i]][5]))
            except:
                interest_list.append(None)
            if interest_list[-1] != interest_list[-1]:
                interest_list[-1] = None

        depreciation_list = []
        for i in range(1, years+1):
            try:
                depreciation_list.append(float(data[list(data)[i]][6]))
            except:
                depreciation_list.append(None)
            if depreciation_list[-1] != depreciation_list[-1]:
                depreciation_list[-1] = None
        net_profit_list = []
        for i in range(1, years+1):
            try:
                net_profit_list.append(float(data[list(data)[i]][9]))
            except:
                net_profit_list.append(None)
            if net_profit_list[-1] != net_profit_list[-1]:
                net_profit_list[-1] = None
        eps = []
        for i in range(1, years+1):
            try:
                eps.append(float(data[list(data)[i]][10]))
            except:
                eps.append(None)
            if eps[-1] != eps[-1]:
                eps[-1] = None
        eps_cagr = calculate_cagr(eps) * 100

        material_cost_percent = []
        try:
            for i in expenses_url_resp['Material Cost %'].values():
                try:
                    material_cost_percent.append(float(i[:-1]))
                except:
                    if i.count('showSchedule') == 1:
                        pass
                    else:
                        material_cost_percent.append(None)
                    if material_cost_percent[-1] != material_cost_percent[-1]:
                        material_cost_percent[-1] = None
        except:
            pass

        manufacuring_cost_percent = []
        try:
            for i in expenses_url_resp['Manufacturing Cost %'].values():
                try:
                    manufacuring_cost_percent.append(float(i[:-1]))
                except:
                    if i.count('showSchedule') == 1:
                        pass
                    else:
                        manufacuring_cost_percent.append(None)
                if manufacuring_cost_percent[-1] != manufacuring_cost_percent[-1]:
                    manufacuring_cost_percent[-1] = None
        except:
            pass
        if not manufacuring_cost_percent:
            material_cost_percent = []
        if not material_cost_percent:
            manufacuring_cost_percent = []
        
        gross_expense = []
        gross_profit=[]
        gross_profit_margin = []
        if material_cost_percent:
            for i in range(0, years):
                try:
                    gross_expense.append(expenses_list[i]*(material_cost_percent[i] + manufacuring_cost_percent[i])/100)
                except:
                    gross_expense.append(None)
            for i in range(0,years):
                try:
                    gross_profit.append(sales_list[i]-gross_expense[i])
                except:
                    gross_profit.append(None)

            for i in range(0, years):
                try:
                    gross_profit_margin.append((sales_list[i] - gross_expense[i])/sales_list[i] * 100)
                except:
                    gross_profit_margin.append(None)

        cash_equivalents = []
        try:
            cash_equivalents_data = other_assests_url_resp['Cash Equivalents']
            for i in cash_equivalents_data.values():
                try:
                    cash_equivalents.append(float(i.replace(',', '')))
                except:
                    if i.count('showSchedule') == 1:
                        pass
                    else:
                        cash_equivalents.append(None)
                if cash_equivalents[-1] != cash_equivalents[-1]:
                    cash_equivalents[-1] = None
        except:
            pass
        trade_receivables = []
        try:
            trade_receivables_data = other_assests_url_resp['Trade receivables']
            for i in trade_receivables_data.values():
                try:
                    trade_receivables.append(float(i.replace(',', '')))
                except:
                    if i.count('showSchedule') == 1:
                        pass
                    else:
                        trade_receivables.append(None)
                if trade_receivables[-1] != trade_receivables[-1]:
                    trade_receivables[-1] = None
        except:
            pass
        cash_from_investing_list = []
        try:
            for i in cash_from_investing['Fixed assets purchased'].values():
                try:
                    cash_from_investing_list.append(-(float(i.replace(',', ''))))
                except:
                    if i.count('showSchedule') == 1:
                        pass
                    else:
                        cash_from_investing_list.append(None)
                if cash_from_investing_list[-1] != cash_from_investing_list[-1]:
                    cash_from_investing_list[-1] = None
        except:
            pass
        balance_sheet = financial_statement[6].to_dict()
        total_assets = []
        for i in range(1, years+1):
            try:
                total_assets.append(float(balance_sheet[list(balance_sheet)[i]][9]))
            except:
                total_assets.append(None)
            if total_assets[-1] != total_assets[-1]:
                total_assets[-1] = None
        equity = []
        for i in range(1, years+1):
            try:
                equity.append(float(balance_sheet[list(balance_sheet)[i]][1]))
            except:
                equity.append(None)
            if equity[-1] != equity[-1]:
                equity[-1] = None
        borrowings = []
        for i in range(1, years+1):
            try:
                borrowings.append(float(balance_sheet[list(balance_sheet)[i]][2]))
            except:
                borrowings.append(None)
            if borrowings[-1] != borrowings[-1]:
                borrowings[-1] = None
        cash_flow = financial_statement[7].to_dict()
        cash_from_operation_list = []
        for i in range(1, years+1):
            try:
                cash_from_operation_list.append(float(cash_flow[list(cash_flow)[i]][0]))
            except:
                cash_from_operation_list.append(None)
            if cash_from_operation_list[-1] != cash_from_operation_list[-1]:
                cash_from_operation_list[-1] = None
        shareholding_pattern = financial_statement[10].to_dict()
        promoter_holding = []
        promoter_holding_years = []
        for i in shareholding_pattern:
            try:
                promoter_holding.append(float(shareholding_pattern[i][0][:-1]))
                promoter_holding_years.append(i)
            except:
                pass
        ratios = financial_statement[8].to_dict()
        cash_conversion_cycle = []
        for i in range(1, years+1):
            try:
                cash_conversion_cycle.append(float(ratios[list(ratios)[i]][3]))
            except:
                cash_conversion_cycle.append(None)
            if cash_conversion_cycle[-1] != cash_conversion_cycle[-1]:
                cash_conversion_cycle[-1] = None
        if all([i==None for i in cash_conversion_cycle]):
            cash_conversion_cycle = []
        roce_percent = []
        for i in range(1, years+1):
            try:
                roce_percent.append(float(ratios[list(ratios)[i]][5][:-1]))
            except:
                roce_percent.append(None)
            if roce_percent[-1] != roce_percent[-1]:
                roce_percent[-1] = None
        if all([i==None for i in roce_percent]):
            roce_percent = []
        year_list = []
        for i in range(1, years+1):
            year_list.append(list(data)[i])
        percent_change_sales = []
        for i in range(1, len(sales_list)):
            try:
                percent_change_sales.append(((sales_list[i] - sales_list[i-1]) / (sales_list[i-1])) * 100)
            except:
                percent_change_sales.append(None)
            if percent_change_sales[-1] != percent_change_sales[-1]:
                percent_change_sales[-1] = None
        operating_profit_list = []
        for i in range(0, years):
            try:
                operating_profit_list.append(sales_list[i] - expenses_list[i])
            except:
                operating_profit_list.append(None)
            if operating_profit_list[-1] != operating_profit_list[-1]:
                operating_profit_list[-1] = None
        net_profit_by_sales = []
        for i in range(0, years):
            try:
                net_profit_by_sales.append(net_profit_list[i] / sales_list[i] * 100)
            except:
                net_profit_by_sales.append(None)
            if net_profit_by_sales[-1] != net_profit_by_sales[-1]:
                net_profit_by_sales[-1] = None

        capex_by_income = sum(cash_from_investing_list) / sum(net_profit_list) * 100
        capex_list = []
        for i in range(0, years):
            try:
                capex_list.append(cash_from_investing_list[i] / net_profit_list[i] * 100)
            except:
                capex_list.append(None)
            if capex_list[-1] != capex_list[-1]:
                capex_list[-1] = None
        if all([i==None for i in capex_list]):
            capex_list = []
        return_on_assets = []
        for i in range(0, years):
            try:
                return_on_assets.append(net_profit_list[i] / total_assets[i] * 100)
            except:
                return_on_assets.append(None)
            if return_on_assets[-1] != return_on_assets[-1]:
                return_on_assets[-1] = None
        return_on_equity = []
        for i in range(0, years):
            try:
                return_on_equity.append(net_profit_list[i] / equity[i] * 100)
            except:
                return_on_equity.append(None)
        cash_equivalents_by_total_assets = []
        for i in range(0, years):
            try:
                cash_equivalents_by_total_assets.append(cash_equivalents[i] / total_assets[i] * 100)
            except:
                cash_equivalents_by_total_assets.append(None)
            if cash_equivalents_by_total_assets[-1] != cash_equivalents_by_total_assets[-1]:
                cash_equivalents_by_total_assets[-1] = None
        debt_to_equity = []
        for i in range(0, years):
            try:
                debt_to_equity.append(borrowings[i] / equity[i])
            except:
                debt_to_equity.append(None)
            if debt_to_equity[-1] != debt_to_equity[-1]:
                debt_to_equity[-1] = None
        
        trade_receivables_by_total_assets = []
        if trade_receivables:
            for i in range(0, years):
                try:
                    trade_receivables_by_total_assets.append(trade_receivables[i] / total_assets[i] * 100)
                except:
                    trade_receivables_by_total_assets.append(None)
                if trade_receivables_by_total_assets[-1] != trade_receivables_by_total_assets[-1]:
                    trade_receivables_by_total_assets[-1] = None
        interest_by_sales = []
        for i in range(0, years):
            try:
                interest_by_sales.append(interest_list[i] / sales_list[i] * 100)
            except:
                interest_by_sales.append(None)
                if interest_by_sales[-1] != interest_by_sales[-1]:
                    interest_by_sales[-1] = None
        depreciation_by_sales = []
        for i in range(0, years):
            try:
                depreciation_by_sales.append(depreciation_list[i] / sales_list[i] * 100)
            except:
                depreciation_by_sales.append(None)
            if depreciation_by_sales[-1] != depreciation_by_sales[-1]:
                depreciation_by_sales[-1] = None
        # normalized_net_profit_list = np.log1p(np.array(net_profit_list) / 100.0)
        # print(normalized_net_profit_list)
        # compounded_growth = (np.sum(normalized_net_profit_list) / len(normalized_net_profit_list))
        # compounded_profit_growth = (np.expm1(compounded_growth)) * 100
        compounded_profit_growth = calculate_cagr(net_profit_list) * 100
            # return compounded_profit_growth
        # compounded_profit_growth = net_profit_list[-1] / net_profit_list[0]
        # compounded_profit_growth = compounded_profit_growth ** (1/len(net_profit_list)) - 1
        # compounded_profit_growth *= 100
        price_willing_to_pay = eps[-1] * compounded_profit_growth
        cmp_info = soup.find('div', {'class': 'company-info'})
        book_value = cmp_info.findAll('li')[4].find('span', {'class': 'value'}).text.replace('₹', '').strip()
        market_cap = cmp_info.findAll('li')[0].find('span', {'class': 'value'}).text.replace('₹', '').replace(',', '').strip()
        current_price = cmp_info.findAll('li')[1].find('span', {'class': 'value'}).text.replace('₹', '').replace(',', '').strip()
        peer_info = soup.find('section', {'id': 'peers'})
        peer_info = peer_info.find('p').find_all('a')
        sector = peer_info[0].text.strip()
        industry = peer_info[1].text.strip()

        key_insights = ''
        for para in soup_key_insights.find_all('p'):
            key_insights += para.text
        key_insights = key_insights.split('Last edited')[0]
        key_insights = re.sub(r'\[.*?\]', '\n', key_insights)
        if key_insights == '':
            key_insights = 'No key insights available'
        eps_data = pe_resp['datasets'][0]
        pe_data = pe_resp['datasets'][1]

        price_data = dma_resp['datasets'][0]
        dma50_data = dma_resp['datasets'][1]
        dma200_data = dma_resp['datasets'][2]
        volume_data = dma_resp['datasets'][3]

        pe_date_list = []
        pe_list = []
        for i in pe_data['values']:
            pe_date_list.append(i[0])
            pe_list.append(i[1])     
        eps_date_list = []
        eps_values_list = []
        for i in eps_data['values']:
            eps_date_list.append(i[0])
            eps_values_list.append(i[1])
        dma50_list = []
        dma50_date_list = []
        for i in dma50_data['values']:
            dma50_list.append(float(i[1]))
            dma50_date_list.append((i[0]))

        dma200_list = []
        dma200_date_list = []
        for i in dma200_data['values']:
            dma200_list.append(float(i[1]))
            dma200_date_list.append((i[0]))
        volume_list = []
        volume_date_list = []
        for i in volume_data['values']:
            volume_list.append(float(i[1]))
            volume_date_list.append((i[0]))
        price_list = []
        price_date_list = []
        for i in price_data['values']:
            price_list.append(float(i[1]))
            price_date_list.append((i[0]))



        if len(eps) > 1 and len(net_profit_list) > 1:
            number_of_shares = net_profit_list[-1] * 10**7 / eps[-1]
        else:
            number_of_shares = None
        compounded_profit_growth_decimal = compounded_profit_growth / 100
        compunded_sales_growth_decimal = None
        if compunded_sales_growth:
            compunded_sales_growth_decimal = compunded_sales_growth / 100
        intrinsic_value = eps[-1] * compounded_profit_growth
        price_to_sales = price_list[-1] / sales_list[-1]
        price_to_earnings = price_list[-1] / eps[-1]
        price_to_book_value = float(current_price.replace(',', '')) / float(book_value.replace(',',''))
        operating_cash_flow = []
        for i in range(years):
            operating_cash_flow.append(net_profit_list[i] + depreciation_list[i])
        
        price_to_operating_cash_flow = price_list[-1] / operating_cash_flow[-1]

        maxV = max(volume_list)
        buying_window = []
        for i in range(len(price_date_list)):
            try:
                if dma200_list[i] > dma50_list[i]:
                    buying_window.append(maxV)
                else:
                    buying_window.append(None)
            except Exception as e:
                print(e)
                buying_window.append(None)


        trading_data_required = {
            # 'USD_INR' : 'USDINR',
            # 'nifty_50' : 'NSE:NIFTY',
            # 'dow_jones' : 'DJI',
            # 'india_GDP' : 'INGDP',
            # 'india_GDP_per_capita' : 'INGDPPC',
            # 'india_GDP_growth_rate' : 'INGDPQQ',
            # 'india_interest_rate' : 'ININTR',
            # 'india_inflation_rate' : 'INIRYY',
            # 'india_unemployment_rate' : 'INUR',
            # 'india_population' : 'INPOP',
            # 'india_government_debt' : 'INGDG',
        }
        trading_data = {}


        # for key, value in trading_data_required.items():
        #     df = load_asset_price(value, 1200,'1M', pytz.timezone('Asia/Kolkata'))
        #     trading_data[key + '_time'] = df['time'].dt.strftime('%Y-%m-%d').tolist()
        #     trading_data[key + '_price'] = df['close'].tolist()
        



        
        async def load_asset_price_with_retry(symbol: str, days: int, interval: str, timezone: pytz.timezone, max_retries: int = 5):
            for attempt in range(max_retries):
                try:
                    return await load_asset_price(symbol, days, interval, timezone)
                except aiohttp.ClientResponseError as e:
                    if e.status == 429:
                        wait_time = (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff with jitter
                        print(f"Rate limit hit for {symbol}. Retrying in {wait_time:.2f} seconds...")
                        await asyncio.sleep(wait_time)
                    else:
                        raise
            raise Exception(f"Failed to load data for {symbol} after {max_retries} attempts")

        async def load_all_asset_prices(trading_data_required: Dict[str, str], days: int, interval: str, timezone: pytz.timezone) -> Dict[str, List]:
            trading_data = {}
            semaphore = asyncio.Semaphore(4)  # Limit to 5 concurrent requests

            async def load_with_semaphore(key: str, symbol: str):
                async with semaphore:
                    try:
                        print(f"Loading data for {key}")
                        df = await load_asset_price_with_retry(symbol, days, interval, timezone)
                        trading_data[key + '_time'] = df['time'].dt.strftime('%Y-%m-%d').tolist()
                        trading_data[key + '_price'] = df['close'].tolist()
                        print(f"Successfully loaded data for {key}")
                    except Exception as e:
                        print(f"Error loading data for {key}: {str(e)}")

            async with aiohttp.ClientSession() as session:
                tasks = [asyncio.create_task(load_with_semaphore(key, value)) for key, value in trading_data_required.items()]
                await asyncio.gather(*tasks)

            return trading_data

        trading_data = await load_all_asset_prices(trading_data_required, 1200, '1M', pytz.timezone('Asia/Kolkata'))



        graph_ratings_and_weightage = {}
        if sales_list: 
            graph_ratings_and_weightage['revenue'] = {'rating':rate_graph(sales_list), 'weightage':10}
        if percent_change_sales: 
            graph_ratings_and_weightage['percentchangeinrevenue'] = {'rating':rate_graph_anchor(percent_change_sales, 8, growth_positive=True), 'weightage':7}
        if expenses_list: 
            graph_ratings_and_weightage['expenses'] = {'rating':rate_graph(expenses_list, growth_percent=0.15), 'weightage':6}
        if operating_profit_list: 
            graph_ratings_and_weightage['operatingprofit'] = {'rating':rate_graph(operating_profit_list,growth_percent=0.2), 'weightage':9}
        if opm_percent_list: 
            graph_ratings_and_weightage['operatingprofitmargin'] = {'rating':rate_graph_anchor(opm_percent_list, 15, weight_anchor=0.2, weight_growth=0.8), 'weightage':9}
        if interest_list: 
            graph_ratings_and_weightage['interest'] = {'rating':rate_graph_anchor(interest_list, 0, False, weight_anchor=0.3, weight_growth=0.7), 'weightage':6}
        if interest_by_sales: 
            graph_ratings_and_weightage['interestbyrevenue'] = {'rating':rate_graph_anchor(interest_by_sales, 0, False, 0.6, 0.4), 'weightage':8}
        if depreciation_list: 
            graph_ratings_and_weightage['depreciation'] = {'rating':rate_graph_anchor(depreciation_list,0,False,0.3,0.7), 'weightage':6}
        if depreciation_by_sales: 
            graph_ratings_and_weightage['depreciationbyrevenue'] = {'rating':rate_graph_anchor(depreciation_by_sales,0,False,0.7,0.3), 'weightage':6}
        if net_profit_list: 
            graph_ratings_and_weightage['netprofit'] = {'rating':rate_graph(net_profit_list), 'weightage':10}
        if net_profit_by_sales: 
            graph_ratings_and_weightage['netprofitbyrevenue'] = {'rating':rate_graph_anchor(net_profit_by_sales,12,True,0.5,0.5), 'weightage':10}
        if eps_values_list: 
            graph_ratings_and_weightage['epsvalues'] = {'rating':rate_graph(eps_values_list, growth_percent=0.2), 'weightage':10}
        if total_assets: 
            graph_ratings_and_weightage['totalassets'] = {'rating':rate_graph(total_assets, growth_percent=0.16), 'weightage':10}
        if return_on_assets: 
            graph_ratings_and_weightage['returnonassets'] = {'rating':rate_graph_anchor(return_on_assets,15,0.4,0.6), 'weightage':10}
        if equity: 
            graph_ratings_and_weightage['equity'] = {'rating':rate_graph(equity, growth_percent=0.2), 'weightage':10}
        if return_on_equity: 
            graph_ratings_and_weightage['returnonequity'] = {'rating':rate_graph_anchor(return_on_equity,20,weight_anchor=0.3, weight_growth=0.7), 'weightage':10}
        if cash_equivalents: 
            graph_ratings_and_weightage['cashequivalents'] = {'rating':rate_graph(cash_equivalents, growth_percent=0.12), 'weightage':8}
        if cash_equivalents_by_total_assets: 
            graph_ratings_and_weightage['cashequivalentsbytotalassets'] = {'rating':rate_graph_anchor(cash_equivalents_by_total_assets, 7, True, 0.2, 0.8), 'weightage':9}
        if borrowings: 
            graph_ratings_and_weightage['borrowings'] = {'rating':rate_graph(borrowings[::-1], growth_percent=0.08), 'weightage':10}
        if debt_to_equity: 
            graph_ratings_and_weightage['debttoequity'] = {'rating':rate_graph_anchor(debt_to_equity, 0, False, 0.6, 0.4), 'weightage':10}
        if capex_list: 
            graph_ratings_and_weightage['capexbyincomeinpercentage'] = {'rating':rate_graph_anchor(capex_list, 0, False, 0.6, 0.4), 'weightage':10}
        if cash_from_operation_list: 
            graph_ratings_and_weightage['cashfromoperations'] = {'rating':rate_graph(cash_from_operation_list, growth_percent=0.2), 'weightage':10}
        if cash_from_investing_list: 
            graph_ratings_and_weightage['cashfrominvesting'] = {'rating':rate_graph(cash_from_investing_list,growth_percent=0.2), 'weightage':9}
        if promoter_holding: 
            graph_ratings_and_weightage['promoterholding'] = {'rating':rate_graph_anchor(promoter_holding, 75, False, 0.6, 0.4), 'weightage':10}
        if roce_percent: 
            graph_ratings_and_weightage['roce'] = {'rating':rate_graph_anchor(roce_percent, 20, True, 0.2, 0.8), 'weightage':6}
        if cash_conversion_cycle:
            graph_ratings_and_weightage['cashconversioncycle'] = {'rating':rate_graph_anchor(cash_conversion_cycle, 0, False, 0.8, 0.2), 'weightage':7}
        if material_cost_percent:
            graph_ratings_and_weightage['materialcost'] = {'rating':rate_graph_anchor(material_cost_percent,20,False,0.1,0.9), 'weightage':4}
            graph_ratings_and_weightage['grossexpense'] = {'rating':rate_graph(gross_expense, growth_percent=0.1), 'weightage':6}
            graph_ratings_and_weightage['grossprofit'] = {'rating':rate_graph(gross_profit,growth_percent=0.12), 'weightage':7}
            graph_ratings_and_weightage['grossprofitmargin'] = {'rating':rate_graph_anchor(gross_profit_margin, 50, weight_anchor=0.2, weight_growth=0.8), 'weightage':7}
            graph_ratings_and_weightage['manufacturingcost'] = {'rating':rate_graph_anchor(manufacuring_cost_percent,20,False,0.1,0.9), 'weightage':4}
        if trade_receivables:
            graph_ratings_and_weightage['tradereceivables'] = {'rating':rate_graph(trade_receivables[::-1], growth_percent=0.1), 'weightage':7}
            graph_ratings_and_weightage['tradereceivablesbytotalassets'] = {'rating':rate_graph_anchor(trade_receivables_by_total_assets, 2, False, 0.5, 0.5), 'weightage':8}


        data = {
            'time_taken': time.time() - start_time,
            'market_cap': market_cap,
            'graph_ratings_and_weightage' : graph_ratings_and_weightage,
            'economic_landscape_graph_names': [i for i in trading_data_required.keys()],
            **trading_data,
            'company': company,
            'company_name': company_name,
            'isConsolidated': isConsolidated,
            'compunded_sales_growth': compunded_sales_growth if compunded_sales_growth else 'Not Applicable',
            'years': years,
        }

        if sales_list:
            data['sales_list']= sales_list
        if expenses_list:
            data['expenses_list']= expenses_list
        if opm_percent_list:
            data['opm_percent_list']= opm_percent_list
        if interest_list:
            data['interest_list']= interest_list
        if depreciation_list:
            data['depreciation_list']= depreciation_list
        if net_profit_list:
            data['net_profit_list']= net_profit_list
        if eps:
            data['eps']= eps
        if eps_cagr:
            data['eps_cagr']= eps_cagr
        if cash_equivalents:
            data['cash_equivalents']= cash_equivalents
        if cash_from_investing_list:
            data['cash_from_investing_list']= cash_from_investing_list
        if total_assets:
            data['total_assets']= total_assets
        if equity:
            data['equity']= equity
        if borrowings:
            data['borrowings']= borrowings
        if cash_from_operation_list:
            data['cash_from_operation_list']= cash_from_operation_list
        if promoter_holding:
            data['promoter_holding']= promoter_holding
        if promoter_holding_years:
            data['promoter_holding_years']= promoter_holding_years
        if roce_percent:
            data['roce_percent']= roce_percent
        if year_list:
            data['year_list']= year_list
        if percent_change_sales:
            data['percent_change_sales']= percent_change_sales
        if operating_profit_list:
            data['operating_profit_list']= operating_profit_list
        if net_profit_by_sales:
            data['net_profit_by_sales']= net_profit_by_sales
        if capex_by_income:
            data['capex_by_income']= capex_by_income
        if capex_list:
            data['capex_list']= capex_list
        if return_on_assets:
            data['return_on_assets']= return_on_assets
        if return_on_equity:
            data['return_on_equity']= return_on_equity
        if cash_equivalents_by_total_assets:
            data['cash_equivalents_by_total_assets']= cash_equivalents_by_total_assets
        if debt_to_equity:
            data['debt_to_equity']= debt_to_equity
        if interest_by_sales:
            data['interest_by_sales']= interest_by_sales
        if depreciation_by_sales:
            data['depreciation_by_sales']= depreciation_by_sales
        if compounded_profit_growth:
            data['compounded_profit_growth']= compounded_profit_growth
        if price_willing_to_pay:
            data['price_willing_to_pay']= price_willing_to_pay
        if number_of_shares:
            data['number_of_shares']= number_of_shares
        if key_insights:
            data['key_insights']= key_insights
        if pe_date_list:
            data['pe_date_list']= pe_date_list
        if pe_list:
            data['pe_list']= pe_list
        if eps_date_list:
            data['eps_date_list']= eps_date_list
        if eps_values_list:
            data['eps_values_list']= eps_values_list
        if dma50_list:
            data['dma50_list']= dma50_list
        if dma50_date_list:
            data['dma50_date_list']= dma50_date_list
        if dma200_list:
            data['dma200_list']= dma200_list
        if dma200_date_list:
            data['dma200_date_list']= dma200_date_list
        if volume_list:
            data['volume_list']= volume_list
        if volume_date_list:
            data['volume_date_list']= volume_date_list
        if price_list:
            data['price_list']= price_list
        if price_date_list:
            data['price_date_list']= price_date_list
        if intrinsic_value:
            data['intrinsic_value']= intrinsic_value
        if price_to_sales:
            data['price_to_sales']= price_to_sales
        if price_to_earnings:
            data['price_to_earnings']= price_to_earnings
        if price_to_book_value:
            data['price_to_book_value']= price_to_book_value
        if price_to_operating_cash_flow:
            data['price_to_operating_cash_flow']= price_to_operating_cash_flow   
        if sector:
            data['sector']= sector
        if industry:
            data['industry']= industry
        if current_price:
            data['current_price']= current_price
        if book_value:
            data['book_value']= book_value
        if compounded_profit_growth_decimal:
            data['compounded_profit_growth_decimal']= compounded_profit_growth_decimal
        if compunded_sales_growth_decimal:
            data['compunded_sales_growth_decimal']= compunded_sales_growth_decimal if compunded_sales_growth_decimal else 'Not Applicable'
        if buying_window:
            data['buying_window']= buying_window
        
        if material_cost_percent:
            data['material_cost_percent'] = material_cost_percent
            data['manufacuring_cost_percent'] = manufacuring_cost_percent
            data['gross_expense'] = gross_expense
            data['gross_profit'] = gross_profit
            data['gross_profit_margin'] = gross_profit_margin
        if trade_receivables:
            data['trade_receivables'] = trade_receivables
            data['trade_receivables_by_total_assets'] = trade_receivables_by_total_assets
        if cash_conversion_cycle:
            data['cash_conversion_cycle'] = cash_conversion_cycle
        return Response(data)

class IndianEconomy(APIView):
    def get(self, request):
        r = '''<div class="tab-content" id="nav-tabContent">

                <div class="tab-pane fade active show" id="snapshot" role="tabpanel" aria-labelledby="snapshot-tab">

                    <div>

                        <section class="common-section introduction">
                            <div class="container-xl">
                                <div class="row gx-xl-5">
                                    <h2 class="text-uppercase fz20 fw800 text-green mb-5 wow fadeInUp">Introduction</h2>
                                    <div class="col-md-7 ">

                                        <p class="fz14 mb-4 fw600 wow fadeInUp">A rise in domestic investments has been
                                            one of the most significant contributors to the growth story of India.
                                            Domestic investments in India are divided into two parts - public
                                            investments and private investments. Private investments are further divided
                                            into two parts, which are household investments and corporate investments.
                                            Private domestic investments depend on a slew of factors - macroeconomic
                                            stability, high household savings, productivity, access to credit,
                                            resolution of non-performing assets, clearing up of balance sheets, etc.</p>



                                        <p class="fz14 mb-4 fw600 wow fadeInUp">Domestic investments and foreign
                                            investments in India work hand-in-hand to help the growth of the country.
                                            Growth in emerging economies like India results mainly from innovations that
                                            allow domestic sectors to catch up with innovative technology. The process
                                            of catching up with the leader in any sector requires the cooperation of a
                                            foreign investor who is familiar with the leading technology and a domestic
                                            entrepreneur/investor who is familiar with the local conditions.</p>



                                        <p class="fz14 mb-4 fw600 wow fadeInUp">The Indian private investing space has
                                            also been showcasing signs of maturity over the past few years. The market
                                            has revealed that new investments accounted for about 50% of VC
                                            transactions. The VC-to-PE pipeline has also become robust and consistent.
                                        </p>

                                    </div>



                                    <div class="col-md-5 ps-xl-5">

                                        <figure class="wow fadeInUp"><img alt="" class="img-thumbnail p-20"
                                                src="../assets/images/indian-economy/domestic-investment-india-2.jpg" />
                                        </figure>

                                    </div>



                                    <div class="col-sm-12">

                                        <p class="fz14 mb-4 fw600 wow fadeInUp">The concept of &#39;Make in India&#39; -
                                            Aatmanirbhar Bharat, various PLI schemes, and financial incentives provided
                                            by the government are a few examples of investor-friendly programmes that
                                            domestic companies are utilising to increase their production base and
                                            create new capacities, which leads to increasing domestic investments. There
                                            are multiple investors driving domestic investments in the country:</p>



                                        <ul class="circle-check fw600">

                                            <li>Government/Public Sector Enterprises</li>

                                            <li>Private Sector Enterprises</li>

                                            <li>Banks/Financial Institutions/Domestic Institutional Investors</li>

                                            <li>Retail Investors</li>

                                        </ul>

                                    </div>

                                </div>
                            </div>
                        </section>
                        <section class="common-section market-activity">
                            <div class="container-xl">
                                <div class="row gx-xl-5">
                                    <h2 class="text-uppercase fz20 fw800 text-green mb-5 wow fadeInUp">Market Activity
                                    </h2>
                                    <p class="fz14 mb-4 fw600  wow fadeInUp">India&#39;s economy showed great signs of
                                        recovery in FY22 after the COVID-19 pandemic. Nominal GDP or GDP at Current
                                        Prices in the year 2023-24 is estimated at Rs. 295.36 lakh crores (US$ 3.54
                                        trillion), compared to the First Revised Estimates (FRE) of GDP for the year
                                        2022-23 of Rs. 269.50 lakh crores (US$ 3.23 trillion). The growth in nominal GDP
                                        during 2023-24 is estimated at 9.6% as compared to 14.2% in 2022-23. Real GDP or
                                        GDP at Constant (2011-12) Prices in the year 2023-24 is estimated at Rs. 173.82
                                        lakh crores (US$ 2.08 trillion), against the First Revised Estimates (FRE) of
                                        GDP for the year 2022-23 of Rs. 160.71 lakh crores (US$ 1.92 trillion). The
                                        growth in real GDP during 2023-24 is estimated at 8.2% as compared to 7.0% in
                                        2022-23. These figures make India the fastest-growing major economy in the
                                        world, and this economic growth has translated to the domestic investment market
                                        in India. Retail investors, mutual funds, and PE/VC firms have all stepped up
                                        their domestic investments in the Indian market.</p>



                                    <p class="fz14 mb-4 fw600  wow fadeInUp">Retail and High Net-worth Individual (HNI)
                                        investors and domestic institutional investors (DIIs) combined share, which
                                        includes domestic mutual funds, insurance companies, banks, financial
                                        institutions, pension funds, etc., reached an all-time high of 25.50% as of June
                                        30, 2023. In the Q1 (April-June) of 2023, Domestic institutional investors
                                        (DIIs) invested a record sum of US$ 405.24 million in Indian equities.</p>



                                    <p class="fz14 mb-4 fw600  wow fadeInUp">The share of retail investors in equity
                                        holding listed on the National Stock Exchange (NSE) reached an all-time high of
                                        27% year-on-year in (April-August) 2023. According to BSE, the number of
                                        registered investors on BSE has jumped nearly 33.28% YoY and 2.62%
                                        month-on-month (MoM) as on July 15, 2024, to reach a total of 18,11,67,457
                                        users. In 2024, states registering a YoY rise of over 40% in the number of
                                        BSE-registered investors are Arunachal Pradesh, Bihar, Chhattisgarh, Himachal
                                        Pradesh, Mizoram, Nagaland, Tripura, and Uttar Pradesh.</p>



                                    <p class="fz14 mb-4 fw600  wow fadeInUp">Around 205 SME companies went public in
                                        FY24, raising a total of Rs. 6,300 crores (US$ 754 million) through IPOs.</p>



                                    <p class="fz14 mb-4 fw600  wow fadeInUp">The share of domestic Mutual Funds (MFs) in
                                        companies listed on the NSE increased and reached an all-time high of 8.64% on
                                        June 30, 2023, up from 7.24% on June 30, 2022.</p>



                                    <p class="fz14 mb-4 fw600  wow fadeInUp">India&#39;s Private Equity (PE)/Venture
                                        Capital (VC) investment environment is also scaling new heights, with increases
                                        in deal size, deal activity, and fundraising, as well as improvements in term
                                        sheets and benchmarking practices. Private Equity-Venture Capital (PE-VC) funds
                                        invested US$ 6.9 billion (across 115 deals) in India-based companies in May 2024
                                        as compared to US$ 4.5 billion of Private Equity (PE) &ndash; Venture Capitalist
                                        (VC) investments in May 2023.</p>

                                </div>
                            </div>
                        </section>
                        <section class="common-section investments/developments">
                            <div class="container-xl">
                                <div class="row gx-xl-5">
                                    <h2 class="text-uppercase fz20 fw800 text-green mb-5 wow fadeInUp">
                                        Investments/developments</h2>
                                    <p>In many ways, the year 2021 was a turning point for the Indian economy as
                                        initiatives like Aatmanirbhar Bharat sped up the formal implementation of
                                        several production-linked incentives (PLI) schemes. There was also a push to
                                        negotiate comprehensive free trade agreements successfully negotiated with
                                        Australia and the UAE. This has led to a huge quantum of domestic inflows coming
                                        into the Indian market and making it resilient amidst global uncertainties. With
                                        the improving economic scenario, there have been quite a few investments in
                                        various sectors in India. Some of them are as follows:</p>



                                    <ul class="circle-check fw600">

                                        <li>According to a recent report by Colliers, a real estate consulting firm,
                                            private equity investments in the Indian real estate sector reached a 3-year
                                            high in the second quarter of this year, totalling US$ 2.5 billion. The
                                            industrial and warehousing segment accounted for the largest share of these
                                            investments, making up 61% of the total, which equates to US$ 1.5 billion.
                                        </li>

                                        <li>Mahindra Susten, a leading renewable energy solutions provider, is embarking
                                            on a pioneering venture into the hybrid renewable energy sector. The company
                                            has launched a groundbreaking Rs. 1,200 crore (US$ 144 million) project in
                                            the state of Maharashtra. This innovative initiative integrates 101 MW of
                                            wind power capacity and 52 MW of solar power capacity, with the aim of
                                            generating a remarkable 460 million kWh of clean, sustainable energy. It is
                                            expected to significantly reduce CO2 emissions by 420,000 tonnes.</li>

                                        <li>In February 2024, Tata Group companies announced of signing memorandum of
                                            understanding (MoU) with Karnataka Government to invest Rs. 2,330 crore (US$
                                            279.48 million) in the state.</li>

                                        <li>Prime Minister, Mr. Narendra Modi recently inaugurated and laid the
                                            foundation stone for 112 National Highway projects valued at approximately
                                            US$ 12.1 billion (Rs. 1 Lakh crores) in Gurugram, Haryana.</li>

                                        <li>Hyundai Motors has successfully acquired General Motors India&#39;s Talegaon
                                            plant in Maharashtra in August 2023 and announced a substantial investment
                                            of US$ 721.94 million (Rs. 6,000 crores) in the state.</li>

                                        <li>In October 2023, NCLT approved resolution plan of Himadri Speciality
                                            Chemical and Dalmia Bharat Refractories to acquire Birla Tyres.</li>

                                        <li>In October 2023, Tata Motors acquired 27% in digital platform Freight Tiger.
                                        </li>

                                        <li>In October 2023, Bajaj Finance acquired 26% stake in Pennant Technologies
                                            for Rs. 267.50 crores (US$ 32.18 million). According to the IVCA-EY monthly
                                            PE/VC roundup, August 2023 recorded investments worth US$ 5.2 billion.</li>

                                        <li>In August 2023, growth deals valued at US$ 2.4 billion were the highest
                                            across 14 deals. PIPE investments recorded US$2.1 billion across 18 deals in
                                            August 2023.</li>

                                        <li>Infrastructure was the top sector in August 2023, backed by GQG Partners
                                            Inc. in Adani Power Limited, recording US$ 1.8 billion in PE/VC investments
                                            across six deals. Retail and consumer products were the second largest
                                            sector with US$ 1 billion recorded across four deals.</li>

                                        <li>In September 2023, Shree Renuka Sugars has inked a share purchase agreement
                                            to acquire 100% stake in Anamika Sugar Mills.</li>

                                        <li>In September 2023, Reliance Retail Ventures acquired majority stake in Alia
                                            Bhatt&rsquo;s Ed-a-Mamma brand.</li>

                                        <li>In August 2023, Jewellery retailer Titan acquired another 27.18% stake in
                                            CaratLane for Rs. 4,621 crores (US$ 556.01 million).</li>

                                        <li>In July 2023, Bikaji Foods International acquired a 49% stake in Bhujialalji
                                            for US$ 6,21,946.53.</li>

                                        <li>In July 2023, India&#39;s leading telecom firm, Bharti Airtel acquired an
                                            additional 20.6% stake in the SD-WAN startup, Lavelle Networks.</li>

                                        <li>In July 2023, Adani Enterprises acquired approximately 30% ownership in
                                            Start Enterprises Pvt Ltd (SEPL), the parent company of Trainman, an online
                                            platform for booking train tickets.</li>

                                        <li>In June 2023, Tata Communications is set to acquire US-based enterprise
                                            messaging firm Kaleyra for US$ 100 million in an all-cash deal.</li>

                                        <li>In June 2023, Asian Paints acquired an additional 11% stake in White Teak.
                                        </li>

                                        <li>In May 2023, JSW Steel acquired National Steel and Agro Industries for US$
                                            75.73 million.</li>

                                        <li>In February-April 2023:

                                            <ul class="list-angle m-4">

                                                <li>PhonePe, India&#39;s most valuable payments firm with an estimated
                                                    value of US$ 12 billion, has raised US$ 650 million across four
                                                    tranches from its backers, including Tiger Global.</li>

                                                <li>The Souled Store, a direct-to-consumer (D2C) apparel brand, has
                                                    raised Rs. 135 crores (US$ 16 million) in funding led by Xponentia
                                                    Capital. The company&rsquo;s existing investors Elevation Capital
                                                    and RPSG Capital also participated in the round.</li>

                                                <li>Agri startup Sorted, a tech platform founded by the ex-CEO of
                                                    Milkbasket for quality fruits and vegetables, has raised over US$ 5
                                                    million as seed funding to grow business.</li>

                                                <li>Electric vehicle charging infra platform CHARGE+ZONE on Monday
                                                    announced raising US$ 54 million in Series A1 funding round led by
                                                    global impact investment management firm BlueOrchard Finance.</li>

                                                <li>NCR-based Industrial and Logistics real estate developer Pragati
                                                    Group, has raised US$ 200 million of equity capital from a Private
                                                    Equity fund based in Singapore. Pragati has been offering customized
                                                    warehouse development solutions since its inception in 2010 to top
                                                    MNCs like Amazon India, Flipkart, DHL-Bluedart, Bosch, Daikin, and
                                                    many more.</li>

                                            </ul>

                                        </li>

                                        <li>In January 2023:

                                            <ul class="list-angle m-4">

                                                <li>Deep-tech battery startup Log9 bagged US$ 40 million from Amara Raja
                                                    Batteries Ltd and Petronas Ventures.</li>

                                                <li>On January 17, 2023, Sequoia Capital invested US$ 15 million in
                                                    CloseFactor as a lead investor.</li>

                                                <li>Virohan, a healthcare edtech start-up raised US$ 7 million from
                                                    Blume Ventures, with participation from Bharat Inclusion Seed Fund,
                                                    Rebright Partners, and others.</li>

                                            </ul>

                                        </li>

                                        <li>In December 2022:

                                            <ul class="list-angle m-4">

                                                <li>A Gurugram-based battery swapping solutions provider, Battery Smart
                                                    raised US$ 9.24 million from Stride Ventures.</li>

                                                <li>A food-tech start-up, SaveEat has raised US$ 5 million from Credent
                                                    Investment Pvt Ltd to expand its business operations in Mumbai,
                                                    Pune, and Bengaluru.</li>

                                                <li>Aquaconnect, an aquaculture platform bagged US$ 15 million from Lok
                                                    Capital, Louis Dreyfus Company Ventures, and Suneight Investment for
                                                    business expansion.</li>

                                            </ul>

                                        </li>

                                        <li>In November 2022:

                                            <ul class="list-angle m-4">

                                                <li>Energy storage solutions startup Clean Electric bagged US$ 2.2
                                                    million in a funding round led by early-stage venture capital firm
                                                    Kalaari Capital.</li>

                                                <li>Prismforce, a SaaS startup, raised US$ 13.6 million in Series A
                                                    funding led by Sequoia Capital India to enhance its product suite,
                                                    strengthen marketing, and grow its talent base.</li>

                                                <li>CashKaro raised US$ 16.02 million in a Series C funding round led by
                                                    Affle Global Pte. Ltd (AGPL) for the expansion of new technology and
                                                    product development.</li>

                                            </ul>

                                        </li>

                                        <li>In October 2022:

                                            <ul class="list-angle m-4">

                                                <li>Shardeum, an EVM-based shared blockchain startup raised a seed round
                                                    of US$ 18.28 million from 60 investors.</li>

                                                <li>A D2C footwear start-up, Yoho raised US$ 2.46 million from Softbank
                                                    Vision Fund, Rukam Capital, and Vijay Shekhar Sharma (founder of
                                                    Paytm) along with participation from other investors.</li>

                                                <li>A real estate developer, Urbanrise/Alliance Group raised US$ 31
                                                    million from Motilal Oswal Financial Services Ltd (MOPE).</li>

                                            </ul>

                                        </li>

                                        <li>In September 2022:

                                            <ul class="list-angle m-4">

                                                <li>In order to finance its expansion strategy, Solvy Tech Solutions,
                                                    which operates the insurtech platform Zopper, has raised US$ 75
                                                    million from investors coordinated by Creaegis. ICICI Venture,
                                                    Bessemer Venture Partners, and existing investor Blume Ventures all
                                                    participated in the investment round.</li>

                                                <li>Kotak Realty Fund has invested US$ 200 million in India&rsquo;s
                                                    first Real Estate Investment Authority (REIT) Embassy Office Parks
                                                    REIT.</li>

                                            </ul>

                                        </li>

                                        <li>In August 2022:

                                            <ul class="list-angle m-4">

                                                <li>Device management startup Servify raised US$ 65 million in funding
                                                    as a part of its pre-initial public offering (IPO) round, which was
                                                    led by the Singularity Growth Opportunity Fund.</li>

                                                <li>Private equity firm Kedaara Capital invested US$ 50 million in Oasis
                                                    Fertility in exchange for sizable minority ownership in the
                                                    business.</li>

                                            </ul>

                                        </li>

                                        <li>In July 2022:

                                            <ul class="list-angle m-4">

                                                <li>Digital therapeutic startup Fitterfly, which focuses on diabetes
                                                    management, raised US$ 12 million in funding led by Amazon Smbhav
                                                    Venture Fund and Fireside Ventures.</li>

                                                <li>DrinkPrime, a subscription-based reverse osmosis (RO)
                                                    water-supplying startup, raised Rs. 60 crores (US$ 7.5 million) in a
                                                    mix of equity and debt funding. The equity component was led by
                                                    Omidyar Network India, Sequoia Surge, and 9 Unicorns, while the debt
                                                    came from Northern Arc Capital and Unitus Capital.</li>

                                                <li>Content monetization platform ConsCent raised Rs. 13.26 crores (US$
                                                    1.66 million) in a funding round led by Inflection Point Ventures.
                                                </li>

                                            </ul>

                                        </li>

                                        <li>In June 2022:

                                            <ul class="list-angle m-4">

                                                <li>Shiprocket signed a deal to acquire a majority stake in its
                                                    competitor e-commerce platform Pickrr for about US$ 200 million in a
                                                    mix of cash and equity.</li>

                                                <li>India&rsquo;s sovereign wealth fund, National Investment, and
                                                    Infrastructure Fund (NIIF) announced that it would invest Rs. 2,250
                                                    crores (US$ 282 million) to acquire around 22.5% stake in Hindustan
                                                    Ports Pvt. Ltd (HPPL).</li>

                                                <li>GetVantage, a revenue-based finance platform, raised US$ 36 million
                                                    in funding led by Varanium Nexgen Fintech Fund and DMI Sparkle Fund.
                                                </li>

                                            </ul>

                                        </li>

                                        <li>In May 2022, Ather Energy raised US$ 128 million in a Series-E funding round
                                            led by NIIF&#39;s Strategic Opportunities Fund and Hero MotoCorp.</li>

                                        <li>In May 2022, Reliance Brands Limited, a subsidiary of Reliance Retail
                                            Ventures Ltd, signed a franchise agreement to sell Italian luxury lifestyle
                                            brand Tod&#39;s products in India.</li>

                                        <li>In May 2022, the Toyota Group of Companies (constituting Toyota Kirloskar
                                            Motor and Toyota Kirloskar Auto Parts) signed an MoU with the Government of
                                            Karnataka to invest Rs. 4,800 crores (US$ 620.23 million) to build electric
                                            powertrain components.</li>

                                        <li>In the first four months of 2022 (up to April 28), M&A deals and deals in
                                            the making have already crossed US$ 105 billion, compared to US$ 44.2
                                            billion in the first four months of 2021.</li>

                                        <li>Startup PE/VC investing in India stood at US$ 28.5 billion in 2021, a 290%
                                            YoY growth.</li>

                                        <li>Technology (US$ 16.3 billion), e-commerce (US$ 15.9 billion), and financial
                                            services (US$ 11.7 billion) accounted for 57% of the total PE/VC investments
                                            by value in 2021.</li>

                                        <li>The AUM of the PE/VC industry in India exceeded US$ 150 billion, as of 2021.
                                        </li>

                                        <li>In 2021, new sectors like edtech, electric vehicles, gaming, online
                                            streaming, and sports-based entertainment recorded significant PE/VC
                                            investment inflows of over US$ 10 billion.</li>

                                    </ul>

                                </div>
                            </div>
                        </section>
                        <section class="common-section government-initiatives">
                            <div class="container-xl">
                                <div class="row gx-xl-5">
                                    <h2 class="text-uppercase fz20 fw800 text-green mb-5 wow fadeInUp">Government
                                        Initiatives</h2>
                                    <p class="fz14 mb-4 fw600  wow fadeInUp">With the government&#39;s focus on making
                                        business in India easier through the establishment of nation-specific offices to
                                        "handhold" foreign investment, India has advanced in recent years in the
                                        rankings for ease of doing business. The government has also attempted to rein
                                        in the aggressive tax administration through more openness and transparency. It
                                        has also taken multiple other initiatives to improve the business regulatory
                                        environment in the country and simplified the process of making domestic
                                        investments. Some of these are:</p>



                                    <ul class="circle-check fw600">

                                        <li class="wow fadeinup">India&rsquo;s new rules for environmental, social and
                                            governance investments and ratings are likely to attract more investors to
                                            the nation&rsquo;s US$ 1.4 billion market and serve as a model for other
                                            countries. Over the last two years, India has implemented many measures to
                                            regulate its market for green and other assets, most notably permitting
                                            domestic fund managers to create plans under six types of ESG strategies.
                                        </li>

                                        <li class="wow fadeinup">The introduction of the Goods and Services Tax, easing
                                            liquidity problems of NBFCs and Banks, the reduction of corporate tax,
                                            improvements to the business environment, changes to the FDI policy,
                                            reduction in Compliance Burden, policies to support domestic manufacturing
                                            through public procurement orders, and the Phased Manufacturing Programme
                                            (PMP) are just a few of the actions taken by the government to encourage
                                            domestic investments.</li>

                                        <li class="wow fadeinup">The National Logistics Policy (NLP) aims to decrease
                                            the cost of logistics and make it to par&nbsp;with that of other developed
                                            nations. A comprehensive approach to address cost inefficiencies is being
                                            laid down by establishing an interdisciplinary, cross-sectoral,
                                            multijurisdictional framework for enhancing the entire logistics ecosystem.
                                            This would bolster India&#39;s economy, provide employment opportunities,
                                            and make Indian products more competitive in the global market. It was
                                            launched on September 17, 2022.</li>

                                        <li class="wow fadeinup">The Department for Promotion of Industry and Internal
                                            Trade (DPIIT) has introduced a dynamic reform exercise called the Business
                                            Reforms Action Plan, which ranks all the states and UTs in the country based
                                            on the implementation of designated reform parameters. The reforms have
                                            focused on streamlining the current rules and procedures and getting rid of
                                            unnecessary requirements and steps. The Action Plan covers multiple reform
                                            areas such as:

                                            <ul class="list-angle m-4">

                                                <li class="wow fadeinup">Investment Enablers</li>

                                                <li class="wow fadeinup">Online Single Window System</li>

                                                <li class="wow fadeinup">Land administration and Transfer of Land and
                                                    Property</li>

                                                <li class="wow fadeinup">Construction Permits Enabler</li>

                                                <li class="wow fadeinup">Labour Regulation Enablers</li>

                                                <li class="wow fadeinup">Environment Registration Enablers</li>

                                                <li class="wow fadeinup">Inspection Enablers</li>

                                                <li class="wow fadeinup">Paying Taxes</li>

                                                <li class="wow fadeinup">Obtaining Utility Permits</li>

                                            </ul>

                                        </li>

                                    </ul>



                                    <ul class="circle-check fw600">

                                        <li class="wow fadeinup">The Ministry of Labour and Employment has taken several
                                            steps to streamline labour laws to make conducting business easier. By
                                            condensing, combining, and rationalising the pertinent provisions of 29
                                            Central Labour Laws, the Government has notified four labour codes: the Code
                                            on Wages, 2019, the Industrial Relations Code, 2020, the Code on Social
                                            Security, 2020, and the Code on Occupational Safety, Health, and Working
                                            Conditions, 2020.</li>

                                        <li class="wow fadeinup">In order to incentivise new domestic companies to set
                                            up their manufacturing units in India, the government has extended the
                                            concessional tax rate of 15% to March 31, 2024.</li>

                                        <li class="wow fadeinup">The government introduced the India Industrial Land
                                            Bank (IILB), which is a GIS-based portal - a one-stop repository of all
                                            industrial infrastructure-related information - connectivity,
                                            infrastructure, natural resources, terrain, plot-level information on vacant
                                            plots, line of activity, and contact details.</li>

                                        <li class="wow fadeinup">On April 30, 2022, Minister of Ports, Shipping and
                                            Waterways, Mr. Sarbananda Sonowal, announced that Cochin Shipyard Limited
                                            has committed to invest an initial corpus of Rs. 50 crores (US$ 6.47
                                            million) in startup companies engaged in the maritime sector.</li>

                                        <li class="wow fadeinup">India&#39;s production-linked incentive (PLI) schemes
                                            generated investment commitments of Rs. 2.34 lakh crores (US$ 30.24
                                            billion). Automobile and auto components, advanced chemistry cell batteries,
                                            speciality steel and high-efficiency solar panels have attracted the maximum
                                            interest.</li>

                                        <li class="wow fadeinup">The government is expected to invest Rs. 1.20 lakh
                                            crores (US$ 15.5 billion) in the automobile industry in the next five years.
                                        </li>

                                        <li class="wow fadeinup">The Ministry of Education (MoE) has proposed an outlay
                                            of Rs. 1,102.91 crores (US$ 142.57 million) for Punjab in FY23 under the
                                            flagship Samagra Shiksha Scheme for school education.</li>

                                        <li class="wow fadeinup">Minister of Home Affairs and Cooperation, Mr. Amit
                                            Shah, inaugurated the newly constructed tourism facilities for SeemaDarshan
                                            at Nadabet in the Banaskantha district of Gujarat. The Gujarat government
                                            spent Rs. 125 crores (US$ 15.66 million) on the same.</li>

                                        <li class="wow fadeinup">The Uttar Pradesh government launched projects worth
                                            Rs. 70,000 crores (US$ 8.77 billion) in the state in June.</li>

                                        <li class="wow fadeinup">In April 2022, the government approved financial
                                            incentives to 61 companies for its textiles production linked incentive
                                            (PLI) scheme. These companies plan investment of Rs. 19,077 crores (US$ 2.39
                                            billion).</li>

                                        <li class="wow fadeinup">In February 2022, The Ministry of Heavy Industries
                                            notified a Phased Manufacturing Programme (PMP) to promote domestic
                                            manufacturing of electric vehicles, their assemblies/sub-assemblies, and
                                            parts/sub-parts/inputs of the sub-assemblies.</li>

                                        <li class="wow fadeinup">In February 2022, Minister of Finance and Corporate
                                            Affairs, Ms. Nirmala Sitharaman, announced a new scheme, Development
                                            Initiative for Northeast&#39; PM DevINE&#39;, allocating Rs. 1,500 crores
                                            (US$ 200.6 million).</li>

                                        <li class="wow fadeinup">In February 2022, Minister of Finance and Corporate
                                            Affairs, Ms. Nirmala Sitharaman, proposed to allocate Rs. 100,000 (US$ 13.37
                                            billion) to assist states in overall investments.</li>

                                        <li class="wow fadeinup">In January 2022, the Cabinet Committee on Economic
                                            Affairs approved equity fusion of Rs. 1,500 crores (US$ 200.6 million) in
                                            the Indian Renewable Energy Development Agency Limited (IREDA).</li>

                                        <li class="wow fadeinup">The Ministry of Finance has granted Rs. 7,309 crores
                                            (US$ 977.4 million) to 11 states for undertaking reforms in the power sector
                                            in January 2022.</li>

                                        <li class="wow fadeinup">In January 2022, the government sanctioned
                                            seven&nbsp;Mega Integrated Textile Regions and Apparel Parks with an
                                            investment of nearly Rs. 4,500 crores (US$ 601.8 million).</li>

                                        <li class="wow fadeinup">In December 2021, Minister of Commerce and Industry,
                                            Consumer Affairs, Food and Public Distribution and Textiles, Mr. Piyush
                                            Goyal, stated that more than 25,000 compliances had been reduced in the
                                            previous exercise implemented by the centre to reduce the compliance burden
                                            and to promote ease of living and ease of doing business.</li>

                                        <li class="wow fadeinup">On December 27, 2021, Prime Minister Mr. Narendra Modi
                                            visited Mandi to inaugurate hydropower projects worth over Rs. 11,000 crores
                                            (US$ 1.47 billion).</li>

                                        <li class="wow fadeinup">In the next five years, the Airports Authority of
                                            India&nbsp;plans to invest roughly Rs.&nbsp;25,000 crores (US$ 3.34
                                            billion)&nbsp;in the expansion and renovation of current terminals.</li>

                                        <li class="wow fadeinup">In September 2021, Minister of Commerce and Industry,
                                            Consumer Affairs, Food and Public Distribution and Textiles, Mr. Piyush
                                            Goyal, launched the National Single Window System (NSWS). The single-window
                                            portal would become a one-stop shop for investors for approvals and
                                            clearances, which would bring transparency, accountability, and
                                            responsiveness to the ecosystem.</li>

                                    </ul>

                                </div>
                            </div>
                        </section>
                        <section class="common-section road-ahead">
                            <div class="container-xl">
                                <div class="row gx-xl-5">
                                    <h2 class="text-uppercase fz20 fw800 text-green mb-5 wow fadeInUp">Road Ahead</h2>
                                    <div class="col-md-7 order-md-2 ps-xl-5">

                                        <p class="fz14 mb-4 fw600 wow fadeInUp" data-wow-delay=".2s"
                                            style="visibility: visible; animation-delay: 0.2s; animation-name: fadeInUp;">
                                            The mutual fund industry in India has been witnessing consistent growth in
                                            portfolio numbers over the past few years, as evidenced by the fact that the
                                            investor count is estimated to have reached 4 crores in September 2023. The
                                            Association of Mutual Funds in India (AMFI) is targeting a nearly five-fold
                                            growth in assets under management (AUM) to Rs. 95 lakh crores (US$ 1.30
                                            trillion) and more than three times growth in investor accounts to 130
                                            million by 2025. The AUM rose by 21% or Rs. 16,042.06 crores (US$ 1.93
                                            billion) in September 2023. Assets Under Management (AUM) of the Indian
                                            Mutual Fund Industry as of September 2023, stood at Rs. 46.58 lakh crores
                                            (US$ 560.46 billion).</p>



                                        <p class="fz14 mb-4 fw600 wow fadeInUp" data-wow-delay=".2s"
                                            style="visibility: visible; animation-delay: 0.2s; animation-name: fadeInUp;">
                                            To achieve a GDP of US$ 5 trillion by FY25, India needs to spend about US$
                                            1.4 trillion over these years on infrastructure. Liberal FDI policies, quick
                                            solutions to corporate disputes, a simplified tax structure, ease of doing
                                            business, and a boost to public and private expenditure are all part of
                                            India&#39;s attempt to implement reforms to unlock the country&#39;s
                                            investment potential, which is expected to improve the business environment.
                                        </p>

                                    </div>



                                    <div class="col-12 mt-5 order-md-3">

                                        <p class="fz14 mb-4 fw600 wow fadeInUp" data-wow-delay=".2s"
                                            style="visibility: visible; animation-delay: 0.2s; animation-name: fadeInUp;">
                                            In line with this, in May 2022, during the India-Denmark Business Forum,
                                            Prime Minister Mr. Narendra Modi applauded India&#39;s reforms and
                                            investment opportunities and stated that those who don&#39;t invest in the
                                            country are bound to miss out. He stated that India&#39;s ongoing economic
                                            reforms have created investment opportunities in various sectors like
                                            renewable energy, health, ports, shipping, circular economy, and water
                                            management, and invited Denmark, as well as other foreign countries, to
                                            invest in these sectors.</p>



                                        <p>Initiatives like Vibrant Gujrat Summit and Production-Linked Incentive (PLI)
                                            schemes has demonstrated good results. Various government initiatives, such
                                            as ease of doing business reforms, infrastructure development, and policy
                                            support are further aiding in driving domestic investments.</p>

                                    </div>



                                    <div class="col-md-5  order-md-1">

                                        <figure class="wow fadeInUp"><img alt="" class="img-thumbnail p-20"
                                                src="../assets/images/indian-economy/domestic-investment-india-2.jpg" />
                                        </figure>

                                    </div>



                                    <div class="mt-5 col-md-12  order-md-3">

                                        <p class="mb-4 fz14 fw500 wow fadeInUp" data-wow-delay=".1s">
                                            <b><i>Note:</i></b><i> Conversion rate used for April 2024 is Rs. 1 = US$
                                                0.012</i></p>



                                        <p class="fz14 wow fadeInUp" data-wow-delay=".1s"><i><strong>References:
                                                </strong>Press Information Bureau (PIB), Media Reports, World Bank,
                                                Database of Indian Economy (DBIE), Knight and Frank</i></p>

                                    </div>

                                </div>
                            </div>
                        </section>

                    </div>

                </div>



                

                </div>

            </div>'''
        from time import sleep
        sleep(5)
        r = r.replace('\n', '')
        return Response(r)
