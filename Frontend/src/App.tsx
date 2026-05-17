import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Dashboard, ManageShipments } from '@/pages';

/**
 * App Component
 * Main application component with routing
 */
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/manage-shipments" element={<ManageShipments />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;

// Made with Bob
