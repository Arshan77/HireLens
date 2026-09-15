import '@testing-library/jest-dom';
import { afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';

// Automatically cleanup after each test
afterEach(() => {
  cleanup();
  localStorage.clear();
});

// Mock recharts ResponsiveContainer for JSDOM environment
vi.mock('recharts', async () => {
  const originalModule = await vi.importActual('recharts');
  return {
    ...originalModule,
    ResponsiveContainer: ({ children }) => (
      <div className="recharts-responsive-container-mock" style={{ width: 800, height: 400 }}>
        {children}
      </div>
    ),
  };
});
