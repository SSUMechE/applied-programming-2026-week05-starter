"""Provided controlled comparisons; runs before any student TODO is completed."""
import argparse

from ap_week05 import Path, supplied_case, sample_path, path_metrics, constraint_margins


def measurements(case, path, method="interpolated", resolution_m=0.5):
    samples = sample_path(path, resolution_m=resolution_m, method=method)
    metrics = path_metrics(path, samples, case["obstacle"])
    return metrics, len(samples)


def margins_and_decision(metrics, max_length_m=9.0):
    margins = constraint_margins(
        metrics["length_m"], metrics["clearance_m"],
        min_clearance_m=0.5, max_length_m=max_length_m,
    )
    feasible = all(value >= 0.0 for value in margins.values())
    return margins, feasible


def show_table(headers, rows):
    cells = [
        [f"{value:.6f}" if isinstance(value, float) else str(value) for value in row]
        for row in rows
    ]
    widths = [
        max(len(header), *(len(row[index]) for row in cells))
        for index, header in enumerate(headers)
    ]
    print(" ".join(header.ljust(width) for header, width in zip(headers, widths)).rstrip())
    for row in cells:
        print(" ".join(value.ljust(width) for value, width in zip(row, widths)).rstrip())


def main():
    parser = argparse.ArgumentParser(
        description="Compare one changed input while keeping the others fixed.",
    )
    parser.add_argument(
        "mode", choices=("metrics", "method", "resolution", "limits", "paths"),
    )
    mode = parser.parse_args().mode
    case = supplied_case()
    detour = case["path"]
    direct = Path([case["start"], case["goal"]])

    if mode == "metrics":
        metrics, count = measurements(case, detour)
        for name, value in metrics.items():
            print(f"{name}: {value:.6f}")
        print(f"sample_count: {count}")

    elif mode == "method":
        print("path=direct; resolution_m=0.500000")
        rows = []
        for method in ("waypoints", "interpolated"):
            metrics, count = measurements(case, direct, method=method)
            rows.append((method, count, metrics["length_m"], metrics["clearance_m"]))
        show_table(("method", "sample_count", "length_m", "clearance_m"), rows)

    elif mode == "resolution":
        print("path=direct; method=interpolated")
        rows = []
        for resolution in (1.0, 0.5):
            metrics, count = measurements(case, direct, resolution_m=resolution)
            rows.append((resolution, count, metrics["length_m"], metrics["clearance_m"]))
        show_table(("resolution_m", "sample_count", "length_m", "clearance_m"), rows)

    elif mode == "limits":
        print("path=detour; method=interpolated; resolution_m=0.500000")
        print("min_clearance_m=0.500000")
        metrics, _ = measurements(case, detour)
        rows = []
        for maximum in (9.0, 8.0, 7.0):
            margins, feasible = margins_and_decision(metrics, max_length_m=maximum)
            rows.append((
                maximum, metrics["length_m"], metrics["clearance_m"],
                margins["length_margin_m"], feasible,
            ))
        show_table(
            ("max_length_m", "length_m", "clearance_m", "length_margin_m", "feasible"),
            rows,
        )

    else:  # paths
        print("method=interpolated; resolution_m=0.500000")
        print("min_clearance_m=0.500000; max_length_m=9.000000")
        rows = []
        for name, path in (("direct", direct), ("detour", detour)):
            metrics, _ = measurements(case, path)
            margins, feasible = margins_and_decision(metrics)
            rows.append((
                name, metrics["length_m"], metrics["clearance_m"],
                margins["clearance_margin_m"], margins["length_margin_m"], feasible,
            ))
        show_table(
            ("path", "length_m", "clearance_m", "clearance_margin_m",
             "length_margin_m", "feasible"),
            rows,
        )


if __name__ == "__main__":
    main()
