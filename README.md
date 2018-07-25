# Catalog

Flask Web application with simple CRUD operations for categories and its sub-items.

This is a project with academic purposes for [Fullstack Web Developer Nanodegree by Udacity](https://br.udacity.com/course/full-stack-web-developer-nanodegree--nd004).

# Before you run this exercise:
- Install Python 3;
- Install Vagrant and VirtualBox;
- Download FSDN-Virtual-Machine;

When executing the `Vagrantfile` inside the virtual machine, it should install our Python dependencies, such as:
- Flask
- OAuth2
- SQLAlchemy ORM

# Running

1. Run `vagrant up` to initialize the VM;
2. Then, run `vagrant ssh` to access the VM's command-line interface;
3. Enter in project's root folder (`cd /vagrant/catalog`)
4. Then, run `FLASK_APP=app.py flask run --host=0.0.0.0`, where:
  - `FLASK_APP=app.py` is setting up our enviroment variable `FLASK_APP` to be our python file with the application endpoints;
  - `--host=0.0.0.0` is exposing the flask application to port 5000 outside the VM, otherwise we can't access in our browsers;
  - `flask run` is running our flask application.
