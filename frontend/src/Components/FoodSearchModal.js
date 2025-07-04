import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const FoodSearchModal = ({ isOpen, onClose, onFoodSelected }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedFood, setSelectedFood] = useState(null);
  const [amount, setAmount] = useState('');
  const [selectedUnit, setSelectedUnit] = useState('');
  const searchTimeoutRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      setSearchQuery('');
      setSearchResults([]);
      setSelectedFood(null);
      setAmount('');
      setSelectedUnit('');
      setError(null);
    }
  }, [isOpen]);

  const searchFoods = async (query) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`http://localhost:5000/api/foods/search?q=${encodeURIComponent(query)}`);
      setSearchResults(response.data.foods);
    } catch (err) {
      setError('Failed to search foods');
      console.error('Error searching foods:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchChange = (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    
    // Debounce search
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    searchTimeoutRef.current = setTimeout(() => {
      searchFoods(query);
    }, 300);
  };

  const handleFoodSelect = (food) => {
    setSelectedFood(food);
    setSelectedUnit('');
    setAmount('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedFood || !amount || !selectedUnit) {
      setError('Please select a food, amount, and unit');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      // Log the individual food
      const response = await axios.post('http://localhost:5000/api/log_individual_food', {
        foodId: selectedFood.id,
        amount: parseFloat(amount),
        unitId: selectedUnit,
        mealTypeId: 1, // Default to breakfast, can be made configurable
        dateOption: 1, // Default to today, can be made configurable
        date: new Date().toLocaleDateString('en-CA') // Send today's date in local timezone
      });
      
      // Trigger parent refresh
      if (onFoodSelected) {
        onFoodSelected();
      }
      
      // Trigger calories chart refresh
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('foodAdded'));
      }
      
      onClose();
      
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to log food');
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
          Search and Log Individual Food
        </h3>
        
        <form onSubmit={handleSubmit}>
          {/* Food Search */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              fontWeight: 'bold',
              color: '#2C3E50'
            }}>
              Search for Food
            </label>
            <input
              type="text"
              value={searchQuery}
              onChange={handleSearchChange}
              style={{
                width: '100%',
                padding: '10px',
                borderRadius: '5px',
                border: '1px solid #BDC3C7',
                fontSize: '14px'
              }}
              placeholder="Enter food name..."
            />
          </div>

          {/* Search Results */}
          {loading && (
            <div style={{ textAlign: 'center', padding: '10px', color: '#7F8C8D' }}>
              Searching...
            </div>
          )}

          {searchResults.length > 0 && (
            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: 'bold',
                color: '#2C3E50'
              }}>
                Select Food
              </label>
              <div style={{
                maxHeight: '200px',
                overflowY: 'auto',
                border: '1px solid #BDC3C7',
                borderRadius: '5px'
              }}>
                {searchResults.map((food) => (
                  <div
                    key={food.id}
                    onClick={() => handleFoodSelect(food)}
                    style={{
                      padding: '10px',
                      borderBottom: '1px solid #E9ECEF',
                      cursor: 'pointer',
                      backgroundColor: selectedFood?.id === food.id ? '#E3F2FD' : 'white',
                      hover: { backgroundColor: '#F8F9FA' }
                    }}
                  >
                    <div style={{ fontWeight: 'bold', color: '#2C3E50' }}>
                      {food.name}
                    </div>
                    {food.brand && (
                      <div style={{ fontSize: '12px', color: '#7F8C8D' }}>
                        {food.brand}
                      </div>
                    )}
                    <div style={{ fontSize: '12px', color: '#E74C3C' }}>
                      {food.calories} calories
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Amount and Unit Selection */}
          {selectedFood && (
            <>
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
                  value={selectedUnit}
                  onChange={(e) => setSelectedUnit(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px',
                    borderRadius: '5px',
                    border: '1px solid #BDC3C7',
                    fontSize: '14px'
                  }}
                >
                  <option value="">Select unit</option>
                  {selectedFood.units && selectedFood.units.map((unit) => (
                    <option key={unit.id} value={unit.id}>
                      {unit.name}
                    </option>
                  ))}
                </select>
              </div>
            </>
          )}

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
              disabled={loading || !selectedFood || !amount || !selectedUnit}
              style={{
                padding: '10px 20px',
                backgroundColor: loading || !selectedFood || !amount || !selectedUnit ? '#95A5A6' : '#3498DB',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                cursor: loading || !selectedFood || !amount || !selectedUnit ? 'not-allowed' : 'pointer',
                fontSize: '14px',
                fontWeight: 'bold'
              }}
            >
              {loading ? 'Logging...' : 'Log Food'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default FoodSearchModal; 