from flask import Flask, request, render_template
import skfuzzy as fuzz
import skfuzzy.control as ctrl

app = Flask(__name__)

# Define the fuzzy variables
current_floor = ctrl.Antecedent(range(1, 19), 'current_floor')
destination_floor = ctrl.Antecedent(range(1, 19), 'destination_floor')
number_of_passengers = ctrl.Antecedent(range(0, 21), 'number_of_passengers')
elevator_load = ctrl.Antecedent(range(0, 101), 'elevator_load')
direction_of_travel = ctrl.Antecedent([0, 1, 2], 'direction_of_travel')  # 0: Idle, 1: Up, 2: Down
assigned_elevator = ctrl.Consequent(range(1, 5), 'assigned_elevator')

# Define the membership functions
current_floor.automf(3)
destination_floor.automf(3)
number_of_passengers.automf(3)
elevator_load.automf(3)

direction_of_travel['idle'] = fuzz.trimf(direction_of_travel.universe, [0, 0, 0])
direction_of_travel['up'] = fuzz.trimf(direction_of_travel.universe, [1, 1, 1])
direction_of_travel['down'] = fuzz.trimf(direction_of_travel.universe, [2, 2, 2])

assigned_elevator.automf(3)

# Define the rules
rule1 = ctrl.Rule(direction_of_travel['idle'], assigned_elevator['average'])
rule2 = ctrl.Rule(direction_of_travel['up'], assigned_elevator['good'])
rule3 = ctrl.Rule(direction_of_travel['down'], assigned_elevator['poor'])

# Create the control system
elevator_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
elevator_simulation = ctrl.ControlSystemSimulation(elevator_ctrl)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/assign_elevator', methods=['POST'])
def assign_elevator():
    current_floor_input = int(request.form['current_floor'])
    destination_floor_input = int(request.form['destination_floor'])
    number_of_passengers_input = int(request.form['number_of_passengers'])
    elevator_load_input = int(request.form['elevator_load'])
    direction_of_travel_input = int(request.form['direction_of_travel'])

    elevator_simulation.input['current_floor'] = current_floor_input
    elevator_simulation.input['destination_floor'] = destination_floor_input
    elevator_simulation.input['number_of_passengers'] = number_of_passengers_input
    elevator_simulation.input['elevator_load'] = elevator_load_input
    elevator_simulation.input['direction_of_travel'] = direction_of_travel_input

    elevator_simulation.compute()

    assigned_elevator_output = elevator_simulation.output['assigned_elevator']

    return render_template('result.html', assigned_elevator=assigned_elevator_output)

if __name__ == '__main__':
    app.run(debug=True)
