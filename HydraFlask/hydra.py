import autopep8
import os
import secrets

def is_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

class FieldType:
    STRING = 1
    STR = 1
    INTEGER = 2
    INT = 2
    DATE = 3

    def get_type(type_name):
        if type_name == "string":
            return FieldType.STRING
        elif type_name == "int" or type_name == "integer":
            return FieldType.INT

class HydraField:
    def __init__(self, field_name, field_type, *field_args):
        self.name = field_name
        self.type = FieldType.get_type(field_type)
        self.args = field_args
    
    def build_model(self):
        output = f"    {self.name} = db.Column("
        if self.type == FieldType.STRING:
            if len(self.args) > 0 and is_int(self.args[0]):
                output += f"db.String({self.args[0]})"
            else:
                output += f"db.String(80)"
        elif self.args == FieldType.INT:
            output += "db.Integer"
        if len(self.args) > 0:
            if "required" in self.args:
                output += ", nullable=False"
            if "unique" in self.args:
                output += ", unique=True"
        return f"{output})\n"

class HydraResource:
    def __init__(self, name, *fields):
        self.name = name
        self.fields = [HydraField(*field) for field in fields]

class HydraBlueprint:
    def __init__(self, name, resources=[]):
        self.name = name
        self.resources = self.generate_resources(resources)
    
    def generate_resources(self, resources):
        output = []
        for resource_name, resource_fields in resources.items():
            output.append(HydraResource(resource_name, *list(resource_fields)))
        return output

class Hydra:
    def __init__(self, app_directory, app_name, app_structure):
        self.app_directory = os.path.join(os.getcwd(), app_directory)
        self.app_name = f"{app_name}_app"
        self.app_structure = app_structure
        self.blueprints = {}
        for name, resources in self.app_structure.items():
            blueprint = HydraBlueprint(name, resources)
            self.blueprints[name] = blueprint

    def init_fs(self):
        structure = {}
        structure[self.app_name] = {}
        for app_name in self.app_structure:
            structure[self.app_name][app_name] = {"files": ["__init__.py", "routes.py", "forms.py"]}
        structure[self.app_name]["static"] = {}
        structure[self.app_name]["templates"] = {"files": ["base.html", "index.html"]}
        structure[self.app_name]["files"] = ["__init__.py", "models.py", "config.py"]
        structure["files"] = ["__init__.py", ".env", ".gitignore", "app.py", "README.md", "requirements.txt"]

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

    def routes_string(self, bp_name):
        bp = self.blueprints[bp_name]
        output = f"from flask import Blueprint, render_template, url_for, redirect, flash\n\
from {self.app_name}.models import *\n\
from {self.app_name}.{bp_name}.forms import *\n\
from {self.app_name} import db\n\n\
{bp_name} = Blueprint('{bp_name}', __name__)\n\n"

        if bp_name == list(self.blueprints.keys())[0]:
            output += f"@{bp_name}.route('/', methods=['GET'])\n\
def homepage():\n\
    return render_template('index.html')\n\n"

        for resource in bp.resources:
            name = resource.name
            caps = name.capitalize()
            create = f"@{bp_name}.route('/{name}s/create', methods=['GET', 'POST'])\n\
def create_{name}():\n\
    form = {caps}Form()\n\
    if form.validate_on_submit():\n\
        {name} = {caps}()\n\
        # TODO: create \n\
        db.session.add({name})\n\
        db.session.commit()\n\
        flash('{caps} Created.')\n\
        return redirect(url_for('{bp_name}.show_{name}', {name}_id={name}.id))\n\
    return render_template('create_{name}.html', form=form)\n\n"

            read = f"@{bp_name}.route('/{name}s/<{name}_id>', methods=['GET'])\n\
def show_{name}({name}_id):\n\
    {name} = {caps}.query.get({name}_id)\n\
    return render_template('show_{name}.html', {name}={name})\n\n"

            update = f"@{bp_name}.route('/{name}s/<{name}_id>/edit', methods=['GET', 'POST'])\n\
def edit_{name}({name}_id):\n\
    {name} = {caps}.query.get({name}_id)\n\
    form = {caps}Form(obj={name})\n\
    if form.validate_on_submit():\n\
        # TODO: edit\n\
        db.session.add({name})\n\
        db.session.commit()\n\
        flash('{caps} Edited.')\n\
        return redirect(url_for('{bp_name}.show_{name}', {name}_id={name}_id))\n\
    return render_template('edit_{name}.html', form=form)\n\n"

            delete = f"@{bp_name}.route('/{name}s/<{name}_id>/delete', methods=['GET', 'POST'])\n\
def delete_{name}({name}_id):\n\
    {name} = {caps}.query.get({name}_id)\n\
    form = Delete{caps}Form()\n\
    # TODO: delete form\n\
    if form.validate_on_submit():\n\
        db.session.delete({name})\n\
        db.session.commit()\n\
        flash('{caps} Deleted.')\n\
        return redirect(url_for('{bp_name}.create_{name}'))\n\
    return render_template('delete_{caps}.html', form=form)\n\n"

            output += create + read + update + delete
        return output

    def forms_string(self, resources):
        output = f"from flask_wtf import FlaskForm\n\
from wtforms import StringField, PasswordField, DateField, SelectField, SubmitField, TextAreaField, IntegerField\n\
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField\n\
from wtforms.validators import DataRequired, Length, ValidationError\n\
from {self.app_name}.models import *\n\n"

        for resource in resources:
            name = resource.name
            caps = name.capitalize()
            output += f"class {caps}Form(FlaskForm):\n"
            for field in resource.fields:
                f_name = field.name
                f_caps = f_name.capitalize()
                f_type = field.type
                output += f"    {field.name} = "
                if f_type == FieldType.STRING:
                    output += f"StringField('{caps} {f_caps}')\n"
                elif f_type == FieldType.INT:
                    output += f"IntegerField('{caps} {f_caps}')\n"
            output += f"    submit = SubmitField()\n\n"
        return output
    
    def models_string(self):
        output = f"from {self.app_name} import db\n\n"
        first_field = ""
        for subapp in self.app_structure:
            resources = [HydraResource(key, *list(value)) for key, value in self.app_structure[subapp].items()]
            for resource in resources:
                name = resource.name
                caps = name.capitalize()
                output += f"class {caps}(db.Model):\n\
    id = db.Column(db.Integer, primary_key=True)\n"
                first_field = resource.fields[0].name
                for field in resource.fields:
                    output += field.build_model()
                output += f"\n\
    def __str__(self):\n\
        return f'<{caps}: {{self.{first_field}}}>'\n\n\
    def __repr__(self):\n\
        return f'<{caps}: {{self.{first_field}}}>'\n\n"

        return output
    
    def init_string(self):
        output = f"from flask import Flask\n\
from flask_sqlalchemy import SQLAlchemy\n\
from {self.app_name}.config import Config\n\
import os\n\n\
app = Flask(__name__)\n\
app.config.from_object(Config)\n\n\
db = SQLAlchemy(app)\n\n"
        
        for blueprint in self.blueprints:
            output += f"from {self.app_name}.{blueprint}.routes import {blueprint} as {blueprint}_routes\n"
            output += f"app.register_blueprint({blueprint}_routes)\n\n"
        
        output += "with app.app_context():\n    db.create_all()"

        return output
    
    def app_string(self):
        return f"from {self.app_name} import app\n\n\
if __name__ == '__main__':\n\
    app.run(debug=True)"

    def env_string(self):
        return f"SQLALCHEMY_DATABASE_URI=sqlite:///database.db\n\
SECRET_KEY={secrets.token_bytes(16)}"

    def init_routes(self, bp_name):
        routes_text = autopep8.fix_code(self.routes_string(bp_name))
        routes_path = os.path.join(self.app_directory, self.app_name, bp_name, "routes.py")
        with open(routes_path, "w") as routes_file:
            routes_file.write(routes_text)
    
    def init_forms(self, bp_name):
        forms_text = autopep8.fix_code(self.forms_string(self.blueprints[bp_name].resources))
        forms_path = os.path.join(self.app_directory, self.app_name, bp_name, "forms.py")
        with open(forms_path, "w") as forms_file:
            forms_file.write(forms_text)
    
    def init_templates(self):
        current_path, _ = os.path.split(os.path.realpath(__file__))
        templates_path = os.path.join(current_path, "templates")
        with open(os.path.join(templates_path, "base_template.txt"), "r") as f, \
            open(os.path.join(self.app_directory, self.app_name, "templates", "base.html"), "w") as t:
            for line in f:
                t.write(line)

    def init_models(self):
        models_text = autopep8.fix_code(self.models_string())
        models_path = os.path.join(self.app_directory, self.app_name, "models.py")
        with open(models_path, "w") as models_file:
            models_file.write(models_text)
    
    def init_init(self):
        init_text = autopep8.fix_code(self.init_string(), options={"ignore": ["E402"]}) # fixing code will break
        init_path = os.path.join(self.app_directory, self.app_name, "__init__.py")
        with open(init_path, "w") as init_file:
            init_file.write(init_text)
    
    def init_app(self):
        app_text = autopep8.fix_code(self.app_string())
        app_path = os.path.join(self.app_directory, "app.py")
        with open(app_path, "w") as app_file:
            app_file.write(app_text)
        
    def init_env(self):
        env_text = self.env_string()
        env_path = os.path.join(self.app_directory, ".env")
        with open(env_path, "w") as env_file:
            env_file.write(env_text)
    
    def init_config(self):
        current_path, _ = os.path.split(os.path.realpath(__file__))
        templates_path = os.path.join(current_path, "templates")
        with open(os.path.join(templates_path, "config_template.txt"), "r") as f, \
            open(os.path.join(self.app_directory, self.app_name, "config.py"), "w") as t:
            for line in f:
                t.write(line)
    
    def init_requirements(self):
        current_path, _ = os.path.split(os.path.realpath(__file__))
        templates_path = os.path.join(current_path, "templates")
        with open(os.path.join(templates_path, "requirements_template.txt"), "r") as f, \
            open(os.path.join(self.app_directory, "requirements.txt"), "w") as t:
            for line in f:
                t.write(line)
    
    def run(self):
        self.init_fs()
        self.init_models()
        self.init_templates()
        self.init_init()
        self.init_app()
        self.init_env()
        self.init_config()
        self.init_requirements()
        for blueprint in self.blueprints:
            self.init_routes(blueprint)
            self.init_forms(blueprint)