import React, { useState } from 'react';
import axios from 'axios';

function ActivityPrediction({activityData}) {
  // State to hold the form input values
  const [steps, setSteps] = useState('');
  const [activityMinutes, setActivityMinutes] = useState('');
  
  // State to hold the prediction result
  const [prediction, setPrediction] = useState(null);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();


    try {
      // Make the POST request to the API
      const response = await axios.post(`http://localhost:5000/api/predict/calories/${steps}/${activityMinutes}`, activityData);
      
      // Set the prediction result
      setPrediction(response.data.prediction);
    } catch (error) {
      console.error('Error making prediction:', error);
    }
  };

  return (
    <div>
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

      {prediction !== null && (
        <div className="mt-4">
          <p className="text-lg">
            Predicted Calories: <strong>{prediction}</strong>
          </p>
        </div>
      )}
    </div>
  );
}

export default ActivityPrediction;
