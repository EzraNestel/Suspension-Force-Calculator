import pandas as pd
import numpy as np
import force_calculator
import matplotlib.pyplot as plt

# Internal units N,mm

# Dummy data to fill up the dataframe, make sure to edit the excel sheet created with correct information
data = {
    'Point A': ['0, 0, 0', '0, 0, 0', '0, 0, 0', '0, 0, 0', '0, 0, 0', '0, 0, 0', '0, 0, 0'],
    'Point B': ['1, 1, 1', '1, 1, 1', '1, 1, 1', '1, 1, 1', '1, 1, 1', '1, 1, 1', '1, 1, 1']
}

# Set standard for suspension linkages
index_ = ['Top_Front_Forward_A-Arm',
          'Top_Front_Rearward_A-Arm',
          'Push-rod',
          'Bottom_Front_Forward_A-arm',
          'Bottom_Front_Rearward_A-arm',
          'Tie-rod',
          'Tire_Contact_To_Upper_A-Arm_Node']


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


if __name__ == '__main__':
    # If no excel sheet exists, create one and fill with dummy values
    try:
        df = pd.read_excel('suspension_points.xlsx', index_col=0)
    except FileNotFoundError as e:
        # print("No suspension point file found...")
        # print("Creating sheet...")

        df = pd.DataFrame(data)
        df.index = index_
        df.to_excel('suspension_points.xlsx')

    # print("Enter Tire Force Vector (separated by commas)")
    # accels = input("Car x,y acceleration (G) and downforce (N) 'x,y,z': ").split(',')
    #
    # solution = force_calculator.calc_forces(accels, df)
    # print("+: Tension")
    # print("-: Compression")
    # i = 0
    # for linkage in solution:
    #     print(index_[i] + ': ' + str(int(linkage)) + ' N')
    #     i = i + 1

    top_front_for_a = []
    top_front_aft_a = []
    push = []
    bot_front_for_a = []
    bot_front_aft_a = []
    tierod = []

    # Longitudinal Sweep
    for x in range(-20, 10, 1):
        accel = [x / 10, 0, 0]

        solution = force_calculator.calc_forces(accel, df)
        top_front_for_a = np.append(top_front_for_a, solution[0])
        top_front_aft_a = np.append(top_front_aft_a, solution[1])
        push = np.append(push, solution[2])
        bot_front_for_a = np.append(bot_front_for_a, solution[3])
        bot_front_aft_a = np.append(bot_front_aft_a, solution[4])
        tierod = np.append(tierod, solution[5])

    xVal = np.arange(-2, 1, .1)
    # #print(np.reshape(solution_matrix,(30,6)))
    # plt.plot(xVal, top_front_for_a, 'r',
    #          xVal, top_front_aft_a, 'orange',
    #          xVal, push, 'g',
    #          xVal, bot_front_for_a, 'b',
    #          xVal, bot_front_aft_a, 'indigo',
    #          xVal, tierod, 'violet')
    #
    # print(top_front_for_a)
    # plt.show()

    fig, axs = plt.subplots(2, 1)
    tffa, = axs[0].plot(xVal, top_front_for_a, 'r', label=index_[0])
    tfaa, = axs[0].plot(xVal, top_front_aft_a, 'orange', label=index_[1])
    push, = axs[0].plot(xVal, push, 'g', label=index_[2])
    bffa, = axs[0].plot(xVal, bot_front_for_a, 'b', label=index_[3])
    bfaa, = axs[0].plot(xVal, bot_front_aft_a, 'indigo', label=index_[4])
    tie, = axs[0].plot(xVal, tierod, 'violet', label=index_[5])
    axs[0].legend(handles=[tffa, tfaa, push, bffa, bfaa, tie], loc='upper right')
    axs[0].set_xlabel('Longitudinal G')
    axs[0].set_ylabel('Force (N)')
    axs[0].grid(True)
    axs[0].set_yticks(np.arange(-5000, 5000, 100), minor=True)
    axs[0].grid(which='minor', alpha=0.2, linestyle='--')

    # Lateral Sweep
    top_front_for_a = []
    top_front_aft_a = []
    push = []
    bot_front_for_a = []
    bot_front_aft_a = []
    tierod = []
    for y in range(-20, 20, 1):
        accel = [0, y / 10, 0]

        solution = force_calculator.calc_forces(accel, df)
        top_front_for_a = np.append(top_front_for_a, solution[0])
        top_front_aft_a = np.append(top_front_aft_a, solution[1])
        push = np.append(push, solution[2])
        bot_front_for_a = np.append(bot_front_for_a, solution[3])
        bot_front_aft_a = np.append(bot_front_aft_a, solution[4])
        tierod = np.append(tierod, solution[5])
    yVal = np.arange(-2, 2, .1)

    tffa, = axs[1].plot(yVal, top_front_for_a, 'r', label=index_[0])
    tfaa, = axs[1].plot(yVal, top_front_aft_a, 'orange', label=index_[1])
    push, = axs[1].plot(yVal, push, 'g', label=index_[2])
    bffa, = axs[1].plot(yVal, bot_front_for_a, 'b', label=index_[3])
    bfaa, = axs[1].plot(yVal, bot_front_aft_a, 'indigo', label=index_[4])
    tie, = axs[1].plot(yVal, tierod, 'violet', label=index_[5])
    axs[1].legend(handles=[tffa, tfaa, push, bffa, bfaa, tie], loc='upper left')
    axs[1].set_xlabel('Lateral G')
    axs[1].set_ylabel('Force (N)')
    axs[1].grid(True)
    axs[1].set_yticks(np.arange(-5000, 5000, 100), minor=True)
    axs[1].grid(which='minor', alpha=0.2, linestyle='--')

    fig.suptitle('Front Right Corner Assembly Loads')
    plt.show()
