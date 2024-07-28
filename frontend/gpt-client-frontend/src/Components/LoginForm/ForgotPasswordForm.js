import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './LoginForm.css';

function ForgotPasswordForm() {
  const [email, setEmail] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleResetPassword = async (event) => {
    event.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/reset-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, new_password: newPassword }),
      });

      if (response.ok) {
        // Redirect to the login page on successful password reset
        navigate('/login');
      } else {
        const data = await response.json();
        setError(data.detail || 'Password reset failed');
      }
    } catch (err) {
      setError('An error occurred while resetting the password');
    }
  };

  return (
    <div className="wrapper">
      <div className="form-box forgot-password">
        <form onSubmit={handleResetPassword}>
          <h1>Forgot Password</h1>
          <h2>Enter your new password</h2>
          <div className="input-box">
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <span className="icon"><i className="fas fa-envelope"></i></span>
          </div>
          <div className="input-box">
            <input
              type="password"
              placeholder="New Password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
            />
            <span className="icon"><i className="fas fa-lock"></i></span>
          </div>
          {error && <p className="error-message">{error}</p>}
          <button type="submit">Set New Password</button>
          <div className="register-link">
            <p>Remembered your password? <Link to="/login">Login</Link></p>
          </div>
          <div className="footer">
            <p>&copy; Finnovators. All rights reserved.</p>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ForgotPasswordForm;