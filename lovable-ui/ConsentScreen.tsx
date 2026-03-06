/**
 * GDPR Consent Screen - Mobile First
 * Explicit consent before data collection
 */

import React, { useState } from 'react';
import { Check, ChevronDown, ChevronUp, Shield, Brain, Database } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface ConsentScreenProps {
  onAccept: (consents: {
    data_processing: boolean;
    ai_analysis: boolean;
    storage: boolean;
  }) => void;
  onDecline: () => void;
}

interface ConsentItem {
  id: 'data_processing' | 'ai_analysis' | 'storage';
  title: string;
  description: string;
  required: boolean;
  icon: React.ReactNode;
  details: string;
}

export function ConsentScreen({ onAccept, onDecline }: ConsentScreenProps) {
  const [consents, setConsents] = useState({
    data_processing: false,
    ai_analysis: false,
    storage: true,
  });

  const [expandedItem, setExpandedItem] = useState<string | null>(null);

  const consentItems: ConsentItem[] = [
    {
      id: 'data_processing',
      title: 'Databehandling',
      description: 'Vi samlar in och behandlar dina svar',
      required: true,
      icon: <Database className="w-5 h-5" />,
      details:
        'Dina svar på frågorna samlas in och lagras säkert. Vi använder pseudonymisering vilket betyder att din data inte är direkt kopplad till din identitet.',
    },
    {
      id: 'ai_analysis',
      title: 'AI-Analys',
      description: 'Claude AI analyserar dina svar',
      required: true,
      icon: <Brain className="w-5 h-5" />,
      details:
        'Vi använder Anthropic Claude AI för att analysera dina personlighetssvar och ge dig insiktsfulla resultat. Din data skickas säkert till Anthropics servrar.',
    },
    {
      id: 'storage',
      title: 'Lagring',
      description: 'Spara resultat för framtida referens',
      required: false,
      icon: <Shield className="w-5 h-5" />,
      details:
        'Dina resultat sparas i max 365 dagar (konfigurerbart). Du kan när som helst exportera eller radera din data. Vi anonymiserar gamla resultat automatiskt.',
    },
  ];

  const allRequiredAccepted =
    consents.data_processing && consents.ai_analysis;

  const toggleConsent = (id: string) => {
    setConsents(prev => ({
      ...prev,
      [id]: !prev[id as keyof typeof prev],
    }));
  };

  const toggleExpand = (id: string) => {
    setExpandedItem(expandedItem === id ? null : id);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-indigo-50 via-white to-pink-50 pb-safe">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-2xl mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center">
              <Shield className="w-5 h-5 text-indigo-600" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Ditt Samtycke</h1>
              <p className="text-sm text-gray-600">GDPR-säker datahantering</p>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">
        {/* Intro */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100"
        >
          <h2 className="text-lg font-semibold text-gray-900 mb-2">
            Varför behöver vi ditt samtycke?
          </h2>
          <p className="text-gray-600 leading-relaxed">
            Enligt GDPR (EU:s dataskyddsförordning) behöver vi ditt <strong>explicita samtycke</strong> innan vi samlar in och behandlar dina personuppgifter.
          </p>
          <p className="text-gray-600 mt-3 leading-relaxed">
            Du har full kontroll och kan när som helst:
          </p>
          <ul className="mt-2 space-y-1 text-gray-600">
            <li className="flex items-center gap-2">
              <Check className="w-4 h-4 text-green-600" />
              Exportera din data
            </li>
            <li className="flex items-center gap-2">
              <Check className="w-4 h-4 text-green-600" />
              Radera din data
            </li>
            <li className="flex items-center gap-2">
              <Check className="w-4 h-4 text-green-600" />
              Dra tillbaka samtycke
            </li>
          </ul>
        </motion.div>

        {/* Consent Items */}
        <div className="space-y-3">
          {consentItems.map((item, index) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden"
            >
              {/* Consent Toggle */}
              <button
                onClick={() => toggleConsent(item.id)}
                className="w-full p-5 flex items-start gap-4 text-left active:bg-gray-50 transition-colors"
              >
                {/* Checkbox */}
                <div className="flex-shrink-0 mt-1">
                  <div
                    className={`w-6 h-6 rounded-lg border-2 flex items-center justify-center transition-all ${
                      consents[item.id]
                        ? 'bg-indigo-600 border-indigo-600'
                        : 'border-gray-300'
                    }`}
                  >
                    {consents[item.id] && (
                      <Check className="w-4 h-4 text-white" />
                    )}
                  </div>
                </div>

                {/* Icon */}
                <div
                  className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center ${
                    consents[item.id]
                      ? 'bg-indigo-100 text-indigo-600'
                      : 'bg-gray-100 text-gray-400'
                  }`}
                >
                  {item.icon}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-gray-900">
                      {item.title}
                    </h3>
                    {item.required && (
                      <span className="px-2 py-0.5 text-xs font-medium bg-red-100 text-red-700 rounded-full">
                        Obligatoriskt
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mt-1">
                    {item.description}
                  </p>
                </div>
              </button>

              {/* Expandable Details */}
              <button
                onClick={() => toggleExpand(item.id)}
                className="w-full px-5 py-3 flex items-center justify-between text-sm text-indigo-600 font-medium border-t border-gray-100 active:bg-gray-50"
              >
                <span>Läs mer</span>
                {expandedItem === item.id ? (
                  <ChevronUp className="w-4 h-4" />
                ) : (
                  <ChevronDown className="w-4 h-4" />
                )}
              </button>

              <AnimatePresence>
                {expandedItem === item.id && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="border-t border-gray-100 overflow-hidden"
                  >
                    <div className="p-5 text-sm text-gray-600 leading-relaxed bg-gray-50">
                      {item.details}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>

        {/* Privacy Policy Link */}
        <div className="text-center">
          <a
            href="/privacy"
            className="text-sm text-indigo-600 font-medium underline"
          >
            Läs vår fullständiga integritetspolicy
          </a>
        </div>
      </div>

      {/* Bottom Actions - Sticky Footer (Thumb Zone) */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4 pb-safe">
        <div className="max-w-2xl mx-auto space-y-3">
          {/* Warning if not all required */}
          {!allRequiredAccepted && (
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 text-sm text-amber-800">
              Du måste acceptera obligatoriska samtycken för att fortsätta
            </div>
          )}

          {/* Accept Button */}
          <button
            onClick={() => onAccept(consents)}
            disabled={!allRequiredAccepted}
            className={`w-full py-4 rounded-xl font-semibold text-lg transition-all ${
              allRequiredAccepted
                ? 'bg-indigo-600 text-white active:bg-indigo-700 shadow-lg shadow-indigo-200'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            }`}
          >
            {allRequiredAccepted
              ? 'Acceptera och fortsätt'
              : 'Acceptera obligatoriska samtycken'}
          </button>

          {/* Decline Button */}
          <button
            onClick={onDecline}
            className="w-full py-3 text-gray-600 font-medium active:text-gray-900"
          >
            Avbryt
          </button>
        </div>
      </div>

      {/* Bottom Safe Area Spacer */}
      <div className="h-32" />
    </div>
  );
}

export default ConsentScreen;
