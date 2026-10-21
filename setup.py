from setuptools import find_packages, setup

package_name = 'risl_onrobot_ros'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mgao18',
    maintainer_email='mgao18@todo.todo',
    description='ROS 2 wrapper for OnRobot RG2 gripper',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'gripper_control = risl_onrobot_ros.rg_gripper:main',
        ],
    },
)
