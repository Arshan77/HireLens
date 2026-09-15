import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Layers, ArrowRight } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function Navbar() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <Link to="/" className="flex items-center space-x-2.5 group">
          <div className="w-9 h-9 rounded-xl bg-brand-600 flex items-center justify-center text-white shadow-xs group-hover:bg-brand-700 transition-colors">
            <Layers className="w-5 h-5" />
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-slate-900 tracking-tight text-lg leading-none">
              HireLens
            </span>
            <span className="text-[10px] font-medium text-slate-500 tracking-wider uppercase mt-0.5">
              Resume Matching
            </span>
          </div>
        </Link>

        {/* Public Navigation */}
        <nav className="hidden md:flex items-center space-x-8 text-sm font-medium text-slate-600">
          <a href="#how-it-works" className="hover:text-slate-900 transition-colors">
            How It Works
          </a>
          <a href="#features" className="hover:text-slate-900 transition-colors">
            Features
          </a>
          <a href="#transparency" className="hover:text-slate-900 transition-colors">
            Explainable Methodology
          </a>
        </nav>

        {/* Actions */}
        <div className="flex items-center space-x-3">
          {isAuthenticated ? (
            <button
              onClick={() => navigate('/app')}
              className="hirelens-button-primary"
            >
              <span>Go to App</span>
              <ArrowRight className="w-4 h-4 ml-1.5" />
            </button>
          ) : (
            <>
              <Link
                to="/login"
                className="text-sm font-medium text-slate-700 hover:text-slate-900 px-3 py-2 transition-colors"
              >
                Sign In
              </Link>
              <Link to="/register" className="hirelens-button-primary">
                <span>Analyze Resume</span>
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
