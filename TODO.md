- `update_kwh` cleaning
    - Database migration: Clear Meter.lastcommit
    - Database migration: Clear Notifier table from database
    - Database migration: Clear Notifier security entries from database
    - Database migration: Remove Meter `last_commit` from database
    - Database migration: Remove Meter `uri` from database
    - Remove production model
    - Clear Mongo production collection
    + Remove or relocate provider deprecated clases


+ Aggregator + Mongotimecurve. Update handling duplicates
- Aggregator + Mongotimecurve. Proper management of gaps
- Aggregator. Improve management of last update. Use previous last update if no specific date interval specified
- Mongotimecurve. Improve implementation of lastFullDate. Current implementation: If there's a single point consider it filled
- Mongotimecurve. Improve implementation of firstFullDate. If there's a single point consider it filled
- GenerationkwhProductionAggregator. Simplify aggregator initialization

## DONE

