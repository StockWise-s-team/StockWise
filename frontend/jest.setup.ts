import '@testing-library/jest-dom';

// Mock Next.js navigation
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
    };
  },
  usePathname() {
    return '';
  },
  useSearchParams() {
    // Return a dummy URLSearchParams
    return new URLSearchParams();
  },
}));

// Mock LightweightCharts as it requires DOM elements that JSDom might struggle with
jest.mock('lightweight-charts', () => ({
  createChart: jest.fn().mockReturnValue({
    addSeries: jest.fn().mockReturnValue({
      setData: jest.fn(),
      update: jest.fn(),
      applyOptions: jest.fn(),
    }),
    removeSeries: jest.fn(),
    timeScale: jest.fn().mockReturnValue({
      fitContent: jest.fn(),
    }),
    applyOptions: jest.fn(),
    remove: jest.fn(),
  }),
  ColorType: { Solid: 'Solid' },
  LineSeries: {},
}), { virtual: true });

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};
