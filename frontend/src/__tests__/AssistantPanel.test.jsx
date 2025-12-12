import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AssistantPanel from '../components/AssistantPanel.jsx';

describe('AssistantPanel', () => {
  it('renders suggestions and sends prompt', async () => {
    const onPrompt = vi.fn();
    render(<AssistantPanel onPrompt={onPrompt} loading={false} reply="" theme="light" />);
    fireEvent.click(screen.getByText('Draft a polite reply to the latest billing email'));
    await waitFor(() => expect(onPrompt).toHaveBeenCalled());
  });

  it('shows reply text', () => {
    render(<AssistantPanel onPrompt={() => {}} loading={false} reply="hello" theme="light" />);
    expect(screen.getByText('hello')).toBeInTheDocument();
  });
});
