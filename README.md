# UTDesign GettIt

UTDesign GettIt (Senior Design, Spring 2019)

Procurement Management System

## Setup

This project requires Python 3. For development purposes (and in general),
a machine should have `pip` and `virtualenv` installed. In Ubuntu, this
can be done with:

```
$ sudo apt install python3-pip
$ python3 -m pip install virtualenv
```


This project depends several PyPI projects. Recommended 
workflow is to create a python3 virtualenv and install these packages there.

For example:

```
$ cd utdesign_procurement
$ python3 -m virtualenv venvProcurement
$ source venvProcurement/bin/activate
$ python3 -m pip install -r requirements.txt
```

Also, to initialize the database development purposes, use this:

```
$ mongo scripts/debug_users.js
```

## Unit Tests

Unit tests can be found in the src/python/tests package. To run them, be sure
to have MongoDB backed up. It's necessary to run the debug_users.js script
before running unit tests. Recommended workflow:

```
$ cd utdesign_procurement/
$ source venvProcurement/bin/activate
$ cd src/python
$ python3 -m unittest
```

## Sphinx Documentation

Sphinx documentation can be generated from within the virtualenv by using
the makefile in the doc directory. For example:

```
$ cd utdesign_procurement
$ source venvProcurement/bin/activate
$ cd doc
$ make html
$ make latexpdf
```

Then documentation can be found in doc/build

## Running

The previously mentioned virtualenv should be sourced before running the
bash script at `scripts/start_procuring.sh`.

```
$ cd utdesign_procurement
$ source venvProcurement/bin/activate
$ bash scripts/start_procuring.sh
```

The server will then be hosted on [http://localhost:8080](http://localhost:8080).