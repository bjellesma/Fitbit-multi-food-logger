import numpy as np
import copy, math

import tensorflow as tf
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras import Sequential
from tensorflow.keras.losses import MeanSquaredError, BinaryCrossentropy
from tensorflow.keras.activations import sigmoid

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

def compute_gradient(X, y, w, b): 
    """
    Computes the gradient for linear regression 
 
    Args:
      X : (array_like Shape (m,n)) variable such as house size 
      y : (array_like Shape (m,1)) actual value 
      w : (array_like Shape (n,1)) Values of parameters of the model      
      b : (scalar )                Values of parameter of the model      
    Returns
      dj_dw: (array_like Shape (n,1)) The gradient of the cost w.r.t. the parameters w. 
      dj_db: (scalar)                The gradient of the cost w.r.t. the parameter b. 
                                  
    """
    m,n = X.shape
    # @ indicates matrix multiplication
    f_wb = X @ w + b              
    e   = f_wb - y                
    dj_dw  = (1/m) * (X.T @ e)    
    dj_db  = (1/m) * np.sum(e)    
        
    return dj_db,dj_dw
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
    # Ensure steps and activity_minutes are numeric
    steps = float(steps)
    activity_minutes = float(activity_minutes)

    x_train = np.array([[entry['steps'], entry['zoneActivityMinutes']] for entry in data])
    y_train = np.array([entry['activityCalories'] for entry in data])

    # normalize the original features
    x_train, x_mu, x_sigma = zscore_normalize_features(x_train)


    m,n = x_train.shape
    # initialize parameters
    initial_w = np.array([ 0,0])
    initial_b = 1766

    print(f'shape: {x_train.shape} - x_mu: {x_mu}, x_sigma: {x_sigma}')
    tf_pred = tf_predict(x_test=np.array([[steps, activity_minutes]]), x_train=x_train, y_train=y_train,w_init=initial_w,
        b_init=initial_b)
    print(f'tf predict: {tf_pred}')

    # gradient descent
    iterations = 10000
    alpha = 1.42e-1
    w_final, b_final, J_hist = gradient_descent(x_train, y_train, initial_w, initial_b,
                                                    compute_cost, compute_gradient, 
                                                    alpha, iterations)
    print(f"b,w found by gradient descent: {b_final:0.2f},{w_final} ")
    m,_ = x_train.shape
    prediction_history = []
    for i in range(m):
        prediction_history.append({
          'dateTime': data[i]['dateTime'],
          'value': np.dot(x_train[i], w_final) + b_final
        })
    
    # Normalize the input features
    steps_normalized = (int(steps) - x_mu[0]) / x_sigma[0]
    activity_minutes_normalized = (int(activity_minutes) - x_mu[1]) / x_sigma[1]
    
    # Calculate the final prediction using normalized features
    prediction_normalized = np.dot(np.array([steps_normalized, activity_minutes_normalized]), w_final) + b_final

    return {
        'tf_prediction': str(tf_pred[0][0]),
        'final_prediction': prediction_normalized,
        'prediction_history': prediction_history
    }

def tf_predict(x_test, x_train, y_train, w_init, b_init):
    # Initialize the normalization layer and adapt it to the training data
    normalize = tf.keras.layers.Normalization(axis=-1)
    normalize.adapt(x_train)  # Learns mean, variance from training data

    # Normalize both training and test data
    x_train = normalize(x_train)
    x_test = normalize(x_test)

    # build the model
    model = Sequential(
      [
          tf.keras.Input(shape=(2,)),
          tf.keras.layers.Dense(1,  activation = 'linear', name='L1')
      ]
    )
    # Manually set the weights and bias to match the initial values used in gradient descent
    model.layers[0].set_weights([np.array(w_init).reshape(-1, 1), np.array([b_init])])
    # Compile the model with a lower learning rate
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=9.3e-5), loss='mean_squared_error')
    
    # Train the model
    model.fit(x_train, y_train, epochs=100, batch_size=32)
    
    return model.predict(x_test)