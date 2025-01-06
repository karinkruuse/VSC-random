import numpy as np
import matplotlib.pyplot as plt

class PIDController:
    def __init__(self, kp=1.0, ki=0.0, kd=0.0, setpoint=0.0):
        """
        Initialize the PID controller with given gains and setpoint.
        
        Args:
            kp (float): Proportional gain.
            ki (float): Integral gain.
            kd (float): Derivative gain.
            setpoint (float): Desired target value the controller tries to achieve.
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        
        # Internal states
        self.integral = 0.0
        self.previous_error = None

    def update(self, measurement, dt):
        """
        Update the PID controller with a new measurement and calculate the control output.
        
        Args:
            measurement (float): Current measured value.
            dt (float): Time interval since the last update.
            
        Returns:
            float: Control output to be used to adjust the system.
        """
        # Calculate error between the setpoint and the measurement
        error = self.setpoint - measurement

        # Proportional term
        p_term = self.kp * error

        # Integral term with anti-windup check
        self.integral += error * dt
        i_term = self.ki * self.integral

        # Derivative term
        d_term = 0.0
        if self.previous_error is not None:
            d_term = self.kd * (error - self.previous_error) / dt

        # Save error for next derivative calculation
        self.previous_error = error

        # Calculate and return the control output
        control_output = p_term + i_term + d_term
        return control_output

    def reset(self):
        """Reset the internal state of the PID controller."""
        self.integral = 0.0
        self.previous_error = None


# Usage Example
setpoint = 10.0  # Desired target value
initial_measurement = 0.0
dt = 0.1  # Time step in seconds

# Initialize PID controller with specific gains
pid = PIDController(kp=1.2, ki=0.5, kd=0.1, setpoint=setpoint)

# Simulate the control loop
time_steps = 100
measurements = [initial_measurement]
control_outputs = []

for _ in range(time_steps):
    # Simulate a measurement (you could replace this with real system measurements)
    current_measurement = measurements[-1] + np.random.normal(0, 0.5)  # Adding some noise
    control_output = pid.update(current_measurement, dt)
    
    # Store the control output and measurement
    control_outputs.append(control_output)
    measurements.append(current_measurement + control_output * dt)  # Apply control to "system"


time = np.arange(time_steps + 1) * dt
plt.figure(figsize=(12, 6))
plt.plot(time, measurements, label="System Output")
plt.axhline(setpoint, color='r', linestyle='--', label="Setpoint")
plt.xlabel("Time (s)")
plt.ylabel("Measurement")
plt.title("PID Controller Simulation")
plt.legend()
plt.grid()
plt.show()
