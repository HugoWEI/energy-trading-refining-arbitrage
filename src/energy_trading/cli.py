"""Terminal research report and EIA refresh commands."""
import argparse
from pathlib import Path
from energy_trading.data import DEFAULT_PATH, SNAPSHOT_SOURCE, load_weekly_prices
from energy_trading.pricing import add_crack_metrics, crack_decomposition
from energy_trading.arbitrage import (
    CargoAssumptions, indicative_margin_usd_bbl, breakeven_brent_usd_bbl, scenario_grid
)
from energy_trading.eia import export_weekly_csv


def create_report(path=DEFAULT_PATH, output_dir="outputs"):
    from matplotlib import pyplot as plt
    data = add_crack_metrics(load_weekly_prices(path))
    last = data.iloc[-1]
    prior = data.iloc[-2] if len(data) > 1 else None
    a = CargoAssumptions()
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    data.to_csv(output / "weekly_analytics.csv", index=False, date_format="%Y-%m-%d")
    scenario_grid(last["wti_cushing_usd_bbl"], last["brent_europe_usd_bbl"], a).to_csv(
        output / "arbitrage_sensitivity.csv", index=False)
    report = [
        "ENERGY TRADING — REFINING & ARBITRAGE RESEARCH",
        f"EIA spot-price weekly averages ending {last['week_ending']:%Y-%m-%d}",
        f"Source: {SNAPSHOT_SOURCE}",
        f"WTI Cushing: USD {last['wti_cushing_usd_bbl']:.2f}/bbl",
        f"Brent Europe: USD {last['brent_europe_usd_bbl']:.2f}/bbl",
        f"US Gulf regular gasoline: USD {last['gasoline_usgc_usd_gal']:.3f}/US gallon",
        f"US Gulf ULSD: USD {last['ulsd_usgc_usd_gal']:.3f}/US gallon",
        f"Gross indicative 3-2-1 crack: USD {last['crack_321_usd_bbl']:.2f}/crude bbl",
        f"Brent Europe minus WTI Cushing benchmark: USD {last['brent_wti_spread_usd_bbl']:.2f}/bbl",
        f"Illustrative cargo screening differential: USD {indicative_margin_usd_bbl(last['wti_cushing_usd_bbl'], last['brent_europe_usd_bbl'], a):.2f}/input bbl",
        f"Break-even Brent Europe proxy: USD {breakeven_brent_usd_bbl(last['wti_cushing_usd_bbl'], a):.2f}/bbl",
    ]
    if prior is not None:
        report.extend([f"Crack arithmetic attribution, {key}: {value:+.2f} USD/bbl"
                       for key, value in crack_decomposition(prior, last).items()])
    report += [
        "Crack proxy is not actual refinery net margin.",
        "Crude benchmarks and refinery products differ in location and specification.",
        "Costs are unverified illustrative assumptions, NOT real freight or executable trade P&L.",
    ]
    (output / "market_summary.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    axes[0].plot(data["week_ending"], data["crack_321_usd_bbl"], marker="o")
    axes[0].set(ylabel="USD per crude bbl", title="EIA weekly-average gross 3-2-1 crack proxy")
    axes[1].plot(data["week_ending"], data["brent_wti_spread_usd_bbl"], marker="o")
    axes[1].set(ylabel="USD per bbl", title="Brent Europe minus WTI Cushing (not cargo prices)")
    for ax in axes:
        ax.grid(alpha=.2)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(output / "market_snapshot.png", dpi=150)
    plt.close(fig)
    return output


def main():
    parser = argparse.ArgumentParser(description="Evidence-led crude and product spread research")
    command = parser.add_subparsers(dest="command", required=True)
    report = command.add_parser("report")
    report.add_argument("--data", default=str(DEFAULT_PATH))
    report.add_argument("--output-dir", default="outputs")
    fetch = command.add_parser("fetch")
    fetch.add_argument("--output", default="data/eia_weekly_live.csv")
    fetch.add_argument("--lookback", type=int, default=365)
    args = parser.parse_args()
    if args.command == "report":
        destination = create_report(args.data, args.output_dir)
        print((destination / "market_summary.txt").read_text(encoding="utf-8"))
        print(f"Reports saved in {destination.resolve()}")
    else:
        print(export_weekly_csv(args.output, lookback_days=args.lookback))


if __name__ == "__main__":
    main()
