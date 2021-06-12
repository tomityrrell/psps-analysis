- Inputs
    - PSPS Report Processing, Duration of events:  Dec 2020 - Jan 2021
        - 2 months of data
        - 3 events
    - CIMIS Weather Station Data
        - 200 Weather Stations
        - 13 readings from the weather station:  wind, humidity, temp, etc.
        - Total records:  230k, 1 hour each
- Outputs
    - How can it be used?
        - Ex. Next 5 days, low fire risk at weather stations x,y,z with prob %
        - Forecasting Humidity, Wind
        - Predicting "crossings", extreme values, negative correlations of humidity and wind
    - What metrics do we have?
- Methods
    1. Preprocessing
        - Document reading/table extraction for PSPS data
        - During PSPS event, extreme wind/humidity values were observed

    2. Processing
        - Get weather station data from APIs (CIMIS, MesoWest, etc.)
        - Join/match data sources based on time

    3. Prediction
        - Built a prediction model to anticipate extreme wind/humidity
        
    4. Model Building
        - Technical details of inputs, wind distribution, simplicity of predicting humidity, temp
        - Technology, Software, Algorithms:  Gluon-ts
        - How is the model built?  Layers, Tuning
        - Performance, Accuracy:  Time to train per config, metrics
        - Potential pitfalls, challenges, failures
        
    5. Future Enhancements
        - Train model on morning data only
        - Domain knowledge, constraints on humidity, wind
        - Data feed morning/evening.  How to handle new data?
        - Input from metereology to improve/tune models

    6. Results
        - Temp, Humid, Wind Prediction Accuracy
        - Relationship between wind/humidity, wind brings humidity down, increasing fire risk
        - 3-day and 7-day forecast (how long do PSPS events last for?  what granularity do we need?)
            - 4, 6-hour intervals, find chance of PSPS events in each interval
            - Distill data/predictions into clear visualizations
        
    7. Reuseability
        - Demand Forecasting
        - Use cases:  Energy and Utilities, Load shedding