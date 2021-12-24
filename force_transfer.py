import numpy as np

height_com = .29
wheelbase = 1.55
lateral_wheelbase = 1.219  # Front
mass = 270
car_COM_x = .823  # Assuming %47 front weight bias


# Calculate the forces on a tire based on the accelerations around the CoM of the Car
# Use superposition to calculate total force on the car
def acceleration_based(x, y, z_force):
    forces = np.array([0, 0, 0])
    static_bias = (wheelbase - car_COM_x) / wheelbase
    # Calculate force from x loading
    weight_adj = (-x * (height_com / wheelbase) * mass) / 2

    # Calculate force from y loading
    # Static bias splits WT between front and rear
    weight_adj = weight_adj + (y * (height_com / lateral_wheelbase) * mass) * static_bias

    # Longitudinal force assume soley based on normal tire force
    # E.G. More downward tire force = more x & y tire forces
    front_weight = (((mass * 9.81) * static_bias) / 2) + (weight_adj * 9.81)
    rear_weight = (((mass * 9.81) * (1 - static_bias)) / 2) - (weight_adj * 9.81)

    new_bias = front_weight / rear_weight

    forces[0] = ((mass * x) / 2) * new_bias
    if (x > 0):
        # No forces imparted on front wheels under accel
        forces[0] = 0
    forces[1] = ((mass * y) / 2) * new_bias

    # Calculate force from z loading, just force as loading is measured in N
    # Assume aero downloading happens through centre of mass, (doesn't effect bias)
    weight_adj = weight_adj + (z_force * static_bias) / 2

    forces[2] = ((mass * 9.81) * static_bias) / 2 + (weight_adj * 9.81)
    #print("Tire loading %: " + str(forces[2] / (9.81 * mass)))

    # Dynamic load multiplication factors
    # Vertical = 3
    # Long/lateral = 1.3

    forces[0] = forces[0] * 1.3
    forces[1] = forces[1] * 1.3
    forces[2] = forces[2] * 3
    return forces
