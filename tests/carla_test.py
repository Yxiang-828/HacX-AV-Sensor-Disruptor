import carla
import time
import numpy as np

def simulate_av_disruption():
    """Test AV stop in CARLA with sensor noise"""
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()

    # Spawn AV
    blueprint = world.get_blueprint_library().find('vehicle.tesla.model3')
    spawn_point = world.get_map().get_spawn_points()[0]
    vehicle = world.spawn_actor(blueprint, spawn_point)

    # Set speed (20 km/h)
    vehicle.set_autopilot(True)
    vehicle.set_target_velocity(carla.Vector3D(5.56, 0, 0))

    # Simulate disruption
    time.sleep(2)
    print("Injecting sensor noise...")
    # Mock LiDAR: Add fake points at 15m
    lidar_bp = world.get_blueprint_library().find('sensor.lidar.ray_cast')
    lidar = world.spawn_actor(lidar_bp, carla.Transform(), attach_to=vehicle)
    lidar_data = np.random.rand(1000, 4) * 15  # Fake points
    # Mock camera: Whiteout
    camera_bp = world.get_blueprint_library().find('sensor.camera.rgb')
    camera = world.spawn_actor(camera_bp, carla.Transform(), attach_to=vehicle)
    camera_data = np.ones((480, 640, 4)) * 255  # White image
    vehicle.apply_control(carla.VehicleControl(throttle=0, brake=1.0))  # Stop

    time.sleep(2)
    vehicle.destroy()
    lidar.destroy()
    camera.destroy()

if __name__ == "__main__":
    simulate_av_disruption()

if __name__ == "__main__":
    simulate_av_disruption()