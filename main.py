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
    return Client(eth_address=eth_address, password=password, staging=False)

def start_date() -> datetime.datetime:
    range = click.prompt(
        "Please specify report time range",
        type=click.STRING,
        default="day"
    )
    start = datetime.datetime.now() - datetime.timedelta(days=1)
    if range == "week":
       start = datetime.datetime.now() - datetime.timedelta(weeks=1)
    elif range == "all time":
        start = None
    print(f"START TIME {start}")
    return start

def generate_report():
    c = get_client()
    c.login()
    analyses = c.analysis_list(date_from=start_date())
    for analysis in analyses:
        if analysis.status is not finished:
            click.echo(f"Cannot generate report for analysis {analysis.uuid}; analysis status: {analysis.status}\n")
            continue 
        resp = c.report(analysis.uuid)
        file_to_issue = defaultdict(list)
        for issue in resp.issues:
            source_locs = [loc.source_map.split(":") for loc in issue.locations]
            source_locs = [(int(o), int(l), int(i)) for o, l, i in source_locs]
            for _, _, file_idx in source_locs:
                filename = resp.source_list[file_idx]
                file_to_issue[filename].append(
                    (issue.swc_title, issue.severity, issue.description_short)
                )
        for filename, data in file_to_issue.items():
            click.echo(f"Report for **{filename}** | UUID: {analysis.uuid}\n")
            click.echo(
                tabulate(
                    data,
                    tablefmt="rst",
                    headers=(
                        "SWC Title",
                        "Severity",
                        "Short Description",
                    ),
                )
            )
            click.echo("\n")

generate_report()