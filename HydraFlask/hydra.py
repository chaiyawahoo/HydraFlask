from re import sub
import autopep8
import os

class Hydra:
    def __init__(self, app_directory, app_name, app_structure):
        self.app_directory = os.path.join(os.getcwd(), app_directory)
        self.app_name = f"{app_name}_app"
        self.app_structure = app_structure

    def init_fs(self):
        structure = {}
        structure[self.app_name] = {}
        for app_name in self.app_structure:
            structure[self.app_name][app_name] = {"files": ["__init__.py", "routes.py", "forms.py"]}
        structure[self.app_name]["static"] = {}
        structure[self.app_name]["templates"] = {"files": ["base.html"]}
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


    def routes_string(self, subapp, *resources):
        output = f"from flask import Blueprint, render_template, url_for, redirect, flash\n\
from {self.app_name}.models import *\n\
from {self.app_name}.{subapp}.forms import *\n\
from {self.app_name} import app, db\n\n\
{subapp} = Blueprint('{subapp}', __name__)\n\n"

        for resource in resources:
            create = f"@{subapp}.route('/{resource}s/create', methods=['GET', 'POST'])\n\
def create_{resource}():\n\
    form = {resource.capitalize()}Form()\n\
    if form.validate_on_submit():\n\
        {resource} = {resource.capitalize()}()\n\
        # TODO: create \n\
        db.session.add({resource})\n\
        db.session.commit()\n\
        flash('{resource.capitalize()} Created.')\n\
        return redirect(url_for('{subapp}.show_{resource}', {resource}_id={resource}.id))\n\
    return render_template('create_{resource}.html', form=form)\n\n"

            read = f"@{subapp}.route('/{resource}s/<{resource}_id>', methods=['GET'])\n\
def show_{resource}({resource}_id):\n\
    {resource} = {resource.capitalize()}.query.get({resource}_id)\n\
    return render_template('show_{resource}.html', {resource}={resource})\n\n"

            update = f"@{subapp}.route('/{resource}s/<{resource}_id>/edit', methods=['GET', 'POST'])\n\
def edit_{resource}({resource}_id):\n\
    {resource} = {resource.capitalize()}.query.get({resource}_id)\n\
    form = {resource.capitalize()}Form(obj={resource})\n\
    if form.validate_on_submit():\n\
        # TODO: edit\n\
        db.session.add({resource})\n\
        db.session.commit()\n\
        flash('{resource.capitalize()} Edited.')\n\
        return redirect(url_for('{subapp}.show_{resource}', {resource}_id={resource}_id))\n\
    return render_template('edit_{resource}.html', form=form)\n\n"

            delete = f"@{subapp}.route('/{resource}s/<{resource}_id>/delete', methods=['GET', 'POST'])\n\
def delete_{resource}({resource}_id):\n\
    {resource} = {resource.capitalize()}.query.get({resource}_id)\n\
    form = Delete{resource.capitalize()}Form()\n\
    # TODO: delete form\n\
    if form.validate_on_submit():\n\
        db.session.delete({resource})\n\
        db.session.commit()\n\
        flash('{resource.capitalize()} Deleted.')\n\
        return redirect(url_for('{subapp}.create_{resource}'))\n\
    return render_template('delete_{resource}.html', form=form)\n\n"

            output += create + read + update + delete
        return output
    
    def forms_string(self, **resources):
        output = f"from flask_wtf import FlaskForm\n\
from wtforms import StringField, PasswordField, DateField, SelectField, SubmitField, TextAreaField\n\
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField\n\
from wtforms.validators import DataRequired, Length, ValidationError\n\
from {self.app_name}.models import *\n\n"

        for resource in resources:
            output += f"class {resource.capitalize()}Form(FlaskForm):\n"
            for field in resources[resource]:
                output += f"    {field[0]} = "
                if field[1] == "string":
                    output += f"StringField('{resource.capitalize()} {field[0].capitalize()}')\n"
                    pass
            output += f"    submit = SubmitField()\n\n"
        
        return output

    def init_routes(self, subapp, *resources):
        routes_text = autopep8.fix_code(self.routes_string(subapp, *resources))
        routes_path = os.path.join(self.app_directory, self.app_name, subapp, "routes.py")
        with open(routes_path, "w") as routes_file:
            routes_file.write(routes_text)
    
    def init_forms(self, subapp, **resources):
        forms_text = autopep8.fix_code(self.forms_string(**resources))
        forms_path = os.path.join(self.app_directory, self.app_name, subapp, "forms.py")
        with open(forms_path, "w") as forms_file:
            forms_file.write(forms_text)
    
    def init_templates(self):
        current_path, current_file = os.path.split(os.path.realpath(__file__))
        templates_path = os.path.join(current_path, "templates")
        with open(os.path.join(templates_path, "base_template.html"), "r") as f, \
            open(os.path.join(self.app_directory, self.app_name, "templates", "base.html"), "w") as t:
            for line in f:
                t.write(line)
    
    def run(self):
        self.init_fs()
        for subapp in self.app_structure:
            resources = self.app_structure[subapp]
            self.init_routes(subapp, *resources)
            self.init_forms(subapp, **resources)
        self.init_templates()