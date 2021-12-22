import pandas as pd
import numpy as np
import force_transfer


# Internal units N,mm

# read through string and convert it into an array
def string_2_array(string):
    # Excel likes numbers separated by commas to start with ' so this removes it
    string = string.replace("'", '')
    string = string.split(",")
    number_list = []
    for x in string:
        number_list.append(float(x))
    return np.array(number_list)


# Take numpy array of points and turn it into an array of vectors
def point_2_vector(points_df):
    points = points_df.to_numpy()
    vector_set = []
    for pointSet in points:
        vec = string_2_array(pointSet[0]) - string_2_array(pointSet[1])
        vector_set.append(vec)
    return np.array(vector_set)


# Convert vector to unit vector
def unit_vector(vector_set):
    unit_vector_group = []
    for vector in vector_set:
        single_unit_vector = []
        for direction in vector:
            magnitude = np.sqrt(vector[0] ** 2 + vector[1] ** 2 + vector[2] ** 2)
            single_unit_vector.append(direction / magnitude)
        unit_vector_group.append(single_unit_vector)
    return np.array(unit_vector_group)


# separate x,y,z components and reorder to match system of linear equations <X1 + X2 = X3><Y1 + Y2...
def create_xyz_system(vector_set):
    # Remove last line since they are for moment creation
    cleaned_vectors = vector_set.take([0, 1, 2, 3, 4, 5], axis=0)
    return cleaned_vectors.transpose()


def create_moment_system(vector_set, point_set):
    # Moment is taken about the upper a-arm node as to remove the most amount of linkages from calculation
    # e.g. both a-arms and push-rod
    # Calculate the moment arms from given information in original dataframe
    moments = []
    for link_number in range(0, 6):
        dist = -string_2_array(point_set[0][0]) + string_2_array(point_set[link_number][0])
        val = np.cross(dist, vector_set[link_number])
        moments.append(val)
    return np.array(moments).transpose()


def tire_force_moment(f_tire, points):
    dist = string_2_array(points[0]) - string_2_array(points[1])
    moment = np.cross(dist, np.array(f_tire).transpose())
    return moment.transpose()


def calc_forces(accels, df):
    # Take accelerations and dataframe points
    # Calculate the corresponding forces on each of the linkages of the corner
    vectors = unit_vector(point_2_vector(df))
    coefficient_matrix = create_xyz_system(vectors)
    coefficient_matrix = np.vstack((coefficient_matrix, create_moment_system(vectors, df.to_numpy())))

    forces = force_transfer.acceleration_based(float(accels[0]), float(accels[1]), float(accels[2]))
    # print(forces)
    # print("Solving system of equations...")
    # Turn forces into list then numpy array
    forces = np.array(list(map(int, forces)))

    # Append the moments created from tire contact path to upper node
    forces = np.hstack((forces, tire_force_moment(forces, df.to_numpy()[6])))

    solution = np.linalg.solve(coefficient_matrix, forces)

    return solution
