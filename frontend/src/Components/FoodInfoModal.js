import React from 'react';

const FoodInfoModal = ({ isOpen, onClose, food }) => {
  if (!isOpen || !food) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      zIndex: 1000
    }}>
      <div style={{
        backgroundColor: 'white',
        padding: '30px',
        borderRadius: '10px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        maxWidth: '500px',
        width: '90%',
        maxHeight: '80vh',
        overflow: 'auto'
      }}>
        <h3 style={{
          margin: '0 0 20px 0',
          color: '#2C3E50',
          textAlign: 'center'
        }}>
          Food Information
        </h3>
        
        <div style={{ marginBottom: '20px' }}>
          <h4 style={{ 
            color: '#34495E',
            marginBottom: '10px',
            borderBottom: '2px solid #3498DB',
            paddingBottom: '5px'
          }}>
            Basic Information
          </h4>
          
          <div style={{ marginBottom: '15px' }}>
            <strong style={{ color: '#2C3E50' }}>Food Name:</strong>
            <div style={{ 
              padding: '8px',
              backgroundColor: '#F8F9FA',
              borderRadius: '4px',
              marginTop: '4px',
              fontFamily: 'monospace'
            }}>
              {food.name}
            </div>
          </div>
          
          <div style={{ marginBottom: '15px' }}>
            <strong style={{ color: '#2C3E50' }}>Food ID:</strong>
            <div style={{ 
              padding: '8px',
              backgroundColor: '#F8F9FA',
              borderRadius: '4px',
              marginTop: '4px',
              fontFamily: 'monospace',
              color: '#E74C3C'
            }}>
              {food.foodId}
            </div>
          </div>
          
          <div style={{ marginBottom: '15px' }}>
            <strong style={{ color: '#2C3E50' }}>Log ID:</strong>
            <div style={{ 
              padding: '8px',
              backgroundColor: '#F8F9FA',
              borderRadius: '4px',
              marginTop: '4px',
              fontFamily: 'monospace',
              color: '#E74C3C'
            }}>
              {food.id}
            </div>
          </div>
        </div>
        
        <div style={{ marginBottom: '20px' }}>
          <h4 style={{ 
            color: '#34495E',
            marginBottom: '10px',
            borderBottom: '2px solid #3498DB',
            paddingBottom: '5px'
          }}>
            Nutritional Information
          </h4>
          
          <div style={{ marginBottom: '15px' }}>
            <strong style={{ color: '#2C3E50' }}>Calories:</strong>
            <div style={{ 
              padding: '8px',
              backgroundColor: '#F8F9FA',
              borderRadius: '4px',
              marginTop: '4px',
              fontFamily: 'monospace',
              color: '#E74C3C'
            }}>
              {food.calories} cal
            </div>
          </div>
          
          <div style={{ marginBottom: '15px' }}>
            <strong style={{ color: '#2C3E50' }}>Amount:</strong>
            <div style={{ 
              padding: '8px',
              backgroundColor: '#F8F9FA',
              borderRadius: '4px',
              marginTop: '4px',
              fontFamily: 'monospace'
            }}>
              {food.amount}
            </div>
          </div>
          
          <div style={{ marginBottom: '15px' }}>
            <strong style={{ color: '#2C3E50' }}>Unit:</strong>
            <div style={{ 
              padding: '8px',
              backgroundColor: '#F8F9FA',
              borderRadius: '4px',
              marginTop: '4px',
              fontFamily: 'monospace'
            }}>
              {food.unit}
            </div>
          </div>
          
          <div style={{ marginBottom: '15px' }}>
            <strong style={{ color: '#2C3E50' }}>Unit ID:</strong>
            <div style={{ 
              padding: '8px',
              backgroundColor: '#F8F9FA',
              borderRadius: '4px',
              marginTop: '4px',
              fontFamily: 'monospace',
              color: '#E74C3C'
            }}>
              {food.unitId || 'Not available'}
            </div>
          </div>
        </div>
        
        <div style={{ marginBottom: '20px' }}>
          <h4 style={{ 
            color: '#34495E',
            marginBottom: '10px',
            borderBottom: '2px solid #3498DB',
            paddingBottom: '5px'
          }}>
            Meal Information
          </h4>
          
          <div style={{ marginBottom: '15px' }}>
            <strong style={{ color: '#2C3E50' }}>Meal Type ID:</strong>
            <div style={{ 
              padding: '8px',
              backgroundColor: '#F8F9FA',
              borderRadius: '4px',
              marginTop: '4px',
              fontFamily: 'monospace',
              color: '#E74C3C'
            }}>
              {food.mealType}
            </div>
          </div>
          
          <div style={{ marginBottom: '15px' }}>
            <strong style={{ color: '#2C3E50' }}>Meal Type Name:</strong>
            <div style={{ 
              padding: '8px',
              backgroundColor: '#F8F9FA',
              borderRadius: '4px',
              marginTop: '4px',
              fontFamily: 'monospace'
            }}>
              {getMealTypeName(food.mealType)}
            </div>
          </div>
        </div>
        
        <div style={{ marginBottom: '20px' }}>
          <h4 style={{ 
            color: '#34495E',
            marginBottom: '10px',
            borderBottom: '2px solid #3498DB',
            paddingBottom: '5px'
          }}>
            Additional Information
          </h4>
          
          <div style={{ marginBottom: '15px' }}>
            <strong style={{ color: '#2C3E50' }}>Log Time:</strong>
            <div style={{ 
              padding: '8px',
              backgroundColor: '#F8F9FA',
              borderRadius: '4px',
              marginTop: '4px',
              fontFamily: 'monospace'
            }}>
              {food.time || 'Not available'}
            </div>
          </div>
        </div>
        
        <div style={{
          display: 'flex',
          gap: '10px',
          justifyContent: 'center'
        }}>
          <button
            onClick={onClose}
            style={{
              padding: '10px 20px',
              backgroundColor: '#3498DB',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 'bold'
            }}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

// Helper function to get meal type name
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

export default FoodInfoModal; 