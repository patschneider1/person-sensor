"""
This file registers the model with the Python SDK.
"""

from viam.components.sensor import Sensor
from viam.resource.registry import Registry, ResourceCreatorRegistration

from .personDetection import personDetection

Registry.register_resource_creator(Sensor.SUBTYPE, personDetection.MODEL, ResourceCreatorRegistration(personDetection.new, personDetection.validate))
