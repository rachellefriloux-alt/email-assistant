import { render, screen, fireEvent } from '@testing-library/react';
import EmailList from '../components/EmailList.jsx';

const emails = [
  { gmail_id: '1', subject: 'Hello', from_email: 'a@example.com', category: 'Billing', snippet: 'Pay me' },
  { gmail_id: '2', subject: 'Hi', from_email: 'b@example.com', category: 'Spam', snippet: 'Win now' },
];

describe('EmailList', () => {
  it('renders emails and allows selection', () => {
    const onToggleSelect = vi.fn();
    render(<EmailList emails={emails} loading={false} selectedIds={new Set()} onToggleSelect={onToggleSelect} />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
    fireEvent.click(screen.getAllByRole('checkbox')[0]);
    expect(onToggleSelect).toHaveBeenCalledWith('1');
  });

  it('shows loading state', () => {
    render(<EmailList emails={[]} loading selectedIds={new Set()} onToggleSelect={() => {}} />);
    expect(screen.getByText('Loading emails…')).toBeInTheDocument();
  });
});
