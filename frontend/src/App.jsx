import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from './components/common';
import NationalRiskMap from './pages/NationalRiskMap';
import ProjectList from './pages/ProjectList';
import ProjectDetail from './pages/ProjectDetail';
import GovernanceQueue from './pages/GovernanceQueue';
import ModelPerformance from './pages/ModelPerformance';
import DataManagement from './pages/DataManagement';
import NewProject from './pages/NewProject';
import DataEntry from './pages/DataEntry';
import VersionHistory from './pages/VersionHistory';
import DataImport from './pages/DataImport';
import DataHealth from './pages/DataHealth';
import AuditTrail from './pages/AuditTrail';
import ReportingCenter from './pages/ReportingCenter';
import NationalReport from './pages/NationalReport';
import ProjectReport from './pages/ProjectReport';
import GovernanceReport from './pages/GovernanceReport';
import ModelReport from './pages/ModelReport';
import ReportHistory from './pages/ReportHistory';
import RiskIntelligence from './pages/RiskIntelligence';
import NetworkExplorer from './pages/NetworkExplorer';
import DecisionCockpit from './pages/DecisionCockpit';
import NarrativeIntelligence from './pages/NarrativeIntelligence';
import PeerIntelligence from './pages/PeerIntelligence';
import ProjectIntelligence from './pages/ProjectIntelligence';
import PositiveDeviance from './pages/PositiveDeviance';
import PlaybookLibrary from './pages/PlaybookLibrary';

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout title="Overview"><NationalRiskMap /></Layout>} />
        <Route path="/risk-intelligence" element={<Layout title="Risk Intelligence"><RiskIntelligence /></Layout>} />
        <Route path="/projects" element={<Layout title="Projects"><ProjectList /></Layout>} />
        <Route path="/projects/:id" element={<Layout title="Project Detail"><ProjectDetail /></Layout>} />
        <Route path="/projects/:id/history" element={<Layout title="Version History"><VersionHistory /></Layout>} />
        <Route path="/projects/:id/intelligence" element={<Layout title="Project Intelligence"><ProjectIntelligence /></Layout>} />
        <Route path="/projects/:id/narrative-intelligence" element={<Layout title="Narrative Intelligence"><NarrativeIntelligence /></Layout>} />
        <Route path="/projects/:id/peer-intelligence" element={<Layout title="Peer Intelligence"><PeerIntelligence /></Layout>} />
        <Route path="/projects/:id/decision-cockpit" element={<Layout title="Decision Cockpit"><DecisionCockpit /></Layout>} />
        <Route path="/governance" element={<Layout title="Governance Queue"><GovernanceQueue /></Layout>} />
        <Route path="/models" element={<Layout title="Model Performance"><ModelPerformance /></Layout>} />
        <Route path="/data-management" element={<Layout title="Data Management"><DataManagement /></Layout>} />
        <Route path="/data-management/new-project" element={<Layout title="New Project"><NewProject /></Layout>} />
        <Route path="/data-entry" element={<Layout title="Data Entry"><DataEntry /></Layout>} />
        <Route path="/data-import" element={<Layout title="Data Import"><DataImport /></Layout>} />
        <Route path="/data-health" element={<Layout title="Data Health"><DataHealth /></Layout>} />
        <Route path="/audit" element={<Layout title="Audit Trail"><AuditTrail /></Layout>} />
        <Route path="/network" element={<Layout title="Network Explorer"><NetworkExplorer /></Layout>} />
        <Route path="/positive-deviance" element={<Layout title="Positive Deviance Radar"><PositiveDeviance /></Layout>} />
        <Route path="/playbooks" element={<Layout title="Playbook Library"><PlaybookLibrary /></Layout>} />
        <Route path="/reports" element={<Layout title="Reports"><ReportingCenter /></Layout>} />
        <Route path="/reports/national" element={<Layout title="National Report"><NationalReport /></Layout>} />
        <Route path="/reports/project/:id" element={<Layout title="Project Report"><ProjectReport /></Layout>} />
        <Route path="/reports/governance" element={<Layout title="Governance Report"><GovernanceReport /></Layout>} />
        <Route path="/reports/models" element={<Layout title="Model Report"><ModelReport /></Layout>} />
        <Route path="/reports/history" element={<Layout title="Report History"><ReportHistory /></Layout>} />
      </Routes>
    </Router>
  );
}
