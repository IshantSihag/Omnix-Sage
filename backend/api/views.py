from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
import pandas as pd
import statistics
from bs4 import BeautifulSoup
# Create your views here.



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
        operating_profit_margin_list = []
        for i in range(0, years):
            try:
                operating_profit_margin_list.append(operating_profit_list[i] / sales_list[i] * 100)
            except:
                operating_profit_margin_list.append(None)
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

        data = {
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
            'operating_profit_margin_list': operating_profit_margin_list,
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
            'free_cash_flow': free_cash_flow
        }
        return Response(data)

