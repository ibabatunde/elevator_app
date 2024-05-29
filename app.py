from flask import Flask, render_template, request
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

app = Flask(__name__)

# Define fuzzy variables for inputs
current_floor = ctrl.Antecedent(np.arange(1, 19, 1), 'current_floor')
destination_floor = ctrl.Antecedent(np.arange(1, 19, 1), 'destination_floor')
number_of_passengers = ctrl.Antecedent(np.arange(0, 21, 1), 'number_of_passengers')
elevator_load = ctrl.Antecedent(np.arange(0, 101, 1), 'elevator_load')
direction_of_travel = ctrl.Antecedent(np.arange(0, 3, 1), 'direction_of_travel')

# Define fuzzy variables for outputs
elevator_assignment = ctrl.Consequent(np.arange(0, 5, 1), 'elevator_assignment')

# Membership functions for current floor
current_floor['low'] = fuzz.trimf(current_floor.universe, [1, 1, 9])
current_floor['medium'] = fuzz.trimf(current_floor.universe, [5, 9, 13])
current_floor['high'] = fuzz.trimf(current_floor.universe, [9, 18, 18])

# Membership functions for destination floor
destination_floor['low'] = fuzz.trimf(destination_floor.universe, [1, 1, 9])
destination_floor['medium'] = fuzz.trimf(destination_floor.universe, [5, 9, 13])
destination_floor['high'] = fuzz.trimf(destination_floor.universe, [9, 18, 18])

# Membership functions for number of passengers
number_of_passengers['few'] = fuzz.trimf(number_of_passengers.universe, [0, 0, 10])
number_of_passengers['moderate'] = fuzz.trimf(number_of_passengers.universe, [5, 10, 15])
number_of_passengers['many'] = fuzz.trimf(number_of_passengers.universe, [10, 20, 20])

# Membership functions for elevator load
elevator_load['light'] = fuzz.trimf(elevator_load.universe, [0, 0, 50])
elevator_load['moderate'] = fuzz.trimf(elevator_load.universe, [25, 50, 75])
elevator_load['heavy'] = fuzz.trimf(elevator_load.universe, [50, 100, 100])

# Membership functions for direction of travel
direction_of_travel['idle'] = fuzz.trimf(direction_of_travel.universe, [0, 0, 0])
direction_of_travel['up'] = fuzz.trimf(direction_of_travel.universe, [0, 1, 2])
direction_of_travel['down'] = fuzz.trimf(direction_of_travel.universe, [1, 2, 2])

# Membership functions for elevator assignment (1 to 4)
elevator_assignment['elevator_1'] = fuzz.trimf(elevator_assignment.universe, [0, 0, 1])
elevator_assignment['elevator_2'] = fuzz.trimf(elevator_assignment.universe, [1, 1, 2])
elevator_assignment['elevator_3'] = fuzz.trimf(elevator_assignment.universe, [2, 2, 3])
elevator_assignment['elevator_4'] = fuzz.trimf(elevator_assignment.universe, [3, 3, 4])

# Define the rules
rule1 = ctrl.Rule(number_of_passengers['many'] & elevator_load['light'] & direction_of_travel['idle'], elevator_assignment['elevator_1'])
rule2 = ctrl.Rule(current_floor['low'] & destination_floor['high'] & direction_of_travel['idle'], elevator_assignment['elevator_2'])
rule3 = ctrl.Rule(current_floor['high'] & destination_floor['low'] & direction_of_travel['idle'], elevator_assignment['elevator_3'])
rule4 = ctrl.Rule(number_of_passengers['few'] & elevator_load['heavy'], elevator_assignment['elevator_4'])

# Create the control system
elevator_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4])
elevator_sim = ctrl.ControlSystemSimulation(elevator_ctrl)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/assign_elevator', methods=['POST'])
def assign_elevator():
    # Get inputs from form
    current_floor_input = int(request.form['current_floor'])
    destination_floor_input = int(request.form['destination_floor'])
    number_of_passengers_input = int(request.form['number_of_passengers'])
    elevator_load_input = int(request.form['elevator_load'])
    direction_of_travel_input = int(request.form['direction_of_travel'])

    # Pass inputs to the fuzzy control system
    elevator_sim.input['current_floor'] = current_floor_input
    elevator_sim.input['destination_floor'] = destination_floor_input
    elevator_sim.input['number_of_passengers'] = number_of_passengers_input
    elevator_sim.input['elevator_load'] = elevator_load_input
    elevator_sim.input['direction_of_travel'] = direction_of_travel_input

    # Compute the result
    elevator_sim.compute()

    # Get the result
    assigned_elevator = elevator_sim.output['elevator_assignment']

    return render_template('result.html', assigned_elevator=assigned_elevator)

if __name__ == '__main__':
    app.run(debug=True)
