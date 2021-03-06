from HydraFlask import Hydra
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("app_directory", metavar="app_directory", type=str)
parser.add_argument("model_file", type=argparse.FileType("r"))
# parser.add_argument("app_name", metavar="app_name", type=str)
# parser.add_argument("models", metavar="models", type=str, nargs="+")

args = parser.parse_args()

model = args.model_file.read()
words = model.split()

app_structure = {}
app_name = ""
keywords = ["app", "blueprint", "model", "field"]

i = 0
while i < len(words):
    if i < len(words) and words[i] == "app":
        app_name = words[i+1]
        i += 1
    while i < len(words) and words[i] == "blueprint":
        blueprint_name = words[i+1]
        app_structure[blueprint_name] = {}
        i += 2
        while i < len(words) and words[i] == "model":
            model_name = words[i+1]
            app_structure[blueprint_name][model_name] = []
            i += 2
            j = 0
            while i < len(words) and words[i] == "field":
                app_structure[blueprint_name][model_name].append([])
                i += 1
                while i < len(words) and words[i] not in keywords:
                    app_structure[blueprint_name][model_name][j].append(words[i])
                    i += 1
                j += 1
    i += 1

hydra = Hydra(args.app_directory, app_name, app_structure)

if __name__ == "__main__":
    hydra.run()