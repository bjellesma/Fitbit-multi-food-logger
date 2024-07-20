import React, { useState } from 'react'; // React core and useState hook for state management
import ReactDatePicker from 'react-datepicker'; // The DatePicker component from react-datepicker
import 'react-datepicker/dist/react-datepicker.css'; // Styles for the DatePicker component

// Modify the DatePicker functional component to accept a prop named onDateChange
function DatePicker({ onDateChange }) {
  // State hook for managing the selected date, initialized to the current date
  const [selectedDate, setSelectedDate] = useState(new Date());

  // Update setSelectedDate to call onDateChange with the new date whenever the date changes
  const handleDateChange = (date) => {
    setSelectedDate(date);
    if (onDateChange) {
      onDateChange(date); // Call the passed in onDateChange function with the new date
    }
  };

  return (
    <div>
      {/* ReactDatePicker component with two props:
          selected - the currently selected date to display
          onChange - function to update the state and call onDateChange when a new date is selected */}
      <ReactDatePicker selected={selectedDate} onChange={handleDateChange} />
    </div>
  );
}

// Export the DatePicker component for use in other parts of the app
export default DatePicker;