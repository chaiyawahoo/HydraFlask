from .hydra import Hydra
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument("app_directory", metavar="app_directory", type=str)
argparser.add_argument("model_file", type=argparse.FileType("r"))
# argparser.add_argument("app_name", metavar="app_name", type=str)
# argparser.add_argument("models", metavar="models", type=str, nargs="+")

args = argparser.parse_args()

def parse_hydra_model(model_str):
    app_structure = {}
    app_name = ""
    keywords = ["app", "section", "model", "field", "relationship"]
    words = model_str.split()
    i = 0
    while i < len(words):
        if i < len(words) and words[i] == "app":
            app_name = words[i+1]
            i += 1
        while i < len(words) and words[i] == "section":
            blueprint_name = words[i+1]
            app_structure[blueprint_name] = {}
            i += 2
            while i < len(words) and words[i] == "model":
                model_name = words[i+1]
                app_structure[blueprint_name][model_name] = []
                i += 2
                j = 0
                while i < len(words) and (words[i] == "field" or words[i] == "relationship"):
                    app_structure[blueprint_name][model_name].append([])
                    i += 1
                    while i < len(words) and words[i] not in keywords:
                        app_structure[blueprint_name][model_name][j].append(words[i])
                        i += 1
                    j += 1
        i += 1

    return Hydra(args.app_directory, app_name, app_structure)

if __name__ == "__main__":
    model = args.model_file.read()
    hydra = parse_hydra_model(model)
    hydra.run()