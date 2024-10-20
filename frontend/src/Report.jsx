import React, { useEffect, useState, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { ClipLoader } from 'react-spinners';
import { Line } from 'react-chartjs-2';
import { Rating as StarRating } from 'react-simple-star-rating';
import Rating from 'react-rating';
import getKPI from './kpi.jsx';
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
  RadialLinearScale, 
  RadarController,   
  Filler,
  registerables,
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
  Legend,
  RadialLinearScale,  
  RadarController,
  Filler,
  ...registerables,
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
          const response = await fetch(`http://localhost:8000/api/analysis?company=${company.url}`);
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
    const pointRadius = label_list.length > 50 ? 0 : 3;
    const extendLabelGraphList = ['Revenue', 'Expenses', 'Gross Expense', 'Gross Profit', 'Operating Profit',
      'Net Profit', 'Total Assets', 'Equity', 'Cash Equivalents', 'Trade Receivables', 'Borrowings',
      'Cash from Operations', 'Cash from Investing', 'EPS Values'];
    const cagrGraphList = ['India GDP', 'India GDP Per Capita', 'India Population', 'Nifty 50',
        'USD INR', 'Dow Jones', 'Revenue', 'Expenses', 'Gross Expense', 'Gross Profit', 'Operating Profit',
        'Interest', 'Depreciation', 'Net Profit', 'Total Assets', 'Equity', 'Cash Equivalents', 'Trade Receivables',
        'Borrowings', 'Cash from Operations', 'Cash from Investing', 'EPS Values'];

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
        const predictions = generatePredictions(plot_data, 3);
        const extendedLabels = generateExtendedLabels(label_list);
        const extendedData = [...plot_data, ...predictions];
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
    const extractYear = (label) => {
      const dateFormat1 = /^\d{4}-\d{2}-\d{2}$/; // Matches 'YYYY-MM-DD'
      const dateFormat2 = /^[A-Za-z]{3} \d{4}$/; // Matches 'MMM YYYY'
    
      if (dateFormat1.test(label)) {
        return new Date(label).getFullYear();
      } else if (dateFormat2.test(label)) {
        return new Date(label).getFullYear();
      } else {
        console.log(label)
        throw new Error('Invalid date format');
      }
    };
    
    const cagrPlugin = {
      id: 'cagrPlugin',
      beforeDraw: (chart) => {
        if (cagrGraphList.includes(chart.config.data.datasets[0].label)) {
          if (chart.config.data.datasets.length === 1 || (chart.config.data.datasets.length > 1 && chart.config.data.datasets[1].label.includes('Prediction'))) {
            const { ctx, chartArea: { top, left } } = chart;
            const xPos = left + 100;
            const yPos = top + 30;
            ctx.save();
            ctx.fillStyle = 'rgba(0, 0, 0, 1)';
            ctx.textAlign = 'center';
            ctx.font = 'bolder 20px Arial';
            // console.log(chart)
            const data = chart.config.data.datasets[0].data
            const labels = chart.config.data.labels
            // console.log('fff', data, labels)
            const startValue = data[0];
            const endValue = data[data.length - 1];
            const startYear = extractYear(labels[0]);
            const endYear = extractYear(labels[labels.length - 1]);
            const numberOfYears = endYear - startYear;
            const cagr = ((endValue / startValue) ** (1 / numberOfYears) - 1) * 100;

            ctx.fillText(`YoY: ${cagr.toFixed(2)}%`, xPos, yPos);
            ctx.restore();
          }
        }
      }
    };
    ChartJS.register(cagrPlugin);
    const returnComponent = (
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
                        cagrPlugin // Register the CAGR plugin here
                    },
                }}
            />
        </div>
    );
    return returnComponent;
};

  const CircleIcon = ({ fill = 'none', stroke = 'black', strokeWidth = 2 }) => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill={fill} xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="10" stroke={stroke} strokeWidth={strokeWidth} />
    </svg>
  );

  const renderChartWithRating = (label, plot_data, color, label_list = data.year_list) => {
    if (plot_data == undefined) return;
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

  const RadarChartComponent = ({ chartRatingAndWeightage }) => {
    const canvasRef = useRef(null);
    const chartInstanceRef = useRef(null);  // Ref to store chart instance
  
    const showPolarRadarChart = (chartRatingAndWeightage) => {
      const ctx = canvasRef.current.getContext('2d');
  
      
      const radarLabels = ['operatingprofitmargin','netprofitbyrevenue','returnonassets','returnonequity','debttoequity','capexbyincomeinpercentage',]
      const radarValues = []
      for (const [key, value] of Object.entries(chartRatingAndWeightage)) {
        if (radarLabels.includes(key)) {
          radarValues.push(value['rating'])
        }
      }
      
      
        
      // Destroy the previous chart instance if it exists
      if (chartInstanceRef.current) {
        chartInstanceRef.current.destroy();
      }
  
           // Create new chart instance
      chartInstanceRef.current = new ChartJS(ctx, {
        type: 'radar',
        data: {
          labels: radarLabels,
          datasets: [{
            label: 'Rating & Weightage',
            data: radarValues,
            fill: true,
            backgroundColor: 'rgba(75, 192, 192, 0.2)', // Light green color
            borderColor: 'rgba(75, 192, 192, 1)', // Light green border color
            borderWidth: 1,
          }]
        },
        options: {
          scales: {
            r: {
              angleLines: {
                display: false
              },
              suggestedMin: 0,
              suggestedMax: 10,
            }
          }
        }
      });
    };
  
    useEffect(() => {
      showPolarRadarChart(chartRatingAndWeightage);
  
      // Cleanup function to destroy the chart when the component unmounts
      return () => {
        if (chartInstanceRef.current) {
          chartInstanceRef.current.destroy();
        }
      };
    }, [chartRatingAndWeightage]);
  
    return (
      <div>
        <canvas className='polar-radar-canva' ref={canvasRef}></canvas>
      </div>
    );
  };

  const color_strings = ['rgba(212, 45, 34, 1)','rgba(34, 45, 212, 1)','rgba(45, 212, 34, 1)','rgba(212, 34, 45, 1)','rgba(34, 212, 45, 1)','rgba(45, 34, 212, 1)',]
  
  const transformName = (name) => {
    return name
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
      ;
  };
  const renderEconomicLandscapeGraphs = (data) => {
    return (
      <div>
        <h3>Economic Landscape</h3>
        <div>
          {data.economic_landscape_graph_names.map((name, i) => {
            return (
              <div key={name}>
                {renderChart(transformName(name), data[name+'_price'], color_strings[i%5], data[name+'_time'])}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

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
                <p dangerouslySetInnerHTML={{ __html: getKPI(data.sector).replace(/\n/g, '<br>') }}></p>
              </div>
              {renderEconomicLandscapeGraphs(data)}
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
                {renderChartWithRating('EPS Values', data.eps, 'rgba(153, 102, 255, 1)')}
                <span className='graph-explaination'>Earnings Per Share (EPS) is a financial metric that measures the portion of a company's profit attributable to each outstanding share of common stock.</span>
              </div>
              <div>
                <h5>PE Ratio</h5>
                {renderChart('PE Ratio', data.pe_list, 'rgba(54, 162, 235, 1)', data.pe_date_list)}
                <span className='graph-explaination'>The price-to-earnings (P/E) ratio is a financial metric that shows the ratio of a company's stock price to its earnings per share (EPS). It is calculated by dividing the current market price of a company's stock by its EPS. The P/E ratio is a key indicator of a company's valuation and is used by investors to determine whether a stock is overvalued, undervalued, or fairly priced.</span>
              </div>
              <div className='polar-radar'>
              <RadarChartComponent chartRatingAndWeightage={{...chartRatingAndWeightage}} />
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
                <h5>EPS CAGR</h5>
                <p>{data.eps_cagr}</p>
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


export default Report;