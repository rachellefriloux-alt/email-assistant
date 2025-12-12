import { render, screen, fireEvent } from '@testing-library/react';
import Dashboard from '../pages/Dashboard.jsx';

const tabs = ['All', 'Billing'];

describe('Dashboard', () => {
  it('renders header and tabs', () => {
    render(
      <Dashboard
        theme="light"
        onToggleTheme={() => {}}
        onRefresh={() => {}}
        onRefreshLive={() => {}}
        tabs={tabs}
        activeTab="All"
        setActiveTab={() => {}}
        loading={false}
      >
        <div>children</div>
      </Dashboard>
    );
    expect(screen.getByText('Inbox Insights')).toBeInTheDocument();
    expect(screen.getByText('All')).toBeInTheDocument();
    expect(screen.getByText('Billing')).toBeInTheDocument();
  });

  it('triggers refresh buttons', () => {
    const onRefresh = vi.fn();
    const onRefreshLive = vi.fn();
    render(
      <Dashboard
        theme="light"
        onToggleTheme={() => {}}
        onRefresh={onRefresh}
        onRefreshLive={onRefreshLive}
        tabs={tabs}
        activeTab="All"
        setActiveTab={() => {}}
        loading={false}
      >
        <div>children</div>
      </Dashboard>
    );
    fireEvent.click(screen.getByText('Refresh (Sample)'));
    fireEvent.click(screen.getByText('Refresh (Live)'));
    expect(onRefresh).toHaveBeenCalled();
    expect(onRefreshLive).toHaveBeenCalled();
  });
});
