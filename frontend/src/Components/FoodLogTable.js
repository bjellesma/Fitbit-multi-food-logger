// FoodLogTable.js
import React from 'react';

function FoodLogTable({ foodLogs }) {
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
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default FoodLogTable;