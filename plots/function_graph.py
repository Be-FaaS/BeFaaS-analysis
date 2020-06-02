#!/usr/bin/env python3
"""
Plot a graph representation of the logs.
"""
from typing import List
import pathlib
from collections import defaultdict, Counter

from argmagic import argmagic
import numpy as np

import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout, to_agraph
import pygraphviz as pgv

import faastermetrics as fm
import faastermetrics.helper as fg
from faastermetrics.requestgroup import create_requestgroups


def get_duration(perfs):
    try:
        measure, = filter(lambda e: e.perf["entryType"] == "measure", perfs)
        duration = measure.perf["duration"]
    except ValueError:
        duration = None
    return duration


def get_rpc_in_duration(rgroups):
    """Calculate request times based on rpcIn."""
    all_durations = defaultdict(list)
    for rgroup in rgroups:
        # find outgoing calls
        rpc_in = rgroup.get_rpc_in()
        duration = get_duration(rpc_in)
        if duration is not None:
            all_durations[rgroup.function].append(duration)
    return all_durations


def reduce_dict(data, fun):
    return {k: fun(v) for k, v in data.items()}


def get_rpc_in_median(rgroups):
    durations = get_rpc_in_duration(rgroups)
    return reduce_dict(durations, np.median)


def get_num_calls(rgroups):
    return Counter([rgroup.function for rgroup in rgroups])


def get_rpc_out_duration(rgroups):
    """Calculate durations based on rpcOut."""
    times = defaultdict(list)
    for rgroup in rgroups:
        # iterate over outer duration measurements
        rpc_out = [e for e in rgroup.get_rpc_out() if e.perf["entryType"] == "measure"]
        for entry in rpc_out:
            called_fname = entry.perf["mark"].split(":")[-1]
            outer_duration = entry.perf["duration"]

            times[(rgroup.function, called_fname)].append(outer_duration)

    return times


def get_transport_times(rgroups):
    times = defaultdict(list)
    for rgroup in rgroups:
        # iterate over outer duration measurements
        rpc_out = [e for e in rgroup.get_rpc_out() if e.perf["entryType"] == "measure"]
        for entry in rpc_out:
            called_fname = entry.perf["mark"].split(":")[-1]
            calleds = [
                rg for rg in rgroups
                if rg.context_id == entry.context_id and rg.function == called_fname
            ]
            inner_durations = get_rpc_in_median(calleds)
            if not inner_durations:
                continue
            inner_duration = inner_durations[called_fname]
            outer_duration = entry.perf["duration"]

            times[(rgroup.function, called_fname)].append((outer_duration - inner_duration) / 2)

    return times


def get_rpc_out_median(rgroups):
    outer = get_rpc_out_duration(rgroups)
    return reduce_dict(outer, np.median)


def get_transport_median(rgroups):
    transport = get_transport_times(rgroups)
    return reduce_dict(transport, np.median)


def format_node_labels(graph):
    durations = nx.get_node_attributes(graph, "duration")
    calls = nx.get_node_attributes(graph, "calls")

    labels = {}
    for fname in calls:
        fcalls = calls.get(fname, 0)
        fduration = durations.get(fname, None)
        if fduration is None:
            label = f"{fname}\n({fcalls} calls)"
        else:
            label = f"{fname}\n({fcalls} calls, {fduration:.2f}ms)"
        labels[fname] = label

    return labels


def format_edge_labels(graph):
    outer = nx.get_edge_attributes(graph, "outer_median")
    trans = nx.get_edge_attributes(graph, "transport")

    labels = {}
    for edge in graph.edges:
        e_outer = outer.get(edge, None)
        e_trans = trans.get(edge, None)

        # TODO: fix negative values
        # labels[edge] = f"Total: {e_outer:.2f}ms\nTransport: {e_trans:.2f}ms"
        labels[edge] = f"Total: {e_outer:.2f}ms"

    return labels


def build_graph(rgroups):
    graph = nx.DiGraph()

    # add nodes
    graph.add_nodes_from([rg.function for rg in rgroups])
    graph.add_edges_from([
        (rg.function, rout.perf["mark"].split(":")[-1])
        for rg in rgroups for rout in rg.get_rpc_out()
    ])

    nx.set_node_attributes(graph, get_rpc_in_median(rgroups), "duration")
    nx.set_node_attributes(graph, get_num_calls(rgroups), "calls")
    nx.set_node_attributes(graph, format_node_labels(graph), "label")

    nx.set_edge_attributes(graph, get_rpc_out_median(rgroups), "outer_median")
    nx.set_edge_attributes(graph, get_transport_median(rgroups), "transport")
    nx.set_edge_attributes(graph, format_edge_labels(graph), "label")

    return graph


def set_graph_weight(graph, key, dest_key="weight"):
    max_val = np.max(list(nx.get_edge_attributes(graph, key).values()))
    for edge in graph.edges:
        graph.edges[edge][dest_key] = max_val + 1 - graph.edges[edge][key]


def plot_graph(graph, plotdir, key="median_outer"):
    A = to_agraph(graph)
    A.layout("dot")
    A.draw(str(plotdir / f"gviz_fgraph_{key}.png"))


def analyze_tree(data: List[fm.LogEntry], plotdir: pathlib.Path):
    """Build the call graph from the given logging data.
    """
    rgroups = create_requestgroups(data)
    graph = build_graph(rgroups)

    plot_graph(graph, plotdir, key="median_outer")


def main(data: pathlib.Path, output: pathlib.Path):
    output = output / data.stem
    output.mkdir(parents=True, exist_ok=True)

    data = fm.load_logs(data)
    analyze_tree(data, output)


if __name__ == "__main__":
    argmagic(main, positional=("data", "output"))
