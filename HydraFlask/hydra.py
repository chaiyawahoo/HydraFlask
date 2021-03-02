import autopep8
import os

class Hydra:
    def __init__(self, app_directory, app_name):
        self.app_directory = os.path.join(os.getcwd(), app_directory)
        self.app_name = f"{app_name}_app"

    def init_fs(self):
        structure = {
            self.app_name: {
                "main": {
                    "files": ["__init__.py", "routes.py", "forms.py"]
                },
                "static": {},
                "templates": {
                    "files": ["base.html"]
                },
                "files": ["__init__.py", "models.py", "config.py"]
            },
            "files": ["__init__.py", ".env", ".gitignore", "app.py", "README.md", "requirements.txt"]
        }

        def create_fs(parent, path):
            if "files" in parent:
                for file in parent["files"]:
                    open(f"{path}/{file}", "a").close()
                parent.pop("files")
            for key in parent:
                if isinstance(parent[key], dict):
                    os.mkdir(f"{path}/{key}")
                    create_fs(parent[key], f"{path}/{key}")

        os.mkdir(self.app_directory)
        create_fs(structure, self.app_directory)


    def routes_string(self, app, *resources):
        output = f"from flask import Blueprint\n\
            from {self.app_name} import app\n\n\
            {app} = Blueprint('{app}', __name__)\n"

        for resource in resources:
            create = f"@{app}.route('/{resource}s/create', methods=['GET', 'POST'])\n\
            def create_{resource}():\n\
                pass\n"

            read = f"@{app}.route('/{resource}s/<{resource}_id>', methods=['GET'])\n\
            def read_{resource}({resource}_id):\n\
                pass\n"

            update = f"@{app}.route('/{resource}s/<{resource}_id>/edit', methods=['GET', 'POST'])\n\
            def edit_{resource}({resource}_id):\n\
                pass\n"

            delete = f"@{app}.route('/{resource}s/<{resource}_id>/delete', methods=['GET', 'POST'])\n\
            def delete_{resource}({resource}_id):\n\
                pass\n"

            output += create + read + update + delete
        return output

    def init_routes(self, app, *resources):
        routes_text = autopep8.fix_code(self.routes_string(app, *resources))
        routes_path = os.path.join(self.app_directory, self.app_name, app, "routes.py")
        with open(routes_path, "w") as routes_file:
            routes_file.write(routes_text)
    
    def init_templates(self):
        current_path, current_file = os.path.split(os.path.realpath(__file__))
        templates_path = os.path.join(current_path, "templates")
        with open(os.path.join(templates_path, "base_template.html"), "r") as f, \
            open(os.path.join(self.app_directory, self.app_name, "templates", "base.html"), "w") as t:
            for line in f:
                t.write(line)
    
    def run(self):
        self.init_fs()
        self.init_routes("main", "user", "post")
        self.init_templates()