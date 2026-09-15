import React from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';
import { FileText, Cpu, CheckCircle2, ArrowRight, ShieldCheck, Search, Target, Layers } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 font-sans">
      <Navbar />

      {/* Hero Section */}
      <main className="flex-1">
        <section className="pt-20 pb-16 md:pt-28 md:pb-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center space-x-2 bg-teal-50 border border-teal-200 px-3.5 py-1.5 rounded-full text-xs font-medium text-teal-800 mb-8">
            <span className="w-2 h-2 rounded-full bg-teal-600 animate-pulse"></span>
            <span>Deterministic & Explainable Resume Matching</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-slate-900 max-w-4xl mx-auto leading-tight">
            Know exactly where your resume stands.
          </h1>

          <p className="mt-6 text-lg sm:text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed">
            Upload your resume and paste a job description to receive clear, objective feedback on skill coverage, experience alignment, and formatting quality.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/app/analyze"
              className="w-full sm:w-auto inline-flex items-center justify-center px-6 py-3.5 bg-teal-700 hover:bg-teal-800 text-white font-medium text-sm rounded-lg shadow-sm transition-colors group"
            >
              <span>Analyze your resume</span>
              <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
            </Link>

            <a
              href="#how-it-works"
              className="w-full sm:w-auto inline-flex items-center justify-center px-6 py-3.5 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 font-medium text-sm rounded-lg shadow-sm transition-colors"
            >
              See how it works
            </a>
          </div>
        </section>

        {/* How It Works Section */}
        <section id="how-it-works" className="py-16 bg-white border-y border-slate-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center max-w-2xl mx-auto mb-14">
              <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
                Simple three-step analysis
              </h2>
              <p className="mt-3 text-slate-600 text-sm sm:text-base">
                Get comprehensive insights into your job match in less than 30 seconds.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="bg-slate-50 p-8 rounded-xl border border-slate-200">
                <div className="text-3xl font-bold text-teal-700 mb-4">01</div>
                <h3 className="text-lg font-semibold text-slate-900 mb-2">Upload Resume</h3>
                <p className="text-slate-600 text-sm leading-relaxed">
                  Support for PDF and DOCX files up to 5 MB. Resume parsing extracts text and sections cleanly.
                </p>
              </div>

              <div className="bg-slate-50 p-8 rounded-xl border border-slate-200">
                <div className="text-3xl font-bold text-teal-700 mb-4">02</div>
                <h3 className="text-lg font-semibold text-slate-900 mb-2">Add Job Description</h3>
                <p className="text-slate-600 text-sm leading-relaxed">
                  Paste the full job specification to identify key technical skills, experience requirements, and preferred qualifications.
                </p>
              </div>

              <div className="bg-slate-50 p-8 rounded-xl border border-slate-200">
                <div className="text-3xl font-bold text-teal-700 mb-4">03</div>
                <h3 className="text-lg font-semibold text-slate-900 mb-2">Understand Your Match</h3>
                <p className="text-slate-600 text-sm leading-relaxed">
                  Review a broken-down score of skill coverage, text similarity, experience alignment, and missing requirements.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Feature Section */}
        <section id="features" className="py-20 bg-slate-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center max-w-2xl mx-auto mb-16">
              <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
                Objective scoring, zero fluff
              </h2>
              <p className="mt-3 text-slate-600 text-sm sm:text-base">
                Four transparent criteria come together to form your match score.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
                <div className="w-10 h-10 rounded-md bg-teal-50 border border-teal-100 flex items-center justify-center text-teal-700 mb-4">
                  <Target className="w-5 h-5" />
                </div>
                <h3 className="text-base font-semibold text-slate-900 mb-2">Skill Coverage (40%)</h3>
                <p className="text-sm text-slate-600 leading-relaxed">
                  Direct match comparison between required skills in the job description and parsed skills on your resume.
                </p>
              </div>

              <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
                <div className="w-10 h-10 rounded-md bg-teal-50 border border-teal-100 flex items-center justify-center text-teal-700 mb-4">
                  <Search className="w-5 h-5" />
                </div>
                <h3 className="text-base font-semibold text-slate-900 mb-2">Text Similarity (30%)</h3>
                <p className="text-sm text-slate-600 leading-relaxed">
                  Calculated using TF-IDF term weighting and cosine similarity across your full document text.
                </p>
              </div>

              <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
                <div className="w-10 h-10 rounded-md bg-teal-50 border border-teal-100 flex items-center justify-center text-teal-700 mb-4">
                  <Layers className="w-5 h-5" />
                </div>
                <h3 className="text-base font-semibold text-slate-900 mb-2">Experience Alignment (15%)</h3>
                <p className="text-sm text-slate-600 leading-relaxed">
                  Evaluates total years of relevant work experience and degree requirements against the job opening.
                </p>
              </div>

              <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
                <div className="w-10 h-10 rounded-md bg-teal-50 border border-teal-100 flex items-center justify-center text-teal-700 mb-4">
                  <CheckCircle2 className="w-5 h-5" />
                </div>
                <h3 className="text-base font-semibold text-slate-900 mb-2">ATS Formatting Quality (15%)</h3>
                <p className="text-sm text-slate-600 leading-relaxed">
                  Heuristic analysis of resume structure, section completeness, action verbs, and quantifiable achievements.
                </p>
              </div>

              <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
                <div className="w-10 h-10 rounded-md bg-teal-50 border border-teal-100 flex items-center justify-center text-teal-700 mb-4">
                  <Cpu className="w-5 h-5" />
                </div>
                <h3 className="text-base font-semibold text-slate-900 mb-2">Missing Skills Breakdown</h3>
                <p className="text-sm text-slate-600 leading-relaxed">
                  Categorized list of missing required skills vs optional preferred skills so you know what to highlight.
                </p>
              </div>

              <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
                <div className="w-10 h-10 rounded-md bg-teal-50 border border-teal-100 flex items-center justify-center text-teal-700 mb-4">
                  <FileText className="w-5 h-5" />
                </div>
                <h3 className="text-base font-semibold text-slate-900 mb-2">Actionable Guidance</h3>
                <p className="text-sm text-slate-600 leading-relaxed">
                  Deterministic recommendations to refine your resume structure and address keyword gaps.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Transparency Section */}
        <section className="py-16 bg-white border-t border-slate-200">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-slate-100 text-slate-700 mb-6">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h2 className="text-2xl font-bold text-slate-900 tracking-tight">
              Transparent & Measurable Analysis
            </h2>
            <p className="mt-4 text-slate-600 leading-relaxed text-base">
              HireLens is designed for clarity. We don't make unsubstantiated claims about guarantee results or secret ATS algorithms.
              Instead, we provide exact mathematical breakdowns based on natural language processing and keyword matching so you can refine your application with confidence.
            </p>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
