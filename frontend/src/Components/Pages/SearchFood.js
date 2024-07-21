import React, { useState } from 'react';
import axios from 'axios';

function SearchFood() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  const searchFood = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/api/searchfoods/${query}`);
      console.log(response.data);
      setResults(response.data.foods);
    } catch (error) {
      console.error('Error searching for food:', error);
    }
  };

  return (
    <div className="max-w-xl mx-auto p-4">
      <h2 className="text-2xl font-bold mb-4">Search Food</h2>
      <div className="flex mb-4">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter food to search"
          className="flex-1 mr-2 p-2 border border-gray-300 rounded"
        />
        <button onClick={searchFood} className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
          Search
        </button>
      </div>
      <table className="min-w-full table-auto">
        <thead className="bg-gray-200">
          <tr>
            <th className="px-4 py-2">Food</th>
            <th className="px-4 py-2">Food ID</th>
            <th className="px-4 py-2">Brand</th>
            <th className="px-4 py-2">Calories</th>
            <th className="px-4 py-2">Default Unit</th>
            <th className="px-4 py-2">Default Unit ID</th>
          </tr>
        </thead>
        <tbody>
          {results.map((food, index) => (
            <tr key={index} className="bg-white border-b">
              <td className="px-4 py-2">{food.name}</td>
              <td className="px-4 py-2">{food.foodId}</td>
              <td className="px-4 py-2">{food.brand || 'N/A'}</td>
              <td className="px-4 py-2">{food.calories}</td>
              <td className="px-4 py-2">{food.defaultUnit.name}</td>
              <td className="px-4 py-2">{food.defaultUnit.id}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default SearchFood;