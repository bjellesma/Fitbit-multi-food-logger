import numpy as np
import copy, math

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

def zscore_normalize_features(X):
    """
    computes  X, zcore normalized by column
    
    Args:
      X (ndarray (m,n))     : input data, m examples, n features
      
    Returns:
      X_norm (ndarray (m,n)): input normalized by column
      mu (ndarray (n,))     : mean of each feature
      sigma (ndarray (n,))  : standard deviation of each feature
    """
    # find the mean of each column/feature
    mu     = np.mean(X, axis=0)                 # mu will have shape (n,)
    # find the standard deviation of each column/feature
    sigma  = np.std(X, axis=0)                  # sigma will have shape (n,)
    # element-wise, subtract mu for that column from each example, divide by std for that column
    X_norm = (X - mu) / sigma      

    return (X_norm, mu, sigma)

def gradient_descent(X, y, w_in, b_in, cost_function, gradient_function, alpha, num_iters): 
    """
    Performs batch gradient descent to learn w and b. Updates w and b by taking 
    num_iters gradient steps with learning rate alpha
    
    Args:
      X (ndarray (m,n))   : Data, m examples with n features
      y (ndarray (m,))    : target values
      w_in (ndarray (n,)) : initial model parameters  
      b_in (scalar)       : initial model parameter
      cost_function       : function to compute cost
      gradient_function   : function to compute the gradient
      alpha (float)       : Learning rate
      num_iters (int)     : number of iterations to run gradient descent
      
    Returns:
      w (ndarray (n,)) : Updated values of parameters 
      b (scalar)       : Updated value of parameter 
      """
    
    # An array to store cost J and w's at each iteration primarily for graphing later
    J_history = []
    w = copy.deepcopy(w_in)  #avoid modifying global w within function
    b = b_in
    
    for i in range(num_iters):

        # Calculate the gradient and update the parameters
        dj_db,dj_dw = gradient_function(X, y, w, b)   ##None

        # Update Parameters using w, b, alpha and gradient
        w = w - alpha * dj_dw               ##None
        b = b - alpha * dj_db               ##None
      
        # Save cost J at each iteration
        if i<1000000:      # prevent resource exhaustion 
            J_history.append( cost_function(X, y, w, b))

        # Print cost every at intervals 10 times or as many iterations if < 10
        if i% math.ceil(num_iters / 10) == 0:
            print(f"Iteration {i:4d}: Cost {J_history[-1]:8.2f}   ")
        
    return w, b, J_history #return final w,b and J history for graphing

def gradient_descent(X, y, learning_rate=0.01, epochs=1000):
    m, n = X.shape
    theta = np.zeros(n)
    mse_history = []

    for epoch in range(epochs):
        y_pred = np.dot(X, theta)
        error = y_pred - y
        gradient = np.dot(X.T, error) / m
        theta -= learning_rate * gradient
        if (epoch + 1) % 100 == 0 or epoch == 0:  # Record MSE at epoch 1 and every 100 epochs
            
            mse = np.mean(error ** 2)
            mse_history.append((epoch + 1, mse))
            print(f'mse - {mse} at epoch {epoch}')

    return theta, mse_history

def compute_cost(X, y, w, b): 
    """
    compute cost
    this will calc the mean squared error
    Args:
      X (ndarray (m,n)): Data, m examples with n features
      y (ndarray (m,)) : target values
      w (ndarray (n,)) : model parameters  
      b (scalar)       : model parameter
      
    Returns:
      cost (scalar): cost
    """
    m = X.shape[0]
    cost = 0.0
    for i in range(m):                                
        f_wb_i = np.dot(X[i], w) + b           #(n,)(n,) = scalar (see np.dot)
        cost = cost + (f_wb_i - y[i])**2       #scalar
    cost = cost / (2 * m)                      #scalar    
    return cost

def predict(x, w, b): 
    """
    single predict using linear regression
    Args:
      x (ndarray): Shape (n,) example with multiple features
      w (ndarray): Shape (n,) model parameters   
      b (scalar):             model parameter 
      
    Returns:
      p (scalar):  prediction
    """
    p = np.dot(x, w) + b     
    return p 

def predict_calories(data, steps, activity_minutes):
    # Prepare the data
    X = np.array([[entry['steps'], entry['zoneActivityMinutes']] for entry in data])
    y = np.array([entry['activityCalories'] for entry in data])

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Normalize the features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # create a linear regression model to analyze the numbers
    model = LinearRegression()
    # train the model with the scaled data and the actual output
    model.fit(X_train_scaled, y_train)

    # use the scaled weights to act on the new unseen data and predict
    input_data = scaler.transform(np.array([[steps, activity_minutes]]))
    # scikit learn gives us a matrix (2d array) so we get the first index which is the true 1d array
    prediction = model.predict(input_data)[0]

    # Calculate prediction history
    X_scaled = scaler.transform(X)
    prediction_history = []
    for i, entry in enumerate(data):
        pred = model.predict(X_scaled[i].reshape(1, -1))[0]
        prediction_history.append({
            'dateTime': entry['dateTime'],
            'value': pred
        })

    # report mse
    # Evaluate the model on the test set
    y_pred = model.predict(X_test_scaled)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    return {
        'final_prediction': prediction,
        'prediction_history': prediction_history,
        'model_performance': {
            'mean_squared_error': mse,
            'r2': r2
        }
    }

def predict_calories_gradient(data, steps, activity_minutes, learning_rate=0.01, epochs=1000):
    """this function does not use sklearn so that we can see how the data performs on each epoch"""
    X = np.array([[entry['steps'], entry['zoneActivityMinutes']] for entry in data])
    y = np.array([entry['activityCalories'] for entry in data])

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Normalize the features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Add bias term
    X_train_scaled = np.c_[np.ones(X_train_scaled.shape[0]), X_train_scaled]
    X_test_scaled = np.c_[np.ones(X_test_scaled.shape[0]), X_test_scaled]


    # Train the model using gradient descent
    theta, mse_history = gradient_descent(X_train_scaled, y_train, learning_rate, epochs)

    # Make predictions on test set
    y_pred_test = np.dot(X_test_scaled, theta)
    mse_test = mean_squared_error(y_test, y_pred_test)
    r2_test = r2_score(y_test, y_pred_test)

    # Make final prediction
    input_data = scaler.transform(np.array([[steps, activity_minutes]]))
    input_data_with_bias = np.c_[np.ones(1), input_data]
    prediction = np.dot(input_data_with_bias, theta)[0]

    # Calculate prediction history
    X_scaled = scaler.transform(X)
    X_scaled_with_bias = np.c_[np.ones(X_scaled.shape[0]), X_scaled]
    prediction_history = []
    for i, entry in enumerate(data):
        pred = np.dot(X_scaled_with_bias[i], theta)
        prediction_history.append({
            'dateTime': entry['dateTime'],
            'value': pred
        })

    return {
        'final_prediction': prediction,
        'prediction_history': prediction_history,
        'model_performance': {
            'mse_test': mse_test,
            'r2_test': r2_test,
            'mse_history': mse_history
        }
    }
