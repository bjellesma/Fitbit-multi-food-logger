import React, { useState, useEffect } from 'react';
import axios from 'axios';
import CaloriesChart from './Components/CaloriesChart';
import FoodLog from './Components/FoodLog';
import FoodSearchModal from './Components/FoodSearchModal';
import CalendarPicker from './Components/CalendarPicker';

function App() {
  const [meal, setMeal] = useState('');
  const [mealType, setMealType] = useState('');
  const [selectedDate, setSelectedDate] = useState(new Date().toLocaleDateString('en-CA'));
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [submitStatus, setSubmitStatus] = useState(null);
  const [loggingMode, setLoggingMode] = useState('meal'); // 'meal' or 'individual'
  const [isFoodSearchModalOpen, setIsFoodSearchModalOpen] = useState(false);



  const handleSubmit = async (event) => {
    event.preventDefault();
    
    if (!meal || !mealType) {
      setSubmitStatus({ type: 'error', message: 'Please select both a meal and meal type' });
      return;
    }
    const foodEntries = {
      meal: parseInt(meal),
      mealType: parseInt(mealType),
      date: selectedDate, // Use the selected date directly
    };

    try {
      setSubmitStatus({ type: 'loading', message: 'Logging food...' });
      const response = await axios.post('http://localhost:5000/api/log_food', foodEntries);
      
      setSubmitStatus({ 
        type: 'success', 
        message: response.data.message,
        loggedFoods: response.data.logged_foods || []
      });
      
      // Trigger calories chart refresh
      setRefreshTrigger(prev => prev + 1);
      
      // Reset form
      setMeal('');
      setMealType('');
      
    } catch (error) {
      setSubmitStatus({ 
        type: 'error', 
        message: error.response?.data?.error || 'Failed to log food' 
      });
    }
  };

  const handleFoodSearchSuccess = () => {
    setRefreshTrigger(prev => prev + 1);
    setSubmitStatus({ 
      type: 'success', 
      message: 'Individual food logged successfully!' 
    });
  };

  return (
    <div className="App" style={{ 
      maxWidth: '1200px', 
      margin: '0 auto', 
      padding: '20px',
      fontFamily: 'Arial, sans-serif'
    }}>
      <h1 style={{ 
        textAlign: 'center', 
        color: '#2C3E50',
        marginBottom: '30px'
      }}>
        Fitbit Multi Food Editor
      </h1>
      
      {/* Date Selection */}
      <div style={{
        backgroundColor: '#F8F9FA',
        padding: '20px',
        borderRadius: '10px',
        marginBottom: '30px',
        textAlign: 'center'
      }}>
        <h3 style={{ 
          color: '#34495E',
          marginBottom: '15px'
        }}>
          Select Date to View
        </h3>
        <CalendarPicker 
          selectedDate={selectedDate}
          onDateChange={setSelectedDate}
        />
      </div>
      
      {/* Calories Chart Section */}
      <div style={{ marginBottom: '40px' }}>
        <h2 style={{ 
          textAlign: 'center', 
          color: '#34495E',
          marginBottom: '20px'
        }}>
          Daily Calories Summary
        </h2>
        <CaloriesChart refreshTrigger={refreshTrigger} />
      </div>
      
      {/* Food Log Section */}
      <div style={{ marginBottom: '40px' }}>
        <h2 style={{ 
          textAlign: 'center', 
          color: '#34495E',
          marginBottom: '20px'
        }}>
          Food Log
        </h2>
        <FoodLog selectedDate={selectedDate} refreshTrigger={refreshTrigger} />
      </div>
      
      {/* Food Logging Section */}
      <div style={{
        backgroundColor: '#F8F9FA',
        padding: '30px',
        borderRadius: '10px',
        boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
      }}>
        <h2 style={{ 
          textAlign: 'center', 
          color: '#34495E',
          marginBottom: '30px'
        }}>
          Log Food Entry
        </h2>
        
        {/* Mode Toggle */}
        <div style={{ 
          textAlign: 'center', 
          marginBottom: '30px' 
        }}>
          <div style={{
            display: 'inline-flex',
            backgroundColor: '#E9ECEF',
            borderRadius: '25px',
            padding: '4px'
          }}>
            <button
              type="button"
              onClick={() => setLoggingMode('meal')}
              style={{
                padding: '10px 20px',
                borderRadius: '20px',
                border: 'none',
                backgroundColor: loggingMode === 'meal' ? '#3498DB' : 'transparent',
                color: loggingMode === 'meal' ? 'white' : '#6C757D',
                cursor: 'pointer',
                fontWeight: 'bold',
                fontSize: '14px'
              }}
            >
              Predefined Meals
            </button>
            <button
              type="button"
              onClick={() => setLoggingMode('individual')}
              style={{
                padding: '10px 20px',
                borderRadius: '20px',
                border: 'none',
                backgroundColor: loggingMode === 'individual' ? '#3498DB' : 'transparent',
                color: loggingMode === 'individual' ? 'white' : '#6C757D',
                cursor: 'pointer',
                fontWeight: 'bold',
                fontSize: '14px'
              }}
            >
              Individual Foods
            </button>
          </div>
        </div>
        
        {/* Status Message */}
        {submitStatus && (
          <div style={{
            padding: '15px',
            marginBottom: '20px',
            borderRadius: '5px',
            textAlign: 'center',
            backgroundColor: submitStatus.type === 'success' ? '#D4EDDA' : 
                           submitStatus.type === 'error' ? '#F8D7DA' : '#D1ECF1',
            color: submitStatus.type === 'success' ? '#155724' : 
                   submitStatus.type === 'error' ? '#721C24' : '#0C5460',
            border: `1px solid ${submitStatus.type === 'success' ? '#C3E6CB' : 
                                submitStatus.type === 'error' ? '#F5C6CB' : '#BEE5EB'}`
          }}>
            {submitStatus.message}
            {submitStatus.loggedFoods && submitStatus.loggedFoods.length > 0 && (
              <div style={{ marginTop: '10px', fontSize: '14px' }}>
                Logged: {submitStatus.loggedFoods.join(', ')}
              </div>
            )}
          </div>
        )}
        
        {loggingMode === 'meal' ? (
          <form onSubmit={handleSubmit} style={{ maxWidth: '500px', margin: '0 auto' }}>
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: '#2C3E50' }}>
                What do you want to add?
              </label>
              <select 
                value={meal} 
                onChange={(e) => setMeal(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px',
                  borderRadius: '5px',
                  border: '1px solid #BDC3C7',
                  fontSize: '14px'
                }}
              >
                <option value="">Select a meal</option>
                <option value="1">Morning Shake</option>
                <option value="2">Oatmeal Pie</option>
                <option value="3">Yogurt</option>
                <option value="4">Grapes/Carrots</option>
                <option value="5">Soylent</option>
                <option value="6">Granola</option>
                <option value="7">Preworkout</option>
                <option value="8">Post Workout</option>
                <option value="9">Chicken and Pasta</option>
              </select>
            </div>
            
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: '#2C3E50' }}>
                When did you eat this?
              </label>
              <select 
                value={mealType} 
                onChange={(e) => setMealType(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px',
                  borderRadius: '5px',
                  border: '1px solid #BDC3C7',
                  fontSize: '14px'
                }}
              >
                <option value="">Select meal type</option>
                <option value="1">Breakfast</option>
                <option value="2">Morning Snack</option>
                <option value="3">Lunch</option>
                <option value="4">Afternoon Snack</option>
                <option value="5">Dinner</option>
              </select>
            </div>
            
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: '#2C3E50' }}>
                Select a Date
              </label>
              <CalendarPicker 
                selectedDate={selectedDate}
                onDateChange={setSelectedDate}
              />
            </div>
            
            <button 
              type="submit"
              disabled={submitStatus?.type === 'loading'}
              style={{
                width: '100%',
                padding: '12px',
                backgroundColor: submitStatus?.type === 'loading' ? '#95A5A6' : '#3498DB',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                fontSize: '16px',
                cursor: submitStatus?.type === 'loading' ? 'not-allowed' : 'pointer',
                fontWeight: 'bold'
              }}
            >
              {submitStatus?.type === 'loading' ? 'Logging...' : 'Log Meal'}
            </button>
          </form>
        ) : (
          <div style={{ textAlign: 'center' }}>
            <p style={{ 
              marginBottom: '20px', 
              color: '#6C757D',
              fontSize: '16px'
            }}>
              Search for and log individual food items
            </p>
            <button
              onClick={() => setIsFoodSearchModalOpen(true)}
              style={{
                padding: '12px 24px',
                backgroundColor: '#3498DB',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                fontSize: '16px',
                cursor: 'pointer',
                fontWeight: 'bold'
              }}
            >
              Search & Log Individual Food
            </button>
          </div>
        )}
      </div>

      {/* Food Search Modal */}
      <FoodSearchModal
        isOpen={isFoodSearchModalOpen}
        onClose={() => setIsFoodSearchModalOpen(false)}
        onFoodSelected={handleFoodSearchSuccess}
        selectedDate={selectedDate}
      />
    </div>
  );
}

export default App;
