import json
import os
import syslog
import validator
from flask import Flask, request, make_response
from jsonschema.exceptions import ValidationError


class BadRequestError(Exception):
    """ Signals a malformed request body
    """
    pass


app = Flask(__name__)
_cars = []


def _get_postman_coll():
    """ returns the postman endpoint collection used to test this API
    """
    dir_path = os.path.dirname(os.path.abspath(__file__))
    coll_path = os.path.join(dir_path, "mycars_api.postman_collection")
    with open(coll_path,'r') as coll:
        return json.loads(coll.read())


def _format_field_path(absolute_path):
    """ Reformats the validation field path to be more readable
    """
    path = []
    for part in absolute_path:
        if type(part) in [unicode, str]:
            path.append(part)
        elif type(part) is int:
            path[-1] = path[-1] + "[{}]".format(part)
    return '.'.join(path)


def _add_car(car):
    """ Adds a car to the database
    """
    try:
        validator.validate_car(car)
    except ValidationError as e:
        message = "Invalid car:\n Field: {}\n Error: {}".format(_format_field_path(e.absolute_path),e.message)
        raise BadRequestError(message)
    _cars.append(car)


def _make_error(status=500, message=None):
    """ Utility method used to create an error response.
    """
    error = {}
    error['code'] = status
    error['message'] = message
    resp = make_response(json.dumps(error), status)
    resp.headers['Content-Type'] = 'application/json'
    return resp


def _make_response(status=200, response=None):
    """ Utility method used to create a successful response.
    """
    resp = make_response(json.dumps(response), status)
    resp.headers['Content-Type'] = 'application/json'
    return resp


@app.route('/swagger/', methods=['GET'])
def get_swagger():
    """ Request handler for the /swagger path.

    GET:  returns the My Cars API spec as a swagger json doc.
    """
    try:
        return _make_response(response=validator.get_swagger_spec())
    except Exception as e:
        return _make_error(500, e.message)


@app.route('/postman/', methods=['GET'])
def get_postman():
    """ Request handler for the /postman/ path.

    GET:  returns a postman collection for the API endpoints.
    """
    try:
        return _make_response(response=_get_postman_coll())
    except Exception as e:
        return _make_error(500, e.message)


@app.route('/cars/', methods=['GET', 'POST'])
def get_post_cars():
    """ Request handler for /cars/ path.

    GET:  returns the list of owned (in my dreams) cars
    POST:  adds a new owned (dream) car
    """
    if request.method == 'POST':
        car_data = request.json
        try:
            return _make_response(response=_add_car(car_data))
        except BadRequestError as e:
            return _make_error(400, e.message)
        except Exception as e:
            return _make_error(500, e.message)
    else:
        try:
            return _make_response(response=_cars)
        except Exception as e:
            return _make_error(500, e.message)


if __name__ == "__main__":
    syslog.openlog("My Cars api service", 0, syslog.LOG_LOCAL0)
    syslog.syslog(syslog.LOG_INFO, "My Cars API service starting on localhost:8080")
    app.debug = True
    app.run(host="localhost", port=8080)
    syslog.syslog(syslog.LOG_INFO, "My Cars API service shutting down")
    syslog.closelog()
