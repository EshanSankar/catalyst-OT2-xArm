# Catalyst OT2-xArm System

A modular automated experimental orchestrator for electrochemical experiments using OT2 and xArm6 robots, as well as Arduino devices. This project integrates with https://github.com/EshanSankar/WATCHDOG to enable real-time safety verification of workflows via digital twins.

## Original Project

This project extends the original Catalyst OT2-Arduino system by integrating xArm6 functionality and ROS 2-based communication with a digital twin. This project primarily focuses on the control and orchestration of robotic devices with WATCHDOG. For detailed instructions on how to run chemical experiments, please refer to the original project: https://github.com/SissiFeng/catalyst-OT2

## Usage

To create a JSON file for your workflow, refer to [workflow_schema.json](workflow_schema.json). Custom labware JSON files can be added to the [labware folder](labware/).

## Prerequisites

- Ubuntu 22.04
- Opentrons OT2 robot
- UFACTORY xArm6 robot with xArm gripper
- Network connection to OT2
- Network connection to the computer running WATCHDOG (if separate from the computer running this orchestrator)

WATCHDOG-related prerequisites can be found on the WATCHDOG repository.

## Installation

1. [Install ROS 2 Humble](https://docs.ros.org/en/humble/Installation.html)
2. Create a ROS 2 workspace and project directory. For example:
```bash
mkdir -p ~/ros2_projects/digital_twin
cd ~/ros2_projects/digital_twin
```
3. Install my fork of [UFACTORY's xArm ROS 2 package](https://github.com/EshanSankar/xarm_ros2) in your new workspace.
- My fork comes with [xarm_api/config/xarm_user_params.yaml](https://github.com/EshanSankar/xarm_ros2/blob/humble/xarm_api/config/xarm_user_params.yaml) which enables complete gripper control. I'm also in the process of modifying [xarm_moveit_servo](https://github.com/EshanSankar/xarm_ros2/tree/humble/xarm_moveit_servo) to integrate the existing teleoperation functionality into the orchestrator.
4. Clone this repository into your workspace:
```bash
git clone https://github.com/EshanSankar/catalyst-OT2-xArm.git
cd catalyst-OT2-xArm
```
5. Create and activate a Python virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```
6. Install dependencies:
```bash
pip install -r requirements.txt
```
7. Install package in development mode:
```bash
pip install -e .
```
8. Create necessary directories:
```bash
mkdir -p logs results config
```
9. If you are using a dual-computer setup with WATCHDOG, run the following to ensure the two computers can communicate over ROS:
```bash
export ROS_DOMAIN_ID=0
export ROS_LOCALHOST_ONLY=0
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
sudo ufw disable # disable Ubuntu's Uncomplicated Firewall; optional, but might be necessary
```
It's recommended to add the above export lines to your ```.bashrc``` file.

## Run the Orchestrator

First, enable the xArm6. The following steps have been compiled from the original repository:
1. In a new terminal:
```bash
cd ~/ros2_projects/digital_twin # or whatever your workspace is named
source install/setup.bash

# launch xarm_driver_node:
ros2 launch xarm_api xarm6_driver.launch.py robot_ip:=192.168.1.117 # replace 117 with the last 3 digits of your robot's IP
```
2. Open another terminal and run:
```bash
cd ~/ros2_projects/digital_twin # or whatever your workspace is named
source install/setup.bash

# enable all joints:
ros2 service call /xarm/motion_enable xarm_msgs/srv/SetInt16ById "{id: 8, data: 1}"

# set proper mode (0) and state (0)
ros2 service call /xarm/set_mode xarm_msgs/srv/SetInt16 "{data: 0}"
ros2 service call /xarm/set_state xarm_msgs/srv/SetInt16 "{data: 0}"

# enable the gripper and configure the grasp speed
ros2 service call /xarm/set_gripper_enable xarm_msgs/srv/SetInt16 "{data: 1}"
ros2 service call /xarm/set_gripper_mode xarm_msgs/srv/SetInt16 "{data: 0}"
ros2 service call /xarm/set_gripper_speed xarm_msgs/srv/SetFloat32 "{data: 1500}"

# run the xArm ROS wrapper to be able to control it from the orchestrator
source venv/bin/activate
python3 xarm_wrapper.py
```
2. Open another terminal and run:
```bash
cd ~/ros2_projects/digital_twin # or whatever your workspace is named
source install/setup.bash
source venv/bin/activate

python3 digital_to_real_workflow_executor.py my_workflow.json # replace with your workflow JSON file
```

## Credits
UFACTORY's xArm ROS 2 packages: https://github.com/xArm-Developer/xarm_ros2 \
Sissi Feng's original Catalyst-OT2 orchestrator: https://github.com/SissiFeng/catalyst-OT2/

## License

MIT License

Copyright (c) 2024 Sissi Feng
