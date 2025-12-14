import math
from typing import List, Dict, Any, Tuple
from lagrange import lagrange_interpolation
from dividedDifference import divided_difference_interpolation

class SmartTrendExtrapolator:
    """
    Core class for the SmartTrend Extrapolation Program.
    Handles data collection, configuration, and performs 
    Lagrange and Divided Difference interpolation (extrapolation).
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

    def collect_data_points(self, data: List[Tuple[float, float]]):
        """
        Collects initial time-series data points (x, y).
        
        Args:
            data: A list of (x, y) tuples representing the historical data.
        """
        print("--- Data Collection ---")
        self.data_points = [{'x': x, 'y': y} for x, y in data]
        print(f"Collected {len(self.data_points)} data points.")

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
            elif self.config['method'] == 'Divided Difference':
                y_predicted = divided_difference_interpolation(x_data, y_data, x_predict)
            else:
                raise ValueError(f"Unknown extrapolation method: {self.config['method']}")
                
            # Store the prediction
            prediction = {
                'x': x_predict,
                'y': y_predicted,
                'method': self.config['method'],
                'subset_size': len(self.subset)
            }
            self.predictions.append(prediction)
            print("Extrapolation successful.")
            
        except ValueError as e:
            print(f"Extrapolation failed: {e}")

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

        # Prediction value
        predict_x: float
        while True:
            try:
                predict_x_input = input("Enter Future X-value for prediction (e.g., 11.5): ").strip()
                predict_x = float(predict_x_input)
                break
            except ValueError:
                print("Invalid input. Please enter a valid number for the prediction X-value.")
        
        return x_title, y_title, method_name, num_points, predict_x

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
            x_title, y_title, method, num_points, predict_x = self.get_config_input()
            self.set_configuration(x_title, y_title, method, num_points, predict_x)
            
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


# --- Application Execution ---

if __name__ == '__main__':
    app = SmartTrendExtrapolator()
    app.run_cli()