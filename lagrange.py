from typing import List


def lagrange_interpolation(x_data: List[float], y_data: List[float], x_predict: float) -> float:
    """
    Performs Lagrange extrapolation (via interpolation polynomial).
    Requires a minimum of 2 data points (n >= 2).
    
    Args:
        x_data: List of x-coordinates (time).
        y_data: List of y-coordinates (value).
        x_predict: The x-value for which to predict y.
        
    Returns:
        The predicted y-value.
    """
    n = len(x_data)
    if n < 2 or n != len(y_data):
        raise ValueError(f"Lagrange method requires a minimum of 2 points. Got {n}.")

    P_x = 0.0
    
    # For each data point j, compute the Lagrange basis polynomial L_j(x)
    for j in range(n):
        L_j_x = 1.0
        
        for i in range(n):
            if i != j:
                denominator = x_data[j] - x_data[i]
                
                if denominator == 0:
                    raise ValueError("Error: Lagrange method detected identical x-values.")
                
                # L_j(x) = Product [ (x - x_i) / (x_j - x_i) ] for all i != j
                L_j_x *= (x_predict - x_data[i]) / denominator
        
        # P(x) = Sum [ y_j * L_j(x) ]
        P_x += y_data[j] * L_j_x
        
    return P_x