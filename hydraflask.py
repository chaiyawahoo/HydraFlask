from HydraFlask import Hydra
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("app_directory", metavar="app_directory", type=str)
parser.add_argument("app_name", metavar="app_name", type=str)
parser.add_argument("models", metavar="models", type=str, nargs="+")

args = parser.parse_args()

hydra = Hydra(args.app_directory, args.app_name)

if __name__ == "__main__":
    hydra.run()