- `update_kwh` cleaning
    - Clear Meter.lastcommit from database
    - Clear Notifier table from database
    - Clear Notifier security from database
    - Clear Mongo production


- Aggregator + Mongotimecurve. Update handling duplicates
- Aggregator + Mongotimecurve. Proper management of gaps
- Aggregator. Improve management of last update. Use previous last update if no specific date interval specified
- Mongotimecurve. Improve implementation of lastFullDate. Current implementation: If there's a single point consider it filled
- Mongotimecurve. Improve implementation of firstFullDate. If there's a single point consider it filled
- GenerationkwhProductionAggregator. Simplify aggregator initialization

## DONE

