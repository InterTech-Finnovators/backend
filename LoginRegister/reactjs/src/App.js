import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link, Navigate } from 'react-router-dom';
import LoginForm from './Components/LoginForm/LoginForm';
import RegisterForm from './Components/LoginForm/RegisterForm';

function App() {
   
    return (
        <Router>
            <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
               
                <Routes>
                    <Route path="/login" element={<LoginForm />} />
                    <Route path="/register" element={<RegisterForm />} />
                    <Route path="/" element={<Navigate to="/login" replace />} />
                </Routes>
                
            </div>
        </Router>
    );
}


export default App;