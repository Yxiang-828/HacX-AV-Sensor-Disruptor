import carla
import time

def simulate_av_disruption():
    """Test AV stop in CARLA sim"""
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()
    
    # Spawn AV (e.g., Tesla Model 3)
    blueprint = world.get_blueprint_library().find('vehicle.tesla.model3')
    spawn_point = world.get_map().get_spawn_points()[0]
    vehicle = world.spawn_actor(blueprint, spawn_point)
    
    # Apply speed (20 km/h)
    vehicle.set_autopilot(True)
    vehicle.set_target_velocity(carla.Vector3D(5.56, 0, 0))  # 20 km/h
    
    # Simulate disruption (noise/spoof)
    time.sleep(2)  # Run for 2s
    # TODO: Inject sensor noise (LiDAR: fake obstacle, camera: dazzle, radar: echo)
    print("Simulating sensor disruption...")
    vehicle.apply_control(carla.VehicleControl(throttle=0, brake=1.0))  # Force stop
    
    time.sleep(2)
    vehicle.destroy()

if __name__ == "__main__":
    simulate_av_disruption()