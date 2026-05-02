import os, sys
import argparse
from Simulation import Simulation
import CONSTANTS
import warnings
def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dataset", help="Dataset", type=str, default="Identical.csv")
    parser.add_argument("-p", "--policy", help="Constant policy", type=str,
                        default=CONSTANTS.PRICING_POLICIES.FIFTY_PRC)
    parser.add_argument("-r", "--repeat", help="Number of repetitions", type=int, default=20)
    parser.add_argument("-m", "--max_daily_reservations", help="Max number of reservation per day", type=int,
                        default=300)
    parser.add_argument("-c", "--cancellation_probability", help="Cancellation probability", type=float, default=0.25)
    parser.add_argument("-s", "--simulation_period", help="Simlation period", type=int, default=30)
    parser.add_argument("--certified", help="Certified policy", action='store_true')
    args = parser.parse_args()
    return args

def debug():
    s = Simulation(
        input_file="Datasets/Identical_FP_vs_+20%_+40%.csv",
        simulation_period=30,
        max_reservations_per_day=5,
        cancellation_probability=0.01,
        constant_incr_policy=[CONSTANTS.PRICING_POLICIES.INCREMENT["all"]],
        certified=True, score={p: [] for p in CONSTANTS.PRICING_POLICIES.DEFAULT_POLICIES}, iterations=1,
        mute=False
    )
    s.setBookingWindow(1)
    s.iterate()


if __name__ == '__main__':
    # debug()
    #
    # sys.exit()

    warnings.simplefilter(action='ignore', category=FutureWarning)
    args = argument_parser()

    if args.policy == "all":
        score = {p: [] for p in CONSTANTS.PRICING_POLICIES.DEFAULT_POLICIES}
    else:
        score = {CONSTANTS.PRICING_POLICIES.FAIRPLAY: [], args.policy: []}
    constant_incr = [CONSTANTS.PRICING_POLICIES.INCREMENT[args.policy]]
    filename = f'{args.dataset}.csv'
    s = Simulation(
        input_file=args.dataset,
        simulation_period=args.simulation_period,
        max_reservations_per_day=args.max_daily_reservations,
        cancellation_probability=args.cancellation_probability,
        constant_incr_policy=constant_incr,
        certified=args.certified,score=score,iterations=args.repeat,
        mute = True
    )

    s.iterate()
