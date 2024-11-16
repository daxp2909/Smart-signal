import numpy as np

# Traffic simulation class
class TrafficSimulation:
    def __init__(self, distances, speeds, volumes, green_times, emergencies, accidents):
        self.distances = distances
        self.speeds = speeds
        self.volumes = volumes
        self.green_times = green_times
        self.emergencies = set(emergencies)
        self.accidents = set(accidents)
        self.flow = []
        self.bad_scenarios = []

    def optimize_signals(self):
        # Example of dynamic adjustment: Increase green time for high volume signals
        optimized_green_times = [
            max(gt, volume * 2 / 3600 * 60)  # Adjust based on volume
            for gt, volume in zip(self.green_times, self.volumes)
        ]
        return optimized_green_times

    def simulate(self):
        optimized_green_times = self.optimize_signals()
        num_signals = len(self.distances)

        for i in range(num_signals):
            if i in self.accidents:
                self.flow.append(0)  # Traffic is blocked due to an accident
                self.bad_scenarios.append((i, 'Accident'))
            elif i in self.emergencies:
                self.flow.append(5)  # Reduced flow due to an emergency
                self.bad_scenarios.append((i, 'Emergency'))
            else:
                try:
                    # Calculate travel time
                    travel_time = self.distances[i] / self.speeds[i]
                    # Compare travel time with green light duration
                    if travel_time <= optimized_green_times[i]:
                        self.flow.append(10)  # Smooth flow
                    else:
                        # Penalty based on how much the travel time exceeds green time
                        excess_time = travel_time - optimized_green_times[i]
                        penalty = min(9, excess_time / optimized_green_times[i] * 9)  # Cap penalty to 9
                        flow_rating = max(1, 10 - penalty)
                        self.flow.append(flow_rating)
                        if flow_rating < 5:
                            self.bad_scenarios.append((i, f'Low flow (Rating: {flow_rating:.2f})'))
                except ZeroDivisionError:
                    print(f"Warning: Speed cannot be zero at signal index {i}.")
                    self.flow.append(0)
                    self.bad_scenarios.append((i, 'Zero Speed'))

        # Calculate the mean flow rating
        self.rating = np.mean(self.flow) if self.flow else 0
        return self.rating

# Function to calculate green times
def calculate_green_times(distances, speeds, volumes):
    green_times = []
    for distance, speed, volume in zip(distances, speeds, volumes):
        if speed <= 0:
            print(f"Warning: Speed should be greater than zero for distance {distance}.")
            green_times.append(0)
        else:
            travel_time = distance / speed
            volume_green_time = volume * 2 / 3600 * 60  # Convert to seconds
            green_time = max(travel_time, volume_green_time)
            green_times.append(green_time)
    return green_times

# Function to get user input with space-separated values
def get_user_input():
    while True:
        try:
            num_signals = int(input("Enter the number of signals: ").strip())
            if num_signals <= 0:
                raise ValueError("Number of signals must be positive.")

            distances = get_input_list(f"Enter distances between {num_signals} signals (space-separated):", num_signals)
            speeds = get_input_list(f"Enter vehicle speeds for {num_signals} signals (space-separated):", num_signals)
            volumes = get_input_list(f"Enter traffic volumes at {num_signals} signals (space-separated):", num_signals)

            return num_signals, distances, speeds, volumes
        except ValueError as e:
            print(f"Input error: {e}. Please try again.")
        except EOFError:
            print("Input error: Unexpected end of input. Please provide input in the expected format.")

# Function to get list input from the user with space-separated values
def get_input_list(prompt, expected_length):
    print(prompt)
    values = list(map(int, input().strip().split()))
    if len(values) != expected_length:
        raise ValueError(f"Expected {expected_length} values, but got {len(values)}.")
    return values

# Function to get emergency and accident input with space-separated values
def get_emergency_accident_input(num_signals):
    emergencies = get_index_list("Enter indices of signals with emergencies (space-separated) or press Enter to skip:", num_signals)
    accidents = get_index_list("Enter indices of signals with accidents (space-separated) or press Enter to skip:", num_signals)
    return emergencies, accidents

# Function to get list of indices from the user with space-separated values
def get_index_list(prompt, num_signals):
    while True:
        try:
            print(prompt)
            indices_input = input().strip()
            if not indices_input:
                return []
            indices = list(map(int, indices_input.split()))
            if any(i >= num_signals for i in indices):
                raise ValueError("Indices must be within the range of signals.")
            return indices
        except ValueError as e:
            print(f"Input error: {e}. Please try again.")
        except EOFError:
            print("Input error: Unexpected end of input. Please provide input in the expected format.")

# Main execution
def main():
    num_signals, distances, speeds, volumes = get_user_input()
    emergencies, accidents = get_emergency_accident_input(num_signals)
    green_times = calculate_green_times(distances, speeds, volumes)

    print(f"Calculated Green Times for each signal: {green_times}")

    simulation = TrafficSimulation(distances, speeds, volumes, green_times, emergencies, accidents)
    rating = simulation.simulate()

    print(f"Simulation Rating (1-10): {rating:.2f}")  # Format rating to 2 decimal places
    if simulation.bad_scenarios:
        print("Bad Scenarios:")
        for index, reason in simulation.bad_scenarios:
            print(f"Signal {index}: {reason}")

if __name__ == "__main__":
    main()
