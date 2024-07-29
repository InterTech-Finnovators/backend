import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './LoginForm.css';

function LoginForm() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch('http://localhost:8000/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    username,
                    password,
                }),
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('token', data.access_token);
                navigate('/chat'); // Redirect to chat page
            } else {
                setError('Invalid username or password');
            }
        } catch (err) {
            setError('An error occurred. Please try again.');
        }
    };

    return (
        <div className="wrapper">
            <div className="form-box login">
                <form onSubmit={handleSubmit}>
                    <h1>Welcome </h1>
                    <h2>Please sign in to your account </h2>
                    <div className="input-box">
                        <input
                            type="text"
                            placeholder="Username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                        />
                        <span className="icon"><i className="fas fa-user"></i></span>
                    </div>
                    <div className="input-box">
                        <input
                            type="password"
                            placeholder="Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                        <span className="icon"><i className="fas fa-lock"></i></span>
                    </div>
                    <div className="remember-forgot">
                        {/* <label>
                            <input type="checkbox" /> Remember me
                        </label> */}
                        <Link to="/forgot-password">Forgot password?</Link>
                    </div>
                    <button type="submit">Login</button>
                    <div className="register-link">
                        <p>Don't have an account? <Link to="/register">Register</Link></p>
                    </div>
                    <div className="footer">
                        <p>&copy; Finnovators. All rights reserved.</p>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default LoginForm;