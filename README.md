### MythX report generator

Builds a rst report of your MythX analyses.

Supports custom date ranges: 'MM/DD/YYYY'

Supported time ranges: [day, week]

Setup:
```bash
virtualenv -p python3 mythxreport
pip install -r requirement.txt
# Replace the values with your MythX credentials (do not use the trial account!)
export PYTHX_USERNAME="0x0000000000000000000000000000000000000000"
export PYTHX_PASSWORD="trial"
```

Generate a report
```bash
python main.py range week # generate report of analyses ran in the past week
python main.py custom startdate enddate # date format 'MM/DD/YYYY'
# report is generated in local folder as report_<date_from> to <date_to>.rst
```

Built upon PythX.