import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const response = await fetch('http://localhost:5001/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    if (data.token) {
      localStorage.setItem('token', data.token);
      navigate('/salles');
    }
  };

  return (
    <div className="container d-flex align-items-center justify-content-center min-vh-100 bg-light">
  <div className="card p-20 shadow" style={{ maxWidth: '800px', width: '100%' }}>
    <h2 className="text-center mb-4">Connexion</h2>
    <form onSubmit={handleSubmit}>
      <div className="mb-3">
        <label htmlFor="email" className="form-label">Email</label>
        <input
          type="email"
          id="email"
          className="form-control"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="votre.email@example.com"
        />
      </div>
      <div className="mb-3">
        <label htmlFor="password" className="form-label">Mot de passe</label>
        <input
          type="password"
          id="password"
          className="form-control"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="••••••••"
        />
      </div>
      <button type="submit" className="btn btn-primary w-100">Se connecter</button>
    </form>
    <p className="mt-3 text-center">
      Pas de compte ? <a href="/register">Créer un compte</a>
    </p>
  </div>
</div>

  );
};

export default Login;
