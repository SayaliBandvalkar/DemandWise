import React, { useState } from 'react';
import { Sidebar, NavTab } from './components/Sidebar';
import { Header } from './components/Header';

import { ExecutiveOverview } from './pages/ExecutiveOverview';
import { DataManagement } from './pages/DataManagement';
import { HierarchyExplorer } from './pages/HierarchyExplorer';
import { ForecastStudio } from './pages/ForecastStudio';
import { ReconciliationLab } from './pages/ReconciliationLab';
import { UncertaintyCalibration } from './pages/UncertaintyCalibration';
import { InventorySimulator } from './pages/InventorySimulator';
import { ModelEvaluation } from './pages/ModelEvaluation';
import { ExperimentsMonitoring } from './pages/ExperimentsMonitoring';
import { AuditTrail } from './pages/AuditTrail';

const tabMetadata: Record<NavTab, { title: string; subtitle: string }> = {
  overview: {
    title: 'Executive Overview',
    subtitle: 'High-level demand metrics, revenue volume, and hierarchical coherence status',
  },
  data: {
    title: 'Data Management & Quality Profiler',
    subtitle: 'Hierarchical dataset validation, summary statistics, and demo data generator',
  },
  hierarchy: {
    title: 'Hierarchy Explorer & Summing Matrix',
    subtitle: 'Interactive structural tree traversal and non-zero matrix S visualization',
  },
  forecast: {
    title: 'Forecast Studio & Point Estimators',
    subtitle: 'Statistical, intermittent, and gradient-boosted time series modeling',
  },
  reconciliation: {
    title: 'Hierarchical Reconciliation Lab',
    subtitle: 'Bottom-Up, Top-Down, and MinT shrinkage optimal projection',
  },
  uncertainty: {
    title: 'Uncertainty & Conformal Calibration',
    subtitle: 'Distribution-free Split Conformal Prediction vs Residual Bootstrap intervals',
  },
  inventory: {
    title: 'Downstream Inventory Simulator',
    subtitle: 'Discrete-event (s, S) replenishment policy evaluation under demand uncertainty',
  },
  evaluation: {
    title: 'Model Evaluation & Benchmark Leaderboard',
    subtitle: 'Scale-free MASE, RMSSE, and multi-tier accuracy verification',
  },
  monitoring: {
    title: 'Experiments, Concept Drift & Monitoring',
    subtitle: 'PSI distribution shift surveillance and stress-test ablation experiments',
  },
  audit: {
    title: 'Cryptographic Governance & Audit Trail',
    subtitle: 'SHA-256 tamper-evident compliance ledger of all system operations',
  },
};

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<NavTab>('overview');
  const currentMeta = tabMetadata[activeTab];

  const renderActivePage = () => {
    switch (activeTab) {
      case 'overview':
        return <ExecutiveOverview />;
      case 'data':
        return <DataManagement />;
      case 'hierarchy':
        return <HierarchyExplorer />;
      case 'forecast':
        return <ForecastStudio />;
      case 'reconciliation':
        return <ReconciliationLab />;
      case 'uncertainty':
        return <UncertaintyCalibration />;
      case 'inventory':
        return <InventorySimulator />;
      case 'evaluation':
        return <ModelEvaluation />;
      case 'monitoring':
        return <ExperimentsMonitoring />;
      case 'audit':
        return <AuditTrail />;
      default:
        return <ExecutiveOverview />;
    }
  };

  return (
    <div className="flex min-h-screen bg-navy-950 text-slate-100 font-sans selection:bg-cyan selection:text-navy-950">
      {/* Fixed Left Navigation */}
      <Sidebar activeTab={activeTab} onSelectTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header title={currentMeta.title} subtitle={currentMeta.subtitle} />
        <main className="flex-1 overflow-y-auto">
          {renderActivePage()}
        </main>
      </div>
    </div>
  );
};

export default App;
