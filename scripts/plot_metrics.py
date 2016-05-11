
import common
import numpy as np
import matplotlib
matplotlib.use("Agg")
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt
import seaborn as sns
import tabler
from datetime import datetime
from collections import defaultdict
from table_common import table_header, line_tp, table_footer

instances = [(500, 1, 0), (500, 2, 0), (500, 3, 0), (500, 4, 0),
             (125, 4, 0), (250, 4, 0), (375, 4, 0), (625, 4, 0),
             (750, 4, 0), (1000, 4, 0), (250, 4, 1), (375, 4, 1),
             (500, 4, 1), (625, 4, 1), (750, 4, 1)]


n_vecs = [125, 250, 375, 500, 625, 750, 1000]
predictions = [0, 100, 200, 300, 400]
waiting_times = [120, 300, 420]
vehicles = [1000, 2000, 3000]
fields = ["mean_waiting_time", "mean_passengers", "mean_delay", "n_pickups",
          "mean_travel_delay", "serviced_percentage"]
caps = [1, 2, 4, 10]
clrs = ["ro-", "go-", "bo-", "co-"]


def prettify(text):
    if text == "n_pickups":
        return "Num Pickups"
    else:
        words = text.split("_")
        return " ".join(w.capitalize() for w in words)


def make_wt_title(field, wt):
    return "{} w/ M.W.T: {}".format(prettify(field), wt)


def make_vec_title(field, nv):
    return "{} w/ N.V: {}".format(prettify(field), nv)


def make_pred_title(field, wt, nv):
    return "{} w/ M.W.T: {}, Cap.: {}".format(prettify(field), wt, cap)


def create_latex_table(df):
    lines = list()
    for i, (n_vecs, cap, rb) in enumerate(instances):
        st = df
        n_hrs = common.MAX_SECONDS / (60 * 60.0)
        pickups = np.sum(st["n_pickups"]) / n_hrs
        ignored = np.sum(st["n_ignored"]) / n_hrs
        pickups_std = 3600 * np.std(st["n_pickups"]) / common.MAX_SECONDS
        ignored_std = 3600 * np.std(st["n_ignored"]) / common.MAX_SECONDS
        waiting_time = np.mean(st["mean_waiting_time"])
        waiting_time_std = np.std(st["mean_waiting_time"])
        delay = np.mean(st["mean_delay"])
        delay_std = np.std(st["mean_delay"])
        occupancy = np.mean(st["mean_passengers"])
        occupancy_std = np.std(st["mean_passengers"])
        line = line_tp.format(
            i + 1, n_vecs, cap, pickups, pickups_std,
            ignored, ignored_std, waiting_time, waiting_time_std,
            delay, delay_std, occupancy, occupancy_std)
        lines.append(line)
    inner_lines = "\n\\hline\n".join(line for line in lines)
    return table_header + inner_lines + table_footer


def plot_ts(df, field, *args, **kwargs):
    dates = df["time"]
    values = df[field]
    dts = list()
    for i in xrange(len(dates)):
        dt = datetime.strptime(dates.iloc[i], common.date_format)
        dts.append(dt)
    dts = matplotlib.dates.date2num(dts)
    plt.plot_date(dts, values, *args, **kwargs)


def make_ts_plots():
    fmt = DateFormatter("%m/%d")
    for field in fields:
        for v in vehicles:
            for wt in waiting_times:
                fig, ax = plt.subplots()
                for cap, clr in zip(caps, clrs):
                    df = tabler.get_metrics(v, cap, wt, 0)
                    plot_ts(df, field, clr, alpha=0.8,
                            label="Cap: {}".format(cap))
                ax.xaxis.set_major_formatter(fmt)
                lgd = plt.legend(loc="center left", fancybox=True,
                                 shadow=True, bbox_to_anchor=(1, 0.5))
                plt.ylabel(field)
                fig.autofmt_xdate()
                plt.savefig("figs/ts-{}-v{}-w{}.pdf".format(field, v, wt),
                            bbox_extra_artists=(lgd,), bbox_inches='tight')


def get_avg_ys_vecs():
    ys = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    stds = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for wt in waiting_times:
        for v in vehicles:
            for field in fields:
                for cap in caps:
                    df = tabler.get_metrics(v, cap, wt, 0)
                    ys[field][cap][wt].append(np.mean(df[field]))
                    stds[field][cap][wt].append(np.std(df[field]))
    return ys, stds


def get_avg_ys_wts():
    ys = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    stds = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for v in vehicles:
        for wt in waiting_times:
            for field in fields:
                for cap in caps:
                    df = tabler.get_metrics(v, cap, wt, 0)
                    ys[field][cap][v].append(np.mean(df[field]))
                    stds[field][cap][v].append(np.std(df[field]))
    return ys, stds


def get_avg_ys_ps():
    ys = defaultdict(lambda: defaultdict(list))
    stds = defaultdict(lambda: defaultdict(list))
    cap = 4
    wt = 300
    for v in vehicles:
        for field in fields:
            for p in predictions:
                df = tabler.get_metrics(v, cap, wt, p)
                ys[field][p].append(np.mean(df[field]))
                stds[field][p].append(np.std(df[field]))
    return ys, stds


def make_avg_plots_with_preds():
    ys, stds = get_avg_ys_ps()
    cap = 4
    wt = 300
    for field in fields:
        fig, ax = plt.subplots()
        for p, clr in zip(predictions, clrs):
            plt.plot(vehicles, ys[field][p], clr,
                    label="Preds: {}".format(p))
        ax.set_xticks(vehicles)
        plt.xlim([min(vehicles) - 100, max(vehicles) + 100])
        plt.ylabel(prettify(field))
        plt.xlabel("Num Vehicles")
        lgd = plt.legend(loc="center left", fancybox=True,
                        shadow=True, bbox_to_anchor=(1, 0.5))
        plt.title(make_pred_title(field, wt, cap))
        plt.savefig(
            "figs/avg-with-preds-{}.pdf".format(field),
            bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.close()


def make_avg_plots_with_vecs():
    ys, stds = get_avg_ys_vecs()
    for field in fields:
        for wt in waiting_times:
            fig, ax = plt.subplots()
            for cap, clr in zip(caps, clrs):
                plt.plot(vehicles, ys[field][cap][wt], clr,
                        label="Cap: {}".format(cap))
            ax.set_xticks(vehicles)
            plt.xlim([min(vehicles) - 100, max(vehicles) + 100])
            plt.ylabel(prettify(field))
            plt.xlabel("Num Vehicles")
            lgd = plt.legend(loc="center left", fancybox=True,
                            shadow=True, bbox_to_anchor=(1, 0.5))
            plt.title(make_wt_title(field, wt))
            plt.savefig("figs/avg-with-vecs-{}-w{}.pdf".format(field, wt),
                        bbox_extra_artists=(lgd,), bbox_inches='tight')
            plt.close()


def make_avg_plots_with_wts():
    ys, stds = get_avg_ys_wts()
    for field in fields:
        for v in vehicles:
            fig, ax = plt.subplots()
            for cap, clr in zip(caps, clrs):
                plt.plot(waiting_times, ys[field][cap][v], clr,
                        label="Cap: {}".format(cap))
            ax.set_xticks(waiting_times)
            plt.xlim([min(waiting_times) - 10, max(waiting_times) + 10])
            plt.ylabel(prettify(field))
            plt.xlabel("Max Waiting Time")
            lgd = plt.legend(loc="center left", fancybox=True,
                            shadow=True, bbox_to_anchor=(1, 0.5))
            plt.title(make_vec_title(field, v))
            plt.savefig("figs/avg-with-wts-{}-v{}.pdf".format(field, v),
                        bbox_extra_artists=(lgd,), bbox_inches='tight')
            plt.close()


if __name__ == "__main__":
    plt.ioff()
    sns.set_context("poster", font_scale=2.2)
    make_avg_plots_with_preds()
    make_avg_plots_with_vecs()
    make_avg_plots_with_wts()
    # make_ts_plots()
