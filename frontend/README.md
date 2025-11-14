# Frontend - TradePal AI

Next.js frontend application for TradePal AI customer service platform.

## Quick Start

```bash
# Install dependencies
npm install

# Set up environment
cp .env.example .env.local
# Edit .env.local and set NEXT_PUBLIC_API_URL=http://localhost:8000

# Run development server
npm run dev
```

Application starts on `http://localhost:3000`

## Project Structure

```
frontend/
├── app/              # Next.js app directory
│   ├── page.tsx     # Home page
│   ├── layout.tsx   # Root layout
│   ├── market/      # Market data page
│   └── disclaimer/  # Disclaimer page
├── components/       # React components
│   ├── chat/        # Chat interface components
│   ├── stock/       # Stock data components
│   └── ui/          # Reusable UI components
├── hooks/           # Custom React hooks
├── lib/             # Utilities and API clients
├── types/           # TypeScript type definitions
└── constants/       # Application constants
```

## Key Components

### Chat Components
- `ChatContainer` - Main chat interface container
- `ChatHeader` - Header with navigation
- `ChatInput` - Message input with suggestions
- `MessageList` - Message display component
- `MessageItem` - Individual message component
- `PDFUpload` - Document upload component
- `UploadView` - Upload view wrapper

### Stock Components
- `StockQuote` - Stock quote display
- `MarketOverview` - Market overview dashboard

### UI Components
- shadcn/ui component library
- Custom components for specific needs
- Error boundary for error handling

## Custom Hooks

### useChat
Manages chat state and message sending logic.

```typescript
const { messages, isLoading, error, sendMessage } = useChat();
```

### useAutoScroll
Handles automatic scrolling to bottom of chat.

```typescript
const scrollRef = useAutoScroll(messages);
```

## API Integration

### API Client
Located in `lib/api.ts` and `lib/api-client.ts`:

- Centralized API client with retry logic
- Error handling and type safety
- Request/response type definitions

### Stock API
Located in `lib/stock-api.ts`:

- Stock quote fetching
- Historical data retrieval
- Options chain data
- Market overview

## Styling

- Tailwind CSS for utility-first styling
- Responsive design with mobile-first approach
- Consistent color scheme and design tokens
- Dark mode support (if configured)

## State Management

- React hooks for local state
- Custom hooks for shared logic
- Context API for global state (if needed)
- No external state management library required

## Error Handling

- Error boundary component for React errors
- API error handling with user-friendly messages
- Retry logic for failed requests
- Loading states for async operations

## Performance Optimizations

- Code splitting with Next.js
- Lazy loading where appropriate
- Memoization with useCallback and useMemo
- Optimized re-renders
- Efficient API calls

## Development

### Available Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm start        # Start production server
npm run lint     # Run ESLint
```

### Code Style

- TypeScript for type safety
- ESLint for code quality
- Consistent naming conventions
- Component-based architecture

## Environment Variables

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Testing

Frontend testing can be added with:
- Jest for unit tests
- React Testing Library for component tests
- Playwright or Cypress for E2E tests

## Build and Deployment

### Production Build

```bash
npm run build
npm start
```

### Deployment Considerations

- Set `NEXT_PUBLIC_API_URL` for production API
- Configure environment variables on hosting platform
- Enable production optimizations
- Set up error tracking (e.g., Sentry)
- Configure analytics if needed

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- ES6+ features required
- Responsive design for mobile devices

## Notes for Future Development

### Potential Enhancements
- Add unit tests for components
- Implement E2E testing
- Add performance monitoring
- Implement offline support
- Add PWA capabilities
- Enhance accessibility features

### Maintenance
- Keep dependencies updated
- Monitor bundle size
- Review performance metrics
- Update TypeScript types as API evolves
