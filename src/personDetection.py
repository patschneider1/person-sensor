from typing import ClassVar, Mapping, Sequence, Any, Dict, Optional, Tuple, Final, List, cast
from typing_extensions import Self
from typing import Any, Final, Mapping, Optional
from viam.utils import SensorReading
from viam.module.types import Reconfigurable
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName, Vector3
from viam.resource.base import ResourceBase
from viam.resource.types import Model, ModelFamily
from viam.components.camera import Camera
from viam.module.module import Module
from viam.resource.registry import Registry, ResourceCreatorRegistration
from viam.services.vision import Vision
from viam.resource.easy_resource import EasyResource
from sensor_python import Sensor
from viam.logging import getLogger
import time
import asyncio

LOGGER = getLogger(__name__)

class personDetection(Sensor, Reconfigurable):

    MODEL: ClassVar[Model] = Model(ModelFamily("patricks", "person-sensor"), "person-detection")

    def __init__(self, name: str):
        super().__init__(name=name)

    @classmethod
    def new(cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]) -> Self:
        service = cls(config.name)
        service.reconfigure(config, dependencies)
        return service

    # Validates JSON Configuration
    @classmethod
    def validate_config(cls, config: ComponentConfig):
        vision_service = config.attributes.fields["vision_service"].string_value 
        camera_name = config.attributes.fields["camera_name"].string_value
        attributes = struct_to_dict(config.attributes)

        if vision_service not in attributes:
            raise ValueError("A vision service required, but not found.")
        if camera_name not in attributes:
            raise ValueError("A camera is required, but not found.")

        return [vision_service, camera_name]
        

    def reconfigure(self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]):
        self.vision_service_name = ocnfig.attributes.fields["vision_service"].string_value
        self.camera_name = ocnfig.attributes.fields["camera_name"].string_value
        self.dependencies = dependencies
    

    async def get_readings(
        self, *, extra: Optional[Mapping[str, Any]] = None, timeout: Optional[float] = None, **kwargs
    ) -> Mapping[str, Any]:
        # Get camera from dependencies
        camera = self.dependencies.get(ResourceName(name=self.camera_name))
        if not camera:
            raise ValueError(f"Camera {self.camera_name} is not available")
        
        # Get vision service from dependencies
        vision_service = self.dependencies.get(ResourceName(namespace="rdk", type="service", subtype="vision", name=self.vision_service_name))
        if not vision_service:
            raise ValueError(f"Vision service {self.vision_service_name} is not available")
        
        # Get image from camera
        image = await camera.get_image()
        if not image:
            raise ValueError("Failed to get image from camera")
        
        # Get detections from vision service
        detections = await vision_service.get_detections(image)
        person_detected = any(
            detection.class_name.lower() == "person" 
            for detection in detections
        )

        LOGGER.info(f"Person detected: {person_detected}")

        return {
            "person_detected": 1 if person_detected else 0
        }
        
if __name__ == "__main__":
    asyncio.run(Module.run_from_registry())

