import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { ClipLoader } from 'react-spinners';
import { Line } from 'react-chartjs-2';
import { Rating as StarRating } from 'react-simple-star-rating';
import Rating from 'react-rating';
import './Report.css';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  BarController,
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
  BarController,
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
  const [finalRating, setFinalRating] = useState(0);
  const [chartRatingAndWeightage, setChartRatingAndWeightage] = useState({});

  // useEffect(() => {
  //   // Calculate the total rating whenever the ratings array changes
  //   const newTotalRating = Object.values(ratings).reduce((acc, rating) => acc + rating, 0);
  //   setTotalRating(newTotalRating);
  // }, [ratings]);

  useEffect(() => {
    if (chartRatingAndWeightage && Object.keys(chartRatingAndWeightage).length > 0) {
      let rw = 0;
      let w = 0;
      console.log("Chart Rating and Weightage in final calculation: ", chartRatingAndWeightage);
      for (const [key, value] of Object.entries(chartRatingAndWeightage)) {
        rw += value['rating'] * value['weightage'];
        w += value['weightage'];
      }
      console.log("rw , w : ", rw, w);
      if(w != 0){
        setFinalRating(rw/w)
      }
    }
  }, [chartRatingAndWeightage]);

  useEffect(() => {
    if (company) {
      const fetchData = async () => {
        try {
          const response = await fetch(`https://cors-anywhere.herokuapp.com/http://139.59.20.158:8000/api/analysis?company=${company.url}`);
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          const result = await response.json();
          //   const result = response;
          console.log("Result ", result);
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
  }, []);

  useEffect(() => {
    setChartRatingAndWeightage(data?.graph_ratings_and_weightage);
  }, [data])



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

  const calculateCAGR = (data) => {
    const startValue = data[0];
    const endValue = data[data.length - 1];
    const periods = data.length - 1;
    return Math.pow(endValue / startValue, 1 / periods) - 1;
  };
  
  const generatePredictions = (data, years) => {
    const cagr = calculateCAGR(data);
    const lastValue = data[data.length - 1];
    const predictions = [];
    for (let i = 1; i <= years; i++) {
      const prediction = lastValue * Math.pow(1 + cagr, i);
      predictions.push(prediction);
    }
    return predictions;
  };
  
  const generateExtendedLabels = (label_list) => {
    const lastLabel = label_list[label_list.length - 1];
    const lastYear = parseInt(lastLabel.split(' ')[1], 10);
    const nextYears = [lastYear + 1, lastYear + 2, lastYear + 3].map(year => `Mar ${year}`);
    return [...label_list, ...nextYears];
  };

  const renderChart = (label, plot_data, color, label_list = data.year_list) => {
    const pointRadius = label_list.length > 100 ? 0 : 3;
    const predictions = generatePredictions(plot_data, 3);
    const extendedLabels = generateExtendedLabels(label_list);
    const extendedData = [...plot_data, ...predictions];
    const extendLabelGraphList = ['Revenue', 'Expenses',  'Gross Profit', 'Operating Profit',
      'Net Profit', 'Total Assets', 'Equity', 'Cash Equivalents', 'Trade Receivables', 'Borrowings',
      'Cash from Operations', 'Cash from Investing', 
    ]

    const datasets = [
      {
          label: label,
          data: plot_data,
          borderColor: color,
          backgroundColor: `${color.replace('1)', '0.2)')}`,
          pointRadius: pointRadius,
          pointHoverRadius: 20,
      }
  ];

  if (extendLabelGraphList.includes(label)) {
      label_list = extendedLabels;
      datasets.push({
          label: label + ' Prediction',
          data: extendedData,
          borderColor: color,
          backgroundColor: `${color.replace('1)', '0.2)')}`,
          pointRadius: pointRadius,
          pointHoverRadius: 20,
      });
  }

    return (
      <div className='graph'>
        <Line
          data={{
            labels: label_list,
            datasets: datasets,
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
      </div>
    );
  };

  const CircleIcon = ({ fill = 'none', stroke = 'black', strokeWidth = 2 }) => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill={fill} xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="10" stroke={stroke} strokeWidth={strokeWidth} />
    </svg>
  );

  const renderChartWithRating = (label, plot_data, color, label_list = data.year_list) => {
    function cleanString(input) {
      // Convert the string to lowercase
      let lowerCaseString = input.toLowerCase();

      // Replace any non-alphabet characters with an empty string
      // or you can replace them with another character if needed
      let cleanedString = lowerCaseString.replace(/[^a-z]/g, '');

      return cleanedString;
    }
    let cleanedLabel = cleanString(label);
    return (<div className='graph-rating-wrapper'>
      <h5>{label}</h5>
      {renderChart(label, plot_data, color, label_list)}
      <div className='rating-weightage-wrapper'>
        <div className='graph-weightage'>
          <span>Weightage : </span>
          <Rating
            initialRating={data.graph_ratings_and_weightage[cleanedLabel]['weightage']}
            onClick={(value) => {handleWeightChange(value, cleanedLabel) }}
            emptySymbol={<CircleIcon fill="none" stroke="black" />}
            fullSymbol={<CircleIcon fill="green" stroke="black" />}
            transition={true}
            start={0} // Start the rating from 0
            stop={10} // End the rating at 10 (number of stars)

          // transition
          // fractions={2} // Adjust this if needed
          />
        </div>
        <div className='graph-ratings'>
          <span>Ratings : </span>
          <StarRating
            initialValue={data.graph_ratings_and_weightage[cleanedLabel]['rating']}
            onClick={(value) => handleRatingChange(value, cleanedLabel)}
            transition={true}
            iconsCount={10}
          />
        </div>
      </div>
    </div>)

  }
  
  const renderCombinedChart = (data) => {
    return (
      <Line
      data={{
        labels: data.dma50_date_list, // Assuming all datasets share the same date list
          datasets: [
            {
              label: 'Price',
              data: data.price_list,
              borderColor: 'rgba(0, 181, 226, 1)',
              backgroundColor: 'rgba(0, 181, 226, 0.2)',
              pointRadius: 0,
              pointHoverRadius: 20,
              yAxisID: 'y-axis-1',
            },
            {
              label: 'Buy Signal',
              data: data.buying_window,
              backgroundColor: 'rgba(0, 255, 0, 0.2)',
              borderColor: 'rgba(0, 255, 0, 0.5)',
              type: 'bar', // Use bar type for volume
              yAxisID: 'y-axis-2',
            },
            {
              label: 'DMA 50',
              data: data.dma50_list,
              borderColor: 'rgba(115, 223, 61, 1)',
              backgroundColor: 'rgba(115, 223, 61, 0.2)',
              borderWidth: 1,
              pointRadius: 0,
              pointHoverRadius: 0,
              yAxisID: 'y-axis-1',
            },
            {
              label: 'DMA 200',
              data: data.dma200_list,
              borderColor: 'rgba(82, 101, 118, 1)',
              backgroundColor: 'rgba(82, 101, 118, 0.2)',
              borderWidth: 1,
              pointRadius: 0,
              pointHoverRadius: 0,
              yAxisID: 'y-axis-1',
            },
            {
              label: 'Volume',
              data: data.volume_list,
              borderColor: 'rgba(0, 181, 226, 1)',
              backgroundColor: 'rgba(0, 181, 226, 0.5)',
              type: 'bar', // Use bar type for volume
              yAxisID: 'y-axis-2',
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
              callbacks: {
                label: function (tooltipItem) {
                  if (tooltipItem.dataset.label === 'Buy Signal') {
                    return null; // Skip the Buy Signal dataset in the tooltip
                  }
                  return `${tooltipItem.dataset.label}: ${tooltipItem.raw}`;
                },
              },
            },
          },
        }}
      />
    );
  };
  const renderCashNetProfitGraph = (data) => {
    return (
      <div className='graph'>
        <Line
          data={{
            labels: data.year_list, // Assuming all datasets share the same date list
            datasets: [
              {
                label: 'Cash from Operations',
                data: data.cash_from_operation_list,
                borderColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                pointRadius: 0,
                pointHoverRadius: 0,
              },
              {
                label: 'Net Profit',
                data: data.net_profit_list,
                borderColor: 'rgba(255, 206, 86, 1)',
                backgroundColor: 'rgba(255, 206, 86, 0.2)',
                pointRadius: 0,
                pointHoverRadius: 0,
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
      </div>
    );
  };

  const handleRatingChange = (event, key) => {
    // setRatings({ ...ratings, [key]: event.target.value });
    console.log("chart ratings and weightage in handleRatingChange: ", chartRatingAndWeightage)
    const prevWeight = chartRatingAndWeightage[key]['weightage'];
    setChartRatingAndWeightage({
      ...chartRatingAndWeightage,
      [key] : {
        "rating" : event,
        "weightage": prevWeight
      }
    })
    console.log(event, key)
    // console.log('ratings', event, key);
  };

  const handleWeightChange = (value, key) => {
    // setRatings({ ...ratings, [key]: value });
    console.log("chart ratings and weightage in handleWeightChange: ", chartRatingAndWeightage)
    const prevRating = chartRatingAndWeightage[key]['rating'];
    setChartRatingAndWeightage({
      ...chartRatingAndWeightage,
      [key] : {
        "rating" : prevRating,
        "weightage": value
      }
    })
    console.log(value, key)
    // console.log('weight', value, key);
  }


  return (
    <div>
      {company ? (
        <div>
          <h1 className='comapny-heading'>{company.name}</h1>
          {data ? (
            <div>
              <div>
                <h3>Industry :{' '}
                  <span className='industry-name'>{data.industry}</span>
                </h3>
              </div>
              <div>
                <h3>Sector :{' '}
                  <span className='industry-name'>{data.sector}</span>
                </h3>
              </div>
              <div>
                <h3>About</h3>
                <p dangerouslySetInnerHTML={{ __html: data.key_insights.replace(/\n/g, '<br>') }}></p>
              </div>
              <div>
                <h3>Key Performing Indicators and Constraints</h3>
                <span>{getKPI(data.sector)}</span>
              </div>
              <div>
                {renderChart('USD INR', data.usd_inr_price, 'rgba(212, 45, 34, 1)', data.usd_inr_time)}
              </div>
              <div>
                {renderChart('Nifty', data.nifty_price, 'rgba(34, 45, 212, 1)', data.nifty_time)}
              </div>
              <div>
                {renderChart('Dow Jones', data.dow_jones_price, 'rgba(45, 212, 34, 1)', data.dow_jones_time)}
              </div>
              <div>
                {renderChart('India GDP Growth Rate', data.india_gdp_growth_rate_price, 'rgba(212, 34, 45, 1)', data.india_gdp_growth_rate_time)}
              </div>
              <div>
                {renderChart('India GDP', data.india_gdp_price, 'rgba(34, 212, 45, 1)', data.india_gdp_time)}
              </div>
              <div>
                {renderChart('India GDP Per Capita', data.india_gdp_per_capita_price, 'rgba(45, 34, 212, 1)', data.india_gdp_per_capita_time)}
              </div>
              <div>
                {renderChart('India Interest Rate', data.india_interest_rate_price, 'rgba(212, 45, 34, 1)', data.india_interest_rate_time)}
              </div>
              <div>
                {renderChart('India Inflation Rate', data.india_inflation_rate_price, 'rgba(34, 45, 212, 1)', data.india_inflation_rate_time)}
              </div>
              <div>
                {renderChart('India Unemployment Rate', data.india_unemployment_rate_price, 'rgba(45, 212, 34, 1)', data.india_unemployment_rate_time)}
              </div>
              <div>
                {renderChart('India Population', data.india_population_price, 'rgba(212, 34, 45, 1)', data.india_population_time)}
              </div>
              <div>
                {renderChart('India Government Debt', data.india_government_debt_price, 'rgba(34, 212, 45, 1)', data.india_government_debt_time)}
              </div>
              <div className='graph-wrapper'>
                {renderChartWithRating('Revenue', data.sales_list, 'rgba(75, 192, 192, 1)')}
                <span className='graph-explaination'>Revenue is the total amount of money a company earns from its business activities before any expenses or costs are deducted. It is a crucial indicator of a company's financial performance and overall health</span>
              </div>
              <div className='graph-wrapper'>
                {renderChartWithRating('Percent Change in Revenue', data.percent_change_sales, 'rgba(123, 104, 238, 1)', data.year_list.slice(1))}
                <span className='graph-explaination'></span>
              </div>
              <div className='graph-wrapper'>
                {renderChartWithRating('Expenses', data.expenses_list, 'rgba(255, 99, 132, 1)')}
                <span className='graph-explaination'></span>
              </div>
              <div className='graph-wrapper'>
                {renderChartWithRating('Material Cost %', data.material_cost_percent, 'rgba(255, 99, 132, 1)')}
                <span className='graph-explaination'></span>
              </div>
              <div className='graph-wrapper'>
                {renderChartWithRating('Manufacturing Cost %', data.manufacuring_cost_percent, 'rgba(54, 162, 235, 1)')}
                <span className='graph-explaination'></span>
              </div>
              <div className='graph-wrapper'>
                {renderChartWithRating('Gross Expense', data.gross_expense, 'rgba(153, 102, 255, 1)')}
                <span className='graph-explaination'></span>
              </div>
              <div className='graph-wrapper'>
                {renderChartWithRating('Gross Profit', data.gross_profit, 'rgba(153, 134, 255, 1)')}
                <span className='graph-explaination'></span>
              </div>
              <div className='graph-wrapper'>
                {renderChartWithRating('Gross Profit Margin', data.gross_profit_margin, 'rgba(255, 159, 64, 1)')}
                <span className='graph-explaination'></span>
              </div>
              <div className='graph-wrapper'>
                {renderChartWithRating('Operating Profit', data.operating_profit_list, 'rgba(255, 206, 86, 1)')}
                <span className='graph-explaination'>Operating profit, also known as operating income or operating earnings, is a key financial metric that represents the profit a company makes from its core business operations. It is calculated by subtracting operating expenses (such as wages, rent, and raw materials) from gross profit (which is revenue minus the cost of goods sold).</span>
              </div>
              <div className='graph-wrapper'>
                {renderChartWithRating('Operating Profit Margin', data.opm_percent_list, 'rgba(54, 162, 235, 1)')}
                <span className='graph-explaination'>The operating profit margin is a financial ratio that shows the percentage of revenue that remains as operating profit after covering operating expense</span>
              </div>
              <div className='graph-wrapper'>
                {renderChartWithRating('Interest', data.interest_list, 'rgba(153, 102, 255, 1)')}
                <span className='graph-explaination'>Interest is the cost of borrowing money. It is calculated as a percentage of the principal amount borrowed and is typically paid periodically, such as monthly or annually.</span>
              </div>
              <div className='graph-wrapper'>
                {renderChartWithRating('Interest by Revenue', data.interest_by_sales, 'rgba(153, 102, 255, 1)')}
                <span className='graph-explaination'></span>
              </div>
              <div className='graph-wrapper'>
                {renderChartWithRating('Depreciation', data.depreciation_list, 'rgba(255, 159, 64, 1)')}
                <span className='graph-explaination'>Depreciation is an accounting method used to allocate the cost of tangible assets over their useful life. It is a non-cash expense that reduces the value of an asset over time.</span>
              </div>
              <div className='graph-wrapper'>
                {renderChartWithRating('Depreciation by Revenue', data.depreciation_by_sales, 'rgba(255, 159, 64, 1)')}
                <span className='graph-explaination'></span>
              </div>
              <div className='graph-wrapper'>
                {renderChartWithRating('Net Profit', data.net_profit_list, 'rgba(255, 206, 86, 1)')}
                <span className='graph-explaination'>Net profit, also known as net income or net earnings, is the total amount of money a company retains after all expenses, including operating costs, interest, taxes, and any other expenses, have been deducted from total revenue.</span>
              </div>
              <div className='graph-wrapper'>
                {renderChartWithRating('Net Profit by Revenue', data.net_profit_by_sales, 'rgba(255, 99, 132, 1)')}
                <span className='graph-explaination'></span>
              </div>
              {/* total dividint */}
              <div>
                {renderChartWithRating('Total Assets', data.total_assets, 'rgba(54, 162, 235, 1)')}
                <span className='graph-explaination'></span>
              </div>
              <div>
                {renderChartWithRating('Return on Assets', data.return_on_assets, 'rgba(255, 159, 64, 1)')}
                <span className='graph-explaination'>Return on Assets (ROA) is a financial metric that measures how efficiently a company uses its assets to generate profit.</span>
              </div>
              <div>
                {renderChartWithRating('Equity', data.equity, 'rgba(153, 102, 255, 1)')}
                <span className='graph-explaination'></span>
              </div>
              <div>
                {renderChartWithRating('Return on Equity', data.return_on_equity, 'rgba(255, 206, 86, 1)')}
                <span className='graph-explaination'>Return on Equity (ROE) is a financial metric that measures how effectively a company uses shareholders' equity to generate profit.</span>
              </div>
              <div>
                {renderChartWithRating('Cash Equivalents', data.cash_equivalents, 'rgba(255, 206, 86, 1)')}
                <span className='graph-explaination'></span>
              </div>
              <div>
                {renderChartWithRating('Cash Equivalents by Total Assets', data.cash_equivalents_by_total_assets, 'rgba(75, 192, 192, 1)')}
                <span className='graph-explaination'></span>
              </div>
              <div>
                {renderChartWithRating('Trade Receivables', data.trade_receivables, 'rgba(75, 192, 192, 1)')}
                <span className='graph-explaination'>Trade receivables are the amounts owed to a company by its customers for goods or services that have been delivered but not yet paid for. They are considered a type of current asset and are typically recorded on a company's balance sheet as accounts receivable.</span>
              </div>
              <div>
                {renderChartWithRating('Trade Receivables by Total Assets', data.trade_receivables_by_total_assets, 'rgba(54, 162, 235, 1)')}
                <span className='graph-explaination'></span>
              </div>
              <div>
                {renderChartWithRating('Borrowings', data.borrowings, 'rgba(255, 159, 64, 1)')}
                <span className='graph-explaination'></span>
              </div>
              <div>
                {renderChartWithRating('Debt to Equity', data.debt_to_equity, 'rgba(255, 99, 132, 1)')}
                <span className='graph-explaination'>The debt-to-equity (D/E) ratio is a financial metric that shows the proportion of a company's financing that comes from debt compared to equity. It is calculated by dividing a company's total liabilities by its shareholders' equity.</span>
              </div>
              <div>
                {renderChartWithRating('Capex by Income in Percentage', data.capex_list, 'rgba(153, 102, 255, 1)')}
                <span className='graph-explaination'>Capital expenditure (CapEx) represents the funds used by a company to acquire, upgrade, or maintain physical assets such as property, buildings, machinery, equipment, and technology. Unlike operating expenses, which are ongoing costs for running the day-to-day operations of a business, capital expenditures are typically long-term investments that provide benefits over several years.</span>
              </div>
              <div>
                {renderChartWithRating('Cash from Operations', data.cash_from_operation_list, 'rgba(255, 206, 86, 1)')}
                <span className='graph-explaination'>Cash from operations, often referred to as operating cash flow, is a key financial metric that shows the amount of cash a company generates from its core business activities. It is calculated by adjusting net income for changes in working capital and non-cash items such as depreciation and amortization.</span>
              </div>
              <div>
                <h5>Cash from Operations and Net profit</h5>
                {renderCashNetProfitGraph(data)}
              </div>
              <div>
                {renderChartWithRating('Cash from Investing', data.cash_from_investing_list, 'rgba(255, 99, 132, 1)')}
                <span className='graph-explaination'></span>
              </div>
              <div>
                {renderChartWithRating('Promoter Holding', data.promoter_holding, 'rgba(75, 192, 192, 1)', data.promoter_holding_years)}
                <span className='graph-explaination'>Promoter holding refers to the percentage of shares held by the promoters or founders of a company. It is an important indicator of the level of control and ownership that the promoters have over the company.</span>
              </div>
              <div>
                {renderChartWithRating('Cash Conversion Cycle', data.cash_conversion_cycle, 'rgba(255, 99, 132, 1)')}
                <span className='graph-explaination'>The cash conversion cycle is a financial metric that shows the amount of time it takes for a company to convert its investments in inventory and other resources into cash flow from sales. It is calculated by adding the days inventory outstanding (DIO) to the days sales outstanding (DSO) and subtracting the days payable outstanding (DPO). A shorter cash conversion cycle indicates that a company is able to generate cash flow more quickly and efficiently.</span>
              </div>
              <div>
                {renderChartWithRating('ROCE %', data.roce_percent, 'rgba(54, 162, 235, 1)')}
                <span className='graph-explaination'>Return on capital employed (ROCE) is a financial metric that shows the percentage return a company earns on its invested capital. It is calculated by dividing a company's earnings before interest and taxes (EBIT) by its total capital employed. ROCE is a key indicator of a company's profitability and efficiency in using its capital to generate returns for shareholders.</span>
              </div>
              <div>
                {renderChartWithRating('EPS Values', data.eps_values_list, 'rgba(153, 102, 255, 1)', data.eps_date_list)}
                <span className='graph-explaination'>Earnings Per Share (EPS) is a financial metric that measures the portion of a company's profit attributable to each outstanding share of common stock.</span>
              </div>
              <div>
                <h5>PE Ratio</h5>
                {renderChart('PE Ratio', data.pe_list, 'rgba(54, 162, 235, 1)', data.pe_date_list)}
                <span className='graph-explaination'>The price-to-earnings (P/E) ratio is a financial metric that shows the ratio of a company's stock price to its earnings per share (EPS). It is calculated by dividing the current market price of a company's stock by its EPS. The P/E ratio is a key indicator of a company's valuation and is used by investors to determine whether a stock is overvalued, undervalued, or fairly priced.</span>
              </div>
              <div>
                <h5>Combined Chart</h5>
                {renderCombinedChart(data)}
                <span className='graph-explaination'>The 50-day moving average (DMA50) and 200-day moving average (DMA200) are technical indicators that show the average price of a security over a specified period. The DMA50 is calculated by adding up the closing prices of a security over the last 50 days and dividing the sum by 50. The DMA200 is calculated in a similar way but over the last 200 days. These moving averages are used by traders and investors to identify trends and potential buy or sell signals.</span>
                <span className='graph-explaination'>Volume is a key technical indicator that shows the number of shares or contracts traded in a security or market during a given period. It is an important measure of market activity and liquidity and is used by traders and investors to identify trends and potential buy or sell signals.</span>
              </div>
              <div>
                <h3>Market Cap</h3>
                <p>{data.market_cap}</p>
              </div>
              <div class="value-card">
                <p><strong>Number of shares</strong></p>
                <p>{data.number_of_shares}</p>
                <p class="value-card-footer">Created by Verma.</p>
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
                <h5>Anchor Value</h5>
                <p>{data.price_willing_to_pay}</p>
              </div>
              <div>
                <h5>Total Rating Sum: {finalRating.toFixed(2)}</h5>
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

function getKPI(sector){
  const sector_info = {};
  sector_info['Alcoholic Beverages'] = `Determine the performance of alcohol beverage companies by tracking these key performance indicators (KPIs):

1. Sales Revenue Growth Rate
2. Market Share
3. Gross Margin Percentage
4. Operating Expense Ratio
5. Net Profit Margin
6. Return on Investment (ROI)
7. Return on Sales (ROS)
8. Inventory Turnover
9. Days Inventory Outstanding (DIO)
10. Customer Satisfaction Ratings

Key constraints in the alcohol beverage industry include:

1. Regulatory Compliance: Adhering to laws, taxes, and licensing requirements.
2. Market Saturation: Competition and market share limitations.
3. Changing Consumer Preferences: Shifts in taste, health awareness, and sustainability concerns.
4. Supply Chain Disruptions: Raw material availability, logistics, and distribution challenges.
5. Reputation and Brand Image: Maintaining a positive brand image and reputation.
6. Quality Control: Ensuring consistent product quality and safety.
7. Environmental Impact: Reducing waste, emissions, and water usage.
8. Seasonality: Managing fluctuations in demand due to seasonal changes.
9. Distribution Channels: Managing relationships with distributors, retailers, and online platforms.
10. Innovation: Keeping up with trends, new products, and packaging innovations.

These KPIs and constraints help alcohol beverage companies monitor performance, address challenges, and make informed decisions to drive growth and success.`

sector_info['Agro Chemicals'] = `Here are some common KPIs (Key Performance Indicators) and key constraints in the Aerospace and Defense industry:

KPIs:

1. Program Performance:
    - Cost Variance (CV)
    - Schedule Performance Index (SPI)
    - Technical Performance Measurement (TPM)
2. Financial:
    - Revenue Growth Rate
    - Operating Profit Margin
    - Return on Investment (ROI)
3. Quality and Safety:
    - Defect Density
    - Mean Time Between Failures (MTBF)
    - Safety Incident Rate
4. Supply Chain and Manufacturing:
    - Supply Chain Reliability
    - Production Cycle Time
    - First Pass Yield (FPY)
5. Innovation and Technology:
    - Research and Development (R&D) Expense as a Percentage of Sales
    - Intellectual Property (IP) Creation
    - Time-to-Market for New Products

Key Constraints:

1. Regulatory Compliance:
    - ITAR (International Traffic in Arms Regulations)
    - EAR (Export Administration Regulations)
    - Cybersecurity requirements
2. Technological Complexity:
    - Integration of advanced materials and technologies
    - Systems integration and interoperability
3. Supply Chain Risks:
    - Single-source suppliers
    - Global supply chain disruptions
4. Talent Acquisition and Retention:
    - Attracting and retaining skilled engineers and technicians
    - Training and development programs
5. Funding and Budget Uncertainty:
    - Government budget fluctuations
    - Program funding risks
6. Schedule and Cost Pressures:
    - Meeting tight program deadlines
    - Managing cost growth and overruns
7. Cybersecurity Threats:
    - Protecting sensitive information and systems
    - Ensuring network and system security
8. Global Competition:
    - Competition from global players
    - Market share protection

These KPIs and constraints help Aerospace and Defense companies monitor performance, address challenges, and make informed decisions to drive growth, innovation, and success.`

sector_info['Air Transport Service'] = `Here are some common KPIs (Key Performance Indicators) and key constraints in the Air Transport Services industry:

KPIs:

1. Safety and Security:
    - Accident rate
    - Incident rate
    - Security breach rate
2. Operational Performance:
    - On-time performance (OTP)
    - Flight completion rate
    - Aircraft utilization
3. Customer Satisfaction:
    - Passenger satisfaction (e.g., surveys)
    - Baggage handling performance
    - Complaint resolution rate
4. Financial Performance:
    - Revenue growth rate
    - Yield (revenue per passenger)
    - Operating profit margin
5. Capacity and Utilization:
    - Available seat kilometers (ASK)
    - Revenue passenger kilometers (RPK)
    - Load factor

Key Constraints:

1. Regulatory Compliance:
    - Aviation regulations (e.g., FAA, EASA)
    - Security regulations (e.g., TSA, EU-ETS)
2. Safety and Risk Management:
    - Managing safety risks
    - Ensuring compliance with safety protocols
3. Fleet and Capacity Management:
    - Aircraft availability and utilization
    - Managing capacity to meet demand
4. Labor and Training:
    - Pilot and crew availability
    - Training and certification requirements
5. Fuel and Energy Costs:
    - Fuel price volatility
    - Energy efficiency and sustainability
6. Competition and Market Dynamics:
    - Competition from low-cost carriers
    - Changing passenger demand and behavior
7. Infrastructure and Slot Constraints:
    - Airport slot availability
    - Air`

sector_info['Automobile'] = `Here are some common KPIs (Key Performance Indicators) and key constraints in the Automobile industry:

KPIs:

1. Sales and Revenue:
    - Sales volume growth rate
    - Revenue growth rate
    - Market share
2. Quality and Reliability:
    - Defect rate (PPM)
    - Warranty claims rate
    - Customer satisfaction (CSI)
3. Manufacturing and Production:
    - Production volume
    - Capacity utilization
    - Production lead time
4. Supply Chain and Logistics:
    - Supplier performance (delivery, quality, cost)
    - Inventory turns
    - Logistics and transportation costs
5. Innovation and Technology:
    - R&D investment as a percentage of sales
    - Number of new model launches
    - Electrification and autonomous driving progress

Key Constraints:

1. Regulatory Compliance:
    - Emissions regulations (e.g., CAFE, Euro 6)
    - Safety regulations (e.g., airbags, ABS)
2. Global Competition:
    - Competition from established players
    - Emerging market competitors
3. Technological Disruption:
    - Electrification and autonomous driving adoption
    - Connectivity and mobility services
4. Supply Chain Risks:
    - Component shortages (e.g., semiconductors)
    - Supplier insolvency
5. Changing Consumer Preferences:
    - Shift to SUVs and crossovers
    - Demand for electric and hybrid vehicles
6. Environmental Sustainability:
    - Carbon footprint reduction
    - End-of-life vehicle recycling
7. Talent Acquisition and Retention:
    - Attracting and retaining skilled engineers
    - Training and development programs
8. Cybersecurity:
    - Protecting connected vehicles from hacking
    - Ensuring data privacy and security

These KPIs and constraints help Automobile companies monitor performance, address challenges, and make informed decisions to drive growth, innovation, and sustainability.`

sector_info['Auto Ancillaries'] = `Here are some common KPIs (Key Performance Indicators) and key constraints in the Auto Ancillary industry:

KPIs:

1. Sales and Revenue:
    - Sales volume growth rate
    - Revenue growth rate
    - Market share
2. Quality and Reliability:
    - Defect rate (PPM)
    - Warranty claims rate
    - Customer satisfaction (CSI)
3. Manufacturing and Production:
    - Production volume
    - Capacity utilization
    - Production lead time
4. Supply Chain and Logistics:
    - Supplier performance (delivery, quality, cost)
    - Inventory turns
    - Logistics and transportation costs
5. Innovation and Technology:
    - R&D investment as a percentage of sales
    - Number of new product launches
    - Technology adoption rate

Key Constraints:

1. OEM (Original Equipment Manufacturer) Dependence:
    - Dependence on few large customers
    - Negotiating power of OEMs
2. Technological Changes:
    - Electrification and autonomous driving adoption
    - Changes in material and manufacturing technologies
3. Global Competition:
    - Competition from low-cost countries
    - Competition from established players
4. Supply Chain Risks:
    - Component shortages (e.g., semiconductors)
    - Supplier insolvency
5. Regulatory Compliance:
    - Compliance with environmental regulations
    - Compliance with safety regulations
6. Working Capital Management:
    - Managing inventory levels
    - Managing accounts receivable and payable
7. Talent Acquisition and Retention:
    - Attracting and retaining skilled engineers
    - Training and development programs
8. Capacity Utilization:
    - Managing capacity to meet demand
    - Avoiding underutilization or overutilization

These KPIs and constraints help Auto Ancillary companies monitor performance, address challenges, and make informed decisions to drive growth, innovation, and sustainability.`

sector_info['Banks'] = `Here are some common KPIs (Key Performance Indicators) and key constraints in the Banking industry:

KPIs:

1. Financial Performance:
    - Return on Assets (ROA)
    - Return on Equity (ROE)
    - Net Interest Margin (NIM)
2. Asset Quality:
    - Non-Performing Assets (NPA) ratio
    - Provisioning coverage ratio
    - Credit growth rate
3. Operational Efficiency:
    - Cost-to-Income ratio
    - Employee productivity
    - Branch and ATM network optimization
4. Customer Satisfaction:
    - Customer satisfaction surveys
    - Net Promoter Score (NPS)
    - Customer retention rate
5. Risk Management:
    - Capital Adequacy Ratio (CAR)
    - Liquidity coverage ratio
    - Risk-weighted assets (RWA)

Key Constraints:

1. Regulatory Compliance:
    - Basel III and IV requirements
    - Anti-Money Laundering (AML) and Know-Your-Customer (KYC) regulations
    - Data privacy and protection regulations
2. Credit Risk:
    - Managing loan defaults and provisioning
    - Credit concentration risk
3. Market Risk:
    - Interest rate risk
    - Foreign exchange risk
    - Equity market risk
4. Operational Risk:
    - Cybersecurity threats
    - IT system failures
    - Employee fraud and misconduct
5. Competition:
    - Competition from fintech and digital banks
    - Competition from traditional banks
6. Economic Conditions:
    - Economic downturns and recessions
    - Interest rate changes
    - Inflation and deflation
7. Talent Acquisition and Retention:
    - Attracting and retaining skilled employees
    - Training and development programs
8. Technology Adoption:
    - Adopting digital banking technologies
    - Implementing AI and machine learning solutions

These KPIs and constraints help banks monitor performance, address challenges, and make informed decisions to drive growth, profitability, and sustainability.`

sector_info['Bearings'] = `Here are some common KPIs (Key Performance Indicators) and key constraints in the Bearings industry:

KPIs:

1. Quality and Reliability:
    - Defect rate (PPM)
    - Warranty claims rate
    - Mean Time Between Failures (MTBF)
2. Manufacturing and Production:
    - Production volume
    - Capacity utilization
    - Lead time
3. Supply Chain and Logistics:
    - Supplier performance (delivery, quality, cost)
    - Inventory turns
    - Logistics and transportation costs
4. Innovation and Technology:
    - R&D investment as a percentage of sales
    - Number of new product launches
    - Technology adoption rate
5. Customer Satisfaction:
    - Customer satisfaction surveys
    - Net Promoter Score (NPS)
    - Customer retention rate

Key Constraints:

1. Material Costs:
    - Fluctuating steel and raw material prices
    - Sourcing and procurement challenges
2. Technological Advancements:
    - Keeping pace with evolving technologies (e.g., electric vehicles, robotics)
    - Investing in R&D and innovation
3. Global Competition:
    - Competition from low-cost countries
    - Competition from established players
4. Supply Chain Disruptions:
    - Managing risks associated with global sourcing
    - Mitigating the impact of natural disasters and geopolitical events
5. Regulatory Compliance:
    - Compliance with environmental regulations
    - Compliance with safety regulations
6. Capacity Utilization:
    - Managing capacity to meet demand
    - Avoiding underutilization or overutilization
7. Talent Acquisition and Retention:
    - Attracting and retaining skilled engineers and technicians
    - Training and development programs
8. Environmental Sustainability:
    - Reducing energy consumption and carbon footprint
    - Implementing sustainable manufacturing practices

These KPIs and constraints help bearing manufacturers monitor performance, address challenges, and make informed decisions to drive growth, innovation, and sustainability.`

sector_info['Cables'] = `Here are some common KPIs (Key Performance Indicators) and key constraints in the Cables industry:

KPIs:

1. Quality and Reliability:
    - Defect rate (PPM)
    - Warranty claims rate
    - Mean Time Between Failures (MTBF)
2. Manufacturing and Production:
    - Production volume
    - Capacity utilization
    - Lead time
3. Supply Chain and Logistics:
    - Supplier performance (delivery, quality, cost)
    - Inventory turns
    - Logistics and transportation costs
4. Innovation and Technology:
    - R&D investment as a percentage of sales
    - Number of new product launches
    - Technology adoption rate
5. Customer Satisfaction:
    - Customer satisfaction surveys
    - Net Promoter Score (NPS)
    - Customer retention rate

Key Constraints:

1. Raw Material Costs:
    - Fluctuating copper and aluminum prices
    - Sourcing and procurement challenges
2. Technological Advancements:
    - Keeping pace with evolving technologies (e.g., fiber optics, 5G)
    - Investing in R&D and innovation
3. Global Competition:
    - Competition from low-cost countries
    - Competition from established players
4. Regulatory Compliance:
    - Compliance with environmental regulations
    - Compliance with safety regulations (e.g., UL, CE)
5. Capacity Utilization:
    - Managing capacity to meet demand
    - Avoiding underutilization or overutilization
6. Talent Acquisition and Retention:
    - Attracting and retaining skilled engineers and technicians
    - Training and development programs
7. Environmental Sustainability:
    - Reducing energy consumption and carbon footprint
    - Implementing sustainable manufacturing practices
8. Certification and Standards:
    - Compliance with industry standards (e.g., ISO, IEC)
    - Obtaining necessary certifications (e.g., UL, CE)

These KPIs and constraints help cable manufacturers monitor performance, address challenges, and make informed decisions to drive growth, innovation, and sustainability.`

sector_info['Castings, Forgings & Fastners'] = `Here are some common KPIs (Key Performance Indicators) and key constraints in the Casting, Forging, and Casters industry:

KPIs:

1. Quality and Reliability:
    - Defect rate (PPM)
    - Warranty claims rate
    - Mean Time Between Failures (MTBF)
2. Manufacturing and Production:
    - Production volume
    - Capacity utilization
    - Lead time
3. Supply Chain and Logistics:
    - Supplier performance (delivery, quality, cost)
    - Inventory turns
    - Logistics and transportation costs
4. Innovation and Technology:
    - R&D investment as a percentage of sales
    - Number of new product launches
    - Technology adoption rate
5. Customer Satisfaction:
    - Customer satisfaction surveys
    - Net Promoter Score (NPS)
    - Customer retention rate

Key Constraints:

1. Raw Material Costs:
    - Fluctuating metal prices (e.g., steel, aluminum, copper)
    - Sourcing and procurement challenges
2. Technological Advancements:
    - Keeping pace with evolving technologies (e.g., 3D printing, automation)
    - Investing in R&D and innovation
3. Global Competition:
    - Competition from low-cost countries
    - Competition from established players
4. Regulatory Compliance:
    - Compliance with environmental regulations
    - Compliance with safety regulations (e.g., OSHA)
5. Capacity Utilization:
    - Managing capacity to meet demand
    - Avoiding underutilization or overutilization
6. Talent Acquisition and Retention:
    - Attracting and retaining skilled engineers and technicians
    - Training and development programs
7. Environmental Sustainability:
    - Reducing energy consumption and carbon footprint
    - Implementing sustainable manufacturing practices
8. Equipment Maintenance:
    - Maintaining equipment reliability and uptime
    - Managing maintenance costs

Additional KPIs for Casting:

1. Scrap rate
2. Yield rate
3. Casting defect rate

Additional KPIs for Forging:

1. Forging yield rate
2. Material utilization rate
3. Forging defect rate

Additional KPIs for Casters:

1. Caster availability rate
2. Caster utilization rate
3. Caster maintenance cost

These KPIs and constraints help Casting, Forging, and Casters companies monitor performance, address challenges, and make informed decisions to drive growth, innovation, and sustainability.`

sector_info['Capital Goods - Electrical Equipment'] = `Here are some common KPIs (Key Performance Indicators) and key constraints in the Capital Goods Electrical Equipment industry:

KPIs:

1. Order Book and Backlog:
    - Order intake rate
    - Order backlog value
    - Order fulfillment rate
2. Revenue and Profitability:
    - Revenue growth rate
    - Gross margin percentage
    - Operating profit margin
3. Product Quality and Reliability:
    - Defect rate (PPM)
    - Warranty claims rate
    - Mean Time Between Failures (MTBF)
4. Innovation and R&D:
    - R&D investment as a percentage of sales
    - Number of new product launches
    - Patent applications filed
5. Supply Chain and Logistics:
    - Supplier performance (delivery, quality, cost)
    - Inventory turns
    - Logistics and transportation costs

Key Constraints:

1. Technological Advancements:
    - Keeping pace with evolving technologies (e.g., IoT, AI, energy efficiency)
    - Investing in R&D and innovation
2. Global Competition:
    - Competition from established players
    - Competition from low-cost countries
3. Regulatory Compliance:
    - Compliance with safety regulations (e.g., UL, CE)
    - Compliance with environmental regulations (e.g., RoHS, WEEE)
4. Raw Material Costs:
    - Fluctuating material prices (e.g., copper, steel)
    - Sourcing and procurement challenges
5. Talent Acquisition and Retention:
    - Attracting and retaining skilled engineers and technicians
    - Training and development programs
6. Project Execution and Delivery:
    - Managing project timelines and budgets
    - Ensuring quality and reliability in project delivery
7. Customer Satisfaction:
    - Customer satisfaction surveys
    - Net Promoter Score (NPS)
    - Customer retention rate

Additional KPIs for Electrical Equipment:

1. Power factor and efficiency
2. Reliability and uptime
3. Mean Time To Repair (MTTR)
4. Customer acceptance rate

These KPIs and constraints help Capital Goods Electrical Equipment companies monitor performance, address challenges, and make informed decisions to drive growth, innovation, and sustainability.`

sector_info['Capital Goods-Non Electrical Equipment'] = `Here are some common KPIs (Key Performance Indicators) and key constraints in the Capital Goods Non-Electrical Equipment industry:

KPIs:

1. Order Book and Backlog:
    - Order intake rate
    - Order backlog value
    - Order fulfillment rate
2. Revenue and Profitability:
    - Revenue growth rate
    - Gross margin percentage
    - Operating profit margin
3. Product Quality and Reliability:
    - Defect rate (PPM)
    - Warranty claims rate
    - Mean Time Between Failures (MTBF)
4. Innovation and R&D:
    - R&D investment as a percentage of sales
    - Number of new product launches
    - Patent applications filed
5. Supply Chain and Logistics:
    - Supplier performance (delivery, quality, cost)
    - Inventory turns
    - Logistics and transportation costs

Key Constraints:

1. Technological Advancements:
    - Keeping pace with evolving technologies (e.g., automation, robotics)
    - Investing in R&D and innovation
2. Global Competition:
    - Competition from established players
    - Competition from low-cost countries
3. Regulatory Compliance:
    - Compliance with safety regulations (e.g., OSHA)
    - Compliance with environmental regulations (e.g., EPA)
4. Raw Material Costs:
    - Fluctuating material prices (e.g., steel, aluminum)
    - Sourcing and procurement challenges
5. Talent Acquisition and Retention:
    - Attracting and retaining skilled engineers and technicians
    - Training and development programs
6. Project Execution and Delivery:
    - Managing project timelines and budgets
    - Ensuring quality and reliability in project delivery
7. Customer Satisfaction:
    - Customer satisfaction surveys
    - Net Promoter Score (NPS)
    - Customer retention rate

Additional KPIs for Non-Electrical Equipment:

1. Equipment uptime and availability
2. Maintenance cost and schedule adherence
3. Customer acceptance rate
4. Field service response time

Key constraints specific to Non-Electrical Equipment:

1. Managing complex projects with long lead times
2. Ensuring compliance with industry-specific regulations (e.g., API, ASME)
3. Managing supply chain risks for critical components
4. Balancing customization with standardization
5. Managing aftermarket sales and service revenue

These KPIs and constraints help Capital Goods Non-Electrical Equipment companies monitor performance, address challenges, and make informed decisions to drive growth, innovation, and sustainability.`

sector_info['Cement'] = `Here are some common KPIs (Key Performance Indicators) and key constraints in the Cement industry:

KPIs:

1. Production and Capacity:
    - Cement production volume
    - Capacity utilization rate
    - Production cost per ton
2. Quality and Reliability:
    - Defect rate (PPM)
    - Quality control measures (e.g., ISO 9001)
    - Customer satisfaction surveys
3. Energy and Environmental:
    - Energy consumption per ton of cement
    - CO2 emissions per ton of cement
    - Alternative fuel usage rate
4. Supply Chain and Logistics:
    - Supplier performance (delivery, quality, cost)
    - Inventory management (e.g., days inventory outstanding)
    - Logistics and transportation costs
5. Financial Performance:
    - Revenue growth rate
    - Gross margin percentage
    - Operating profit margin

Key Constraints:

1. Energy Costs:
    - High energy costs (e.g., fuel, electricity)
    - Volatility in energy prices
2. Raw Material Costs:
    - Fluctuating raw material prices (e.g., limestone, coal)
    - Sourcing and procurement challenges
3. Environmental Regulations:
    - Compliance with emissions regulations (e.g., NESHAP)
    - Compliance with waste management regulations
4. Global Competition:
    - Competition from established players
    - Competition from low-cost countries
5. Logistics and Transportation:
    - Managing logistics and transportation costs
    - Ensuring timely delivery to customers
6. Technological Advancements:
    - Keeping pace with evolving technologies (e.g., alternative fuels, energy efficiency)
    - Investing in R&D and innovation
7. Talent Acquisition and Retention:
    - Attracting and retaining skilled engineers and technicians
    - Training and development programs

Additional KPIs for Cement:

1. Kiln uptime and availability
2. Grinding capacity utilization
3. Clinker factor (ratio of clinker to cement)
4. Alternative fuel substitution rate

These KPIs and constraints help Cement companies monitor performance, address challenges, and make informed decisions to drive growth, innovation, and sustainability.`

sector_info['Ceramic Products'] = `Here are some common KPIs (Key Performance Indicators) and key constraints in the Ceramic Products industry:

KPIs:

1. Production and Capacity:
    - Production volume
    - Capacity utilization rate
    - Production cost per unit
2. Quality and Reliability:
    - Defect rate (PPM)
    - Quality control measures (e.g., ISO 9001)
    - Customer satisfaction surveys
3. Design and Innovation:
    - Number of new product designs
    - Design-to-market lead time
    - Patent applications filed
4. Supply Chain and Logistics:
    - Supplier performance (delivery, quality, cost)
    - Inventory management (e.g., days inventory outstanding)
    - Logistics and transportation costs
5. Financial Performance:
    - Revenue growth rate
    - Gross margin percentage
    - Operating profit margin

Key Constraints:

1. Raw Material Costs:
    - Fluctuating raw material prices (e.g., clay, silica)
    - Sourcing and procurement challenges
2. Energy Costs:
    - High energy costs (e.g., fuel, electricity)
    - Volatility in energy prices
3. Technological Advancements:
    - Keeping pace with evolving technologies (e.g., 3D printing, automation)
    - Investing in R&D and innovation
4. Global Competition:
    - Competition from established players
    - Competition from low-cost countries
5. Environmental Regulations:
    - Compliance with emissions regulations (e.g., VOCs, particulate matter)
    - Compliance with waste management regulations
6. Talent Acquisition and Retention:
    - Attracting and retaining skilled engineers and technicians
    - Training and development programs
7. Customer Preferences:
    - Changing customer preferences (e.g., sustainability, aesthetics)

Additional KPIs for Ceramic Products:

1. Warpage and shrinkage rates
2. Color consistency and stability
3. Glaze quality and consistency
4. Product durability and lifespan

These KPIs and constraints help Ceramic Products companies monitor performance, address challenges, and make informed decisions to drive growth, innovation, and sustainability.`

sector_info['Chemicals'] = `Here are some common KPIs (Key Performance Indicators) and key constraints in the Chemicals industry:

KPIs:

1. Production and Capacity:
    - Production volume
    - Capacity utilization rate
    - Production cost per unit
2. Quality and Reliability:
    - Defect rate (PPM)
    - Quality control measures (e.g., ISO 9001)
    - Customer satisfaction surveys
3. Safety and Environmental:
    - Lost Time Injury Frequency Rate (LTIFR)
    - Total Recordable Injury Frequency Rate (TRIFR)
    - Environmental incident rate
4. Supply Chain and Logistics:
    - Supplier performance (delivery, quality, cost)
    - Inventory management (e.g., days inventory outstanding)
    - Logistics and transportation costs
5. Financial Performance:
    - Revenue growth rate
    - Gross margin percentage
    - Operating profit margin

Key Constraints:

1. Raw Material Costs:
    - Fluctuating raw material prices (e.g., oil, natural gas)
    - Sourcing and procurement challenges
2. Regulatory Compliance:
    - Compliance with environmental regulations (e.g., REACH, TSCA)
    - Compliance with safety regulations (e.g., OSHA)
3. Technological Advancements:
    - Keeping pace with evolving technologies (e.g., process automation, digitalization)
    - Investing in R&D and innovation
4. Global Competition:
    - Competition from established players
    - Competition from low-cost countries
5. Talent Acquisition and Retention:
    - Attracting and retaining skilled engineers and technicians
    - Training and development programs
6. Supply Chain Disruptions:
    - Managing risks associated with global sourcing
    - Mitigating the impact of natural disasters and geopolitical events
7. Environmental Sustainability:
    - Reducing energy consumption and carbon footprint
    - Implementing sustainable manufacturing practices

Additional KPIs for Chemicals:

1. Yield rates
2. Batch cycle times
3. Product purity and quality
4. Waste reduction and recycling rates

These KPIs and constraints help Chemicals companies monitor performance, address challenges, and make informed decisions to drive growth, innovation, and sustainability.`

sector_info['Cement - Products'] = `Here are some common KPIs (Key Performance Indicators) and key constraints in the Cement Products industry:

KPIs:

1. Production and Capacity:
    - Production volume (tons)
    - Capacity utilization rate (%)
    - Production cost per ton
2. Quality and Reliability:
    - Defect rate (PPM)
    - Quality control measures (e.g., ISO 9001)
    - Customer satisfaction surveys
3. Energy and Environmental:
    - Energy consumption per ton (kWh)
    - CO2 emissions per ton (kg)
    - Alternative fuel usage rate (%)
4. Supply Chain and Logistics:
    - Supplier performance (delivery, quality, cost)
    - Inventory management (e.g., days inventory outstanding)
    - Logistics and transportation costs
5. Financial Performance:
    - Revenue growth rate (%)
    - Gross margin percentage (%)
    - Operating profit margin (%)

Key Constraints:

1. Raw Material Costs:
    - Fluctuating raw material prices (e.g., limestone, coal)
    - Sourcing and procurement challenges
2. Energy Costs:
    - High energy costs (e.g., fuel, electricity)
    - Volatility in energy prices
3. Environmental Regulations:
    - Compliance with emissions regulations (e.g., NESHAP)
    - Compliance with waste management regulations
4. Global Competition:
    - Competition from established players
    - Competition from low-cost countries
5. Logistics and Transportation:
    - Managing logistics and transportation costs
    - Ensuring timely delivery to customers
6. Technological Advancements:
    - Keeping pace with evolving technologies (e.g., alternative fuels, energy efficiency)
    - Investing in R&D and innovation
7. Talent Acquisition and Retention:
    - Attracting and retaining skilled engineers and technicians
    - Training and development programs

Additional KPIs for Cement Products:

1. Kiln uptime and availability (%)
2. Grinding capacity utilization (%)
3. Clinker factor (ratio of clinker to cement)
4. Alternative fuel substitution rate (%)

These KPIs and constraints help Cement Products companies monitor performance, address challenges, and make informed decisions to drive growth, innovation, and sustainability.`

sector_info['Computer Education'] = `Here are some common KPIs (Key Performance Indicators) and key constraints in the Computer Education industry:

KPIs:

1. Student Enrollment and Retention:
    - Number of students enrolled
    - Student retention rate
    - Graduation rate
2. Academic Performance:
    - Student assessment results
    - Course completion rates
    - Certification pass rates
3. Faculty and Staff:
    - Faculty-to-student ratio
    - Faculty qualifications and experience
    - Staff training and development
4. Curriculum and Programs:
    - Program relevance and currency
    - Curriculum alignment with industry needs
    - Program accreditation and certification
5. Infrastructure and Resources:
    - Computer lab and equipment availability
    - Software and technology resources
    - Library and research resources
6. Career Services and Placement:
    - Job placement rates
    - Career counseling and support
    - Alumni network and engagement

Key Constraints:

1. Technological Advancements:
    - Keeping pace with rapidly changing technology
    - Upgrading curriculum and infrastructure to match industry demands
2. Competition:
    - Competition from other educational institutions
    - Competition from online and MOOC (Massive Open Online Course) providers
3. Funding and Resources:
    - Limited budget and resources
    - Dependence on government funding or grants
4. Faculty Recruitment and Retention:
    - Attracting and retaining qualified faculty
    - Faculty burnout and turnover
5. Student Engagement and Motivation:
    - Keeping students engaged and motivated
    - Addressing student needs and concerns
6. Accreditation and Compliance:
    - Maintaining accreditation and certification
    - Compliance with regulatory requirements

Additional KPIs for Computer Education:

1. Student satisfaction surveys
2. Employer satisfaction surveys
3. Alumni success and achievement
4. Research and publication output
5. Industry partnerships and collaborations

These KPIs and constraints help Computer Education institutions monitor performance, address challenges, and make informed decisions to drive growth, innovation, and student success.`

sector_info['Construction'] = `Here are some common KPIs (Key Performance Indicators) and key constraints in the Construction industry:

KPIs:

1. Project Performance:
    - Project completion rate
    - Project timeline performance
    - Project budget performance
2. Safety:
    - Lost Time Injury Frequency Rate (LTIFR)
    - Total Recordable Injury Frequency Rate (TRIFR)
    - Safety audit scores
3. Quality:
    - Defect rate
    - Quality control measures
    - Customer satisfaction surveys
4. Productivity:
    - Labor productivity
    - Equipment utilization
    - Material waste reduction
5. Financial Performance:
    - Revenue growth rate
    - Gross margin percentage
    - Operating profit margin
6. Customer Satisfaction:
    - Customer satisfaction surveys
    - Net Promoter Score (NPS)
    - Customer retention rate

Key Constraints:

1. Project Delays:
    - Weather-related delays
    - Design changes
    - Permitting and approval delays
2. Cost Overruns:
    - Material price fluctuations
    - Labor cost increases
    - Design changes
3. Safety Risks:
    - Workplace accidents
    - Regulatory non-compliance
    - Safety culture
4. Quality Issues:
    - Defective materials
    - Workmanship errors
    - Design flaws
5. Labor Shortages:
    - Skilled labor availability
    - Labor turnover
    - Training and development
6. Environmental Factors:
    - Weather conditions
    - Natural disasters
    - Environmental regulations

Additional KPIs for Construction:

1. Schedule Performance Index (SPI)
2. Cost Performance Index (CPI)
3. Earned Value Management (EVM)
4. Building Information Modeling (BIM) adoption
5. Sustainability and energy efficiency metrics

These KPIs and constraints help Construction companies monitor performance, address challenges, and make informed decisions to drive growth, innovation, and project success.`

sector_info['Consumer Durables'] = `Here are some common KPIs (Key Performance Indicators) and key constraints in the Consumer Durables industry:

KPIs:

1. Sales and Growth:
    - Sales growth rate
    - Market share
    - Sales by distribution channel
2. Quality and Customer Satisfaction:
    - Defect rate
    - Customer satisfaction surveys
    - Net Promoter Score (NPS)
3. Operational Efficiency:
    - Production cycle time
    - Cost per unit
    - Material usage efficiency
4. Inventory and Logistics Management:
    - Inventory level
    - Inventory turnover
    - Shipping and handling cost
5. Financial Performance:
    - Gross margin
    - Operating margin
    - Return on Investment (ROI)

Key Constraints:

1. Market Demand Changes:
    - Changes in consumer preferences
    - Global economic changes
2. Pricing Pressure:
    - Price competition
    - Retailer pressure to reduce prices
3. Production Costs:
    - Increases in material costs
    - Increases in labor costs
4. Quality and Consistency:
    - Maintaining quality and consistency in production
    - Reducing defect rate
5. Innovation and Technology:
    - Keeping up with latest technologies and trends
    - Investing in R&D
6. Sustainability and Social Responsibility:
    - Reducing environmental impact
    - Improving social responsibility practices

Additional KPIs for Consumer Durables:

1. Customer retention rate
2. Customer lifetime value
3. Customer acquisition cost
4. Complaint response rate
5. Employee satisfaction level

These KPIs and constraints help Consumer Durables companies monitor performance, address challenges, and make informed decisions to drive growth, innovation, and customer satisfaction.`

sector_info['Credit Rating Agencies'] = `Here are some common KPIs (Key Performance Indicators) and key constraints in the Credit Rating Agency industry:

KPIs:

1. Rating Accuracy:
    - Accuracy of credit ratings
    - Consistency of ratings across industries and regions
2. Market Share:
    - Market share of rated issuers
    - Market share of rated instruments
3. Revenue Growth:
    - Revenue growth rate
    - Diversification of revenue streams
4. Customer Satisfaction:
    - Customer satisfaction surveys
    - Net Promoter Score (NPS)
5. Regulatory Compliance:
    - Compliance with regulatory requirements
    - Timeliness of regulatory filings

Key Constraints:

1. Regulatory Scrutiny:
    - Increasing regulatory requirements
    - Regulatory oversight and examinations
2. Competition:
    - Competition from other credit rating agencies
    - Competition from alternative credit assessment providers
3. Data Quality:
    - Availability and quality of data for rating purposes
    - Data security and protection
4. Methodology and Model Risk:
    - Complexity of rating methodologies and models
    - Risk of model errors or biases
5. Reputation and Trust:
    - Maintaining reputation and trust among investors and issuers
    - Managing conflicts of interest
6. Technological Advancements:
    - Keeping pace with technological advancements in data analytics and artificial intelligence
    - Investing in technology infrastructure and talent

Additional KPIs for Credit Rating Agencies:

1. Rating stability
2. Rating transition rates
3. Default rates
4. Customer retention rate
5. Employee expertise and training

These KPIs and constraints help Credit Rating Agencies monitor performance, address challenges, and make informed decisions to drive growth, innovation, and trust in the credit markets.`

sector_info['Crude Oil & Natural Gas'] = `Here are some common KPIs (Key Performance Indicators) and key constraints in the Crude Oil and Natural Gas industry:

KPIs:

1. Production and Reserves:
    - Daily production rate
    - Total proved reserves
    - Reserve replacement ratio
2. Operational Efficiency:
    - Production costs per barrel/unit
    - Operating expenses as a percentage of revenue
    - Uptime and availability of equipment
3. Safety and Environmental:
    - Lost Time Injury Frequency Rate (LTIFR)
    - Total Recordable Injury Frequency Rate (TRIFR)
    - Greenhouse gas emissions intensity
4. Financial Performance:
    - Revenue growth rate
    - Net income margin
    - Return on Capital Employed (ROCE)
5. Exploration and Development:
    - Exploration success rate
    - Development well delivery rate
    - Finding and Development (F&D) costs

Key Constraints:

1. Price Volatility:
    - Fluctuations in global oil and gas prices
    - Impact of price changes on revenue and profitability
2. Regulatory Environment:
    - Changing regulatory requirements
    - Compliance with environmental and safety regulations
3. Operational Risks:
    - Well blowouts and accidents
    - Equipment failures and downtime
4. Reserve Replacement:
    - Replacing depleted reserves with new discoveries
    - Maintaining reserve life index
5. Environmental and Social Concerns:
    - Managing environmental impact
    - Addressing social concerns and community engagement
6. Technological Advancements:
    - Keeping pace with technological innovations
    - Investing in digitalization and automation

Additional KPIs for Crude Oil and Natural Gas:

1. Water usage and management
2. Methane emissions intensity
3. Drilling and completion costs
4. Production forecasting accuracy
5. Supply chain optimization

These KPIs and constraints help Crude Oil and Natural Gas companies monitor performance, address challenges, and make informed decisions to drive growth, efficiency, and sustainability.`

sector_info['Diamond, Gems and Jewellery'] = `Here are some common KPIs (Key Performance Indicators) and key constraints in the Diamond Gems and Jewelry industry:

KPIs:

1. Sales and Revenue:
    - Sales growth rate
    - Average transaction value
    - Revenue per square foot (for retail)
2. Product Quality and Authenticity:
    - Quality control metrics (e.g., 4Cs)
    - Authentication and certification rates
    - Return and exchange rates
3. Customer Satisfaction:
    - Customer satisfaction surveys
    - Net Promoter Score (NPS)
    - Customer retention rate
4. Operational Efficiency:
    - Inventory turnover
    - Supply chain lead times
    - Labor productivity
5. Marketing and Branding:
    - Brand awareness metrics (e.g., social media engagement)
    - Marketing return on investment (ROI)
    - Customer acquisition cost

Key Constraints:

1. Supply Chain Disruptions:
    - Diamond and gemstone sourcing challenges
    - Supply chain transparency and traceability
2. Market Fluctuations:
    - Diamond and gemstone price volatility
    - Currency fluctuations
3. Competition:
    - Intense competition in the market
    - Competition from lab-grown diamonds and alternative gemstones
4. Regulatory Compliance:
    - Compliance with industry regulations (e.g., Kimberley Process)
    - Compliance with consumer protection regulations
5. Consumer Preferences:
    - Shifting consumer preferences (e.g., sustainability, ethics)
    - Changing consumer behavior (e.g., online shopping)

Additional KPIs for Diamond Gems and Jewelry:

1. Diamond grading and certification accuracy
2. Jewelry design and manufacturing efficiency
3. Store display and visual merchandising effectiveness
4. Employee knowledge and sales training
5. Customer loyalty program effectiveness

These KPIs and constraints help Diamond Gems and Jewelry companies monitor performance, address challenges, and make informed decisions to drive growth, quality, and customer satisfaction.`

sector_info['Diversified'] = `Here are some common KPIs (Key Performance Indicators) and key constraints for a diversified company (a company with multiple business segments or industries):

KPIs:

1. Financial Performance:
    - Revenue growth rate
    - Profit margin
    - Return on Investment (ROI)
    - Debt-to-Equity ratio
2. Segment Performance:
    - Revenue growth rate by segment
    - Profit margin by segment
    - Return on Investment (ROI) by segment
3. Operational Efficiency:
    - Operating expense ratio
    - Asset utilization
    - Supply chain efficiency
4. Innovation and R&D:
    - R&D expenditure as a percentage of revenue
    - Number of patents filed
    - Innovation pipeline
5. Customer Satisfaction:
    - Customer satisfaction surveys
    - Net Promoter Score (NPS)
    - Customer retention rate

Key Constraints:

1. Complexity Management:
    - Managing multiple business segments and industries
    - Coordinating across different functions and geographies
2. Resource Allocation:
    - Allocating resources (capital, talent, etc.) across segments
    - Prioritizing investments and initiatives
3. Risk Management:
    - Managing risks across different segments and industries
    - Identifying and mitigating potential risks
4. Talent Management:
    - Attracting and retaining top talent across segments
    - Developing leadership and skills
5. Integration and Synergies:
    - Integrating acquisitions and new businesses
    - Realizing synergies across segments and functions

Additional KPIs for a diversified company:

1. Segment diversification metrics (e.g., Herfindahl-Hirschman Index)
2. Cross-selling and upselling metrics
3. Shared services efficiency metrics
4. Corporate social responsibility (CSR) metrics
5. Employee engagement and satisfaction metrics

These KPIs and constraints help diversified companies monitor performance, address challenges, and make informed decisions to drive growth, innovation, and profitability across multiple business segments and industries.`

sector_info['Dry cells'] = `Dry cells`

sector_info['E-Commerce/App based Aggregator'] = `E-Commerce/App based Aggregator`

sector_info['Edible Oil'] = `Edible Oil`

sector_info['Education'] = `Education`

sector_info['Electronics'] = `Electronics`

sector_info['Engineering'] = `Engineering`

sector_info['Entertainment'] = `Entertainment`

sector_info['ETF'] = `ETF`

sector_info['Ferro Alloys'] = `Ferro Alloys`

sector_info['Fertilizers'] = `Fertilizers`

sector_info['Finance'] = `Finance`

sector_info['Financial Services'] = `Financial Services`

sector_info['FMCG'] = `FMCG`

sector_info['Gas Distribution'] = `Gas Distribution`

sector_info['Glass & Glass Products'] = `Glass & Glass Products`

sector_info['Healthcare'] = `Healthcare`

sector_info['Hotels & Restaurants'] = `Hotels & Restaurants`

sector_info['Infrastructure Developers & Operators'] = `Infrastructure Developers & Operators`

sector_info['Infrastructure Investment Trusts'] = `Infrastructure Investment Trusts`

sector_info['Insurance'] = `Insurance`

sector_info['IT - Hardware'] = `IT - Hardware`

sector_info['IT - Software'] = `IT - Software`

sector_info['Leather'] = `Leather`

sector_info['Logistics'] = `Logistics`

sector_info['Marine Port & Services'] = `Marine Port & Services`

sector_info['Media - Print/Television/Radio'] = `Media - Print/Television/Radio`

sector_info['Mining & Mineral products'] = `Mining & Mineral products`

sector_info['Miscellaneous'] = `Miscellaneous`

sector_info['Non Ferrous Metals'] = `Non Ferrous Metals`

sector_info['Oil Drill/Allied'] = `Oil Drill/Allied`

sector_info['Online Media'] = `Online Media`

sector_info['Packaging'] = `Packaging`

sector_info['Paints/Varnish'] = `Paints/Varnish`

sector_info['Paper'] = `Paper`

sector_info['Petrochemicals'] = `Petrochemicals`

sector_info['Pharmaceuticals'] = `Pharmaceuticals`

sector_info['Plantation & Plantation Products'] = `Plantation & Plantation Products`

sector_info['Plastic products'] = `Plastic products`

sector_info['Plywood Boards/Laminates'] = `Plywood Boards/Laminates`

sector_info['Power Generation & Distribution'] = `Power Generation & Distribution`

sector_info['Power Infrastructure'] = `Power Infrastructure`

sector_info['Printing & Stationery'] = `Printing & Stationery`

sector_info['Quick Service Restaurant'] = `Quick Service Restaurant`

sector_info['Railways'] = `Railways`

sector_info['Readymade Garments/ Apparells'] = `Readymade Garments/ Apparells`

sector_info['Real Estate Investment Trusts'] = `Real Estate Investment Trusts`

sector_info['Realty'] = `Realty`

sector_info['Refineries'] = `Refineries`

sector_info['Refractories'] = `Refractories`

sector_info['Retail'] = `Retail`

sector_info['Sanitaryware'] = `Sanitaryware`

sector_info['Ship Building'] = `Ship Building`

sector_info['Shipping'] = `Shipping`

sector_info['Steel'] = `Steel`

sector_info['Stock/ Commodity Brokers'] = `Stock/ Commodity Brokers`

sector_info['Sugar'] = `Sugar`

sector_info['Telecom-Handsets/Mobile'] = `Telecom-Handsets/Mobile`

sector_info['Telecomm Equipment & Infra Services'] = `Telecomm Equipment & Infra Services`

sector_info['Telecomm-Service'] = `Telecomm-Service`

sector_info['Textiles'] = `Here are some common KPIs (Key Performance Indicators) and key constraints in the Textile industry:

KPIs:

1. Production and Quality:
    - Production capacity utilization
    - Defect rate
    - Quality control metrics (e.g., fabric strength, colorfastness)
2. Sales and Revenue:
    - Sales volume
    - Revenue growth rate
    - Market share
3. Supply Chain and Logistics:
    - Inventory turnover
    - Supply chain lead times
    - On-time delivery rate
4. Cost and Efficiency:
    - Cost per unit
    - Labor productivity
    - Energy and water consumption
5. Innovation and Sustainability:
    - R&D expenditure as a percentage of revenue
    - Number of new product launches
    - Sustainability metrics (e.g., recycled materials, waste reduction)

Key Constraints:

1. Raw Material Costs:
    - Fluctuations in cotton, polyester, and other raw material prices
    - Sourcing and procurement challenges
2. Competition:
    - Intense competition from low-cost countries
    - Competition from alternative materials (e.g., synthetic fibers)
3. Regulatory Compliance:
    - Compliance with textile regulations (e.g., REACH, CPSIA)
    - Compliance with labor and environmental regulations
4. Technological Advancements:
    - Keeping pace with technological innovations (e.g., digital printing, automation)
    - Investing in R&D and new equipment
5. Sustainability and Social Responsibility:
    - Managing environmental impact (e.g., water, energy, waste)
    - Ensuring social responsibility (e.g., labor practices, fair trade)

Additional KPIs for Textiles:

1. Fabric quality metrics (e.g., softness, durability)
2. Color consistency and accuracy metrics
3. Lead time and cycle time metrics
4. Inventory levels and turnover metrics
5. Employee training and development metrics

These KPIs and constraints help Textile companies monitor performance, address challenges, and make informed decisions to drive growth, innovation, and sustainability.`

sector_info['Tobacco Products'] = `Here are some common KPIs (Key Performance Indicators) and key constraints in the Tobacco Products industry:

KPIs:

1. Sales and Revenue:
    - Sales volume
    - Revenue growth rate
    - Market share
2. Product Quality and Innovation:
    - Product quality metrics (e.g., taste, texture)
    - New product launch success rate
    - Innovation pipeline
3. Manufacturing and Supply Chain:
    - Production capacity utilization
    - Supply chain lead times
    - Inventory turnover
4. Regulatory Compliance:
    - Compliance with tobacco regulations
    - Compliance with tax and duty requirements
    - Reporting and disclosure requirements
5. Customer Satisfaction:
    - Customer satisfaction surveys
    - Net Promoter Score (NPS)
    - Customer retention rate

Key Constraints:

1. Regulatory Environment:
    - Increasing regulations and restrictions
    - Compliance with changing regulations
2. Declining Demand:
    - Declining tobacco consumption
    - Increasing competition from alternative products
3. Illicit Trade:
    - Counterfeit and contraband products
    - Loss of revenue due to illicit trade
4. Reputation and Social Responsibility:
    - Managing reputation and social responsibility
    - Addressing health and environmental concerns
5. Innovation and Differentiation:
    - Differentiating products in a declining market
    - Investing in innovation and R&D

Additional KPIs for Tobacco Products:

1. Nicotine content and delivery metrics
2. Tar and carbon monoxide reduction metrics
3. Product waste and recycling metrics
4. Employee training and development metrics
5. Community engagement and CSR metrics

These KPIs and constraints help Tobacco Products companies monitor performance, address challenges, and make informed decisions to drive growth, innovation, and sustainability`

sector_info['Trading'] = `Here are some common KPIs (Key Performance Indicators) and key constraints in Trading:

KPIs:

1. Profitability:
    - Net profit
    - Gross profit margin
    - Return on investment (ROI)
2. Trading Performance:
    - Win/loss ratio
    - Profit factor
    - Maximum drawdown
3. Risk Management:
    - Value-at-Risk (VaR)
    - Expected Shortfall (ES)
    - Risk-reward ratio
4. Market Impact:
    - Market share
    - Order book visibility
    - Slippage and market impact costs
5. Operational Efficiency:
    - Trade execution speed
    - Trade settlement efficiency
    - IT system uptime and reliability

Key Constraints:

1. Market Volatility:
    - Managing risk in volatile markets
    - Adapting to changing market conditions
2. Regulatory Compliance:
    - Compliance with trading regulations
    - Reporting and disclosure requirements
3. Competition:
    - Competition from other traders and market makers
    - Competition for market share and liquidity
4. Technology and Infrastructure:
    - Maintaining reliable and efficient trading systems
    - Upgrading technology to stay competitive
5. Talent and Expertise:
    - Attracting and retaining skilled traders and analysts
    - Developing and maintaining expertise in trading strategies and markets

Additional KPIs for Trading:

1. Sharpe ratio
2. Sortino ratio
3. Calmar ratio
4. Trading frequency and volume
5. Customer satisfaction and retention

Key constraints to consider:

1. Liquidity constraints
2. Counterparty risk
3. Market data and analytics quality
4. IT system security and reliability
5. Talent acquisition and retention

These KPIs and constraints help Trading firms monitor performance, address challenges, and make informed decisions to drive profitability, growth, and competitiveness.`

sector_info['Tyres'] = `Here are some common KPIs (Key Performance Indicators) and key constraints in the Tyre industry:

KPIs:

1. Sales and Revenue:
    - Sales volume
    - Revenue growth rate
    - Market share
2. Production and Quality:
    - Production capacity utilization
    - Defect rate
    - Quality control metrics (e.g., ISO 9001)
3. Supply Chain and Logistics:
    - Inventory turnover
    - Supply chain lead times
    - On-time delivery rate
4. Research and Development:
    - R&D expenditure as a percentage of revenue
    - Number of new product launches
    - Patent filings
5. Customer Satisfaction:
    - Customer satisfaction surveys
    - Net Promoter Score (NPS)
    - Warranty claims rate

Key Constraints:

1. Raw Material Costs:
    - Fluctuations in rubber and other raw material prices
    - Sourcing and procurement challenges
2. Competition:
    - Intense competition from established players
    - Competition from low-cost countries
3. Regulatory Compliance:
    - Compliance with safety and environmental regulations
    - Compliance with labeling and testing requirements
4. Technological Advancements:
    - Keeping pace with technological innovations (e.g., electric vehicles, autonomous driving)
    - Investing in R&D and new product development
5. Distribution and Retail:
    - Managing relationships with distributors and retailers
    - Ensuring product availability and visibility

Additional KPIs for Tyres:

1. Tyre mileage and durability metrics
2. Fuel efficiency and rolling resistance metrics
3. Noise reduction and vibration metrics
4. Recycling and sustainability metrics
5. Employee training and development metrics

These KPIs and constraints help Tyre companies monitor performance, address challenges, and make informed decisions to drive growth, innovation, and customer satisfaction.`
  return sector_info[sector];
}

export default Report;