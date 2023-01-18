# plantmeter 
[![CI](https://github.com/Som-Energia/plantmeter/actions/workflows/main.yml/badge.svg)](https://github.com/Som-Energia/plantmeter/actions/workflows/main.yml)
[![Coverage Status](https://coveralls.io/repos/github/Som-Energia/plantmeter/badge.svg?branch=master)](https://coveralls.io/github/Som-Energia/plantmeter?branch=master)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/plantmeter)](https://pypi.org/project/plantmeter)

OpenERP module and library to manage multisite energy generation

## To be extinguished package

Most of the content of this packages is in progress of being
moved to somenergia-generationkwh o generic packages like
somenergia-utils.

Further development should consider continuing this transition.

## Install and test

```bash
pip install -e .
pytest plantmeter # Run unit tests
pytest som_plantmeter/tests # Run erp tests (require a working local erp)
```

Some erp tests clean up collections on the mongo database the erp points to,
which could be a disaster if your dbconfig is pointing to a production setup.
So, those tests are disabled by default.
In order to enable clean room test in erp tests:

- Ensure your dbconfig.py configuration is pointing to a testing database
- Run `enable_destructive_tests.py` from somenergia-utils
- This enables an erp config flag, that makes destrutive testing not to be skipped.
- If, later, you accidentally change dbconfig to point a production setup, and run those tests they won't actually be run

## Code Map

Refer to somenergia-generationkwh documentation on tips on how
the code is structured.

## How to release

- Update the version in README changelogs
- Update the version in setup.py
- Commit "Bump to plantmeter-M.m.p"
- git tag plantmeter-M.m.p
- git push && git push --tags
- The later push will generate the source package in pypi for the non-erp module


## CHANGES

### plantmeter 1.7.5 2023-01-18

- Add filter capabilities to MongoTimeCurve.get()

### plantmeter 1.7.4 2022-01-08

_"Keeping up with Python 2.7" Release_

- Github actions for CI
- Moved isodates to somutils
- Python 2.7 compatibility: added conditional dependencies

### plantmeter 1.7.3 2019-07-29

_Py3 portability back_

- MTC: mongo's bjson do not accept numpy types as attributes,
  so we are taking the native item when updating with numpy arrays.

### plantmeter 1.7.2 2019-07-18

_Not importing anymore release_

- Removing logic for importing metering since now is done by Gisce:
    - Removed `Meter.last_commit` related to the meter importing logic
    - Removed `GenerationkwhProductionNotifier` and related helpers
    - `update_kwh` methods removed
    - Removed all (metering) providers
    - Removed `GenerationkwhProductionAggregator.getNShares()`
- `genkwh_production` script renamed as `genkwh_plants`
- `genkwh_production curve` extracted as `genkwh_mtc`
- `genkwh_mtc`: collections alias renamed:
    - `gisce` -> `production`
    - `production` -> `production_old`
- `genkwh_mtc`: New collection `rightscorrection`
- Plants have `first/last_active_date`
- Meters have `first/last_active_date`
- New `Aggregator.firstActiveDate()` returning the min of the plant's `first_active_date`
- Functional tests moved to `som_plantmeter/tests`
- FIX: Fontivsolar meter number was wrong
- New migration script to perform the former fix and rewrite the rights


### plantmeter 1.7.1 2019-04-04

- Removed deprecated scripts `genkwh_pull_status` and `genkwh_export`
- Removed deprecated `genkwh_production` subcommands: pull-status, load-meassures and update-kwh
- Script `genkwh_production.py` installed by setup.py

### plantmeter 1.7.0 2019-04-02

- Meters and plants have `first_active_date` attribute
- Built plant shares is not a constant curve anymore, changes when adding new plants
- Meter `first_active_date` filters out earlier meassures
- Fix: lastMesurement in a mix/plant is the first one of lastMeasurement of the childs
- `genkwh_migrate_1_6_3_newplant.sh`: Script to migrate old plant and incorporate the new one
- In general, fixes to really enable multiple plants
- `genkwh_production.py`: editmix, editplant, editmeter
- `genkwh_production.py`: editmix, editplant, editmeter
- `genkwh_production.py`: delmix, delplant, delmeter
- `genkwh_production.py`: meterset -> editmeter


### plantmeter 1.6.2 2019-01-21

- Deprecated `genkwh_pull_status.py` and `genkwh_pull_status.sh`
- `genkwh_production.py`: added `pull_status` as subcommand
- `genkwh_production.py pull_status`: nicer output and exit status
- `genkwh_migration_ftp_to_tmprofile.py` migration script

### plantmeter 1.6.1 2019-01-03

- Show erp configuration at the begining of every command
- Protect `genkwh_production.py clear` againts lossy fingers

### plantmeter 1.6.0 2019-01-03

- Python 3 supported (python module, not yet the erp code)
- Migrated to pymongo 3
- MongoTimeCurve takes some field names as parameters (_timestamp_ and _creation_)
- Abstracted ResourceParent from ProductionPlant and ProductionAggregator
- `genkwh_production.py list`: list all the resorce hierarchy (mixes, plants, meters)
- `genkwh_production.py addmix`: to add an aggregator, now 'mix'
- `genkwh_production.py addplant`: to add a plant
- `genkwh_production.py addmeter`: to add a meter
- `genkwh_production.py curve`: to extract stored curves as TSV (production, rights...)
- `genkwh_production.py` commmand documentation






