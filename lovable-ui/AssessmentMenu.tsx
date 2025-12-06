/**
 * Assessment Menu - Mobile First
 * Main entry point for personality assessments
 */

import React from 'react';
import { Brain, Play, Shield, History, TrendingUp, Clock } from 'lucide-react';
import { motion } from 'framer-motion';

interface AssessmentMenuProps {
  onStartNew: () => void;
  onViewHistory: () => void;
  onPrivacySettings: () => void;
  previousAssessments?: number;
}

export function AssessmentMenu({
  onStartNew,
  onViewHistory,
  onPrivacySettings,
  previousAssessments = 0,
}: AssessmentMenuProps) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-indigo-50 via-white to-pink-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-2xl mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-indigo-600 to-pink-600 rounded-2xl flex items-center justify-center shadow-lg">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Personlighetstest
              </h1>
              <p className="text-sm text-gray-600">
                Upptäck din unika profil
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">
        {/* Hero Card - Start New Test */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative overflow-hidden"
        >
          <button
            onClick={onStartNew}
            className="w-full text-left bg-gradient-to-br from-indigo-600 to-pink-600 rounded-3xl p-6 shadow-xl active:scale-[0.98] transition-transform"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="inline-flex items-center gap-2 bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full mb-3">
                  <Play className="w-4 h-4 text-white" />
                  <span className="text-sm font-medium text-white">
                    Börja nu
                  </span>
                </div>

                <h2 className="text-2xl font-bold text-white mb-2">
                  Starta Nytt Test
                </h2>

                <p className="text-white/90 leading-relaxed mb-4">
                  Få djupgående insikter om din personlighet med AI-drivna
                  analyser baserade på vetenskaplig forskning.
                </p>

                <div className="flex items-center gap-4 text-white/80 text-sm">
                  <div className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    <span>10-30 min</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <TrendingUp className="w-4 h-4" />
                    <span>AI-analys</span>
                  </div>
                </div>
              </div>

              {/* Arrow */}
              <div className="flex-shrink-0 ml-4">
                <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center">
                  <Play className="w-5 h-5 text-white" />
                </div>
              </div>
            </div>

            {/* Decorative Background */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full blur-3xl -mr-32 -mt-32" />
          </button>
        </motion.div>

        {/* Stats */}
        {previousAssessments > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="grid grid-cols-2 gap-3"
          >
            <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
              <div className="text-3xl font-bold text-indigo-600">
                {previousAssessments}
              </div>
              <div className="text-sm text-gray-600 mt-1">
                Genomförda test
              </div>
            </div>

            <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
              <div className="text-3xl font-bold text-pink-600">100%</div>
              <div className="text-sm text-gray-600 mt-1">GDPR-säkert</div>
            </div>
          </motion.div>
        )}

        {/* Action Cards */}
        <div className="space-y-3">
          {/* History */}
          {previousAssessments > 0 && (
            <motion.button
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              onClick={onViewHistory}
              className="w-full bg-white rounded-2xl p-5 shadow-sm border border-gray-100 active:bg-gray-50 transition-colors text-left"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center flex-shrink-0">
                  <History className="w-6 h-6 text-indigo-600" />
                </div>

                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">Mina Test</h3>
                  <p className="text-sm text-gray-600">
                    Se tidigare resultat och jämför
                  </p>
                </div>

                <div className="flex-shrink-0">
                  <div className="w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center">
                    <svg
                      className="w-3 h-3 text-gray-600"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5l7 7-7 7"
                      />
                    </svg>
                  </div>
                </div>
              </div>
            </motion.button>
          )}

          {/* Privacy Settings */}
          <motion.button
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: previousAssessments > 0 ? 0.3 : 0.2 }}
            onClick={onPrivacySettings}
            className="w-full bg-white rounded-2xl p-5 shadow-sm border border-gray-100 active:bg-gray-50 transition-colors text-left"
          >
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center flex-shrink-0">
                <Shield className="w-6 h-6 text-green-600" />
              </div>

              <div className="flex-1">
                <h3 className="font-semibold text-gray-900">
                  Integritet & Data
                </h3>
                <p className="text-sm text-gray-600">
                  Hantera dina samtycken och exportera data
                </p>
              </div>

              <div className="flex-shrink-0">
                <div className="w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center">
                  <svg
                    className="w-3 h-3 text-gray-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                </div>
              </div>
            </div>
          </motion.button>
        </div>

        {/* Info Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-gradient-to-r from-indigo-50 to-pink-50 rounded-2xl p-5 border border-indigo-100"
        >
          <h3 className="font-semibold text-gray-900 mb-3">
            Vad du får:
          </h3>

          <div className="space-y-2">
            {[
              'Personlighetsprofil baserad på Big Five, DISC eller MBTI',
              'AI-driven analys av dina svar',
              'Styrkor och utvecklingsområden',
              'Personliga rekommendationer',
              'Fullständig GDPR-skyddad data',
            ].map((item, index) => (
              <div key={index} className="flex items-start gap-2">
                <div className="w-5 h-5 rounded-full bg-indigo-600 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <svg
                    className="w-3 h-3 text-white"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={3}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                </div>
                <span className="text-sm text-gray-700">{item}</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Bottom Safe Area */}
      <div className="h-8" />
    </div>
  );
}

export default AssessmentMenu;
