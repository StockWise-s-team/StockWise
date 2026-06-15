import React from 'react';
import { render } from '@testing-library/react';
import SandboxPage from '@/app/dashboard/sandbox/page';

// Mock AuthProvider and MarketDataProvider context
jest.mock('@/components/providers/AuthProvider', () => ({
  useAuth: () => ({ user: { id: 'test-user-id', role: 'ROLE_USER' }, isAuthenticated: true }),
}));

jest.mock('@/components/providers/MarketDataProvider', () => ({
  useMarketData: () => ({
    getLiveHistory: jest.fn().mockReturnValue([]),
    subscribe: jest.fn(),
    unsubscribe: jest.fn(),
    connectionState: 'idle'
  }),
  useMarketTicker: () => ({ ticker: null, tickCount: 0, connectionState: 'idle' }),
}));

jest.mock('@/hooks/usePortfolio', () => ({
  usePortfolio: () => ({ data: { holdings: [], account: { virtualCash: 1000000 } }, reload: jest.fn() }),
}));

describe('Sandbox Page', () => {
  it('renders successfully without Next.js Suspense boundary cache errors', () => {
    // Next.js throws errors to console when useSearchParams is used without Suspense
    // By providing a Suspense boundary in SandboxPage, it shouldn't throw.
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    // Render the page
    const { unmount, getByText } = render(<SandboxPage />);
    
    expect(consoleErrorSpy).not.toHaveBeenCalled();

    unmount();
    consoleErrorSpy.mockRestore();
  });
});
