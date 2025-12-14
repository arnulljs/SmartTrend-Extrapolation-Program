from typing import List


def divided_difference_interpolation(x_data: List[float], y_data: List[float], x_predict: float) -> float:
    """
    Performs Newton's Divided Difference interpolation.
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
        raise ValueError(f"Divided Difference method requires a minimum of 2 points. Got {n}.")

    # 1. Initialize the divided difference table
    # We only need the first column (the coefficients)
    coef = list(y_data) 
    
    # 2. Compute the divided differences (in-place modification of coef)
    for i in range(1, n):
        for j in range(n - 1, i - 1, -1):
            # f[x_j, ..., x_{j-i}] = (f[x_j, ...] - f[x_{j-1}, ...]) / (x_j - x_{j-i})
            numerator = coef[j] - coef[j-1]
            denominator = x_data[j] - x_data[j-i]
            
            if denominator == 0:
                raise ValueError("Error: Divided difference method detected identical x-values.")
            
            coef[j] = numerator / denominator

    # 3. Use Newton's form to evaluate the polynomial at x_predict
    # P(x) = c_0 + c_1(x-x_0) + c_2(x-x_0)(x-x_1) + ...
    
    P_x = coef[n-1]
    
    # Horner's method for efficient evaluation
    for i in range(n - 2, -1, -1):
        P_x = P_x * (x_predict - x_data[i]) + coef[i]
        
    return P_x