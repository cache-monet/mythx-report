import click
import datetime
import pythx.models
from collections import defaultdict
from os import environ, path
from pythx import Client
from pythx.models import response as respmodels
from tabulate import tabulate

finished = respmodels.AnalysisStatus.FINISHED

def get_client() -> Client:
    eth_address = environ.get("PYTHX_USERNAME") or click.prompt(
        "Please enter your Ethereum address",
        type=click.STRING,
        default="0x0000000000000000000000000000000000000000",
    )
    password = environ.get("PYTHX_PASSWORD") or click.prompt(
        "Please enter your MythX password",
        type=click.STRING,
        hide_input=True,
        default="trial",
    )
    c = Client(eth_address=eth_address, password=password, staging=False)
    c.login()
    return c

def generate_report(date_from: datetime = None, date_to: datetime = None):
    c = get_client()
    detectedIssues = failed_analyses = 0
    if date_from is not None:
        date_from = date_from.date()
        report_range = f"{date_from} to "
        report_range += "present" if date_to is None else f"{date_to.date()}"
    else: report_range = "All time"
    analyses = c.analysis_list(date_from=date_from, date_to=date_to)

    # Report title
    # click.echo("=========================================")
    click.echo(f"Analyses report: {report_range}")
    click.echo("=========================================")

    for analysis in analyses:
        if analysis.status is not finished:
            click.echo(f"*Cannot generate report for analysis {analysis.uuid}; analysis status: {analysis.status}*\n")
            failed_analyses += 1
            continue 
        resp = c.report(analysis.uuid)
        file_to_issue = defaultdict(list)
        formatted_date = analysis.submitted_at.strftime("%m/%d/%Y, %H:%M")
        for issue in resp.issues:
            source_locs = [loc.source_map.split(":") for loc in issue.locations]
            source_locs = [(int(o), int(l), int(i)) for o, l, i in source_locs]
            for _, _, file_idx in source_locs:
                filename = resp.source_list[file_idx]
                file_to_issue[filename].append(
                    (issue.swc_id, issue.swc_title, issue.severity, issue.description_short, formatted_date)
                )
        detectedIssues += len(resp.issues)
        for filename, data in file_to_issue.items():
            click.echo(f"Report for **{filename}** | UUID: {analysis.uuid}\n")
            click.echo(
                tabulate(
                    data,
                    tablefmt="rst",
                    headers=(
                        "SWC ID",
                        "SWC Title",
                        "Severity",
                        "Short Description",
                        "Time Submitted",
                    ),
                )
            )
            click.echo("\n")
    click.echo("Summary:")
    click.echo("--------")
    click.echo(f"Total analyses: {analyses.total}; Detected issues: {detectedIssues}; Failed analyses: {failed_analyses}")

@click.group()
def main():
    """
    Simple CLI for generating analysis reports
    """
    pass

@main.command(help="Get a report for analyses ran in the past: ['day', 'week', 'all time'].")
@click.argument("date_range")
def range(date_range: str):
    current = datetime.datetime.now()
    start =  current - datetime.timedelta(days=1)
    if date_range == "week":
       start = current - datetime.timedelta(weeks=1)
    elif date_range == "all time":
        start = None
    generate_report(date_from=start)

@main.command(help="Set custom report date range. Date format: 'MM/DD/YYYY'")
@click.argument("date_from")
@click.argument("date_to")
def custom(date_from, date_to):
    m, d, y = date_from.split('/')
    datefrom = datetime.datetime(int(y), int(m), int(d))
    m, d, y = date_to.split('/')
    dateto = datetime.datetime(int(y), int(m), int(d))
    generate_report(datefrom, dateto)
    return

if __name__ == "__main__":
    main()
