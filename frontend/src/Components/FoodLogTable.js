// FoodLogTable.js
import React from 'react';
import axios from 'axios';

function FoodLogTable({ foodLogs, setFoodLogs }) {
  
  // Function to delete a food entry
  const handleDelete = async (foodId) => {
    try {
      await axios.delete(`http://localhost:5000/api/delete_food/${foodId}`);
      setFoodLogs(prevLogs => ({
        ...prevLogs,
        foods: prevLogs.foods.filter(food => food.logId !== foodId) // Remove the deleted entry from the state
      }));
    } catch (error) {
      console.error('Failed to delete food entry:', error);
    }
  };

  return (
    <div id="logTable" className="p-4">
      <h3 className="text-xl font-bold mb-4">Foods</h3>
      <div className="overflow-x-auto">
        <table className="min-w-full table-auto border-collapse border border-gray-300">
          <thead>
            <tr>
              <th className="border border-gray-300 p-2">Date</th>
              <th className="border border-gray-300 p-2">Food Name</th>
              <th className="border border-gray-300 p-2">Brand</th>
              <th className="border border-gray-300 p-2">Calories</th>
              <th className="border border-gray-300 p-2">Amount</th>
              <th className="border border-gray-300 p-2">Action</th>
            </tr>
          </thead>
          <tbody>
            {foodLogs && foodLogs.foods && foodLogs.foods.map((food, index) => (
              <tr key={index} className="hover:bg-gray-100">
                <td className="border border-gray-300 p-2">{food.logDate}</td>
                <td className="border border-gray-300 p-2">{food.loggedFood.name}</td>
                <td className="border border-gray-300 p-2">{food.loggedFood.brand}</td>
                <td className="border border-gray-300 p-2">{food.loggedFood.calories}</td>
                <td className="border border-gray-300 p-2">{food.loggedFood.amount} {food.loggedFood.unit.name}</td>
                <td className="border border-gray-300 p-2">
                  <button 
                    onClick={() => handleDelete(food.logId)} // Pass the food entry ID to the delete handler
                    className="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-2 rounded"
                  >
                    Delete
                  </button>
                </td>

              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default FoodLogTable;