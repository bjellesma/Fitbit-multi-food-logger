import React, { useState, useEffect } from 'react';
import axios from 'axios';

function AnalyzeActivity() {
  // State to hold the activity data
  const [activityData, setActivityData] = useState([]);

  // Fetch data when the component mounts
  useEffect(() => {
    // Get today's date
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0'); // Months are zero-based
    const day = String(today.getDate()).padStart(2, '0');

    // Format the date as YYYY-MM-DD
    const formattedDate = `${year}-${month}-${day}`;
    axios.get(`http://localhost:5000/api/activity?before_date=${formattedDate}`)
      .then(response => {
        setActivityData(response.data);
        console.log(response.data);
      })
      .catch(error => {
        console.error('Error fetching activity data:', error);
      });
  }, []);

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Activity Analysis</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full table-auto border-collapse border border-gray-300">
          <thead>
            <tr>
              <th className="border border-gray-300 p-2">Date</th>
              <th className="border border-gray-300 p-2">Steps</th>
              <th className="border border-gray-300 p-2">Moderate Activity Minutes</th>
              <th className="border border-gray-300 p-2">Rigorous Activity Minutes</th>
              <th className="border border-gray-300 p-2">Calories Burned</th>
            </tr>
          </thead>
          <tbody>
            {activityData.length > 0 ? (
              activityData.map((activity, index) => (
                <tr key={index} className="hover:bg-gray-100">
                  <td className="border border-gray-300 p-2">{activity.dateTime}</td>
                  <td className="border border-gray-300 p-2">{activity.steps}</td>
                  <td className="border border-gray-300 p-2">{activity.minutesFairlyActive}</td>
                  <td className="border border-gray-300 p-2">{activity.minutesVeryActive}</td>
                  <td className="border border-gray-300 p-2">{activity.activityCalories}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="4" className="border border-gray-300 p-2 text-center">No activity data available</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default AnalyzeActivity;
