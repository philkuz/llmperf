import argparse
import csv
import os
import sys
import time
import uuid
from datetime import datetime, timezone

import grpc
import requests
from pb2 import metrics_pb2, metrics_pb2_grpc
from tabulate import tabulate

GML_API_KEY = ""
GML_SERVER_ADDRESS = ""


def get_single_query_value(query, start, stop, range):
    # Create SSL credentials using default trusted certificates
    credentials = grpc.ssl_channel_credentials()
    channel = grpc.secure_channel(GML_SERVER_ADDRESS, credentials)

    stub = metrics_pb2_grpc.MetricsReaderServiceStub(channel)

    metadata = [("x-api-key", GML_API_KEY)]

    request = metrics_pb2.RangeQueryRequest(
        query=query, start=start, stop=stop, step=range
    )
    response = stub.RangeQuery(request, metadata=metadata)

    return response.results[0].metric_sample.values[0]


def get_multi_query_value(query, start, stop, range):
    # Create SSL credentials using default trusted certificates
    credentials = grpc.ssl_channel_credentials()
    channel = grpc.secure_channel(GML_SERVER_ADDRESS, credentials)

    stub = metrics_pb2_grpc.MetricsReaderServiceStub(channel)

    metadata = [("x-api-key", GML_API_KEY)]
    request = metrics_pb2.RangeQueryRequest(
        query=query, start=start, stop=stop, step=range
    )
    response = stub.RangeQuery(request, metadata=metadata)

    try:
        return response.results[0].metric_sample.values
    except:
        print("uh oh", query, response)


# Use a start time of -45s, +45s
# This is a bursty workload so we need to ensure we are catching the metrics at the right moment when the queries are run.
# We need to add a bit of padding to the time ranges because there is some buffer in when the metrics actually show up in VM.
def run_pipeline_queries(filters, start_time_ns, stop_time_ns):
    PIPELINE_QUERIES = {
        "number_of_queries": f"sum(increase(gml_gem_pipe_latency_seconds_count{{{filters}}}))",
        "time_to_first_token": f"sum(increase(gml_gem_pipe_gentokens_time_to_first_hist_sum{{{filters}}}))/sum(increase(gml_gem_pipe_gentokens_time_to_first_hist_count{{{filters}}}))",
        "time_to_full_response": f"sum(rate(gml_gem_pipe_latency_seconds_sum{{{filters}}})) / sum(rate(gml_gem_pipe_latency_seconds_count{{{filters}}}))",
        "input_size_tokens": f"sum(increase(gml_gem_pipe_gentokens_input_hist_sum{{{filters}}}))/sum(increase(gml_gem_pipe_gentokens_input_hist_count{{{filters}}}))",
        "output_size_tokens": f"sum(increase(gml_gem_pipe_gentokens_output_hist_sum{{{filters}}}))/sum(increase(gml_gem_pipe_gentokens_output_hist_count{{{filters}}}))",
    }

    end_time_s = stop_time_ns / 1e9 + 45
    range_ms = (stop_time_ns - start_time_ns) / 1e6 + 90 * 1e3

    # Due to how VM does lookback, we start with the endtime and make the end of the query
    # range only 1 second greater. this allows us to get a single result back over [start,end].
    start = datetime.fromtimestamp(end_time_s, tz=timezone.utc).isoformat()
    stop = datetime.fromtimestamp(end_time_s + 1, tz=timezone.utc).isoformat()
    range = f"{int(range_ms)}ms"

    res = {}
    for query_name, query in PIPELINE_QUERIES.items():
        res["pipeline_" + query_name] = get_single_query_value(
            query, start, stop, range
        )

    return res


# Use a start time of +0s, +30s and a range of 5s.
# This is a bursty workload so we need to ensure we are catching the metrics at the right moment when the queries are run.
# We need to add a bit of padding to the time ranges because there is some buffer in when the metrics actually show up in VM.
# Get the max value over the timeframe because the system is idle before and after.
def run_system_queries(filters, start_time_ns, stop_time_ns):
    SYSTEM_QUERIES = {
        "num_cores": f"avg(gml_system_cpu_virtual{{{filters}}}) by (device_id)",
        "cpu_utilization": f"(sum(rate(gml_system_cpu_seconds_total{{state!='idle', {filters}}})) by (device_id)) / (avg(gml_system_cpu_virtual{{{filters}}}) by (device_id))",
        "cpu_used_cores": f"sum(rate(gml_system_cpu_seconds_total{{state!='idle', {filters}}})) by (device_id)",
        "gem_cpu_utilization": f"(sum(rate(gml_gem_cpu_seconds_total{{thread_group_leader='true', {filters}}})) by (device_id)) / (avg(gml_system_cpu_virtual{{{filters}}}) by (device_id))",
        "gem_cpu_used_cores": f"sum(rate(gml_gem_cpu_seconds_total{{thread_group_leader='true', {filters}}})) by (device_id)",
        "memory_usage": f"sum(avg_over_time(gml_system_memory_total_bytes{{{filters}}})) - sum(avg_over_time(gml_system_memory_free_bytes{{{filters}}})) - sum(avg_over_time(gml_system_memory_cached_bytes{{{filters}}})) - sum(avg_over_time(gml_system_memory_buffered_bytes{{{filters}}})) by (device_id)",
        "gem_memory_usage": f"sum(avg by (tgid, device_id) (gml_gem_memory_usage_bytes{{{filters}}})) by (device_id)",
        "system_gpu_utilization": f"(sum(rate(gml_system_gpu_seconds_total{{{filters}}})) by (device_id)) / count(gml_system_gpu_seconds_total{{gpu_id=~'.*', {filters}}}) by (device_id)",
        "system_gem_gpu_utilization": f"(sum(rate(gml_gem_gpu_seconds_total{{{filters}}})) by (device_id)) / count(gml_gem_gpu_seconds_total{{gpu_id=~'.*', {filters}}}) by (device_id)",
    }

    start_time_s = start_time_ns / 1e9
    end_time_s = stop_time_ns / 1e9 + 30
    start = datetime.fromtimestamp(start_time_s, tz=timezone.utc).isoformat()
    stop = datetime.fromtimestamp(end_time_s, tz=timezone.utc).isoformat()
    range = "5s"

    res = {}
    for query_name, query in SYSTEM_QUERIES.items():
        res["system_" + query_name] = max(
            get_multi_query_value(query, start, stop, range)
        )

    return res


def compute_metrics(in_directory, out_filepath, device_id):
    rows = []
    for filename in os.listdir(in_directory):
        in_filepath = os.path.join(in_directory, filename)
        with open(in_filepath, "r") as file:
            csv_reader = csv.DictReader(file)
            filters = f'device_id="{device_id}"'
            for row in csv_reader:
                start_time_ns = int(row["start_time"])
                end_time_ns = int(row["end_time"])
                pipeline_metrics = run_pipeline_queries(
                    filters, start_time_ns, end_time_ns
                )
                system_metrics = run_system_queries(filters, start_time_ns, end_time_ns)
                row["device_id"] = device_id
                out_row = row | pipeline_metrics | system_metrics
                rows.append(out_row)

    with open(out_filepath, "w") as file:
        csv_writer = csv.DictWriter(file, rows[0].keys())
        csv_writer.writeheader()
        csv_writer.writerows(rows)


parser = argparse.ArgumentParser()
parser.add_argument(
    "--input",
    type=str,
    help="input path to the directory containing CSV files to be parsed",
)
parser.add_argument(
    "--output",
    type=str,
    help="output path to the destination file to write to (does not append)",
)
parser.add_argument("--device_id", type=str, help="device ID for the queries")
args = parser.parse_args()

compute_metrics(args.input, args.output, args.device_id)
