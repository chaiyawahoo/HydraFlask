from typing import Text
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
    RELATIONSHIP = 0
    BOOL = 1
    BOOLEAN = 1
    INTEGER = 2
    INT = 2
    FLOAT = 3
    STRING = 4
    STR = 4
    TEXT = 5
    UNICODE = 6
    UNICODE_TEXT = 7
    DATE = 8
    TIME = 9
    DATETIME = 10

    def get_type(type_name):
        if type_name == "bool" or type_name == "boolean":
            return FieldType.BOOL
        elif type_name == "int" or type_name == "integer":
            return FieldType.INT
        elif type_name == "float":
            return FieldType.FLOAT
        elif type_name == "str" or type_name == "string":
            return FieldType.STRING
        elif type_name == "text":
            return FieldType.TEXT
        elif type_name == "unicode":
            return FieldType.UNICODE
        elif type_name == "unicode-text":
            return FieldType.UNICODE_TEXT
        elif type_name == "date":
            return FieldType.DATE
        elif type_name == "time":
            return FieldType.TIME
        elif type_name == "datetime":
            return FieldType.DATETIME

class HydraTable:
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.name = f"{self.left}s_{self.right}s"
    
    def build_table(self):
        output = f"{self.name} = db.Table('{self.name}',"
        output += f" db.Column('{self.left}_id', db.Integer, db.ForeignKey('{self.left}.id')), "
        output += f" db.Column('{self.right}_id', db.Integer, db.ForeignKey('{self.right}.id'))"
        return f"{output})\n\n"

class HydraField:
    def __init__(self, resource_name, field_name, field_type, *field_args):
        if field_name == "one-to-one" or field_name == "many-to-one" or field_name == "one-to-many" or field_name == "many-to-many":
            self.name = field_type
            self.type = FieldType.RELATIONSHIP
            self.args = [field_name]
            self.args.extend(field_args) # populate = back_populates
            if "many-to-many" in self.args and not "populate" in self.args:
                self.args.append("populate")
        else:
            self.name = field_name
            self.type = FieldType.get_type(field_type)
            self.args = field_args
        self.resource_name = resource_name
        if "populate" in self.args:
            Hydra.flask_populated_fields.append(self.name)
    
    def build_fk(self, name):
        output = f"    {name} = db.Column(db.Integer, db.ForeignKey('{self.name}.id')"
        if "required" in self.args:
            output += ", nullable=False"
        return f"{output})\n"
    
    def build_relationship(self, name, resource, secondary):
        output = f"    {name} = db.relationship('{self.name.capitalize()}'"
        if secondary is not None:
            output += f", secondary='{secondary}'"
        if "populate" in self.args:
            output += f", back_populates='{resource}'"
        return output
    
    def build_model(self):
        output = ""
        if self.type == FieldType.RELATIONSHIP:
            name, resource, secondary = None, None, None
            if self.resource_name not in Hydra.flask_populated_fields:
                if self.args[0] == "one-to-one" or self.args[0] == "many-to-one":
                    output += self.build_fk(f"{self.name}_id")
                elif self.args[0] == "one-to-many":
                    output += self.build_fk(f"{self.name}_ids")
            if self.args[0] == "one-to-one":
                name = self.name
                resource = self.resource_name
            elif self.args[0] == "one-to-many":
                name = f"{self.name}s"
                resource = self.resource_name
            elif self.args[0] == "many-to-one":
                name = self.name
                resource = f"{self.resource_name}s"
            elif self.args[0] == "many-to-many":
                name = f"{self.name}s"
                resource = f"{self.resource_name}s"
                secondary = Hydra.flask_tables[self.name]
            output += self.build_relationship(name, resource, secondary)
        else:
            output += f"    {self.name} = db.Column("
            if self.type == FieldType.BOOL:
                output += "db.Boolean"
            elif self.type == FieldType.INT:
                output += "db.Integer"
            elif self.type == FieldType.FLOAT:
                output += "db.Float"
            elif self.type == FieldType.STRING:
                if len(self.args) > 0 and is_int(self.args[0]):
                    output += f"db.String({self.args[0]})"
                else:
                    output += f"db.String(80)"
            elif self.type == FieldType.TEXT:
                output += "db.Text"
            elif self.type == FieldType.UNICODE:
                if len(self.args) > 0 and is_int(self.args[0]):
                    output += f"db.Unicode({self.args[0]})"
                else:
                    output += f"db.Unicode(80)"
            elif self.type == FieldType.UNICODE_TEXT:
                output += "db.UnicodeText"
            elif self.type == FieldType.DATE:
                output += "db.Date"
            elif self.type == FieldType.TIME:
                output += "db.Time"
            elif self.type == FieldType.DATETIME:
                output += "db.DateTime"
            if len(self.args) > 0:
                if "required" in self.args:
                    output += ", nullable=False"
                if "unique" in self.args:
                    output += ", unique=True"
        return f"{output})\n"

class HydraResource:
    def __init__(self, section_name, name, *fields):
        self.name = name
        self.fields = [HydraField(self.name, *field) for field in fields]
        self.section_name = section_name
    
    def create_route_string(self):
        return f"@{self.section_name}.route('/{self.name}s/create', methods=['GET', 'POST'])\n\
def create_{self.name}():\n\
    form = {self.name.capitalize()}Form()\n\
    if form.validate_on_submit():\n\
        {self.name} = {self.name.capitalize()}()\n\
        # TODO: create \n\
        db.session.add({self.name})\n\
        db.session.commit()\n\
        flash('{self.name.capitalize()} Created.')\n\
        return redirect(url_for('{self.section_name}.show_{self.name}', {self.name}_id={self.name}.id))\n\
    return render_template('create_{self.name}.html', form=form)\n\n"

    def read_route_string(self):
        return f"@{self.section_name}.route('/{self.name}s/<{self.name}_id>', methods=['GET'])\n\
def show_{self.name}({self.name}_id):\n\
    {self.name} = {self.name.capitalize()}.query.get({self.name}_id)\n\
    return render_template('show_{self.name}.html', {self.name}={self.name})\n\n"

    def update_route_string(self):
        return f"@{self.section_name}.route('/{self.name}s/<{self.name}_id>/edit', methods=['GET', 'POST'])\n\
def edit_{self.name}({self.name}_id):\n\
    {self.name} = {self.name.capitalize()}.query.get({self.name}_id)\n\
    form = {self.name.capitalize()}Form(obj={self.name})\n\
    if form.validate_on_submit():\n\
        # TODO: edit\n\
        db.session.add({self.name})\n\
        db.session.commit()\n\
        flash('{self.name.capitalize()} Edited.')\n\
        return redirect(url_for('{self.section_name}.show_{self.name}', {self.name}_id={self.name}_id))\n\
    return render_template('edit_{self.name}.html', form=form)\n\n"

    def delete_route_string(self):
        return f"@{self.section_name}.route('/{self.name}s/<{self.name}_id>/delete', methods=['GET', 'POST'])\n\
def delete_{self.name}({self.name}_id):\n\
    {self.name} = {self.name.capitalize()}.query.get({self.name}_id)\n\
    form = Delete{self.name.capitalize()}Form()\n\
    # TODO: delete form\n\
    if form.validate_on_submit():\n\
        db.session.delete({self.name})\n\
        db.session.commit()\n\
        flash('{self.name.capitalize()} Deleted.')\n\
        return redirect(url_for('{self.section_name}.create_{self.name}'))\n\
    return render_template('delete_{self.name.capitalize()}.html', form=form)\n\n"

    def all_routes_string(self, crud=15):
        to_crud = "{:0{}b}".format(crud, 4)
        output = ""
        if to_crud[0] == "1":
            output += self.create_route_string()
        if to_crud[1] == "1":
            output += self.read_route_string()
        if to_crud[2] == "1":
            output += self.update_route_string()
        if to_crud[3] == "1":
            output += self.delete_route_string()
        return output
    
    def tables_string(self):
        output = ""
        for table in self.tables:
            output += table.build_table()
        return output


class HydraSection:
    def __init__(self, name, resources=[]):
        self.name = name
        self.resources = self.generate_resources(resources)
    
    def generate_resources(self, resources):
        output = []
        for resource_name, resource_fields in resources.items():
            output.append(HydraResource(self.name, resource_name, *list(resource_fields)))
        return output

class Hydra:
    flask_tables = {}
    flask_populated_fields = []
    def __init__(self, app_directory, app_name, app_structure):
        self.app_directory = os.path.join(os.getcwd(), app_directory)
        self.app_name = f"{app_name}_app"
        self.app_structure = app_structure
        self.sections = {}
        for name, resources in self.app_structure.items():
            section = HydraSection(name, resources)
            self.sections[name] = section
        self.tables = self.make_tables()
        for table in self.tables:
            Hydra.flask_tables[table.left] = table.name
            Hydra.flask_tables[table.right] = table.name
    
    def make_tables(self):
        tables = []
        left_temp = None
        for _, section in self.sections.items():
            for resource in section.resources:
                for field in resource.fields:
                    if field.type == FieldType.RELATIONSHIP and field.args[0] == "many-to-many":
                        if left_temp is None:
                            left_temp = field.name
                        else:
                            tables.append(HydraTable(left_temp, field.name))
                            left_temp = None
        return tables

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

    def routes_string(self, section_name):
        sec = self.sections[section_name]
        output = f"from flask import Blueprint, render_template, url_for, redirect, flash\n\
from {self.app_name}.models import *\n\
from {self.app_name}.{section_name}.forms import *\n\
from {self.app_name} import db\n\n\
{section_name} = Blueprint('{section_name}', __name__)\n\n"

        if section_name == list(self.sections.keys())[0]:
            output += f"@{section_name}.route('/', methods=['GET'])\n\
def homepage():\n\
    return render_template('index.html')\n\n"

        output += "".join([resource.all_routes_string() for resource in sec.resources])
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
                    output += f"StringField('{f_caps}')\n"
                elif f_type == FieldType.INT:
                    output += f"IntegerField('{f_caps}')\n"
            output += f"    submit = SubmitField()\n\n"
        return output
    
    def models_string(self):
        output = f"from {self.app_name} import db\n\n"
        first_field = ""
        for _, section in self.sections.items():
            for resource in section.resources:
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
        for table in self.tables:
            output += table.build_table()

        return output
    
    def init_string(self):
        output = f"from flask import Flask\n\
from flask_sqlalchemy import SQLAlchemy\n\
from {self.app_name}.config import Config\n\
import os\n\n\
app = Flask(__name__)\n\
app.config.from_object(Config)\n\n\
db = SQLAlchemy(app)\n\n"
        
        for section in self.sections:
            output += f"from {self.app_name}.{section}.routes import {section} as {section}_routes\n"
            output += f"app.register_blueprint({section}_routes)\n\n"
        
        output += "with app.app_context():\n    db.create_all()"

        return output
    
    def app_string(self):
        return f"from {self.app_name} import app\n\n\
if __name__ == '__main__':\n\
    app.run(debug=True)"

    def env_string(self):
        return f"SQLALCHEMY_DATABASE_URI=sqlite:///database.db\n\
SECRET_KEY={secrets.token_bytes(16)}"

    def init_routes(self, section_name):
        routes_text = autopep8.fix_code(self.routes_string(section_name))
        routes_path = os.path.join(self.app_directory, self.app_name, section_name, "routes.py")
        with open(routes_path, "w") as routes_file:
            routes_file.write(routes_text)
    
    def init_forms(self, section_name):
        forms_text = autopep8.fix_code(self.forms_string(self.sections[section_name].resources))
        forms_path = os.path.join(self.app_directory, self.app_name, section_name, "forms.py")
        with open(forms_path, "w") as forms_file:
            forms_file.write(forms_text)
    
    def init_templates(self):
        current_path, _ = os.path.split(os.path.realpath(__file__))
        templates_path = os.path.join(current_path, "templates")
        with open(os.path.join(templates_path, "base_template.txt"), "r") as f, \
            open(os.path.join(self.app_directory, self.app_name, "templates", "base.html"), "w") as t:
            for line in f:
                t.write(line)
        for section in self.sections.values():
            for resource in section.resources:
                with open(os.path.join(templates_path, "form_template.txt"), "r") as f, \
                    open(os.path.join(self.app_directory, self.app_name, "templates", f"create_{resource.name}.html"), "w") as t:
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
        for section in self.sections:
            self.init_routes(section)
            self.init_forms(section)