import json
import os
from bravado_core.spec import Spec
from bravado_core.validate import validate_object
from yaml import load, Loader, dump, Dumper


def validate_car(car):
    validate_object(spec, Car, car)


def get_swagger_spec():
    with open(spec_path,'r') as spec:
        return load(spec.read(), Loader)


bravado_config = {
    'validate_swagger_spec': False,
    'validate_requests': False,
    'validate_responses': False,
    'use_models': True,
}


dir_path = os.path.dirname(os.path.abspath(__file__))
spec_path = os.path.join(dir_path, "swagger-spec.yaml")
spec_dict = get_swagger_spec()
spec = Spec.from_dict(spec_dict, config=bravado_config)
Car = spec_dict['definitions']['Car']
