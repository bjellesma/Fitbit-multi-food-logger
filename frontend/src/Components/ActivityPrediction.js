import React, { useState } from 'react';
import axios from 'axios';
import Plot from 'react-plotly.js';

function ActivityPrediction({activityData}) {
  // State to hold the form input values
  const [steps, setSteps] = useState('');
  const [activityMinutes, setActivityMinutes] = useState('');
  
  // State to hold the prediction result
  const [prediction, setPrediction] = useState(null);
  const [modelPerformance, setModelPerformance] = useState(null);
  const [predictionHistory, setPredictionHistory] = useState([]);
  const [predictionGradient, setPredictionGradient] = useState(null);
  const [modelPerformanceGradient, setModelPerformanceGradient] = useState(null);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();


    try {
      // Make the POST request to the API
      const response = await axios.post(`http://localhost:5000/api/predict/calories/${steps}/${activityMinutes}`, activityData);
      
      // Set the prediction result and history
      setPrediction(response.data.sklearn.final_prediction);
      setModelPerformance(response.data.sklearn.model_performance);
      setPredictionGradient(response.data.gradient.final_prediction);
      setModelPerformanceGradient(response.data.gradient.model_performance);
      setPredictionHistory(response.data.sklearn.prediction_history || []);
    } catch (error) {
      console.error('Error making prediction:', error);
    }
  };

  return (
    <div>
      <Plot
          data={[
            {
              x: activityData.map(data => data.dateTime), // Original data x-axis
              y: activityData.map(data => data.activityCalories), // Original data y-axis
              type: 'scatter',
              mode: 'lines+markers',
              name: 'Calories Burned',
              line: { color: 'green' }
            },
            {
              x: predictionHistory.map(pred => pred.dateTime), // Prediction history x-axis
              y: predictionHistory.map(pred => pred.value), // Prediction history y-axis
              type: 'scatter',
              mode: 'lines+markers',
              name: 'Prediction History',
              marker: { color: 'red' }
            }
          ]}
          layout={{
            title: 'Activity Data Over Time',
            xaxis: { title: 'Date' },
            yaxis: { title: 'Calories' },
            margin: { t: 30, l: 50, r: 50, b: 50 },
            legend: { orientation: 'h', y: -0.2 }
          }}
          style={{ width: '100%', height: '100%' }}
        />
      <h2 className="text-2xl font-bold mb-4">Activity Prediction</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="steps" className="block text-sm font-medium text-gray-700">
            Steps
          </label>
          <input
            type="number"
            id="steps"
            name="steps"
            value={steps}
            onChange={(e) => setSteps(e.target.value)}
            className="mt-1 p-2 block w-full border border-gray-300 rounded-md shadow-sm"
            required
          />
        </div>

        <div>
          <label htmlFor="activityMinutes" className="block text-sm font-medium text-gray-700">
            Activity Minutes
          </label>
          <input
            type="number"
            id="activityMinutes"
            name="activityMinutes"
            value={activityMinutes}
            onChange={(e) => setActivityMinutes(e.target.value)}
            className="mt-1 p-2 block w-full border border-gray-300 rounded-md shadow-sm"
            required
          />
        </div>

        <button
          type="submit"
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Predict Calories
        </button>
      </form>

      {prediction !== null &&
      modelPerformance !== null && (
        <div className='row'>
          <div className="mt-4">
            <p className="text-lg">
              Predicted Calories: <strong>{prediction}</strong><br />
              Mean Squared Error: <strong>{modelPerformance.mean_squared_error}</strong>
            </p>
          </div>
          <div className="mt-4">
            <p className="text-lg">
              Gradient Predicted Calories: <strong>{predictionGradient}</strong><br />
            </p>
            <div>
              <h3>Gradient Mean Squared Error History:</h3>
              <table className="w-full text-sm text-left text-gray-500">
                <thead className="text-xs text-gray-700 uppercase bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3">Epoch</th>
                    <th scope="col" className="px-6 py-3">MSE</th>
                  </tr>
                </thead>
                <tbody>
                  {modelPerformanceGradient.mse_history.map(([epoch, mse]) => (
                    <tr key={epoch} className="bg-white border-b">
                      <td className="px-6 py-4">{epoch}</td>
                      <td className="px-6 py-4">{mse.toFixed(4)}</td>
                      
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ActivityPrediction;
