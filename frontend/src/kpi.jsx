// Total sectors ['Aerospace & Defence', 'Agro Chemicals', 'Air Transport Service', 'Alcoholic Beverages', 'Auto Ancillaries', 'Automobile', 'Banks', 'Bearings', 'Cables', 'Capital Goods - Electrical Equipment', 'Capital Goods-Non Electrical Equipment', 'Castings, Forgings & Fastners', 'Cement', 'Cement - Products', 'Ceramic Products', 'Chemicals', 'Computer Education', 'Construction', 'Consumer Durables', 'Credit Rating Agencies', 'Crude Oil & Natural Gas', 'Diamond, Gems and Jewellery', 'Diversified', 'Dry cells', 'E-Commerce/App based Aggregator', 'Edible Oil', 'Education', 'Electronics', 'Engineering', 'Entertainment', 'ETF', 'Ferro Alloys', 'Fertilizers', 'Finance', 'Financial Services', 'FMCG', 'Gas Distribution', 'Glass & Glass Products', 'Healthcare', 'Hotels & Restaurants', 'Infrastructure Developers & Operators', 'Infrastructure Investment Trusts', 'Insurance', 'IT - Hardware', 'IT - Software', 'Leather', 'Logistics', 'Marine Port & Services', 'Media - Print/Television/Radio', 'Mining & Mineral products', 'Miscellaneous', 'Non Ferrous Metals', 'Oil Drill/Allied', 'Online Media', 'Packaging', 'Paints/Varnish', 'Paper', 'Petrochemicals', 'Pharmaceuticals', 'Plantation & Plantation Products', 'Plastic products', 'Plywood Boards/Laminates', 'Power Generation & Distribution', 'Power Infrastructure', 'Printing & Stationery', 'Quick Service Restaurant', 'Railways', 'Readymade Garments/ Apparells', 'Real Estate Investment Trusts', 'Realty', 'Refineries', 'Refractories', 'Retail', 'Sanitaryware', 'Ship Building', 'Shipping', 'Steel', 'Stock/ Commodity Brokers', 'Sugar', 'Telecom-Handsets/Mobile', 'Telecomm Equipment & Infra Services', 'Telecomm-Service', 'Textiles', 'Tobacco Products', 'Trading', 'Tyres']

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
  

  sector_info['Aerospace & Defence'] = `Here are some common KPIs (Key Performance Indicators) and key constraints in the Aerospace and Defense industry:
  
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
  
  sector_info['Agro Chemicals'] = 'Agro Chemicals'
    
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
  

export default getKPI;