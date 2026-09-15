import React from 'react';
import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-400 py-12 border-t border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="space-y-4 md:col-span-2">
            <div className="flex items-center space-x-2">
              <span className="text-xl font-semibold tracking-tight text-white">
                Hire<span className="text-teal-400">Lens</span>
              </span>
            </div>
            <p className="text-sm text-slate-400 max-w-sm">
              Understand how well your resume matches any job description with explainable, deterministic analysis.
            </p>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-200 tracking-wider uppercase mb-4">
              Product
            </h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/app/analyze" className="hover:text-white transition-colors">
                  Analyze Resume
                </Link>
              </li>
              <li>
                <Link to="/login" className="hover:text-white transition-colors">
                  Sign In
                </Link>
              </li>
              <li>
                <Link to="/register" className="hover:text-white transition-colors">
                  Register
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-200 tracking-wider uppercase mb-4">
              Transparency
            </h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              HireLens uses objective section parsing, TF-IDF vector similarity, and rule-based skill extraction to evaluate alignment.
            </p>
          </div>
        </div>
        <div className="mt-8 pt-8 border-t border-slate-800 text-xs text-slate-500 text-center">
          &copy; {new Date().getFullYear()} HireLens. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
