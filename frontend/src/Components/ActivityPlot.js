import React from 'react';
import Plot from 'react-plotly.js';

function ActivityPlot({ dateTime, steps, zoneActivityMinutes, activityCalories }) {

  return (
    <div className="mt-8">
        <Plot
          data={[
            {
              x: dateTime,
              y: steps,
              type: 'scatter',
              mode: 'lines+markers',
              name: 'Steps',
              line: { color: 'blue' }
            },
            {
              x: dateTime,
              y: zoneActivityMinutes,
              type: 'scatter',
              mode: 'lines+markers',
              name: 'Zone Active Minutes',
              line: { color: 'orange' }
            },
            {
              x: dateTime,
              y: activityCalories,
              type: 'scatter',
              mode: 'lines+markers',
              name: 'Calories Burned',
              line: { color: 'green' }
            }
          ]}
          layout={{
            title: 'Activity Data Over Time',
            xaxis: { title: 'Date' },
            yaxis: { title: 'Count' },
            margin: { t: 30, l: 50, r: 50, b: 50 },
            legend: { orientation: 'h', y: -0.2 }
          }}
          style={{ width: '100%', height: '100%' }}
        />
      </div>
  );
}

export default ActivityPlot;