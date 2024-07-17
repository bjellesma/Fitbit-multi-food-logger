import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [meal, setMeal] = useState('');
  const [mealType, setMealType] = useState('');
  const [dateOption, setDateOption] = useState('');

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
    <div className="App">
      <h1>Log Food Entry</h1>
      <form onSubmit={handleSubmit}>
        <label>
          What do you want to add?
          <select value={meal} onChange={(e) => setMeal(e.target.value)}>
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
        <br />
        <label>
          When did you eat this?
          <select value={mealType} onChange={(e) => setMealType(e.target.value)}>
            <option value="">Select meal type</option>
            <option value="1">Breakfast</option>
            <option value="2">Morning Snack</option>
            <option value="3">Lunch</option>
            <option value="4">Afternoon Snack</option>
            <option value="5">Dinner</option>
          </select>
        </label>
        <br />
        <label>
          Select the date:
          <select value={dateOption} onChange={(e) => setDateOption(e.target.value)}>
            <option value="">Select date</option>
            <option value="1">Today</option>
            <option value="2">Yesterday</option>
            <option value="3">Two days ago</option>
            <option value="4">Three days ago</option>
          </select>
        </label>
        <br />
        <button type="submit">Log Food</button>
      </form>
    </div>
  );
}

export default App;
