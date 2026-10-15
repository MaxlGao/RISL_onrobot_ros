#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import sys
import os
import time
import subprocess
from std_msgs.msg import String, Float64  # Message type for commands

# # Fix onrobot.py path
# onrobot_path = "/home/kpatnaik/Desktop/colcon_ws/src/onrobot-rg/src"
# if onrobot_path not in sys.path:
#     sys.path.append(onrobot_path)

from onrobot_ros.custom_libraries.onrobot import RG  # Import OnRobot RG class

class RGGripperNode(Node):
    def __init__(self):
        super().__init__('rg_gripper')

        # Use `/tmp/ttyUR` instead of IP
        self.declare_parameter('gripper', 'rg2')
        self.declare_parameter('device', '/tmp/ttyUR')  # Default to socat virtual serial port

        self.gripper_type = self.get_parameter('gripper').value
        self.device = self.get_parameter('device').value

        self.get_logger().info(f"Connecting to {self.gripper_type} gripper at {self.device}")

        # Ensure `socat` is running before trying to connect
        self.ensure_socat()

        # Initialize gripper using serial device
        self.rg = RG(gripper=self.gripper_type, device=self.device)

        # Subscribe to `/gripper_command` topic
        self.subscription = self.create_subscription(
            String,
            'gripper_command',
            self.command_callback,
            10)
        
        self.gripper_width_pub = self.create_publisher(Float64, 'gripper_queried_width', 10)
        
        self.get_logger().info("Waiting for gripper commands on /gripper_command topic...")

    def ensure_socat(self):
        """Ensure socat is running to forward the virtual serial port."""
        socat_cmd = f"socat -d -d pty,link={self.device},raw,ignoreeof,waitslave tcp:192.168.1.111:54321"
        self.get_logger().info(f"Starting socat: {socat_cmd}")

        # Run socat in a subprocess
        subprocess.Popen(socat_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)  # Give socat time to start

    def command_callback(self, msg: String):
        """Handles incoming ROS 2 commands for the gripper."""
        command = msg.data.lower()
        self.get_logger().info(f"Received command: {command}")

        if command == "open":
            self.get_logger().info("Opening gripper...")
            self.rg.open_gripper()
        elif command == "close":
            self.get_logger().info("Closing gripper...")
            self.rg.close_gripper()
        elif command == "query":
            width_mm = self.rg.get_width_with_offset()
            msg = Float64()
            msg.data = width_mm
            self.gripper_width_pub.publish(msg)
            self.get_logger().info(f"Query gripper. Answer: {width_mm}")
        elif command.isdigit():
            width_mm = self.rg.get_width_with_offset()
            width = int(command)
            self.get_logger().info(f"Moving to {(0.1*width):4.1f} mm, from {width_mm}")
            self.rg.move_gripper(width)
        else:
            self.get_logger().warn("Unknown command received.")

def main(args=None):
    rclpy.init(args=args)
    node = RGGripperNode()
    rclpy.spin(node)  # Keeps node alive for commands
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
