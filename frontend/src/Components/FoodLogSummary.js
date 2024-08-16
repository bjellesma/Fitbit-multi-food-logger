// FoodLogSummary.js
import React from 'react';

function FoodLogSummary({ foodLogs }) {
  return (
    <div id="logSummary" className="grid grid-cols-2 gap-4 p-4">
      <h3 className="col-span-2 text-xl font-bold">Summary</h3>
      {foodLogs && foodLogs.summary && Object.entries(foodLogs.summary).map(([key, value]) => (
        <div key={key} className="flex justify-between">
          <strong>{key}:</strong>
          <span>{value}</span>
        </div>
      ))}
    </div>
  );
}

export default FoodLogSummary;