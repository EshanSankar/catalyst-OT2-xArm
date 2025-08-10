import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32
from xarm_msgs.srv import SetInt16ById, SetInt16, MoveCartesian, MoveJoint, GripperMove, GetFloat32
from typing import List

class xArmClient(Node):
    def __init__(self):
        super().__init__('xarm_client')
        self.action_subscriber = self.create_subscription(String, "/orchestrator/xarm/action", self.action_callback, 10)
        self.motion_enable_client = self.create_client(SetInt16ById, "/xarm/motion_enable")
        self.set_mode_client = self.create_client(SetInt16ById, "/xarm/set_mode")
        self.set_state_client = self.create_client(SetInt16ById, "/xarm/set_state")
        self.set_position_client = self.create_client(MoveCartesian, "/xarm/set_position")
        self.set_servo_angle_client = self.create_client(MoveJoint, "/xarm/set_servo_angle")
        self.set_gripper_position_client = self.create_client(GripperMove, "/xarm/set_gripper_position")
        self.get_gripper_position_client = self.create_client(GetFloat32, "/xarm/get_gripper_position")
        self.get_logger().info("Waiting for xArm services...")
        self.motion_enable_client.wait_for_service(timeout_sec=1.0)
        self.set_mode_client.wait_for_service(timeout_sec=1.0)
        self.set_state_client.wait_for_service(timeout_sec=1.0)
        self.set_position_client.wait_for_service(timeout_sec=1.0)
        self.set_servo_angle_client.wait_for_service(timeout_sec=1.0)
        self.set_gripper_position_client.wait_for_service(timeout_sec=1.0)
        self.get_gripper_position_client.wait_for_service(timeout_sec=1.0)
        self.get_logger().info("xArm services available")
        self.gripper_position_publisher = self.create_publisher(Float32, "/orchestrator/gripper_position", 10)
        self._call_service(self.get_gripper_position_client, GetFloat32.Request(), "get_gripper_position")
    def action_callback(self, msg: String):
        action = msg.data
        if action == "motion_enable":
            self.motion_enable(True)
        elif action == "set_mode":
            self.set_mode(0)
        elif action == "set_state":
            self.set_state(0)
        elif action.startswith("set_position"):
            raw = action.split(" ")
            self.set_position([float(x) for x in raw[1:7]], raw[7], raw[8], raw[9])
        elif action.startswith("set_servo_angle"):
            raw = action.split(" ")
            raw[11] = True if raw[11] == "True" else False
            self.set_servo_angle([float(x) for x in raw[1:8]], float(raw[8]), float(raw[9]), float(raw[10]), raw[11])
        elif action.startswith("set_gripper_position"):
            raw = action.split(" ")
            self.set_gripper_position(float(raw[1]))
        elif action.startswith("get_gripper_position"):
            self.get_gripper_position()
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
    def set_servo_angle(self, angles: List[float], speed: float=100, acc: float=500, mvtime: float=0, relative: bool=True):
        req = MoveJoint.Request()
        req.angles = angles
        req.speed = speed
        req.acc = acc
        req.mvtime = mvtime
        req.relative = relative
        return self._call_service(self.set_servo_angle_client, req, "set_servo_angle")
    def set_gripper_position(self, pos: float):
        req = GripperMove.Request()
        req.pos = pos
        return self._call_service(self.set_gripper_position_client, req, "set_gripper_position")
    def get_gripper_position(self):
        req = GetFloat32.Request()
        return self._call_service(self.get_gripper_position_client, req, "get_gripper_position")
    def _call_service(self, client, request, service):
        self.get_logger().info(f"Calling /xarm/{service}...")
        future = client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        if future.result() is not None:
            if service == "get_gripper_position":
                self.gripper_position_publisher.publish(Float32(data=future.result().data))
            self.get_logger().info(f"Successfully called /xarm/{service}")
        else:
            self.get_logger().error(f"Failed to call /xarm/{service}: {future.exception()}")

def main():
    rclpy.init()
    xarm_client = xArmClient()
    rclpy.spin(xarm_client)
    xarm_client.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()