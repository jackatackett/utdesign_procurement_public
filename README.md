# UTDesign Procurement Management System

UTDesign Procurement Management System (Senior Design, Spring 2019)


## Setup

This project requires Python 3. For development purposes (and in general),
a machine should have `pip` and `virtualenv` installed. In Ubuntu, this
can be done with:

```
$ sudo apt install python3-pip
$ python3 -m pip install virtualenv
```


This project depends on the PyPI projects `cherrypy` and `mako`. Recommended 
workflow is to create a python3 virtualenv and install these packages there.

For example:

```
$ cd utdesign_procurement
$ python3 -m virtualenv venvProcurement
$ source venvProcurement/bin/activate
$ python3 -m pip install -r requirements.txt
```

Also, to add one of each user for debugging, use this:

```
$ mongo scripts/debug_users.js
```

And users will be created as below:

| Email                | Password | Role    |
| -------------------- | ---------| ------- |
| admin@utdallas.edu   | oddrun   | admin   |
| manager@utdallas.edu | oddrun   | manager |
| student@utdallas.edu | oddrun   | student |

## Running

The previously mentioned virtualenv should be sourced before running the
bash script at `scripts/start_procuring.sh`.

```
$ cd utdesign_procurement
$ source venvProcurement/bin/activate
$ bash scripts/start_procuring.sh
```

The server will then be hosted on [http://localhost:8080](http://localhost:8080).