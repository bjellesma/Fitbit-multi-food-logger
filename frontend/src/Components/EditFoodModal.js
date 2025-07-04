import React, { useState, useEffect } from 'react';
import axios from 'axios';

const EditFoodModal = ({ isOpen, onClose, food, onUpdate, currentDate }) => {
  const [amount, setAmount] = useState('');
  const [unitId, setUnitId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [units, setUnits] = useState([]);

  // Common unit options
  const commonUnits = [
    { id: 91, name: 'Cups' },
    { id: 226, name: 'Ounces' },
    { id: 301, name: 'scoop' },
    { id: 17, name: 'Bar' },
    { id: 69, name: 'Container' },
    { id: 27, name: 'Container' },
    { id: 229, name: 'Packets' },
    { id: 148, name: 'Grapes' },
    { id: 147, name: 'Banana' },
    { id: 364, name: 'Teaspoon' },
    { id: 304, name: 'Ounces' }
  ];

  // Get all available units including the original unit
  const getAllUnits = async () => {
    const allUnits = [...commonUnits];
    
    // Add the original unit if it's not already in the list
    if (food && food.unit) {
      const originalUnitExists = allUnits.some(unit => unit.name === food.unit);
      if (!originalUnitExists) {
        try {
          // Search for the unit by name to get its ID
          const response = await axios.get(`http://localhost:5000/api/units/search?q=${encodeURIComponent(food.unit)}`);
          if (response.data.units && response.data.units.length > 0) {
            // Use the first matching unit
            const foundUnit = response.data.units[0];
            allUnits.push({ id: foundUnit.id, name: foundUnit.name });
          } else {
            // If not found, add with a placeholder that will be handled by the backend
            allUnits.push({ id: 'original', name: food.unit });
          }
        } catch (err) {
          console.error('Error searching for unit:', err);
          // Add with a placeholder that will be handled by the backend
          allUnits.push({ id: 'original', name: food.unit });
        }
      } else {
        // If the original unit exists in common units, make sure we use the correct ID
        const existingUnit = allUnits.find(unit => unit.name === food.unit);
        if (existingUnit) {
          // Update the existing unit to ensure it has the correct ID
          const index = allUnits.findIndex(unit => unit.name === food.unit);
          if (index !== -1) {
            allUnits[index] = { id: existingUnit.id, name: existingUnit.name };
          }
        }
      }
    }
    
    return allUnits;
  };

  useEffect(() => {
    if (isOpen && food) {
      setAmount(food.amount.toString());
      
      // Get all units including the original unit
      getAllUnits().then(allUnits => {
        // Find the unit ID based on the unit name
        const unit = allUnits.find(u => u.name === food.unit);
        setUnitId(unit ? unit.id.toString() : '');
        setUnits(allUnits);
      });
      
      setError(null);
    }
  }, [isOpen, food]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!amount || !unitId) {
      setError('Please fill in all fields');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      // Prepare the payload - send all required fields
      console.log('DEBUG: food object:', food);
      console.log('DEBUG: food.time value:', food.time);
      
      // Handle unitId properly - if it's 'original', we need to find the actual unit ID
      let finalUnitId = unitId;
      if (unitId === 'original') {
        // Find the unit in our units list that matches the original unit name
        const originalUnit = units.find(u => u.name === food.unit);
        if (originalUnit && originalUnit.id !== 'original') {
          finalUnitId = originalUnit.id;
        } else {
          // If we can't find a proper ID, we'll need to handle this case
          setError('Unable to determine unit ID for the original unit. Please select a different unit.');
          return;
        }
      }
      
      console.log('DEBUG: Original unitId:', unitId);
      console.log('DEBUG: Final unitId:', finalUnitId);
      console.log('DEBUG: Food unit name:', food.unit);
      console.log('DEBUG: Available units:', units);
      console.log('DEBUG: Current date from food log:', currentDate);
      console.log('DEBUG: Food time field:', food.time);
      
      const payload = {
        amount: parseFloat(amount),
        unitId: finalUnitId,
        foodId: food.foodId,
        mealTypeId: food.mealType || food.mealTypeId,
        date: currentDate || new Date().toLocaleDateString('en-CA') // Use the current date from the food log view
      };
      
      const response = await axios.put(`http://localhost:5000/api/foods/${food.id}`, payload);
      
      // Trigger parent refresh
      if (onUpdate) {
        onUpdate();
      }
      
      onClose();
      
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update food');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

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
        maxWidth: '400px',
        width: '90%',
        maxHeight: '80vh',
        overflow: 'auto'
      }}>
        <h3 style={{
          margin: '0 0 20px 0',
          color: '#2C3E50',
          textAlign: 'center'
        }}>
          Edit Food Item
        </h3>
        
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              fontWeight: 'bold',
              color: '#2C3E50'
            }}>
              Food Name
            </label>
            <input
              type="text"
              value={food?.name || ''}
              disabled
              style={{
                width: '100%',
                padding: '10px',
                borderRadius: '5px',
                border: '1px solid #BDC3C7',
                fontSize: '14px',
                backgroundColor: '#F8F9FA',
                color: '#7F8C8D'
              }}
            />
          </div>
          
          <div style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              fontWeight: 'bold',
              color: '#2C3E50'
            }}>
              Amount
            </label>
            <input
              type="number"
              step="0.01"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              style={{
                width: '100%',
                padding: '10px',
                borderRadius: '5px',
                border: '1px solid #BDC3C7',
                fontSize: '14px'
              }}
              placeholder="Enter amount"
            />
          </div>
          
          <div style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              fontWeight: 'bold',
              color: '#2C3E50'
            }}>
              Unit
            </label>
            <select
              value={unitId}
              onChange={(e) => setUnitId(e.target.value)}
              style={{
                width: '100%',
                padding: '10px',
                borderRadius: '5px',
                border: '1px solid #BDC3C7',
                fontSize: '14px'
              }}
            >
              <option value="">Select unit</option>
              {units.map(unit => (
                <option key={unit.id} value={unit.id}>
                  {unit.name}
                </option>
              ))}
            </select>
          </div>
          
          {error && (
            <div style={{
              padding: '10px',
              marginBottom: '20px',
              backgroundColor: '#F8D7DA',
              color: '#721C24',
              borderRadius: '5px',
              border: '1px solid #F5C6CB',
              fontSize: '14px'
            }}>
              {error}
            </div>
          )}
          
          <div style={{
            display: 'flex',
            gap: '10px',
            justifyContent: 'flex-end'
          }}>
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              style={{
                padding: '10px 20px',
                backgroundColor: '#95A5A6',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                cursor: loading ? 'not-allowed' : 'pointer',
                fontSize: '14px'
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              style={{
                padding: '10px 20px',
                backgroundColor: loading ? '#95A5A6' : '#3498DB',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                cursor: loading ? 'not-allowed' : 'pointer',
                fontSize: '14px',
                fontWeight: 'bold'
              }}
            >
              {loading ? 'Updating...' : 'Update Food'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditFoodModal; 