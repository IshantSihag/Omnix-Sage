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
from typing import Optional
import datetime
import pytz


# Create your views here.


def calculate_cagr(net_profits):
    initial_value = net_profits[0]
    final_value = net_profits[-1]
    n = len(net_profits) - 1  # number of intervals
    if initial_value == 0:  # Avoid division by zero
        return -1  # Return an invalid CAGR to indicate an error
    cagr = (final_value / initial_value) ** (1 / n) - 1
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

    final_value = data[-1]
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


def load_asset_price(
    symbol: str,
    look_back_bars: int,
    time_frame: AvailableTimeFrame,
    timezone: Optional[pytz.timezone] = None,
) -> pd.DataFrame:
    """Run full process to scrape TradingView data

    Args:
        symbol (str): Asset symbol
        look_back_bars (int): Number of look back bars
        time_frame (AvailableTimeFrame): Time frame
        timezone (Optional[pytz.timezone], optional): Timezone.
            Defaults to None.

    Returns:
        pd.DataFrame: return as a dataframe
    """
    chart = load_raw_data(symbol, look_back_bars, time_frame)
    return aggregate_to_dataframe(chart, timezone)




class SearchView(APIView):
    def get(self, request):
        company = request.query_params.get('company')
        seach_url = f'https://www.screener.in/api/company/search/?q={company}'
        content = requests.get(seach_url).json()
        return Response(content)
    
class AnalysisView(APIView):
    def get(self, request):
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
        financial_statement = pd.read_html(str(table))
        df = financial_statement[1]
        data = df.to_dict()
        compunded_sales_growth = (float(data[list(data)[-2]][0]) / float(data[list(data)[1]][0])) ** (1/11) - 1
        compunded_sales_growth *= 100
        years = len(list(data)) - 1
        if list(data)[-1] == 'TTM':
            years -= 1
        if years < 1:
            return Response({'error': 'Data not available'})
        
        sales_list = []
        for i in range(1, years+1):
            try:
                sales_list.append(float(data[list(data)[i]][0]))
            except:
                sales_list.append(None)
        expenses_list = []
        for i in range(1, years+1):
            try:
                expenses_list.append(float(data[list(data)[i]][1]))
            except:
                expenses_list.append(None)
        opm_percent_list = []
        for i in range(1, years+1):
            try:
                opm_percent_list.append(float(data[list(data)[i]][3][:-1].replace(',','')))
            except:
                opm_percent_list.append(None)
        interest_list = []
        for i in range(1, years+1):
            try:
                interest_list.append(float(data[list(data)[i]][5]))
            except:
                interest_list.append(None)
        depreciation_list = []
        for i in range(1, years+1):
            try:
                depreciation_list.append(float(data[list(data)[i]][6]))
            except:
                depreciation_list.append(None)
        net_profit_list = []
        for i in range(1, years+1):
            try:
                net_profit_list.append(float(data[list(data)[i]][9]))
            except:
                net_profit_list.append(None)
        eps = []
        for i in range(1, years+1):
            try:
                eps.append(float(data[list(data)[i]][10]))
            except:
                eps.append(None)
        expenses_url = f'https://www.screener.in/api/company/{company_id}/schedules/?parent=Expenses&section=profit-loss'+ ('&consolidated=' if isConsolidated else '')
        expenses_url_resp = requests.get(expenses_url).json()
        material_cost_percent = []
        for i in expenses_url_resp['Material Cost %'].values():
            try:
                material_cost_percent.append(float(i[:-1]))
            except:
                pass
        manufacuring_cost_percent = []
        for i in expenses_url_resp['Manufacturing Cost %'].values():
            try:
                manufacuring_cost_percent.append(float(i[:-1]))
            except:
                pass
        gross_expense = []
        for i in range(0, years):
            gross_expense.append(expenses_list[i]*(material_cost_percent[i] + manufacuring_cost_percent[i])/100)
        gross_profit=[]
        for i in range(0,years):
            gross_profit.append(sales_list[i]-gross_expense[i])
        gross_profit_margin = []
        for i in range(0, years):
            gross_profit_margin.append((sales_list[i] - gross_expense[i])/sales_list[i] * 100)
        other_assests_url = f'https://www.screener.in/api/company/{company_id}/schedules/?parent=Other+Assets&section=balance-sheet' + ('&consolidated=' if isConsolidated else '')
        other_assests_url_resp = requests.get(other_assests_url)
        cash_equivalents = []
        cash_equivalents_data = other_assests_url_resp.json()['Cash Equivalents']
        for i in cash_equivalents_data.values():
            try:
                cash_equivalents.append(float(i.replace(',', '')))
            except:
                pass
        trade_receivables = []
        trade_receivables_data = other_assests_url_resp.json()['Trade receivables']
        for i in trade_receivables_data.values():
            try:
                trade_receivables.append(float(i.replace(',', '')))
            except:
                pass
        cash_from_investing_url = f'https://www.screener.in/api/company/{company_id}/schedules/?parent=Cash+from+Investing+Activity&section=cash-flow' + ('&consolidated=' if isConsolidated else '')        
        cash_from_investing = requests.get(cash_from_investing_url)
        cash_from_investing_list = []
        for i in cash_from_investing.json()['Fixed assets purchased'].values():
            try:
                cash_from_investing_list.append(-(float(i.replace(',', ''))))
            except:
                pass
        balance_sheet = financial_statement[6].to_dict()
        total_assets = []
        for i in range(1, years+1):
            try:
                total_assets.append(float(balance_sheet[list(balance_sheet)[i]][9]))
            except:
                total_assets.append(None)
        equity = []
        for i in range(1, years+1):
            try:
                equity.append(float(balance_sheet[list(balance_sheet)[i]][1]))
            except:
                equity.append(None)
        borrowings = []
        for i in range(1, years+1):
            try:
                borrowings.append(float(balance_sheet[list(balance_sheet)[i]][2]))
            except:
                borrowings.append(None)
        cash_flow = financial_statement[7].to_dict()
        cash_from_operation_list = []
        for i in range(1, years+1):
            try:
                cash_from_operation_list.append(float(cash_flow[list(cash_flow)[i]][0]))
            except:
                cash_from_operation_list.append(None)
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
        roce_percent = []
        for i in range(1, years+1):
            try:
                roce_percent.append(float(ratios[list(ratios)[i]][5][:-1]))
            except:
                roce_percent.append(None)
        year_list = []
        for i in range(1, years+1):
            year_list.append(list(data)[i])
        percent_change_sales = []
        for i in range(1, len(sales_list)):
            percent_change_sales.append(((sales_list[i] - sales_list[i-1]) / sales_list[i-1]) * 100)
        std_dev_sales = statistics.stdev(percent_change_sales)
        operating_profit_list = []
        for i in range(0, years):
            try:
                operating_profit_list.append(sales_list[i] - expenses_list[i])
            except:
                operating_profit_list.append(None)
        net_profit_by_sales = []
        for i in range(0, years):
            try:
                net_profit_by_sales.append(net_profit_list[i] / sales_list[i] * 100)
            except:
                net_profit_by_sales.append(None)
        capex_by_income = sum(cash_from_investing_list) / sum(net_profit_list) * 100
        capex_list = []
        for i in range(0, years):
            try:
                capex_list.append(cash_from_investing_list[i] / net_profit_list[i] * 100)
            except:
                capex_list.append(None)
        return_on_assets = []
        for i in range(0, years):
            try:
                return_on_assets.append(net_profit_list[i] / total_assets[i] * 100)
            except:
                return_on_assets.append(None)
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
        debt_to_equity = []
        for i in range(0, years):
            try:
                debt_to_equity.append(borrowings[i] / equity[i])
            except:
                debt_to_equity.append(None)
        trade_receivables_by_total_assets = []
        for i in range(0, years):
            try:
                trade_receivables_by_total_assets.append(trade_receivables[i] / total_assets[i] * 100)
            except:
                trade_receivables_by_total_assets.append(None)
        interest_by_sales = []
        for i in range(0, years):
            try:
                interest_by_sales.append(interest_list[i] / sales_list[i] * 100)
            except:
                interest_by_sales.append(None)
        depreciation_by_sales = []
        for i in range(0, years):
            try:
                depreciation_by_sales.append(depreciation_list[i] / sales_list[i] * 100)
            except:
                depreciation_by_sales.append(None)
        compounded_profit_growth = net_profit_list[-1] / net_profit_list[0]
        compounded_profit_growth = compounded_profit_growth ** (1/len(net_profit_list)) - 1
        compounded_profit_growth *= 100
        price_willing_to_pay = eps[-1] * compounded_profit_growth
        cmp_info = soup.find('div', {'class': 'company-info'})
        book_value = cmp_info.findAll('li')[4].find('span', {'class': 'value'}).text.replace('₹', '').strip()
        market_cap = cmp_info.findAll('li')[0].find('span', {'class': 'value'}).text.replace('₹', '').replace(',', '').strip()
        current_price = cmp_info.findAll('li')[1].find('span', {'class': 'value'}).text.replace('₹', '').replace(',', '').strip()
        peer_info = soup.find('section', {'id': 'peers'})
        peer_info = peer_info.find('p').find_all('a')
        sector = peer_info[0].text.strip()
        industry = peer_info[1].text.strip()
        auth_token = 'csrftoken=14cOcxbER7QfBXEcyZeCwBvCFAbZYigJ; sessionid=rr3fp4r5umhqwrnh0bu8iyq5vfsxeg0l'
        key_insights_url = f'https://www.screener.in/wiki/company/{company_id}/commentary/v2/'
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
        key_insights_resp = requests.get(key_insights_url, headers=headers)
        soup_key_insights = BeautifulSoup(key_insights_resp.content, 'html.parser')
        key_insights = ''
        for para in soup_key_insights.find_all('p'):
            key_insights += para.text
        key_insights = key_insights.split('Last edited')[0]
        key_insights = re.sub(r'\[.*?\]', '\n', key_insights)
        pe_url = f'https://www.screener.in/api/company/{company_id}/chart/?q=Price+to+Earning-Median+PE-EPS&days=10000' + ('&consolidated=true' if isConsolidated else '')
        pe_resp = requests.get(pe_url).json()
        eps_data = pe_resp['datasets'][0]
        pe_data = pe_resp['datasets'][1]
        dma_url = f'https://www.screener.in/api/company/{company_id}/chart/?q=Price-DMA50-DMA200-Volume&days=10000' + ('&consolidated=true' if isConsolidated else '')
        dma_resp = requests.get(dma_url).json()
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
        compunded_sales_growth_decimal = compunded_sales_growth / 100
        free_cash_flow = []
        for i in range(years):
            try:
                free_cash_flow.append(net_profit_list[i] + depreciation_list[i] - capex_list[i] - interest_list[i])
            except:
                free_cash_flow.append(None)
        intrinsic_value = eps[-1] * compounded_profit_growth
        price_to_sales = price_list[-1] / sales_list[-1]
        price_to_earnings = price_list[-1] / eps[-1]
        price_to_book_value = float(current_price.replace(',', '')) / float(book_value.replace(',',''))
        price_to_free_cash_flow = price_list[-1] / free_cash_flow[-1]
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



        india_gdp_growth_rate = 'INGDPQQ'
        india_gdp = 'INGDP'
        india_gdp_per_capita = 'INGDPPC'
        india_interest_rate = 'ININTR'
        india_inflation_rate = 'INIRYY'
        india_unemployment_rate = 'INUR'
        india_population = 'INPOP'
        india_government_debt = 'INGDG'
        usd_inr = 'USDINR'
        nifty_50 = 'NSE:NIFTY'
        dow_jones = 'DJI'



        df = load_asset_price(usd_inr, 1200,'1M', pytz.timezone('Asia/Kolkata'))
        usd_inr_time = df['time'].dt.strftime('%Y-%m-%d').tolist()
        usd_inr_price = df['close'].tolist()

        df = load_asset_price(nifty_50, 1200,'1M', pytz.timezone('Asia/Kolkata'))
        nifty_time = df['time'].dt.strftime('%Y-%m-%d').tolist()
        nifty_price = df['close'].tolist()

        df = load_asset_price(dow_jones, 1200,'1M', pytz.timezone('Asia/Kolkata'))
        dow_jones_time = df['time'].dt.strftime('%Y-%m-%d').tolist()
        dow_jones_price = df['close'].tolist()

        df = load_asset_price(india_gdp_growth_rate, 1200,'1M', pytz.timezone('Asia/Kolkata'))
        india_gdp_growth_rate_time = df['time'].dt.strftime('%Y-%m-%d').tolist()
        india_gdp_growth_rate_price = df['close'].tolist()

        df = load_asset_price(india_gdp, 1200,'1M', pytz.timezone('Asia/Kolkata'))
        india_gdp_time = df['time'].dt.strftime('%Y-%m-%d').tolist()
        india_gdp_price = df['close'].tolist()

        df = load_asset_price(india_gdp_per_capita, 1200,'1M', pytz.timezone('Asia/Kolkata'))
        india_gdp_per_capita_time = df['time'].dt.strftime('%Y-%m-%d').tolist()
        india_gdp_per_capita_price = df['close'].tolist()

        df = load_asset_price(india_interest_rate, 1200,'1M', pytz.timezone('Asia/Kolkata'))
        india_interest_rate_time = df['time'].dt.strftime('%Y-%m-%d').tolist()
        india_interest_rate_price = df['close'].tolist()

        df = load_asset_price(india_inflation_rate, 1200,'1M', pytz.timezone('Asia/Kolkata'))
        india_inflation_rate_time = df['time'].dt.strftime('%Y-%m-%d').tolist()
        india_inflation_rate_price = df['close'].tolist()

        df = load_asset_price(india_unemployment_rate, 1200,'1M', pytz.timezone('Asia/Kolkata'))
        india_unemployment_rate_time = df['time'].dt.strftime('%Y-%m-%d').tolist()
        india_unemployment_rate_price = df['close'].tolist()

        df = load_asset_price(india_population, 1200,'1M', pytz.timezone('Asia/Kolkata'))
        india_population_time = df['time'].dt.strftime('%Y-%m-%d').tolist()
        india_population_price = df['close'].tolist()

        df = load_asset_price(india_government_debt, 1200,'1M', pytz.timezone('Asia/Kolkata'))
        india_government_debt_time = df['time'].dt.strftime('%Y-%m-%d').tolist()
        india_government_debt_price = df['close'].tolist()






        graph_ratings_and_weightage = {
            'revenue' : {'rating':rate_graph(sales_list), 'weightage':10},
            'percentchangeinrevenue' : {'rating':rate_graph_anchor(percent_change_sales, 8, growth_positive=True), 'weightage':7},
            'expenses' : {'rating':rate_graph(expenses_list, growth_percent=0.15), 'weightage':6},
            'materialcost' : {'rating':rate_graph_anchor(material_cost_percent,20,False,0.1,0.9), 'weightage':4},
            'manufacturingcost' : {'rating':rate_graph_anchor(manufacuring_cost_percent,20,False,0.1,0.9), 'weightage':4},
            'grossexpense' : {'rating':rate_graph(gross_expense, growth_percent=0.1), 'weightage':6},
            'grossprofit':{'rating':rate_graph(gross_profit,growth_percent=0.12), 'weightage':7},
            'grossprofitmargin' : {'rating':rate_graph_anchor(gross_profit_margin, 50, weight_anchor=0.2, weight_growth=0.8), 'weightage':7},
            'operatingprofit' : {'rating':rate_graph(operating_profit_list,growth_percent=0.2), 'weightage':9},
            'operatingprofitmargin' : {'rating':rate_graph_anchor(opm_percent_list, 15, weight_anchor=0.2, weight_growth=0.8), 'weightage':9},
            'interest' : {'rating':rate_graph_anchor(interest_list, 0, False, weight_anchor=0.3, weight_growth=0.7), 'weightage':6},
            'interestbyrevenue' : {'rating':rate_graph_anchor(interest_by_sales, 0, False, 0.6, 0.4), 'weightage':8},
            'depreciation' : {'rating':rate_graph_anchor(depreciation_list,0,False,0.3,0.7), 'weightage':6},
            'depreciationbyrevenue' : {'rating':rate_graph_anchor(depreciation_by_sales,0,False,0.7,0.3), 'weightage':6},
            'netprofit' : {'rating':rate_graph(net_profit_list), 'weightage':10},
            'netprofitbyrevenue' : {'rating':rate_graph_anchor(net_profit_by_sales,12,True,0.5,0.5), 'weightage':10},
            'epsvalues' : {'rating':rate_graph(eps_values_list, growth_percent=0.2), 'weightage':10},
            'totalassets' : {'rating':rate_graph(total_assets, growth_percent=0.16), 'weightage':10},
            'returnonassets' : {'rating':rate_graph_anchor(return_on_assets,15,0.4,0.6), 'weightage':10},
            'equity' : {'rating':rate_graph(equity, growth_percent=0.2), 'weightage':10},
            'returnonequity' : {'rating':rate_graph_anchor(return_on_equity,20,weight_anchor=0.3, weight_growth=0.7), 'weightage':10},
            'cashequivalents' : {'rating':rate_graph(cash_equivalents, growth_percent=0.12), 'weightage':8},
            'cashequivalentsbytotalassets' : {'rating':rate_graph_anchor(cash_equivalents_by_total_assets, 7, True, 0.2, 0.8), 'weightage':9},
            'tradereceivables' : {'rating':rate_graph(trade_receivables[::-1], growth_percent=0.1), 'weightage':7},
            'tradereceivablesbytotalassets' : {'rating':rate_graph_anchor(trade_receivables_by_total_assets, 2, False, 0.5, 0.5), 'weightage':8},
            'borrowings' : {'rating':rate_graph(borrowings[::-1], growth_percent=0.08), 'weightage':10},
            'debttoequity' : {'rating':rate_graph_anchor(debt_to_equity, 0, False, 0.6, 0.4), 'weightage':10},
            'capexbyincomeinpercentage' : {'rating':8, 'weightage':10},
            'cashfromoperations' : {'rating':rate_graph(cash_from_operation_list, growth_percent=0.2), 'weightage':10},
            'cashfrominvesting' : {'rating':rate_graph(cash_from_investing_list,growth_percent=0.2), 'weightage':9},
            'promoterholding' : {'rating':rate_graph_anchor(promoter_holding, 75, False, 0.6, 0.4), 'weightage':10},
            'cashconversioncycle' : {'rating':rate_graph_anchor(cash_conversion_cycle, 0, False, 0.8, 0.2), 'weightage':7},
            'roce' : {'rating':rate_graph_anchor(roce_percent, 20, True, 0.2, 0.8), 'weightage':6},
        }




        data = {
            'market_cap': market_cap,
            'graph_ratings_and_weightage' : graph_ratings_and_weightage,
            'usd_inr_time': usd_inr_time,
            'usd_inr_price': usd_inr_price,
            'nifty_time': nifty_time,
            'nifty_price': nifty_price,
            'dow_jones_time': dow_jones_time,
            'dow_jones_price': dow_jones_price,
            'india_gdp_growth_rate_time': india_gdp_growth_rate_time,
            'india_gdp_growth_rate_price': india_gdp_growth_rate_price,
            'india_gdp_time': india_gdp_time,
            'india_gdp_price': india_gdp_price,
            'india_gdp_per_capita_time': india_gdp_per_capita_time,
            'india_gdp_per_capita_price': india_gdp_per_capita_price,
            'india_interest_rate_time': india_interest_rate_time,
            'india_interest_rate_price': india_interest_rate_price,
            'india_inflation_rate_time': india_inflation_rate_time,
            'india_inflation_rate_price': india_inflation_rate_price,
            'india_unemployment_rate_time': india_unemployment_rate_time,
            'india_unemployment_rate_price': india_unemployment_rate_price,
            'india_population_time': india_population_time,
            'india_population_price': india_population_price,
            'india_government_debt_time': india_government_debt_time,
            'india_government_debt_price': india_government_debt_price,
            'company': company,
            'company_name': company_name,
            'isConsolidated': isConsolidated,
            'compunded_sales_growth': compunded_sales_growth,
            'years': years,
            'sales_list': sales_list,
            'expenses_list': expenses_list,
            'opm_percent_list': opm_percent_list,
            'interest_list': interest_list,
            'depreciation_list': depreciation_list,
            'net_profit_list': net_profit_list,
            'eps': eps,
            'material_cost_percent': material_cost_percent,
            'manufacuring_cost_percent': manufacuring_cost_percent,
            'gross_expense': gross_expense,
            'gross_profit':gross_profit,
            'gross_profit_margin': gross_profit_margin,
            'cash_equivalents': cash_equivalents,
            'trade_receivables': trade_receivables,
            'cash_from_investing_list': cash_from_investing_list,
            'total_assets': total_assets,
            'equity': equity,
            'borrowings': borrowings,
            'cash_from_operation_list': cash_from_operation_list,
            'promoter_holding': promoter_holding,
            'promoter_holding_years': promoter_holding_years,
            'cash_conversion_cycle': cash_conversion_cycle,
            'roce_percent': roce_percent,
            'year_list': year_list,
            'percent_change_sales': percent_change_sales,
            'std_dev_sales': std_dev_sales,
            'operating_profit_list': operating_profit_list,
            'net_profit_by_sales': net_profit_by_sales,
            'capex_by_income': capex_by_income,
            'capex_list': capex_list,
            'return_on_assets': return_on_assets,
            'return_on_equity': return_on_equity,
            'cash_equivalents_by_total_assets': cash_equivalents_by_total_assets,
            'debt_to_equity': debt_to_equity,
            'trade_receivables_by_total_assets': trade_receivables_by_total_assets,
            'interest_by_sales': interest_by_sales,
            'depreciation_by_sales': depreciation_by_sales,
            'compounded_profit_growth': compounded_profit_growth,
            'price_willing_to_pay': price_willing_to_pay,
            'number_of_shares': number_of_shares,
            'key_insights': key_insights,
            'pe_date_list': pe_date_list,
            'pe_list': pe_list,
            'eps_date_list': eps_date_list,
            'eps_values_list': eps_values_list,
            'dma50_list': dma50_list,
            'dma50_date_list': dma50_date_list,
            'dma200_list': dma200_list,
            'dma200_date_list': dma200_date_list,
            'volume_list': volume_list,
            'volume_date_list': volume_date_list,
            'price_list': price_list,
            'price_date_list': price_date_list,
            'intrinsic_value': intrinsic_value,
            'price_to_sales': price_to_sales,
            'price_to_earnings': price_to_earnings,
            'price_to_book_value': price_to_book_value,
            'price_to_free_cash_flow': price_to_free_cash_flow, 
            'price_to_operating_cash_flow': price_to_operating_cash_flow,   
            'sector': sector,
            'industry': industry,
            'current_price': current_price,
            'book_value': book_value,
            'compounded_profit_growth_decimal': compounded_profit_growth_decimal,
            'compunded_sales_growth_decimal': compunded_sales_growth_decimal,
            'free_cash_flow': free_cash_flow,
            'buying_window' : buying_window,
        }
        return Response(data)

