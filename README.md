# SmartTrend Extrapolation Program

## Overview
The **SmartTrend Extrapolation Program** is a modular Python-based application designed to analyze time-series data and predict future parameter trends using numerical extrapolation techniques. The program dynamically adapts based on user-selected methods, specifically **Lagrange Polynomial** and **Divided Difference** methods.

This project serves as a **course fulfillment for CPE 3108 – Numerical Methods** and is implemented as a **non-real-time prototype** intended for future integration into real-time monitoring systems such as industrial, environmental, or health-related applications.

---

## Features
- Simple graphical user interface (GUI) for data input and method selection  
- Supports:
  - Lagrange Polynomial Extrapolation  
  - Divided Difference Extrapolation  
- Suggests an optimal number of recent samples with user-defined limits to reduce overfitting  
- Graphical visualization of historical and predicted data  
- Modular architecture for future expansion (e.g., sensor feeds, larger datasets)

## Technologies Used
- **Python 3**
- **Kivy**
- **KivyMD (v2.0.1.dev0)**
- **Matplotlib**
- **NumPy**

---

## Installation & Setup

2. **Create a virtual environment (optional but recommended)**
    
    ```
    python -m venv venv
    ```

    Activate the virtual environment:

    **Windows**
    ```
    venv\Scripts\activate
    ```

    **Linux / macOS**
    ```
    source venv/bin/activate
    ```

3. **Install dependencies**
    
    ```
    pip install numpy matplotlib kivy
    pip install kivymd==2.0.1.dev0
    ```

---

## Academic Context
This project demonstrates the practical application of numerical methods, specifically polynomial interpolation and extrapolation, highlighting method selection, numerical stability, and error behavior.
