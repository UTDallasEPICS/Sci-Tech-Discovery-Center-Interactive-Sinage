import { useState, useEffect } from 'react';
import LangaugeSelect from './components/langaugeSelect';
import VideoScreen from './components/videoScreen';

function App() {
  // State to track which screen to display
  const [view, setView] = useState('welcome');
  
 
  const [eventData, setEventData] = useState(null);

  useEffect(() => {
    // Replace '/api/sse-endpoint' with your actual backend URL
    const eventSource = new EventSource('http://localhost:8000/api/events');

    // listening for messages
    eventSource.onmessage = (event) => {
      console.log("New event received:", event.data);
      
      // Parse data if your server sends JSON
      const parsedData = JSON.parse(event.data);
      setEventData(parsedData);

      // 3. Trigger the screen change
      setView('exploration');
    };


    return () => {
      eventSource.close();
    };
  }, []); 

  // 5. Conditional Rendering
  return (
    <main>

      {view === 'welcome' && <LangaugeSelect />}
      
      {view === 'exploration' && (
        <VideoScreen data={eventData} />
      )}
    </main>
  );
}

export default App;