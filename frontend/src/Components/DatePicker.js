import React, { useState } from 'react'; // React core and useState hook for state management
import ReactDatePicker from 'react-datepicker'; // The DatePicker component from react-datepicker
import 'react-datepicker/dist/react-datepicker.css'; // Styles for the DatePicker component

// Define the DatePicker functional component
function DatePicker() {
  // State hook for managing the selected date, initialized to the current date
  const [selectedDate, setSelectedDate] = useState(new Date());

  return (
    <div>
      {/* ReactDatePicker component with two props:
          selected - the currently selected date to display
          onChange - function to update the state when a new date is selected */}
      <ReactDatePicker selected={selectedDate} onChange={(date) => setSelectedDate(date)} />
    </div>
  );
}

// Export the DatePicker component for use in other parts of the app
export default DatePicker;