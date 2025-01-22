import argparse
import csv
import datetime
import os
import sys
import time
import uuid

import grpc
import requests
from tabulate import tabulate

GML_API_KEY = ""
GML_DEVICE_ID = ""

QUERIES = [
    "Who is the CEO of Salesforce?",
    "What are the First Quarter Fiscal 2025 Results?",
    "Can you tell me about Spiff?",
    "What were the earnings in 2024?",
    "When is the Annual Stockholders Meeting in 2024?",
]


def run_query(query):
    url = "https://localhost:60002/v1/chat/completions"
    params = {"deviceID": GML_DEVICE_ID}
    headers = {"Authorization": f"Bearer {GML_API_KEY}"}
    data = {"messages": [{"role": "user", "content": query}]}

    start = time.perf_counter()
    response = requests.post(
        url, headers=headers, json=data, params=params, verify=False
    )
    duration = time.perf_counter() - start

    print(f"query took {round(duration, 2)}")
    if response.status_code != 200:
        raise Exception("status code is " + str(response.status_code))


def repeat_query(query, num_times):
    print(f"running query '{query}'")
    for _ in range(num_times):
        run_query(query)


def run_query_and_mark_times(query, num_times):
    start_time = time.time_ns()
    repeat_query(query, num_times)
    end_time = time.time_ns()
    return start_time, end_time


def run_queries_and_mark_times(model, device):
    results = []
    for query in QUERIES:
        start_time, end_time = run_query_and_mark_times(query, 10)
        time.sleep(180)
        results.append(
            {
                "model": model,
                "device": device,
                "start_time": start_time,
                "end_time": end_time,
                "query": query,
            }
        )

    filename = str(uuid.uuid4()) + ".csv"

    with open(filename, "w") as output_file:
        dict_writer = csv.DictWriter(output_file, results[0].keys())
        dict_writer.writeheader()
        dict_writer.writerows(results)

    print(f"Wrote results to {filename}")


parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str)
parser.add_argument("--device", type=str)
args = parser.parse_args()

run_queries_and_mark_times(args.model, args.device)
