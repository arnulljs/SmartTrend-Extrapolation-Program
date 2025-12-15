import math
from typing import List, Dict, Any, Tuple
from lagrange import lagrange_interpolation
from dividedDifference import divided_difference_interpolation

class SmartTrendExtrapolator:
    """
    Core class for the SmartTrend Extrapolation Program.
    Handles data collection, configuration, and performs 
    Lagrange and Divided Difference extrapolation.
    """

    def __init__(self):
        # Time-series data points: [{'x': time, 'y': value}, ...]
        self.data_points: List[Dict[str, float]] = []
        # Configuration settings
        self.config: Dict[str, Any] = {
            'x_title': 'Time',
            'y_title': 'Value',
            'method': 'Lagrange', # Default method
            'num_points': 5,      # Default number of points for subset
            'extrapolation_value': None # The future x-value to predict
        }
        # The subset of points selected for extrapolation
        self.subset: List[Dict[str, float]] = []
        # Predicted outputs
        self.predictions: List[Dict[str, float]] = []
        self.last_solution: str = ""  # Store the solution steps

    def collect_data_points(self, data: List[Tuple[float, float]]):
        """
        Collects initial time-series data points (x, y).
        
        Args:
            data: A list of (x, y) tuples representing the historical data.
        """
        print("--- Data Collection ---")
        self.data_points = [{'x': x, 'y': y} for x, y in data]
        print(f"Collected {len(self.data_points)} data points.")

    def get_max_x(self) -> float:
        """Returns the largest X value in the current data set; 0 if empty."""
        return max((p['x'] for p in self.data_points), default=0)

    def set_prediction_horizon(self, horizon_value: float) -> float:
        """Sets extrapolation target based on a horizon added to the current max X."""
        max_x = self.get_max_x()
        target_x = max_x + horizon_value
        self.config['extrapolation_value'] = target_x
        print(f"Horizon set: +{horizon_value} (Target X={target_x})")
        return target_x

    def set_configuration(self, x_title: str, y_title: str, method: str, num_points: int, predict_x: float):
        """
        Inputs additional details for the extrapolation process.
        
        Args:
            x_title: Title for the x-axis (e.g., 'Time in Hours').
            y_title: Title for the y-axis (e.g., 'Temperature in C').
            method: Extrapolation method ('Lagrange' or 'Divided Difference').
            num_points: The number of closest points to use (Min 2, Max available data points).
            predict_x: The x-value for which to predict the y-value.
        """
        print("--- Configuration Setup ---")
        self.config['extrapolation_value'] = predict_x
        self.config['x_title'] = x_title
        self.config['y_title'] = y_title
        self.config['method'] = method
        # Clamp num_points between 2 and total available data points
        max_points = len(self.data_points)
        self.config['num_points'] = max(2, min(max_points, num_points))
        print(f"Method: {self.config['method']}, Subset Size: {self.config['num_points']}, Predict at X={predict_x}")

    def select_extrapolation_subset(self):
        """
        Selects the specified number of data points closest to the prediction X value.
        """
        N = self.config['num_points']
        x_predict = self.config['extrapolation_value']
        
        if len(self.data_points) < 2:
            raise ValueError("Not enough data points collected for extrapolation (minimum 2 required).")

        # Sort data by distance from prediction point
        sorted_data = sorted(self.data_points, key=lambda p: abs(p['x'] - x_predict))
        
        # Select the N closest points
        self.subset = sorted_data[:N]
        print(f"Selected {len(self.subset)} data points closest to X={x_predict}:")
        for p in self.subset:
            print(f"  ({p['x']:.2f}, {p['y']:.2f})")

    def assess_koi_risk(self, do_value: float) -> dict:
        """Assess dissolved oxygen risk level for Koi fish health."""
        if do_value >= 6.0:
            return {
                'status': 'SAFE',
                'message': 'Optimal oxygen level',
                'action': 'Maintain current aeration',
                'color': '#00FF00'
            }
        if 4.0 <= do_value <= 5.9:
            return {
                'status': 'CAUTION',
                'message': 'Oxygen slightly low',
                'action': 'Increase aeration and monitor closely',
                'color': '#FFFF00'
            }
        if 3.0 <= do_value <= 3.9:
            return {
                'status': 'DANGER',
                'message': 'Oxygen dangerously low',
                'action': 'Add aeration immediately and reduce stocking stressors',
                'color': '#FFA500'
            }
        return {
            'status': 'CRITICAL',
            'message': 'Oxygen critically low',
            'action': 'Activate aerators immediately and consider emergency oxygenation',
            'color': '#FF0000'
        }

    def generate_lagrange_solution(self, x_data: List[float], y_data: List[float], x_predict: float) -> str:
        """Generate step-by-step Lagrange interpolation solution."""
        n = len(x_data)
        solution = []
        solution.append("=" * 50)
        solution.append("LAGRANGE INTERPOLATION - STEP BY STEP SOLUTION")
        solution.append("=" * 50)
        solution.append(f"\nGiven Data Points (n = {n}):")
        for i, (x, y) in enumerate(zip(x_data, y_data)):
            solution.append(f"  P{i}: (x{i}, y{i}) = ({x:.4f}, {y:.4f})")
        solution.append(f"\nTarget X value to predict: x = {x_predict:.4f}")
        solution.append("\n" + "-" * 50)
        solution.append("Lagrange Formula:")
        solution.append("P(x) = SUM [y_j * L_j(x)]  for j = 0 to n-1")
        solution.append("where L_j(x) = PRODUCT [(x - x_i) / (x_j - x_i)]  for i != j")
        solution.append("-" * 50)
        
        P_x = 0.0
        for j in range(n):
            solution.append(f"\n--- Computing L_{j}(x) ---")
            L_j_x = 1.0
            numerator_terms = []
            denominator_terms = []
            
            for i in range(n):
                if i != j:
                    num = x_predict - x_data[i]
                    denom = x_data[j] - x_data[i]
                    numerator_terms.append(f"({x_predict:.4f} - {x_data[i]:.4f})")
                    denominator_terms.append(f"({x_data[j]:.4f} - {x_data[i]:.4f})")
                    L_j_x *= num / denom
            
            solution.append(f"L_{j}(x) = [{' * '.join(numerator_terms)}]")
            solution.append(f"         / [{' * '.join(denominator_terms)}]")
            solution.append(f"L_{j}({x_predict:.4f}) = {L_j_x:.6f}")
            
            term = y_data[j] * L_j_x
            solution.append(f"y_{j} * L_{j}(x) = {y_data[j]:.4f} * {L_j_x:.6f} = {term:.6f}")
            P_x += term
        
        solution.append("\n" + "=" * 50)
        solution.append("FINAL CALCULATION:")
        solution.append(f"P({x_predict:.4f}) = SUM [y_j * L_j(x)]")
        terms_str = " + ".join([f"({y_data[j]:.4f} * L_{j})" for j in range(n)])
        solution.append(f"P({x_predict:.4f}) = {terms_str}")
        solution.append(f"\nPREDICTED VALUE: P({x_predict:.4f}) = {P_x:.6f}")
        solution.append("=" * 50)
        
        return "\n".join(solution)

    def generate_divided_diff_solution(self, x_data: List[float], y_data: List[float], x_predict: float) -> str:
        """Generate step-by-step Divided Difference interpolation solution."""
        n = len(x_data)
        solution = []
        solution.append("=" * 50)
        solution.append("NEWTON'S DIVIDED DIFFERENCE - STEP BY STEP SOLUTION")
        solution.append("=" * 50)
        solution.append(f"\nGiven Data Points (n = {n}):")
        for i, (x, y) in enumerate(zip(x_data, y_data)):
            solution.append(f"  P{i}: (x{i}, y{i}) = ({x:.4f}, {y:.4f})")
        solution.append(f"\nTarget X value to predict: x = {x_predict:.4f}")
        solution.append("\n" + "-" * 50)
        solution.append("Divided Difference Formula:")
        solution.append("P(x) = f[x0] + f[x0,x1](x-x0) + f[x0,x1,x2](x-x0)(x-x1) + ...")
        solution.append("-" * 50)
        
        # Build divided difference table using same method as actual calculation
        coef = list(y_data)
        
        solution.append("\n--- Building Divided Difference Table ---")
        solution.append(f"\nOrder 0 (f[x_i] = y_i):")
        for i in range(n):
            solution.append(f"  f[x{i}] = {coef[i]:.6f}")
        
        # Store coefficients for final polynomial
        coefficients = [coef[0]]
        
        for j in range(1, n):
            solution.append(f"\nOrder {j} Divided Differences:")
            for i in range(n - 1, j - 1, -1):
                old_val = coef[i]
                old_prev = coef[i-1]
                coef[i] = (coef[i] - coef[i-1]) / (x_data[i] - x_data[i-j])
                solution.append(f"  f[x{i-j},...,x{i}] = ({old_val:.6f} - {old_prev:.6f}) / ({x_data[i]:.4f} - {x_data[i-j]:.4f})")
                solution.append(f"                    = {coef[i]:.6f}")
            coefficients.append(coef[j])
        
        # Show coefficients
        solution.append("\n--- Coefficients for Newton's Polynomial ---")
        for j, c in enumerate(coefficients):
            solution.append(f"  c{j} = {c:.6f}")
        
        # Evaluate polynomial using Horner's method
        solution.append(f"\n--- Evaluating P({x_predict:.4f}) using Horner's Method ---")
        P_x = coefficients[n - 1]
        solution.append(f"Starting with c{n-1} = {P_x:.6f}")
        
        for i in range(n - 2, -1, -1):
            old_P = P_x
            P_x = P_x * (x_predict - x_data[i]) + coefficients[i]
            solution.append(f"P = {old_P:.6f} * ({x_predict:.4f} - {x_data[i]:.4f}) + {coefficients[i]:.6f} = {P_x:.6f}")
        
        solution.append("\n" + "=" * 50)
        solution.append(f"PREDICTED VALUE: P({x_predict:.4f}) = {P_x:.6f}")
        solution.append("=" * 50)
        
        return "\n".join(solution)

    def extrapolate_and_store(self):
        """
        Executes the selected extrapolation method on the data subset 
        and stores the resulting prediction.
        """
        if not self.subset:
            print("Error: No subset selected. Run select_extrapolation_subset first.")
            return

        x_data = [p['x'] for p in self.subset]
        y_data = [p['y'] for p in self.subset]
        x_predict = self.config['extrapolation_value']
        
        if x_predict is None:
            print("Error: Extrapolation target value (predict_x) is not set.")
            return

        print(f"--- Performing Extrapolation ({self.config['method']}) ---")
        
        try:
            if self.config['method'] == 'Lagrange':
                y_predicted = lagrange_interpolation(x_data, y_data, x_predict)
                self.last_solution = self.generate_lagrange_solution(x_data, y_data, x_predict)
            elif self.config['method'] == 'Divided Difference':
                y_predicted = divided_difference_interpolation(x_data, y_data, x_predict)
                self.last_solution = self.generate_divided_diff_solution(x_data, y_data, x_predict)
            else:
                raise ValueError(f"Unknown extrapolation method: {self.config['method']}")
            
            # Print solution to console
            print(self.last_solution)
                
            # Store the prediction
            prediction = {
                'x': x_predict,
                'y': y_predicted,
                'method': self.config['method'],
                'subset_size': len(self.subset),
                'risk': self.assess_koi_risk(y_predicted),
                'solution': self.last_solution
            }
            self.predictions.append(prediction)
            print("Extrapolation successful.")
            
        except Exception as e:
            print(f"Extrapolation failed: {e}")
            # Store prediction with error
            self.last_solution = f"Error generating solution: {e}"
            raise

    def display_predicted_outputs(self):
        """
        Displays the stored predicted outputs.
        """
        print("\n==============================================")
        print("          Extrapolated Forecast Curve           ")
        print("==============================================")
        
        if not self.predictions:
            print("No predictions have been generated yet.")
            return

        x_title = self.config['x_title']
        y_title = self.config['y_title']
        
        print(f"X-Axis: {x_title} | Y-Axis: {y_title}\n")

        for i, pred in enumerate(self.predictions, 1):
            print(f"Prediction {i}:")
            print(f"  Method Used: {pred['method']} (Subset Size: {pred['subset_size']})")
            print(f"  {x_title} (X-Value): {pred['x']:.4f}")
            print(f"  {y_title} (Predicted Y-Value): {pred['y']:.4f}")
            risk = pred['risk']
            print(f"  DO Risk Assessment: {risk['status']} - {risk['message']}")
            print(f"  Recommended Action: {risk['action']}")
            print("-" * 40)

    def get_data_input(self) -> List[Tuple[float, float]]:
        """Prompts the user to input historical data points."""
        print("\n--- Input Historical Data Points (x, y) ---")
        print("Enter time-series data points. Enter 'done' when finished.")
        data = []
        while True:
            try:
                x_input = input("Enter X-value (time) or 'done': ").strip().lower()
                if x_input == 'done':
                    if len(data) < 2:
                        print("Warning: You must enter at least 2 data points.")
                        continue
                    break
                
                x = float(x_input)
                
                y_input = input(f"Enter Y-value for X={x}: ").strip()
                y = float(y_input)
                
                data.append((x, y))
                print(f"Point added: ({x}, {y})")
            except ValueError:
                print("Invalid input. Please enter a valid number or 'done'.")
        return data

    def get_config_input(self) -> Tuple[str, str, str, int, float]:
        """Prompts the user for configuration details."""
        print("\n--- Input Extrapolation Configuration ---")
        
        # Titles
        x_title = input(f"Enter X-axis Title (Default: '{self.config['x_title']}'): ").strip() or self.config['x_title']
        y_title = input(f"Enter Y-axis Title (Default: '{self.config['y_title']}'): ").strip() or self.config['y_title']
        
        # Method
        method_name = ""
        while True:
            method = input("Select Extrapolation Method ('L' for Lagrange, 'D' for Divided Difference): ").strip().upper()
            if method == 'L':
                method_name = 'Lagrange'
                break
            elif method == 'D':
                method_name = 'Divided Difference'
                break
            else:
                print("Invalid method. Please enter 'L' or 'D'.")

        # Number of points
        num_points: int
        while True:
            try:
                max_available = len(self.data_points)
                num_points_input = input(f"Enter Number of closest points to use (Min 2, Max {max_available}, Default {self.config['num_points']}): ").strip()
                if not num_points_input:
                    num_points = self.config['num_points']
                    break
                
                num_points = int(num_points_input)
                if 2 <= num_points <= max_available:
                    break
                else:
                    print(f"Invalid number. Must be an integer between 2 and {max_available}.")
            except ValueError:
                print("Invalid input. Please enter a valid integer.")

        # Prediction horizon
        horizon_value: float
        while True:
            try:
                horizon_input = input("Prediction Horizon (e.g., how far into the future?): ").strip()
                horizon_value = float(horizon_input)
                break
            except ValueError:
                print("Invalid input. Please enter a valid number for the prediction horizon.")
        
        return x_title, y_title, method_name, num_points, horizon_value

    def run_cli(self):
        """Runs the command-line interface for the application."""
        print("\n==============================================")
        print("    SmartTrend Extrapolation Program (CLI)    ")
        print("==============================================")
        
        try:
            # 1. Collect Data from user
            data = self.get_data_input()
            self.collect_data_points(data)
            
            # 2. Collect Configuration from user
            x_title, y_title, method, num_points, horizon = self.get_config_input()
            target_x = self.set_prediction_horizon(horizon)
            self.set_configuration(x_title, y_title, method, num_points, target_x)
            
            # 3. Select Subset and Extrapolate
            self.select_extrapolation_subset()
            self.extrapolate_and_store()
            
            # 4. Display Output
            self.display_predicted_outputs()
            
        except ValueError as e:
            print(f"\nFATAL ERROR: {e}")
            print("Application halted.")
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")
            print("Application halted.")

    def generate_interpretation(self, current_x: float, current_y: float, pred_x: float, pred_y: float) -> str:
        delta_y = pred_y - current_y
        horizon = pred_x - current_x
        direction = "Stable" if abs(delta_y) < 0.1 else ("Rising" if delta_y > 0 else "Dropping")
        warning = ""
        if current_y > 4.0 and pred_y < 4.0:
            warning = "Crossing into Caution zone."
        if pred_y < 3.0:
            warning = "Critical Drop."
        current_status = self.assess_koi_risk(current_y)['status']
        future_status = self.assess_koi_risk(pred_y)['status']
        return (
            f"Oxygen is {direction} by {abs(delta_y):.2f} mg/L over the next {horizon:.2f} hours. "
            f"It is projected to shift from {current_status} to {future_status}. "
            f"Warning: {warning or 'None.'}"
        )


# --- Application Execution ---

if __name__ == '__main__':
    app = SmartTrendExtrapolator()
    app.run_cli()