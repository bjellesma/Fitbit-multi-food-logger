import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import EditFoodModal from './EditFoodModal';
import FoodInfoModal from './FoodInfoModal';

const FoodLog = ({ selectedDate, refreshTrigger = 0 }) => {
  const [foodsData, setFoodsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deletingFood, setDeletingFood] = useState(null);
  const [editingFood, setEditingFood] = useState(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedFood, setSelectedFood] = useState(null);
  const [isInfoModalOpen, setIsInfoModalOpen] = useState(false);

  const fetchFoodsData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(`http://localhost:5000/api/foods?date=${selectedDate}`);
      setFoodsData(response.data);
      setError(null);
    } catch (err) {
      if (err.response && err.response.status === 429) {
        setError('Fitbit API rate limit reached. Please wait and try again later.');
      } else {
        setError('Failed to fetch foods data');
      }
      console.error('Error fetching foods data:', err);
    } finally {
      setLoading(false);
    }
  }, [selectedDate]);

  useEffect(() => {
    if (selectedDate) {
      fetchFoodsData();
    }
  }, [selectedDate, refreshTrigger, fetchFoodsData]);

  const handleDeleteFood = async (foodId, foodName) => {
    if (!window.confirm(`Are you sure you want to delete "${foodName}"?`)) {
      return;
    }

    try {
      setDeletingFood(foodId);
      await axios.delete(`http://localhost:5000/api/foods/${foodId}`);
      
      // Refresh the food data after successful deletion
      await fetchFoodsData();
      
    } catch (err) {
      console.error('Error deleting food:', err);
      alert('Failed to delete food. Please try again.');
    } finally {
      setDeletingFood(null);
    }
  };

  const handleEditFood = (food) => {
    setEditingFood(food);
    setIsEditModalOpen(true);
  };

  const handleCloseEditModal = () => {
    setIsEditModalOpen(false);
    setEditingFood(null);
  };

  const handleShowFoodInfo = (food) => {
    setSelectedFood(food);
    setIsInfoModalOpen(true);
  };

  const handleCloseInfoModal = () => {
    setIsInfoModalOpen(false);
    setSelectedFood(null);
  };

  const handleFoodUpdate = async () => {
    await fetchFoodsData();
  };

  const getMealTypeName = (mealTypeId) => {
    const mealTypes = {
      1: 'Breakfast',
      2: 'Morning Snack',
      3: 'Lunch',
      4: 'Afternoon Snack',
      5: 'Dinner'
    };
    return mealTypes[mealTypeId] || 'Unknown';
  };

  const groupFoodsByMeal = (foods) => {
    const grouped = {};
    foods.forEach(food => {
      const mealType = getMealTypeName(food.mealType);
      if (!grouped[mealType]) {
        grouped[mealType] = [];
      }
      grouped[mealType].push(food);
    });
    return grouped;
  };

  if (loading) {
    return (
      <div style={{ 
        textAlign: 'center', 
        padding: '40px',
        color: '#7F8C8D',
        fontSize: '16px'
      }}>
        Loading food log...
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
          onClick={fetchFoodsData}
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

  if (!foodsData || foodsData.foods.length === 0) {
    return (
      <div style={{ 
        textAlign: 'center', 
        padding: '40px',
        color: '#7F8C8D',
        fontSize: '16px',
        backgroundColor: '#F8F9FA',
        borderRadius: '8px',
        border: '1px solid #E9ECEF'
      }}>
        No foods logged for {foodsData?.date || 'this date'}
      </div>
    );
  }

  const groupedFoods = groupFoodsByMeal(foodsData.foods);
  const totalCalories = foodsData.foods.reduce((sum, food) => sum + food.calories, 0);

  return (
    <>
      <div style={{ 
        padding: '20px', 
        backgroundColor: '#FFFFFF', 
        borderRadius: '10px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        margin: '20px 0'
      }}>
        <h3 style={{ 
          textAlign: 'center', 
          color: '#2C3E50',
          marginBottom: '20px'
        }}>
          Food Log - {foodsData.date}
        </h3>
        
        {/* Total Calories Summary */}
        <div style={{
          textAlign: 'center',
          marginBottom: '20px',
          padding: '15px',
          backgroundColor: '#E8F5E8',
          borderRadius: '8px',
          border: '2px solid #27AE60'
        }}>
          <h4 style={{ 
            margin: '0 0 5px 0',
            color: '#27AE60'
          }}>
            Total Calories: {totalCalories}
          </h4>
          <p style={{ 
            margin: '0',
            fontSize: '14px',
            color: '#636E72'
          }}>
            {foodsData.total_foods} foods logged
          </p>
        </div>

        {/* Foods by Meal Type */}
        {Object.entries(groupedFoods).map(([mealType, foods]) => (
          
          <div key={mealType} style={{ marginBottom: '20px' }}>
            <h4 style={{ 
              color: '#34495E',
              borderBottom: '2px solid #3498DB',
              paddingBottom: '5px',
              marginBottom: '15px'
            }}>
              {mealType}
            </h4>
            
            {foods.map((food, index) => (
              <div key={index} style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '10px',
                marginBottom: '8px',
                backgroundColor: '#F8F9FA',
                borderRadius: '5px',
                border: '1px solid #E9ECEF',
                position: 'relative',
                cursor: 'pointer',
                transition: 'background-color 0.2s ease'
              }}
              onMouseEnter={(e) => e.target.style.backgroundColor = '#E9ECEF'}
              onMouseLeave={(e) => e.target.style.backgroundColor = '#F8F9FA'}
              onClick={() => handleShowFoodInfo(food)}
              >
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 'bold', color: '#2C3E50' }}>
                    {food.name}
                  </div>
                  <div style={{ fontSize: '12px', color: '#7F8C8D' }}>
                    {food.amount} {food.unit}
                  </div>
                </div>
                <div style={{ 
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <div style={{ 
                    textAlign: 'right',
                    color: '#E74C3C',
                    fontWeight: 'bold'
                  }}>
                    {food.calories} cal
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleEditFood(food);
                    }}
                    style={{
                      padding: '4px 8px',
                      backgroundColor: '#3498DB',
                      color: 'white',
                      border: 'none',
                      borderRadius: '3px',
                      cursor: 'pointer',
                      fontSize: '10px',
                      fontWeight: 'bold',
                      minWidth: '40px'
                    }}
                    title="Edit this food item"
                  >
                    ✏️
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteFood(food.id, food.name);
                    }}
                    disabled={deletingFood === food.id}
                    style={{
                      padding: '4px 8px',
                      backgroundColor: deletingFood === food.id ? '#95A5A6' : '#E74C3C',
                      color: 'white',
                      border: 'none',
                      borderRadius: '3px',
                      cursor: deletingFood === food.id ? 'not-allowed' : 'pointer',
                      fontSize: '10px',
                      fontWeight: 'bold',
                      minWidth: '40px'
                    }}
                    title="Delete this food item"
                  >
                    {deletingFood === food.id ? '...' : '×'}
                  </button>
                </div>
              </div>
            ))}
            
            {/* Meal Type Total */}
            <div style={{
              textAlign: 'right',
              padding: '8px',
              backgroundColor: '#E3F2FD',
              borderRadius: '5px',
              marginTop: '10px',
              border: '1px solid #2196F3'
            }}>
              <span style={{ fontWeight: 'bold', color: '#1976D2' }}>
                {foods.reduce((sum, food) => sum + food.calories, 0)} calories
              </span>
            </div>
          </div>
        ))}
        
        {/* Refresh Button */}
        <div style={{ textAlign: 'center', marginTop: '20px' }}>
          <button 
            onClick={fetchFoodsData}
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
            Refresh Food Log
          </button>
        </div>
      </div>

      {/* Edit Food Modal */}
      <EditFoodModal
        isOpen={isEditModalOpen}
        onClose={handleCloseEditModal}
        food={editingFood}
        onUpdate={handleFoodUpdate}
        currentDate={selectedDate}
      />

      {/* Food Info Modal */}
      <FoodInfoModal
        isOpen={isInfoModalOpen}
        onClose={handleCloseInfoModal}
        food={selectedFood}
      />
    </>
  );
};

export default FoodLog; 