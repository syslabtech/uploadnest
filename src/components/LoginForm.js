import React from 'react';

const LoginForm = ({
  loginUsername,
  setLoginUsername,
  loginPassword,
  setLoginPassword,
  handleLogin,
  loginError,
  isLoading
}) => (
  <div className="login-container">
    <form className="login-form" onSubmit={handleLogin} autoComplete="off">
      <h2>🔒 Welcome Back</h2>
      <input
        type="text"
        placeholder="Enter your username"
        value={loginUsername}
        onChange={e => setLoginUsername(e.target.value)}
        className="input"
        autoFocus
        disabled={isLoading}
      />
      <input
        type="password"
        placeholder="Enter your password"
        value={loginPassword}
        onChange={e => setLoginPassword(e.target.value)}
        className="input"
        disabled={isLoading}
      />
      <button type="submit" className="btn btn-primary" disabled={isLoading}>
        {isLoading ? 'Logging in...' : 'Login'}
      </button>
      {loginError && <div className="error-message">{loginError}</div>}
    </form>
  </div>
);

export default LoginForm;
