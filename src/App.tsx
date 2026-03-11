/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */
import { Beaker, Download, Terminal } from 'lucide-react';

export default function App() {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-8 font-sans">
      <div className="max-w-2xl w-full bg-white rounded-2xl shadow-xl p-10 border border-slate-100">
        <div className="flex items-center gap-4 mb-6">
          <div className="bg-emerald-100 p-3 rounded-xl">
            <Beaker className="w-8 h-8 text-emerald-600" />
          </div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">
            Comparador Analítico Pro
          </h1>
        </div>
        
        <p className="text-slate-600 text-lg mb-8 leading-relaxed">
          Esta aplicação foi desenvolvida em <strong>Python (Streamlit)</strong> para garantir a máxima precisão estatística e performance em análise de dados laboratoriais.
        </p>

        <div className="space-y-4 bg-slate-50 rounded-xl p-6 border border-slate-200 mb-8">
          <div className="flex items-start gap-3">
            <Terminal className="w-5 h-5 text-slate-500 mt-1" />
            <div>
              <p className="font-semibold text-slate-800">Como executar:</p>
              <code className="text-sm text-emerald-700 block mt-1">pip install -r requirements.txt</code>
              <code className="text-sm text-emerald-700 block">streamlit run app.py</code>
            </div>
          </div>
        </div>

        <div className="flex flex-col gap-3">
          <div className="flex items-center gap-2 text-sm text-slate-500 italic">
            <Download className="w-4 h-4" />
            Os arquivos app.py e requirements.txt já estão disponíveis no seu projeto.
          </div>
        </div>
      </div>
      
      <footer className="mt-8 text-slate-400 text-sm">
        Ferramenta Técnica para Validação de Métodos Quantitativos
      </footer>
    </div>
  );
}
