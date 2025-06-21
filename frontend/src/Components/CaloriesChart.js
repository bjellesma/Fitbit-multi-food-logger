import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';
import axios from 'axios';

const CaloriesChart = ({ refreshTrigger = 0 }) => {
  const [caloriesData, setCaloriesData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCaloriesData();
  }, [refreshTrigger]); // Refetch when refreshTrigger changes

  const fetchCaloriesData = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:5000/api/calories');
      setCaloriesData(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch calories data');
      console.error('Error fetching calories data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ 
        textAlign: 'center', 
        padding: '40px',
        color: '#7F8C8D',
        fontSize: '16px'
      }}>
        Loading calories data...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        textAlign: 'center', 
        padding: '20px',
        backgroundColor: '#F8F9FA',
        borderRadius: '8px',
        border: '1px solid #E9ECEF'
      }}>
        <div style={{ color: '#DC3545', marginBottom: '15px' }}>{error}</div>
        <button 
          onClick={fetchCaloriesData}
          style={{
            padding: '8px 16px',
            backgroundColor: '#007BFF',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Retry
        </button>
      </div>
    );
  }

  if (!caloriesData) {
    return (
      <div style={{ 
        textAlign: 'center', 
        padding: '40px',
        color: '#7F8C8D',
        fontSize: '16px'
      }}>
        No data available
      </div>
    );
  }

  // Prepare data for Plotly
  const data = [
    {
      x: ['Calories Consumed', 'Calories Burned'],
      y: [caloriesData.calories_consumed, caloriesData.calories_burned],
      type: 'bar',
      name: 'Calories',
      marker: {
        color: ['#FF6B6B', '#4ECDC4'],
        opacity: 0.8
      }
    }
  ];

  const layout = {
    title: {
      text: `Daily Calories Summary - ${caloriesData.date}`,
      font: {
        size: 20,
        color: '#2C3E50'
      }
    },
    xaxis: {
      title: 'Type',
      font: {
        size: 14,
        color: '#34495E'
      }
    },
    yaxis: {
      title: 'Calories',
      font: {
        size: 14,
        color: '#34495E'
      }
    },
    plot_bgcolor: '#F8F9FA',
    paper_bgcolor: '#FFFFFF',
    margin: {
      l: 60,
      r: 40,
      t: 80,
      b: 60
    },
    showlegend: false,
    annotations: [
      {
        x: 'Calories Consumed',
        y: caloriesData.calories_consumed,
        text: `${caloriesData.calories_consumed}`,
        showarrow: false,
        yshift: 10,
        font: {
          size: 14,
          color: '#2C3E50'
        }
      },
      {
        x: 'Calories Burned',
        y: caloriesData.calories_burned,
        text: `${caloriesData.calories_burned}`,
        showarrow: false,
        yshift: 10,
        font: {
          size: 14,
          color: '#2C3E50'
        }
      }
    ]
  };

  const config = {
    displayModeBar: false,
    responsive: true
  };

  return (
    <div style={{ 
      padding: '20px', 
      backgroundColor: '#FFFFFF', 
      borderRadius: '10px',
      boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
      margin: '20px 0'
    }}>
      <Plot
        data={data}
        layout={layout}
        config={config}
        style={{ width: '100%', height: '400px' }}
      />
      
      {/* Net Calories Display */}
      <div style={{
        textAlign: 'center',
        marginTop: '20px',
        padding: '15px',
        backgroundColor: caloriesData.net_calories > 0 ? '#FFE6E6' : '#E6F7FF',
        borderRadius: '8px',
        border: `2px solid ${caloriesData.net_calories > 0 ? '#FF6B6B' : '#4ECDC4'}`
      }}>
        <h3 style={{ 
          margin: '0 0 10px 0',
          color: caloriesData.net_calories > 0 ? '#D63031' : '#00B894'
        }}>
          Net Calories: {caloriesData.net_calories}
        </h3>
        <p style={{ 
          margin: '0',
          fontSize: '14px',
          color: '#636E72'
        }}>
          {caloriesData.net_calories > 0 
            ? 'Calorie surplus' 
            : caloriesData.net_calories < 0 
              ? 'Calorie deficit' 
              : 'Calorie balance'
          }
        </p>
      </div>
      
      {/* Refresh Button */}
      <div style={{ textAlign: 'center', marginTop: '15px' }}>
        <button 
          onClick={fetchCaloriesData}
          style={{
            padding: '10px 20px',
            backgroundColor: '#3498DB',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer',
            fontSize: '14px'
          }}
        >
          Refresh Data
        </button>
      </div>
    </div>
  );
};

export default CaloriesChart; 