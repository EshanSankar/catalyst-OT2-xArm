import rclpy
from rclpy.node import Node
from xarm_msgs.srv import SetInt16ById, SetInt16, MoveCartesian, MoveJoint
from typing import List

class xArmClient(Node):
    def __init__(self):
        super().__init__('xarm_client')
        self.motion_enable_client = self.create_client(SetInt16ById, "/xarm/motion_enable")
        self.set_mode_client = self.create_client(SetInt16ById, "/xarm/set_mode")
        self.set_state_client = self.create_client(SetInt16ById, "/xarm/set_state")
        self.set_position_client = self.create_client(MoveCartesian, "/xarm/set_position")
        self.set_servo_angle_client = self.create_client(MoveJoint, "/xarm/set_servo_angle")
        self.get_logger.info("Waiting for xArm services...")
        self.motion_enable_client.wait_for_service(timeout_sec=5.0)
        self.set_mode_client.wait_for_service(timeout_sec=5.0)
        self.set_state_client.wait_for_service(timeout_sec=5.0)
        self.set_position_client.wait_for_service(timeout_sec=5.0)
        self.set_servo_angle_client.wait_for_service(timeout_sec=5.0)
        self.get_logger.info("xArm services available")
    def motion_enable(self, on: bool = True):
        req = SetInt16ById.Request()
        req.id = 8
        req.data = 1 if on else 0
        return self._call_service(self.motion_enable_client, req, "motion_enable")
    def set_mode(self, mode: int=0):
        req = SetInt16.Request()
        req.data = mode
        return self._call_service(self.set_mode_client, req, "set_mode")
    def set_state(self, state: int=0):
        req = SetInt16.Request()
        req.data = state
        return self._call_service(self.set_state_client, req, "set_state")
    def set_position(self, pose: List[float], speed: int=100, acc: int=500, mvtime: int=0):
        req = MoveCartesian.Request()
        req.pose = pose
        req.speed = speed
        req.acc = acc
        req.mvtime = mvtime
        return self._call_service(self.set_position_client, req, "set_position")
    def set_servo_angle(self, angles: List[float], speed: int=100, acc: int=500, mvtime: int=0, relative: bool=True):
        req = MoveJoint.Request()
        req.angles = angles
        req.speed = speed
        req.acc = acc
        req.mvtime = mvtime
        req.relative = relative
        return self._call_service(self.set_servo_angle_client, req, "set_position")
    def _call_service(self, client, request, service):
        self.get_logger.info(f"Calling /xarm/{service}...")
        future = client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        if future.result() is not None:
            self.get_logger.info(f"Successfully called /xarm/{service}")
        else:
            self.get_logger.error(f"Failed to call /xarm/{service}: {future.exception()}")