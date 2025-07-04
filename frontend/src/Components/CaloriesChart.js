import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';
import axios from 'axios';

const CaloriesChart = ({ refreshTrigger = 0 }) => {
    const [caloriesData, setCaloriesData] = useState(null);
    const [weightData, setWeightData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchCaloriesData();
        fetchWeightData();
    }, [refreshTrigger]); // Refetch when refreshTrigger changes

    const fetchCaloriesData = async () => {
        try {
            setLoading(true);
            const response = await axios.get('http://localhost:5000/api/calories?days=7');
            setCaloriesData(response.data);
            setError(null);
        } catch (err) {
            if (err.response && err.response.status === 429) {
                setError('Fitbit API rate limit reached. Please wait and try again later.');
            } else {
                setError('Failed to fetch calories data');
            }
            console.error('Error fetching calories data:', err);
        } finally {
            setLoading(false);
        }
    };

    const fetchWeightData = async () => {
        try {
            const response = await axios.get('http://localhost:5000/api/weight?days=7');
            if (response.data && response.data.data) {
                setWeightData(response.data.data);
            }
        } catch (err) {
            console.error('Error fetching weight data:', err);
            // Don't set error for weight data since it's optional
        }
    };

    const calculateStats = () => {
        if (!caloriesData || !caloriesData.data || caloriesData.data.length === 0) return null;

        const totalConsumed = caloriesData.data.reduce((sum, day) => sum + (parseFloat(day.calories_consumed) || 0), 0);
        const totalBurned = caloriesData.data.reduce((sum, day) => sum + (parseFloat(day.calories_burned) || 0), 0);
        const weeklyDeficit = totalBurned - totalConsumed;
        const weeklySurplus = totalConsumed - totalBurned;
        
        // Calculate weight change (3500 calories = 1 pound)
        const poundsChange = weeklyDeficit > 0 ? weeklyDeficit / 3500 : -weeklySurplus / 3500;
        
        // Get current weight (most recent non-null weight)
        const currentWeight = weightData
            .filter(day => day.weight !== null && day.weight !== undefined)
            .pop()?.weight;
        
        // Calculate projected weight in a month (4 weeks)
        const monthlyPoundsChange = poundsChange * 4;
        const projectedWeight = currentWeight ? currentWeight - monthlyPoundsChange : null;

        return {
            totalConsumed: Number(totalConsumed) || 0,
            totalBurned: Number(totalBurned) || 0,
            weeklyDeficit: Number(weeklyDeficit) || 0,
            weeklySurplus: Number(weeklySurplus) || 0,
            poundsChange: Number(poundsChange) || 0,
            currentWeight: currentWeight ? Number(currentWeight) : null,
            monthlyPoundsChange: Number(monthlyPoundsChange) || 0,
            projectedWeight: projectedWeight ? Number(projectedWeight) : null
        };
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

    // Calculate statistics
    const stats = calculateStats();

    // Prepare data for Plotly
    const dates = caloriesData.data.map(item => {
        const date = new Date(item.date);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    
    const consumedData = caloriesData.data.map(item => item.calories_consumed);
    const burnedData = caloriesData.data.map(item => item.calories_burned);
    
    const data = [
        {
            x: dates,
            y: consumedData,
            type: 'bar',
            name: 'Calories Consumed',
            marker: {
                color: '#FF6B6B',
                opacity: 0.8
            }
        },
        {
            x: dates,
            y: burnedData,
            type: 'bar',
            name: 'Calories Burned',
            marker: {
                color: '#4ECDC4',
                opacity: 0.8
            }
        }
    ];

    const layout = {
        title: {
            text: '7-Day Calories Summary',
            font: {
                size: 20,
                color: '#2C3E50'
            }
        },
        xaxis: {
            title: 'Date',
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
        showlegend: true,
        legend: {
            x: 0.5,
            y: 1.1,
            orientation: 'h'
        },
        barmode: 'group',
        annotations: caloriesData.data.map((day, index) => ({
            x: dates[index],
            y: Math.max(day.calories_consumed, day.calories_burned) + 50, // Position above the higher bar
            text: `${day.net_calories > 0 ? '+' : ''}${day.net_calories}`,
            showarrow: false,
            font: {
                size: 12,
                color: day.net_calories > 0 ? '#D63031' : '#00B894'
            },
            bgcolor: 'rgba(255, 255, 255, 0.8)',
            bordercolor: day.net_calories > 0 ? '#D63031' : '#00B894',
            borderwidth: 1
        }))
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
            
            {/* Statistics Summary */}
            {stats && (
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                    gap: '15px',
                    marginBottom: '20px',
                    padding: '15px',
                    backgroundColor: '#F8F9FA',
                    borderRadius: '8px',
                    border: '2px solid #E9ECEF'
                }}>
                    <div style={{ textAlign: 'center' }}>
                        <h3 style={{ margin: '0 0 10px 0', color: '#2C3E50', fontSize: '14px' }}>Weekly Balance</h3>
                        <p style={{ 
                            margin: '0', 
                            fontSize: '24px', 
                            fontWeight: 'bold',
                            color: (stats.weeklyDeficit || 0) > 0 ? '#00B894' : '#D63031'
                        }}>
                            {(stats.weeklyDeficit || 0) > 0 ? `-${(stats.weeklyDeficit || 0).toFixed(0)}` : `+${(stats.weeklySurplus || 0).toFixed(0)}`} cal
                        </p>
                        <p style={{ margin: '5px 0 0 0', fontSize: '12px', color: '#636E72' }}>
                            {(stats.weeklyDeficit || 0) > 0 ? 'Deficit' : 'Surplus'}
                        </p>
                    </div>
                    
                    <div style={{ textAlign: 'center' }}>
                        <h3 style={{ margin: '0 0 10px 0', color: '#2C3E50', fontSize: '14px' }}>Weight Change</h3>
                        <p style={{ 
                            margin: '0', 
                            fontSize: '24px', 
                            fontWeight: 'bold',
                            color: (stats.poundsChange || 0) > 0 ? '#00B894' : '#D63031'
                        }}>
                            {(stats.poundsChange || 0) > 0 ? `-${(stats.poundsChange || 0).toFixed(2)}` : `+${Math.abs(stats.poundsChange || 0).toFixed(2)}`} lbs
                        </p>
                        <p style={{ margin: '5px 0 0 0', fontSize: '12px', color: '#636E72' }}>This week</p>
                    </div>
                    
                    <div style={{ textAlign: 'center' }}>
                        <h3 style={{ margin: '0 0 10px 0', color: '#2C3E50', fontSize: '14px' }}>Current Weight</h3>
                        <p style={{ 
                            margin: '0', 
                            fontSize: '24px', 
                            fontWeight: 'bold',
                            color: '#00B894'
                        }}>
                            {stats.currentWeight ? `${stats.currentWeight.toFixed(1)} lbs` : 'N/A'}
                        </p>
                        <p style={{ margin: '5px 0 0 0', fontSize: '12px', color: '#636E72' }}>Latest recorded</p>
                    </div>
                    
                    <div style={{ textAlign: 'center' }}>
                        <h3 style={{ margin: '0 0 10px 0', color: '#2C3E50', fontSize: '14px' }}>Projected Weight</h3>
                        <p style={{ 
                            margin: '0', 
                            fontSize: '24px', 
                            fontWeight: 'bold',
                            color: '#F39C12'
                        }}>
                            {stats.projectedWeight ? `${stats.projectedWeight.toFixed(1)} lbs` : 'N/A'}
                        </p>
                        <p style={{ margin: '5px 0 0 0', fontSize: '12px', color: '#636E72' }}>In 1 month</p>
                    </div>
                </div>
            )}
            
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
                backgroundColor: '#F8F9FA',
                borderRadius: '8px',
                border: '2px solid #E9ECEF'
            }}>
                <h3 style={{ 
                    margin: '0 0 10px 0',
                    color: '#2C3E50'
                }}>
                    7-Day Summary
                </h3>
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-around',
                    flexWrap: 'wrap',
                    gap: '20px'
                }}>
                    <div>
                        <p style={{ margin: '0', fontSize: '14px', color: '#636E72' }}>Avg Consumed</p>
                        <p style={{ margin: '5px 0 0 0', fontSize: '18px', fontWeight: 'bold', color: '#FF6B6B' }}>
                            {Math.round(caloriesData.data.reduce((sum, day) => sum + day.calories_consumed, 0) / caloriesData.data.length)}
                        </p>
                    </div>
                    <div>
                        <p style={{ margin: '0', fontSize: '14px', color: '#636E72' }}>Avg Burned</p>
                        <p style={{ margin: '5px 0 0 0', fontSize: '18px', fontWeight: 'bold', color: '#4ECDC4' }}>
                            {Math.round(caloriesData.data.reduce((sum, day) => sum + day.calories_burned, 0) / caloriesData.data.length)}
                        </p>
                    </div>
                    <div>
                        <p style={{ margin: '0', fontSize: '14px', color: '#636E72' }}>Avg Net</p>
                        <p style={{ 
                            margin: '5px 0 0 0', 
                            fontSize: '18px', 
                            fontWeight: 'bold',
                            color: (() => {
                                const avgNet = caloriesData.data.reduce((sum, day) => sum + day.net_calories, 0) / caloriesData.data.length;
                                return avgNet > 0 ? '#D63031' : '#00B894';
                            })()
                        }}>
                            {Math.round(caloriesData.data.reduce((sum, day) => sum + day.net_calories, 0) / caloriesData.data.length)}
                        </p>
                    </div>
                </div>
            </div>
            
            {/* Additional Insights */}
            {stats && (
                <div style={{
                    marginTop: '15px',
                    padding: '15px',
                    backgroundColor: '#F8F9FA',
                    borderRadius: '8px',
                    border: '2px solid #E9ECEF'
                }}>
                    <h3 style={{ 
                        margin: '0 0 10px 0',
                        color: '#2C3E50',
                        fontSize: '16px'
                    }}>
                        Weekly Insights
                    </h3>
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                        gap: '10px',
                        fontSize: '12px',
                        color: '#636E72'
                    }}>
                        <div>
                            <p style={{ margin: '5px 0' }}>
                                <strong>Total Calories Consumed:</strong> {(stats.totalConsumed || 0).toFixed(0)} cal
                            </p>
                            <p style={{ margin: '5px 0' }}>
                                <strong>Total Calories Burned:</strong> {(stats.totalBurned || 0).toFixed(0)} cal
                            </p>
                            <p style={{ margin: '5px 0' }}>
                                <strong>Daily Average Consumed:</strong> {((stats.totalConsumed || 0) / 7).toFixed(0)} cal
                            </p>
                            <p style={{ margin: '5px 0' }}>
                                <strong>Daily Average Burned:</strong> {((stats.totalBurned || 0) / 7).toFixed(0)} cal
                            </p>
                        </div>
                        <div>
                            <p style={{ margin: '5px 0' }}>
                                <strong>Weekly {(stats.weeklyDeficit || 0) > 0 ? 'Deficit' : 'Surplus'}:</strong> {Math.abs((stats.weeklyDeficit || 0) > 0 ? (stats.weeklyDeficit || 0) : (stats.weeklySurplus || 0)).toFixed(0)} cal
                            </p>
                            <p style={{ margin: '5px 0' }}>
                                <strong>Weight Change This Week:</strong> {(stats.poundsChange || 0) > 0 ? `-${(stats.poundsChange || 0).toFixed(2)}` : `+${Math.abs(stats.poundsChange || 0).toFixed(2)}`} lbs
                            </p>
                            <p style={{ margin: '5px 0' }}>
                                <strong>Projected Monthly Change:</strong> {(stats.monthlyPoundsChange || 0) > 0 ? `-${(stats.monthlyPoundsChange || 0).toFixed(1)}` : `+${Math.abs(stats.monthlyPoundsChange || 0).toFixed(1)}`} lbs
                            </p>
                            {stats.projectedWeight && (
                                <p style={{ margin: '5px 0' }}>
                                    <strong>Weight in 1 Month:</strong> {stats.projectedWeight.toFixed(1)} lbs
                                </p>
                            )}
                        </div>
                    </div>
                </div>
            )}
            
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