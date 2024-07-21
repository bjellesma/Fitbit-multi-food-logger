import React, { useState, useEffect } from 'react';
import axios from 'axios';
import DatePicker from '../DatePicker';

function LogFood() {
  const [foodLogs, setFoodLogs] = useState(null);
  const [requestStatus, setRequestStatus] = useState(null);
  const [meal, setMeal] = useState('');
  const [mealType, setMealType] = useState('');
  const [mealDetails, setMealDetails] = useState(null);
  const [selectedDate, setSelectedDate] = useState('');

  useEffect(() => {
    const fetchTodaysFoodLogs = async () => {
      const date = selectedDate;
      console.log(date);
      try {
        const response = await axios.get(`http://localhost:5000/api/foodLogs/${date}?data=summary`);
        setFoodLogs(response.data);
      } catch (error) {
        console.error('Failed to fetch today\'s food logs:', error);
      }
    };

    if (selectedDate) {
      fetchTodaysFoodLogs();
    }
  }, [selectedDate]);

  useEffect(() => {
    const fetchMealDetails = async () => {
      if (meal) {
        try {
          const response = await axios.get(`http://localhost:5000/api/getmeal/${meal}`);
          setMealDetails(response.data);
        } catch (error) {
          console.error('Failed to fetch meal details:', error);
        }
      }
    };

    fetchMealDetails();
  }, [meal]);

  const handleDateChange = (date) => {
    const d = new Date(date);
    const year = d.getFullYear();
    const month = (d.getMonth() + 1).toString().padStart(2, '0');
    const day = d.getDate().toString().padStart(2, '0');
    const formattedDate = `${year}-${month}-${day}`;
    setSelectedDate(formattedDate);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const foodEntries = mealDetails.map(entry => ({
      ...entry,
      mealTypeId: mealType,
      date: selectedDate
    }));

    try {
      const response = await axios.post('http://localhost:5000/api/log_food', foodEntries);
      console.log(response.data);
      setRequestStatus(response.status);
    } catch (error) {
      console.error(error.response.data.error);
    }
  };

  return (
    <>
        {/* green if request was good and red otherwise */}
        {requestStatus !== null ? (
            requestStatus === 201 ? (
            <div className="bg-green-100 border-l-4 border-green-500 text-green-700 p-4" role="alert">
                <p className="font-bold">Success</p>
                <p>Your food entry has been logged successfully.</p>
            </div>
            ) : (
            <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4" role="alert">
                <p className="font-bold">Error</p>
                <p>Failed to log your food entry. Please try again.</p>
            </div>
            )
        ) : null}
        {/* display log for the currently selected day */}
        {/* todo not working */}
        {/* {foodLogs && (
            <div className="food-logs">
            <h2>Today's Food Logs</h2>
            {foodLogs.map((log, index) => (
                <div key={index}>
                {Object.entries(log).map(([key, value]) => (
                    <p key={key}><strong>{key}:</strong> {value}</p>
                ))}
                </div>
            ))}
            </div>
        )} */}
        <div className="App container mx-auto p-4">
            <h1 className="text-2xl font-bold mb-4">Log Food Entry</h1>
            <form onSubmit={handleSubmit} className="space-y-4">
            <div className="flex flex-col">
                <label className="font-semibold">
                What do you want to add?
                <select className="mt-1 p-2 border border-gray-300 rounded" value={meal} onChange={(e) => setMeal(e.target.value)}>
                    <option value="">Select a meal</option>
                    <option value="1">Morning shake</option>
                    <option value="2">Oatmeal pie</option>
                    <option value="3">Yogurt</option>
                    <option value="4">Grapes/Carrots</option>
                    <option value="5">Soylent</option>
                    <option value="6">Granola</option>
                    <option value="7">Preworkout</option>
                    <option value="8">Post workout</option>
                    <option value="9">Chicken and Pasta</option>
                    <option value="10">Nighttime shake</option>
                    <option value="11">Kind Granola</option>
                    <option value="12">Unsalted Nuts</option>
                    <option value="13">Celsius</option>
                </select>
                </label>
            </div>
            {/* display the meal details */}
            {mealDetails && (
                <div style={{ marginTop: '20px', border: '1px solid #ccc', padding: '10px' }}>
                <h3>Meal Details</h3>
                <pre>{JSON.stringify(mealDetails, null, 2)}</pre>
                </div>
            )}

            <div className="flex flex-col">
                <label className="font-semibold">
                When did you eat this?
                <select className="mt-1 p-2 border border-gray-300 rounded" value={mealType} onChange={(e) => setMealType(e.target.value)}>
                    <option value="">Select meal type</option>
                    <option value="1">Breakfast</option>
                    <option value="2">Morning Snack</option>
                    <option value="3">Lunch</option>
                    <option value="4">Afternoon Snack</option>
                    <option value="5">Dinner</option>
                    <option value="6">Evening Snack</option>
                </select>
                </label>
            </div>
            <div className="flex flex-col">
                <label className="font-semibold">
                <div>
                    <h1 className="text-xl font-bold">Select a Date</h1>
                    <h1>Selected Date: {selectedDate.toString()}</h1>
                    {/* Pass handleDateChange as a prop to DatePicker */}
                    <DatePicker onDateChange={handleDateChange}/>
                </div>
                </label>
            </div>
            <button type="submit" className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                Log Food
            </button>
            </form>
        </div>
      </>
  );
}

export default LogFood;