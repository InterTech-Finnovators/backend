import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './LoginForm.css';

function RegisterForm() {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    const handleRegister = async (e) => {
        e.preventDefault();
        setError(null);

        try {
            const response = await fetch('http://localhost:8000/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username,
                    email,
                    password,
                }),
            });

            if (!response.ok) {
                throw new Error('Registration failed');
            }

            const data = await response.json();
            if (data.success) {
                navigate('/login'); // Navigate to login page on successful registration
            } else {
                setError(data.message || 'Registration failed');
            }
        } catch (error) {
            setError('Registration failed. Please try again.');
        }
    };

    return (
        <div className="wrapper">
            <div className="form-box register">
                <form onSubmit={handleRegister}>
                    <h1>Create Account</h1>
                    {error && <div style={{ color: 'red' }}>{error}</div>}
                    <div className="input-box">
                        <input 
                            type="text" 
                            placeholder="Username" 
                            required 
                            value={username} 
                            onChange={(e) => setUsername(e.target.value)} 
                        />
                        <span className="icon"><i className="fas fa-user"></i></span>
                    </div>
                    <div className="input-box">
                        <input 
                            type="email" 
                            placeholder="Email" 
                            required 
                            value={email} 
                            onChange={(e) => setEmail(e.target.value)} 
                        />
                        <span className="icon"><i className="fas fa-envelope"></i></span>
                    </div>
                    <div className="input-box">
                        <input 
                            type="password" 
                            placeholder="Password" 
                            required 
                            value={password} 
                            onChange={(e) => setPassword(e.target.value)} 
                        />
                        <span className="icon"><i className="fas fa-lock"></i></span>
                    </div>
                    <button type="submit">Register</button>
                    <div className="register-link">
                        <p>Already have an account? <Link to="/login">Login</Link></p>
                    </div>
                    <div className="footer">
                        <p>&copy; Finnovators. All rights reserved.</p>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default RegisterForm;