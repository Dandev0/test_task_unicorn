import argparse

list_debug_args = ['0', '1', 'true', 'false', 'True', 'False', 'y', 'n', 'Y', 'N']
parser = argparse.ArgumentParser()
parser.add_argument('--rub', type=float, default=0)
parser.add_argument('--usd', type=float, default=0)
parser.add_argument('--eur', type=float, default=0)
parser.add_argument('--period', type=float, default=0)
parser.add_argument('--debug', choices={'0', 'false', 'False', 'n', 'N', '1', 'true', 'True', 'y', 'Y'}, default='0', type=str)

args = parser.parse_args()