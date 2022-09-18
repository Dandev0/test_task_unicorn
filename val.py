import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--rub', type=float, default=0)
parser.add_argument('--usd', type=float, default=0)
parser.add_argument('--eur', type=float, default=0)
parser.add_argument('--period', type=float, default=0)
parser.add_argument('--debug', type=str)

args = parser.parse_args()