from .hydra import Hydra, HydraDefault
import re
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
    last_section = ""
    last_model = ""
    lines = model_str.split("\n")
    lines = [line for line in lines if len(line) > 1]
    for line in lines:
        words_list = re.split(r"(\s+)", line)
        word_index = 0
        while word_index < len(words_list):
            while word_index < len(words_list) and len(words_list[word_index].split()) == 0:
                word_index += 1
            words_list = words_list[word_index:]
            if len(words_list[word_index].split()) > 0:
                break
            word_index += 1
        if words_list[0] != "field:" and words_list[0] != "relationship:":
            words_list = [word for word in words_list if len(word.strip()) > 0]
        second_word = words_list[1]
        if words_list[0] == "app:":
            app_name = second_word
        elif words_list[0] == "section:":
            last_section = second_word
            app_structure[last_section] = {}
        elif words_list[0] == "model:":
            last_model = second_word
            app_structure[last_section][last_model] = {}
        elif words_list[0] == "field:" or words_list[0] == "relationship:":
            field_name = words_list[2]
            word_index = 4
            app_structure[last_section][last_model][field_name] = []
            while word_index < len(words_list):
                default = ""
                if words_list[word_index][:8] == "default(":
                    default += words_list[word_index][8:]
                    while words_list[word_index][-1:] != ")":
                        word_index += 1
                        default += words_list[word_index]
                    default = default[:-1]
                    app_structure[last_section][last_model][field_name].append(HydraDefault(default))
                elif len(words_list[word_index].split()) > 0:
                    app_structure[last_section][last_model][field_name].append(words_list[word_index])
                word_index += 1
    return Hydra(args.app_directory, app_name, app_structure)

if __name__ == "__main__":
    model = args.model_file.read()
    hydra = parse_hydra_model(model)
    hydra.run()