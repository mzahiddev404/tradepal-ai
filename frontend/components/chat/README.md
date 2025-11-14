# Chat Components

React components for the TradePal AI chat interface.

## Components Overview

### ChatContainer
Main container component managing chat state and UI switching between chat and document upload views.

**Location:** `components/chat/chat-container.tsx`

**Responsibilities:**
- Message state management
- Backend API integration
- Error handling
- Toggle between chat and document views
- Auto-scroll functionality

**Props:** None (self-contained)

**State:**
- Messages array
- Loading state
- Error state
- Upload view visibility

### ChatHeader
Header component displaying title, description, and action buttons.

**Location:** `components/chat/chat-header.tsx`

**Props:**
- `showUpload: boolean` - Whether upload view is active
- `onToggleUpload: () => void` - Toggle upload view callback
- `error?: string | null` - Error message to display

### ChatInput
Input component for sending messages with suggestion chips.

**Location:** `components/chat/chat-input.tsx`

**Props:**
- `onSend: (message: string) => void` - Send message callback
- `disabled: boolean` - Disable input during loading
- `suggestions?: string[]` - Optional suggestion chips

**Features:**
- Enter key to send
- Suggestion chip clicks
- Disabled state handling
- Input validation

### MessageList
Component displaying conversation messages.

**Location:** `components/chat/message-list.tsx`

**Props:**
- `messages: Message[]` - Array of messages to display
- `isLoading: boolean` - Loading indicator state

**Features:**
- Empty state display
- Message rendering
- Loading indicator
- Auto-scroll support

### MessageItem
Individual message bubble component.

**Location:** `components/chat/message-item.tsx`

**Props:**
- `message: Message` - Message data to display

**Features:**
- User/assistant styling
- Error message styling
- Timestamp display
- Responsive design

### PDFUpload
PDF file upload component with drag-and-drop support.

**Location:** `components/chat/pdf-upload.tsx`

**Props:**
- `onUploadComplete?: (files: UploadedFile[]) => void` - Upload completion callback
- `maxSizeMB?: number` - Maximum file size (default: 10MB)

**Features:**
- Drag-and-drop zone
- File validation (PDF only)
- Progress tracking
- Multiple file support
- File list management

### UploadView
Wrapper component for the upload interface.

**Location:** `components/chat/upload-view.tsx`

**Props:**
- `onReturnToChat: () => void` - Return to chat callback

## Usage Example

```tsx
import { ChatContainer } from "@/components/chat/chat-container";

export default function Page() {
  return <ChatContainer />;
}
```

## State Management

Chat state is managed using the `useChat` hook:

```tsx
const { messages, isLoading, error, sendMessage } = useChat();
```

## Custom Hooks

### useChat
Manages chat functionality including message sending and state.

**Location:** `hooks/useChat.ts`

**Returns:**
- `messages: Message[]` - Current messages
- `isLoading: boolean` - Loading state
- `error: string | null` - Error message
- `sendMessage: (content: string) => Promise<void>` - Send message function
- `clearError: () => void` - Clear error function
- `clearMessages: () => void` - Clear all messages

### useAutoScroll
Handles automatic scrolling to bottom of chat.

**Location:** `hooks/useAutoScroll.ts`

**Usage:**
```tsx
const scrollRef = useAutoScroll(messages);
```

## Type Definitions

Message types are defined in `types/chat.ts`:

```typescript
interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  error?: boolean;
}
```

## Styling

Components use Tailwind CSS with consistent design tokens:
- Primary colors: teal, cyan, emerald
- Responsive breakpoints
- Consistent spacing and typography

## Accessibility

- ARIA labels on interactive elements
- Keyboard navigation support
- Screen reader friendly
- Focus management

## Performance Considerations

- Memoization with useCallback
- Optimized re-renders
- Efficient message list rendering
- Lazy loading where appropriate

## Notes for Future Development

### Potential Enhancements
- Message editing functionality
- Message deletion
- Copy message to clipboard
- Message search
- Export conversation
- Message reactions
- File attachments beyond PDF

### Maintenance
- Keep components focused on single responsibility
- Maintain type safety
- Update tests when adding features
- Document new props and callbacks
