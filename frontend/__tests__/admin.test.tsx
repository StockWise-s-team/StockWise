import React from 'react';
import { render } from '@testing-library/react';
import AdminPage from '@/app/dashboard/admin/page';

// Mock EventSource since JSDOM doesn't support it
global.EventSource = jest.fn(() => ({
  close: jest.fn(),
  onmessage: null,
  onerror: null,
})) as any;

jest.mock('@/lib/api', () => ({
  newsSourcesApi: { list: jest.fn().mockResolvedValue([]) },
  trackedSymbolsApi: { list: jest.fn().mockResolvedValue([]) },
  wikiApi: { list: jest.fn().mockResolvedValue({ wikis: [], total: 0 }) },
  pipelineApi: { getStatus: jest.fn().mockResolvedValue({}) },
  createProgressSSE: jest.fn().mockReturnValue({ close: jest.fn() }),
}));

describe('Admin Page', () => {
  it('mounts and unmounts without causing console errors or infinite loops', () => {
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    const consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});

    // Render the page
    const { unmount } = render(<AdminPage />);
    
    // At this point, the SSE connection is established
    expect(consoleErrorSpy).not.toHaveBeenCalled();

    // Unmount the component to trigger the cleanup function
    unmount();
    
    // There should be no state update on an unmounted component, which would 
    // otherwise trigger a console error in React 18, and no infinite loop.
    expect(consoleErrorSpy).not.toHaveBeenCalled();

    consoleErrorSpy.mockRestore();
    consoleWarnSpy.mockRestore();
  });
});
