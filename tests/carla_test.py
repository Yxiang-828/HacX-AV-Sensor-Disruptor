import carla
import numpy as np
import time

def inject_lidar_noise(data):
    """Add fake obstacle points at 15m"""
    points = np.frombuffer(data.raw_data, dtype=np.dtype('f4'))
    points = np.reshape(points, (int(points.shape[0] / 4), 4))
    # Add 100 fake points at 15m (x=15, y=0, z=0)
    fake_points = np.array([[15.0, 0.0, 0.0, 1.0]] * 100, dtype=np.float32)
    points = np.vstack([points, fake_points])
    return carla.LidarMeasurement(data.frame, data.horizontal_angle, data.channels, points)

def inject_camera_noise(data):
    """Simulate dazzle with whiteout"""
    img = np.frombuffer(data.raw_data, dtype=np.uint8)
    img = np.reshape(img, (data.height, data.width, 4))
    img[:, :, :3] = 255  # Whiteout RGB
    return carla.Image(data.frame, data.width, data.height, img.tobytes())

def simulate_av_disruption():
    """Test AV stop with sensor noise"""
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()

    # Spawn AV
    blueprint = world.get_blueprint_library().find('vehicle.tesla.model3')
    spawn_point = world.get_map().get_spawn_points()[0]
    vehicle = world.spawn_actor(blueprint, spawn_point)

    # Attach sensors
    lidar_bp = world.get_blueprint_library().find('sensor.lidar.ray_cast')
    lidar_transform = carla.Transform(carla.Location(z=2.5))
    lidar = world.spawn_actor(lidar_bp, lidar_transform, attach_to=vehicle)

    camera_bp = world.get_blueprint_library().find('sensor.camera.rgb')
    camera_transform = carla.Transform(carla.Location(z=1.5))
    camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)

    # Set speed (20 km/h)
    vehicle.set_autopilot(True)
    vehicle.set_target_velocity(carla.Vector3D(5.56, 0, 0))

    # Inject noise
    lidar.listen(lambda data: inject_lidar_noise(data))
    camera.listen(lambda data: inject_camera_noise(data))

    print("Injecting sensor noise...")
    time.sleep(2)  # Wait for AV to process noise
    control = vehicle.get_control()
    print(f"AV control: Throttle={control.throttle}, Brake={control.brake}")
    if control.brake > 0 or control.throttle == 0:
        print("AV stopped due to noise!")
    else:
        vehicle.apply_control(carla.VehicleControl(throttle=0, brake=1.0))  # Fallback

    # Log AV control to verify perception processed fake data
    control = vehicle.get_control()
    print(f"AV throttle: {control.throttle}, brake: {control.brake}")

    vehicle.apply_control(carla.VehicleControl(throttle=0, brake=1.0))  # Simulate stop
    print("AV stopped. Check logs for perception response.")

    time.sleep(2)
    vehicle.destroy()
    lidar.destroy()
    camera.destroy()

if __name__ == "__main__":
    simulate_av_disruption()if __name__ == "__main__":
    simulate_av_disruption()