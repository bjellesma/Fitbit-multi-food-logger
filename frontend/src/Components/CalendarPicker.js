import React, { useState, useEffect } from 'react';

const CalendarPicker = ({ selectedDate, onDateChange }) => {
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [isOpen, setIsOpen] = useState(false);

  // Convert date string (YYYY-MM-DD) to Date object
  const getDateFromString = (dateString) => {
    if (!dateString) return new Date();
    const [year, month, day] = dateString.split('-').map(Number);
    return new Date(year, month - 1, day);
  };

  // Convert Date object to string (YYYY-MM-DD)
  const getDateString = (date) => {
    return date.toLocaleDateString('en-CA');
  };

  // Initialize with selected date
  useEffect(() => {
    if (selectedDate) {
      const date = getDateFromString(selectedDate);
      setCurrentMonth(new Date(date.getFullYear(), date.getMonth(), 1));
    }
  }, [selectedDate]);

  const getDaysInMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  };

  const formatDate = (date) => {
    return date.toLocaleDateString('en-US', { 
      weekday: 'short', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  const isToday = (date) => {
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  const isSelected = (date) => {
    if (!selectedDate) return false;
    return getDateString(date) === selectedDate;
  };

  const handleDateClick = (date) => {
    const dateString = getDateString(date);
    onDateChange(dateString);
    setIsOpen(false);
  };

  const goToPreviousMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1));
  };

  const goToNextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1));
  };

  const goToToday = () => {
    const today = new Date();
    setCurrentMonth(new Date(today.getFullYear(), today.getMonth(), 1));
    onDateChange(getDateString(today));
    setIsOpen(false);
  };

  const renderCalendar = () => {
    const daysInMonth = getDaysInMonth(currentMonth);
    const firstDayOfMonth = getFirstDayOfMonth(currentMonth);
    const days = [];

    // Add empty cells for days before the first day of the month
    for (let i = 0; i < firstDayOfMonth; i++) {
      days.push(<div key={`empty-${i}`} className="calendar-day empty"></div>);
    }

    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day);
      const isTodayDate = isToday(date);
      const isSelectedDate = isSelected(date);
      
      days.push(
        <div
          key={day}
          className={`calendar-day ${isTodayDate ? 'today' : ''} ${isSelectedDate ? 'selected' : ''}`}
          onClick={() => handleDateClick(date)}
          style={{
            padding: '8px',
            textAlign: 'center',
            cursor: 'pointer',
            borderRadius: '4px',
            backgroundColor: isSelectedDate ? '#3498DB' : isTodayDate ? '#E8F4FD' : 'transparent',
            color: isSelectedDate ? 'white' : isTodayDate ? '#3498DB' : '#2C3E50',
            fontWeight: isTodayDate || isSelectedDate ? 'bold' : 'normal',
            border: isTodayDate && !isSelectedDate ? '2px solid #3498DB' : 'none'
          }}
        >
          {day}
        </div>
      );
    }

    return days;
  };

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  return (
    <div style={{ position: 'relative', display: 'inline-block' }}>
      {/* Date Display Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          padding: '10px 15px',
          borderRadius: '5px',
          border: '1px solid #BDC3C7',
          fontSize: '14px',
          minWidth: '200px',
          backgroundColor: 'white',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}
      >
        <span>{selectedDate ? formatDate(getDateFromString(selectedDate)) : 'Select a date'}</span>
        <span style={{ fontSize: '12px' }}>▼</span>
      </button>

      {/* Calendar Dropdown */}
      {isOpen && (
        <div style={{
          position: 'absolute',
          top: '100%',
          left: '0',
          right: '0',
          backgroundColor: 'white',
          border: '1px solid #BDC3C7',
          borderRadius: '8px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          zIndex: 1000,
          padding: '15px',
          marginTop: '5px'
        }}>
          {/* Header */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '15px'
          }}>
            <button
              onClick={goToPreviousMonth}
              style={{
                background: 'none',
                border: 'none',
                fontSize: '18px',
                cursor: 'pointer',
                color: '#3498DB',
                padding: '5px'
              }}
            >
              ‹
            </button>
            <h3 style={{
              margin: '0',
              fontSize: '16px',
              fontWeight: 'bold',
              color: '#2C3E50'
            }}>
              {monthNames[currentMonth.getMonth()]} {currentMonth.getFullYear()}
            </h3>
            <button
              onClick={goToNextMonth}
              style={{
                background: 'none',
                border: 'none',
                fontSize: '18px',
                cursor: 'pointer',
                color: '#3498DB',
                padding: '5px'
              }}
            >
              ›
            </button>
          </div>

          {/* Today Button */}
          <button
            onClick={goToToday}
            style={{
              width: '100%',
              padding: '8px',
              marginBottom: '10px',
              backgroundColor: '#27AE60',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px',
              fontWeight: 'bold'
            }}
          >
            Today
          </button>

          {/* Day Headers */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(7, 1fr)',
            gap: '2px',
            marginBottom: '5px'
          }}>
            {dayNames.map(day => (
              <div
                key={day}
                style={{
                  padding: '8px',
                  textAlign: 'center',
                  fontSize: '12px',
                  fontWeight: 'bold',
                  color: '#7F8C8D'
                }}
              >
                {day}
              </div>
            ))}
          </div>

          {/* Calendar Grid */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(7, 1fr)',
            gap: '2px'
          }}>
            {renderCalendar()}
          </div>
        </div>
      )}

      {/* Click outside to close */}
      {isOpen && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            zIndex: 999
          }}
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

export default CalendarPicker; 