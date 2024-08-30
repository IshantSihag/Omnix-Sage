import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { ClipLoader } from 'react-spinners';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

function Report() {
  const location = useLocation();
  const { company } = location.state || {};
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (company) {
      const fetchData = async () => {
        try {
          const response = await fetch(`http://127.0.0.1:8000/api/analysis?company=${company.url}`);
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          const result = await response.json();
        //   const result = response;
          setData(result);
        } catch (error) {
          setError(error);
        } finally {
          setLoading(false);
        }
      };

      fetchData();
    } else {
      setLoading(false);
    }
  }, [company]);

  if (loading) {
    return (
      <div className="spinner-container">
        <ClipLoader size={50} color={"#123abc"} loading={loading} />
      </div>
    );
  }

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  const renderChart = (label, plot_data, color, label_list = data.year_list) => {
    const pointRadius = label_list.length > 100 ? 0 : 3;
     return (
      <Line
        data={{
          labels: label_list,
          datasets: [
            {
              label: label,
              data: plot_data,
              borderColor: color,
              backgroundColor: `${color.replace('1)', '0.2)')}`,
              pointRadius: pointRadius,
              pointHoverRadius: 20,
            },
          ],
        }}
        options={{
          interaction: {
            mode: 'index',
            intersect: false,
          },
        plugins: {
          tooltip: {
            mode: 'index',
            intersect: false,
            
          },
        },
        }}
      />
    );
  };

  const renderCombinedChart = (data) => {
    return (
      <Line
        data={{
          labels: data.dma50_date_list, // Assuming all datasets share the same date list
          datasets: [
            {
              label: 'DMA 50',
              data: data.dma50_list,
              borderColor: 'rgba(255, 159, 64, 1)',
              backgroundColor: 'rgba(255, 159, 64, 0.2)',
              pointRadius: 0,
              pointHoverRadius: 0,
              yAxisID: 'y-axis-1',
            },
            {
              label: 'DMA 200',
              data: data.dma200_list,
              borderColor: 'rgba(255, 206, 86, 1)',
              backgroundColor: 'rgba(255, 206, 86, 0.2)',
              pointRadius: 0,
              pointHoverRadius: 0,
              yAxisID: 'y-axis-1',
            },
            {
              label: 'Volume',
              data: data.volume_list,
              borderColor: 'rgba(75, 192, 192, 1)',
              backgroundColor: 'rgba(72, 192, 192, 0.5)',
              type: 'bar', // Use bar type for volume
              yAxisID: 'y-axis-2',
            },
            {
              label: 'Price',
              data: data.price_list,
              borderColor: 'rgba(255, 99, 132, 1)',
              backgroundColor: 'rgba(255, 99, 132, 0.2)',
              pointRadius: 0,
              pointHoverRadius: 20,
              yAxisID: 'y-axis-1',
            },
          ],
        }}
        options={{
          interaction: {
            mode: 'index',
            intersect: false,
          },
          scales: {
            x: {
              beginAtZero: true,
              grid: {
                display: false,
              },
              
            },
            'y-axis-1': {
              type: 'linear',
              position: 'left',
              beginAtZero: true,
              grid: {
                drawOnChartArea: false, // only want the grid lines for one axis to show up
              },
            },
            'y-axis-2': {
              type: 'linear',
              position: 'right',
              beginAtZero: true,
              grid: {
                drawOnChartArea: false, // only want the grid lines for one axis to show up
              },
            },
          },
          plugins: {
            tooltip: {
              mode: 'index',
              intersect: false,
              
            },
          },
        }}
      />
    );
  };
  
const renderBarChart = (label, plot_data, color, label_list) => {
  return (
    <Bar
      data={{
        labels: label_list,
        datasets: [
          {
            label: label,
            data: plot_data,
            backgroundColor: `${color.replace('1)', '0.2)')}`,
            borderColor: color,
            borderWidth: 1,
          },
        ],
      }}
      options={{
        scales: {
          x: {
            beginAtZero: true,
          },
          y: {
            beginAtZero: true,
          },
        },
      }}
    />
  );
};

  return (
    <div>
      <h2>Report Page</h2>
      {company ? (
        <div>
          <h3>{company.name}</h3>
          <p>URL: {company.url}</p>
          {data ? (
            <div>
              <h4>Data from API:</h4>

              <div>
                <h5>Industry</h5>
                <p>{data.industry}</p>
              </div>
              <div>
                <h5>Sector</h5>
                <p>{data.sector}</p>
              </div>
              <div>
                <h5>USD INR</h5>
                {renderChart('USD INR', data.usd_inr_price, 'rgba(212, 45, 34, 1)', data.usd_inr_time)}
              </div>
              <div>
                <h5>Nifty</h5>
                {renderChart('Nifty', data.nifty_price, 'rgba(34, 45, 212, 1)', data.nifty_time)}
              </div>
              <div>
                <h5>Dow Jones</h5>
                {renderChart('Dow Jones', data.dow_jones_price, 'rgba(45, 212, 34, 1)', data.dow_jones_time)}
              </div>
              <div>
                <h5>India GDP Growth Rate</h5>
                {renderChart('India GDP Growth Rate', data.india_gdp_growth_rate_price, 'rgba(212, 34, 45, 1)', data.india_gdp_growth_rate_time)}
              </div>
              <div>
                <h5>India GDP</h5>
                {renderChart('India GDP', data.india_gdp_price, 'rgba(34, 212, 45, 1)', data.india_gdp_time)}
              </div>
              <div>
                <h5>India GDP Per Capita</h5>
                {renderChart('India GDP Per Capita', data.india_gdp_per_capita_price, 'rgba(45, 34, 212, 1)', data.india_gdp_per_capita_time)}
              </div>
              <div>
                <h5>India Interest Rate</h5>
                {renderChart('India Interest Rate', data.india_interest_rate_price, 'rgba(212, 45, 34, 1)', data.india_interest_rate_time)}
              </div>
              <div>
                <h5>India Inflation Rate</h5>
                {renderChart('India Inflation Rate', data.india_inflation_rate_price, 'rgba(34, 45, 212, 1)', data.india_inflation_rate_time)}
              </div>
              <div>
                <h5>India Unemployment Rate</h5>
                {renderChart('India Unemployment Rate', data.india_unemployment_rate_price, 'rgba(45, 212, 34, 1)', data.india_unemployment_rate_time)}
              </div>
              <div>
                <h5>India Population</h5>
                {renderChart('India Population', data.india_population_price, 'rgba(212, 34, 45, 1)', data.india_population_time)}
              </div>
              <div>
                <h5>India Government Debt</h5>
                {renderChart('India Government Debt', data.india_government_debt_price, 'rgba(34, 212, 45, 1)', data.india_government_debt_time)}
              </div>
              <div>
                <h5>Key Insights</h5>
                <pre>{JSON.stringify(data.key_insights, null, 2)}</pre>
              </div>
              <div>
                <h5>Revenue</h5>
                {renderChart('Revenue', data.sales_list, 'rgba(75, 192, 192, 1)')}
              </div>
              <div>
              <h5>Percent Change in Revenue</h5>
                {renderChart('Percent Change in Revenue', data.percent_change_sales, 'rgba(123, 104, 238, 1)', data.year_list.slice(1))}
              </div>
              <div>
                <h5>Expenses</h5>
                {renderChart('Expenses', data.expenses_list, 'rgba(255, 99, 132, 1)')}
              </div>
              <div>
                <h5>Material Cost %</h5>
                {renderChart('Material Cost %', data.material_cost_percent, 'rgba(255, 99, 132, 1)')}
              </div>
              <div>
                <h5>Manufacturing Cost %</h5>
                {renderChart('Manufacturing Cost %', data.manufacuring_cost_percent, 'rgba(54, 162, 235, 1)')}
              </div>
              <div>
                <h5>Gross Expense</h5>
                {renderChart('Gross Expense', data.gross_expense, 'rgba(153, 102, 255, 1)')}
              </div>
              <div>
                <h5>Gross Profit Margin</h5>
                {renderChart('Gross Profit Margin', data.gross_profit_margin, 'rgba(255, 159, 64, 1)')}
              </div>
              <div>
                <h5>Operating Profit</h5>
                {renderChart('Operating Profit', data.operating_profit_list, 'rgba(255, 206, 86, 1)')}
              </div>
              <div>
                <h5>OPM %</h5>
                {renderChart('OPM %', data.opm_percent_list, 'rgba(54, 162, 235, 1)')}
              </div>
              <div>
                <h5>Interest</h5>
                {renderChart('Interest', data.interest_list, 'rgba(153, 102, 255, 1)')}
              </div>
              <div>
                <h5>Interest by Revenue</h5>
                {renderChart('Interest by Revenue', data.interest_by_sales, 'rgba(153, 102, 255, 1)')}
              </div>
              <div>
                <h5>Depreciation</h5>
                {renderChart('Depreciation', data.depreciation_list, 'rgba(255, 159, 64, 1)')}
              </div>
              <div>
                <h5>Depreciation by Revenue</h5>
                {renderChart('Depreciation by Revenue', data.depreciation_by_sales, 'rgba(255, 159, 64, 1)')}
              </div>
              <div>
                <h5>Net Profit</h5>
                {renderChart('Net Profit', data.net_profit_list, 'rgba(255, 206, 86, 1)')}
              </div>
              <div>
                <h5>Net Profit by Revenue</h5>
                {renderChart('Net Profit by Revenue', data.net_profit_by_sales, 'rgba(255, 99, 132, 1)')}
              </div>
              <div>
                <h5>EPS</h5>
                {renderChart('EPS', data.eps, 'rgba(75, 192, 192, 1)')}
              </div>
              {/* divident aayega */}
              <div>
                <h5>Total Assets</h5>
                {renderChart('Total Assets', data.total_assets, 'rgba(54, 162, 235, 1)')}
              </div>
              <div>
                <h5>Return on Assets</h5>
                {renderChart('Return on Assets', data.return_on_assets, 'rgba(255, 159, 64, 1)')}
              </div>
              <div>
                <h5>Equity</h5>
                {renderChart('Equity', data.equity, 'rgba(153, 102, 255, 1)')}
              </div>
              <div>
                <h5>Return on Equity</h5>
                {renderChart('Return on Equity', data.return_on_equity, 'rgba(255, 206, 86, 1)')}
              </div>
              <div>
                <h5>Cash Equivalents</h5>
                {renderChart('Cash Equivalents', data.cash_equivalents, 'rgba(255, 206, 86, 1)')}
              </div>
              <div>
                <h5>Cash Equivalents by Total Assets</h5>
                {renderChart('Cash Equivalents by Total Assets', data.cash_equivalents_by_total_assets, 'rgba(75, 192, 192, 1)')}
              </div>
              <div>
                <h5>Trade Receivables</h5>
                {renderChart('Trade Receivables', data.trade_receivables, 'rgba(75, 192, 192, 1)')}
              </div>
              <div>
                <h5>Trade Receivables by Total Assets</h5>
                {renderChart('Trade Receivables by Total Assets', data.trade_receivables_by_total_assets, 'rgba(54, 162, 235, 1)')}
              </div>
              <div>
                <h5>Borrowings</h5>
                {renderChart('Borrowings', data.borrowings, 'rgba(255, 159, 64, 1)')}
              </div>
              <div>
                <h5>Debt to Equity</h5>
                {renderChart('Debt to Equity', data.debt_to_equity, 'rgba(255, 99, 132, 1)')}
              </div>
              <div>
                <h5>Capex</h5>
                {renderChart('Capex', data.capex_list, 'rgba(153, 102, 255, 1)')}
              </div>
              <div>
                <h5>Capex by Income in Percentage</h5>
                <p>{data.capex_by_income}</p>
              </div>
              <div>
                <h5>Cash from Operations</h5>
                {renderChart('Cash from Operations', data.cash_from_operation_list, 'rgba(255, 206, 86, 1)')}
              </div>
              <div>
                <h5>Cash from Investing</h5>
                {renderChart('Cash from Investing', data.cash_from_investing_list, 'rgba(255, 99, 132, 1)')}
              </div>
              <div>
                <h5>Free Cash Flow</h5>
                {renderChart('Free Cash Flow', data.free_cash_flow, 'rgba(123, 104, 238, 1)')}
              </div>
              <div>
                <h5>Promoter Holding</h5>
                {renderChart('Promoter Holding', data.promoter_holding, 'rgba(75, 192, 192, 1)')}
              </div>
              <div>
                <h5>Cash Conversion Cycle</h5>
                {renderChart('Cash Conversion Cycle', data.cash_conversion_cycle, 'rgba(255, 99, 132, 1)')}
              </div>
              <div>
                <h5>ROCE %</h5>
                {renderChart('ROCE %', data.roce_percent, 'rgba(54, 162, 235, 1)')}
              </div>
              <div>
                <h5>PE Ratio</h5>
                {renderChart('PE Ratio', data.pe_list, 'rgba(54, 162, 235, 1)', data.pe_date_list)}
              </div>
              <div>
                <h5>EPS Values</h5>
                {renderChart('EPS Values', data.eps_values_list, 'rgba(153, 102, 255, 1)', data.eps_date_list)}
              </div>
              <div>
              <h5>DMA 50</h5>
                {renderChart('DMA50', data.dma50_list, 'rgba(255, 159, 64, 1)', data.dma50_date_list)}
              </div>
              <div>
                <h5>DMA 200</h5>
                {renderChart('DMA200', data.dma200_list, 'rgba(255, 206, 86, 1)', data.dma200_date_list)}
              </div>
              <div>
                <h5>Volume</h5>
                {renderBarChart('Volume', data.volume_list, 'rgba(75, 192, 192, 1)', data.volume_date_list)}
              </div>
              <div>
                <h5>Price</h5>
                {renderChart('Price', data.price_list, 'rgba(255, 99, 132, 1)', data.price_date_list)}
              </div>
              <div>
                <h5>Combined Chart</h5>
                {renderCombinedChart(data)}
                </div>
              <div>
                <h5>Number of Shares</h5>
                <p>{data.number_of_shares}</p>
              </div>
              <div>
                <h5>Intrinsic Value</h5>
                <p>{data.intrinsic_value}</p>
              </div>
              <div>
                <h5>Price to Sales</h5>
                <p>{data.price_to_sales}</p>
              </div>
              <div>
                <h5>Price to Earnings</h5>
                <p>{data.price_to_earnings}</p>
              </div>
              <div>
                <h5>Price to Book Value</h5>
                <p>{data.price_to_book_value}</p>
              </div>
              <div>
                <h5>Price to Free Cash Flow</h5>
                <p>{data.price_to_free_cash_flow}</p>
              </div>
              <div>
                <h5>Price to Operating Cash Flow</h5>
                <p>{data.price_to_operating_cash_flow}</p>
              </div>
              <div>
                <h5>Current Price</h5>
                <p>{data.current_price}</p>
              </div>
              <div>
                <h5>Book Value</h5>
                <p>{data.book_value}</p>
              </div>
              <div>
                <h5>Compounded Profit Growth</h5>
                <p>{data.compounded_profit_growth}</p>
              </div>
              <div>
                <h5>Compounded Sales Growth</h5>
                <p>{data.compunded_sales_growth}</p>
              </div>
              <div>
                <h5>Price Willing to Pay</h5>
                <p>{data.price_willing_to_pay}</p>
              </div>
            </div>
          ) : (
            <p>No data available.</p>
          )}
        </div>
      ) : (
        <div>
          <h1>Invalid Entry</h1>
          <p>No company selected.</p>
          <p>Please go to homepage and try again.</p>
        </div>
      )}
    </div>
  );
}

export default Report;