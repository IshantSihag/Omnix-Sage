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

        report_links = {}
        for i in soup.find('div', {'class': 'annual-reports'}).find_all('a'):
            try:
                i.find('div', {'class':'smaller'}).decompose()
            except:
                pass
            report_links[i.get_text().strip()] = i['href']  
        credit_ratings = {}
        for i in soup.find('div', {'class': 'credit-ratings'}).find_all('a'):
            credit_ratings[i.find('div').get_text().strip()] = i['href']  

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
        if data[list(data)[0]][1].count('Expenses'):
            for i in range(1, years+1):
                try:
                    expenses_list.append(float(data[list(data)[i]][1]))
                except:
                    expenses_list.append(None)
                if expenses_list[-1] != expenses_list[-1]:
                    expenses_list[-1] = None
        
        financing_profit = []
        if data[list(data)[0]][3].count('Financing Profit'):
            for i in range(1, years+1):
                try:
                    financing_profit.append(float(data[list(data)[i]][3]))
                except:
                    financing_profit.append(None)
                if financing_profit[-1] != financing_profit[-1]:
                    financing_profit[-1] = None
        
        financing_profit_margin = []
        if data[list(data)[0]][4].count('Financing Margin'):
            for i in range(1, years+1):
                try:
                    financing_profit_margin.append(float(data[list(data)[i]][4][:-1]))
                except:
                    financing_profit_margin.append(None)
                if financing_profit_margin[-1] != financing_profit_margin[-1]:
                    financing_profit_margin[-1] = None
        
            

        opm_percent_list = []
        if data[list(data)[0]][3].count('OPM'):
            for i in range(1, years+1):
                try:
                    opm_percent_list.append(float(data[list(data)[i]][3][:-1].replace(',','')))
                except:
                    opm_percent_list.append(None)
                if opm_percent_list[-1] != opm_percent_list[-1]:
                    opm_percent_list[-1] = None

        interest_list = []
        if data[list(data)[0]][5].count('Interest'):
            for i in range(1, years+1):
                try:
                    interest_list.append(float(data[list(data)[i]][5]))
                except:
                    interest_list.append(None)
                if interest_list[-1] != interest_list[-1]:
                    interest_list[-1] = None
        elif data[list(data)[0]][1].count('Interest'):
            for i in range(1, years+1):
                try:
                    interest_list.append(float(data[list(data)[i]][1]))
                except:
                    interest_list.append(None)
                if interest_list[-1] != interest_list[-1]:
                    interest_list[-1] = None

        depreciation_list = []
        if data[list(data)[0]][6].count('Depreciation'):
            for i in range(1, years+1):
                try:
                    depreciation_list.append(float(data[list(data)[i]][6]))
                except:
                    depreciation_list.append(None)
                if depreciation_list[-1] != depreciation_list[-1]:
                    depreciation_list[-1] = None
        
        net_profit_list = []
        if data[list(data)[0]][9].count('Net Profit'):
            for i in range(1, years+1):
                try:
                    net_profit_list.append(float(data[list(data)[i]][9]))
                except:
                    net_profit_list.append(None)
                if net_profit_list[-1] != net_profit_list[-1]:
                    net_profit_list[-1] = None

        eps = []
        if data[list(data)[0]][10].count('EPS'):
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
        if balance_sheet[list(balance_sheet)[0]][9].count('Total Assets'):
            for i in range(1, years+1):
                try:
                    total_assets.append(float(balance_sheet[list(balance_sheet)[i]][9]))
                except:
                    total_assets.append(None)
                if total_assets[-1] != total_assets[-1]:
                    total_assets[-1] = None
        equity_partial = []
        if balance_sheet[list(balance_sheet)[0]][0].count('Equity'):
            for i in range(1, years+1):
                try:
                    equity_partial.append(float(balance_sheet[list(balance_sheet)[i]][0]))
                except:
                    equity_partial.append(None)
                if equity_partial[-1] != equity_partial[-1]:
                    equity_partial[-1] = None
        reserves = []
        if balance_sheet[list(balance_sheet)[0]][1].count('Reserves'):
            for i in range(1, years+1):
                try:
                    reserves.append(float(balance_sheet[list(balance_sheet)[i]][1]))
                except:
                    reserves.append(None)
                if reserves[-1] != reserves[-1]:
                    reserves[-1] = None
        equity = []
        for i in range(0, years):
            try:
                equity.append(equity_partial[i] + reserves[i])
            except:
                equity.append(None)


        borrowings = []
        if balance_sheet[list(balance_sheet)[0]][2].count('Borrowings'):
            for i in range(1, years+1):
                try:
                    borrowings.append(float(balance_sheet[list(balance_sheet)[i]][2]))
                except:
                    borrowings.append(None)
                if borrowings[-1] != borrowings[-1]:
                    borrowings[-1] = None
        cash_flow = financial_statement[7].to_dict()
        cash_from_operation_list = []
        if cash_flow[list(cash_flow)[0]][0].count('Cash from Operating Activity'):
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
        try:
            if ratios[list(ratios)[0]][3].count('Cash Conversion Cycle'):
                for i in range(1, years+1):
                    try:
                        cash_conversion_cycle.append(float(ratios[list(ratios)[i]][3]))
                    except:
                        cash_conversion_cycle.append(None)
                    if cash_conversion_cycle[-1] != cash_conversion_cycle[-1]:
                        cash_conversion_cycle[-1] = None
        except:
            pass

        if all([i==None for i in cash_conversion_cycle]):
            cash_conversion_cycle = []
        roce_percent = []
        try:
            if ratios[list(ratios)[0]][5].count('ROCE'):
                for i in range(1, years+1):
                    try:
                        roce_percent.append(float(ratios[list(ratios)[i]][5][:-1]))
                    except:
                        roce_percent.append(None)
                    if roce_percent[-1] != roce_percent[-1]:
                        roce_percent[-1] = None
        except:
            pass
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
        if all([i==None for i in operating_profit_list]):
            operating_profit_list = []

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
            key_content = para.text.split('\n')
            if len(key_content[0]) < 50:
                key_insights += '<strong>' + key_content[0] + '</strong>\n'
            else:
                key_insights += key_content[0] + '\n'
            for i in key_content[1:]:
                key_insights += i
                key_insights += '\n'
            key_insights += '\n\n'
        key_insights = key_insights.split('Last edited')[0]
        key_insights = re.sub(r'\[.*?\]', '', key_insights)
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
        if financing_profit:
            graph_ratings_and_weightage['financingprofit'] = {'rating':rate_graph(financing_profit, growth_percent=0.2), 'weightage':8}
        if financing_profit_margin:
            graph_ratings_and_weightage['financingprofitmargin'] = {'rating':rate_graph_anchor(financing_profit_margin, 15, weight_anchor=0.2, weight_growth=0.8), 'weightage':9}
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
        if financing_profit:
            data['financing_profit']= financing_profit
        if financing_profit_margin:
            data['financing_profit_margin']= financing_profit_margin
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
        if credit_ratings:
            data['credit_ratings'] = credit_ratings
        if report_links:
            data['report_links'] = report_links
        return Response(data)

class IndianEconomy(APIView):
    def get(self, request):
        reports_economy = request.query_params.get('r')
        url = f'https://www.ibef.org/{reports_economy}'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        for img in soup.find_all('img'):
            img.decompose()
        data = soup.find('div', {'class': 'tab-content', 'id': 'nav-tabContent'})
        if data is None:
            return Response('No data available! Please retry after some time')
        final_data = str(data.contents[1]).replace('\n', '').replace('\t', '').replace('\r', '')
        return Response(final_data)


class IndianIndustry(APIView):
    def get(self, request):
        reports_industry = request.query_params.get('r')
        url = f'https://www.ibef.org/industry/{reports_industry}'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        for img in soup.find_all('img'):
            img.decompose()
        data = soup.find('div', {'id': 'snapshot'})
        for pdfs in data.findAll('div', {'class': 'downloadPdflink'}):
            pdfs.decompose()
        if data is None:
            return Response('No data available! Please retry after some time')
        final_data = str(''.join([str(i) for i in data.contents])).replace('\n', '').replace('\t', '').replace('\r', '')
        return Response(final_data)

