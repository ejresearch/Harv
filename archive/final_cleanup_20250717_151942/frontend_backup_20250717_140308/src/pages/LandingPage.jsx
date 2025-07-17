// Harv Landing Page - Clean Centered Design
import React, { useState, useEffect } from 'react';
import { utils } from '../services/api';

const Logo = () => (
  <div className="logo" style={{
    fontFamily: 'Nunito, sans-serif',
    fontWeight: 700,
    fontSize: '3rem',
    color: 'var(--primary-green)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '0.5rem',
    marginBottom: '2rem'
  }}>
    <span>harv</span>
    <span style={{ fontSize: '2rem' }}>🌱</span>
  </div>
);

const LandingPage = ({ onNavigate }) => {
  const [backendStatus, setBackendStatus] = useState('checking');

  useEffect(() => {
    // Check if backend is available
    const checkBackend = async () => {
      const isAvailable = await utils.isBackendAvailable();
      setBackendStatus(isAvailable ? 'available' : 'unavailable');
    };
    
    checkBackend();
  }, []);

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: 'var(--beige-bg)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '2rem'
    }}>
      <div style={{
        maxWidth: '600px',
        width: '100%',
        textAlign: 'center'
      }}>
        {/* Logo prominently displayed */}
        <Logo />
        
        {/* Brief, inviting overview text */}
        <h1 style={{ 
          color: 'var(--primary-green)', 
          fontSize: '2.5rem',
          fontWeight: 700,
          marginBottom: '1rem',
          fontFamily: 'Nunito, sans-serif'
        }}>
          Welcome to Harv
        </h1>
        
        <p style={{ 
          color: 'var(--standard-black)', 
          fontSize: '1.2rem',
          marginBottom: '2rem',
          lineHeight: '1.6',
          fontFamily: 'Nunito, sans-serif'
        }}>
          Your AI-powered Socratic learning companion for communication mastery
        </p>

        {/* Backend Status Indicator */}
        <div style={{ 
          marginBottom: '3rem',
          padding: '0.75rem 1.5rem',
          borderRadius: '8px',
          backgroundColor: backendStatus === 'available' ? '#d4edda' : '#f8d7da',
          color: backendStatus === 'available' ? '#155724' : '#721c24',
          fontSize: '1rem',
          fontFamily: 'Nunito, sans-serif',
          fontWeight: 500
        }}>
          {backendStatus === 'checking' && '🔍 Connecting to Harv AI...'}
          {backendStatus === 'available' && '✅ Harv AI Ready'}
          {backendStatus === 'unavailable' && '⚠️ Harv AI Offline - Demo Mode'}
        </div>
        
        {/* Clear, centrally located Register and Login buttons */}
        <div style={{ 
          display: 'flex', 
          gap: '1.5rem',
          justifyContent: 'center',
          alignItems: 'center',
          flexWrap: 'wrap'
        }}>
          <button 
            onClick={() => onNavigate('register')}
            style={{
              backgroundColor: 'var(--primary-green)',
              color: 'var(--accent-white)',
              padding: '1.25rem 2.5rem',
              border: 'none',
              borderRadius: '8px',
              fontFamily: 'Nunito, sans-serif',
              fontWeight: 600,
              fontSize: '1.1rem',
              cursor: 'pointer',
              minHeight: '56px',
              minWidth: '140px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.3s ease',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}
            onMouseOver={(e) => {
              e.target.style.backgroundColor = '#2d3f30';
              e.target.style.transform = 'translateY(-2px)';
              e.target.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
            }}
            onMouseOut={(e) => {
              e.target.style.backgroundColor = 'var(--primary-green)';
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
            }}
          >
            Register
          </button>
          
          <button 
            onClick={() => onNavigate('login')}
            style={{
              backgroundColor: 'transparent',
              color: 'var(--primary-green)',
              border: '2px solid var(--primary-green)',
              padding: '1.25rem 2.5rem',
              borderRadius: '8px',
              fontFamily: 'Nunito, sans-serif',
              fontWeight: 600,
              fontSize: '1.1rem',
              cursor: 'pointer',
              minHeight: '56px',
              minWidth: '140px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.3s ease',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}
            onMouseOver={(e) => {
              e.target.style.backgroundColor = 'var(--primary-green)';
              e.target.style.color = 'var(--accent-white)';
              e.target.style.transform = 'translateY(-2px)';
              e.target.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
            }}
            onMouseOut={(e) => {
              e.target.style.backgroundColor = 'transparent';
              e.target.style.color = 'var(--primary-green)';
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
            }}
          >
            Login
          </button>
        </div>

        {/* Simple footer */}
        <div style={{ 
          marginTop: '4rem',
          fontSize: '0.9rem',
          color: '#666',
          fontFamily: 'Nunito, sans-serif'
        }}>
          <p>Powered by the Primer Initiative</p>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
