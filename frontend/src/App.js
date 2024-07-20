import React, { useState } from 'react';
import axios from 'axios';
import DatePicker from './Components/DatePicker';

function App() {
  const [meal, setMeal] = useState('');
  const [mealType, setMealType] = useState('');
  const [dateOption] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    let currentDate = new Date();
    switch (parseInt(dateOption)) {
      case 1:
        currentDate = currentDate.toISOString().split('T')[0];
        break;
      case 2:
        currentDate.setDate(currentDate.getDate() - 1);
        currentDate = currentDate.toISOString().split('T')[0];
        break;
      case 3:
        currentDate.setDate(currentDate.getDate() - 2);
        currentDate = currentDate.toISOString().split('T')[0];
        break;
      case 4:
        currentDate.setDate(currentDate.getDate() - 3);
        currentDate = currentDate.toISOString().split('T')[0];
        break;
      default:
        currentDate = new Date().toISOString().split('T')[0];
    }

    const foodEntries = {
      meal,
      mealType,
      date: currentDate,
    };

    try {
      const response = await axios.post('http://localhost:5000/api/log_food', foodEntries);
      console.log(response.data.message);
    } catch (error) {
      console.error(error.response.data.error);
    }
  };

  return (
    <div className="App container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Log Food Entry</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex flex-col">
          <label className="font-semibold">
            What do you want to add?
            <select className="mt-1 p-2 border border-gray-300 rounded" value={meal} onChange={(e) => setMeal(e.target.value)}>
              <option value="">Select a meal</option>
              <option value="1">morning shake</option>
              <option value="2">oatmeal pie</option>
              <option value="3">Yogurt</option>
              <option value="4">Grapes/Carrots</option>
              <option value="5">Soylent</option>
              <option value="6">Granola</option>
              <option value="7">Preworkout</option>
              <option value="8">Post workout</option>
              <option value="9">Chicken and Pasta</option>
            </select>
          </label>
        </div>
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
            </select>
          </label>
        </div>
        <div className="flex flex-col">
          <label className="font-semibold">
            <div>
              <h1 className="text-xl font-bold">Select a Date</h1>
              <DatePicker />
            </div>
          </label>
        </div>
        <button type="submit" className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
          Log Food
        </button>
      </form>
    </div>
  );
}

export default App;
