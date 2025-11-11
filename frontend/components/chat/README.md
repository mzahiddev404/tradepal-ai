# Chat Components

React components for the TradePal AI chat interface.

## Components

### ChatContainer
Main container managing chat state and UI switching between chat and document upload.

**Features:**
- Message state management
- Backend API integration
- Error handling
- Toggle between chat and document views

### MessageList
Displays conversation messages with user/AI distinction.

**Features:**
- Message bubbles (user/assistant)
- Loading indicator
- Timestamps
- Empty state

### ChatInput
Input field for sending messages.

**Features:**
- Text input
- Send button
- Enter key support
- Disabled state during loading

### PDFUpload
PDF file upload component with drag-and-drop.

**Features:**
- Drag-and-drop zone
- File validation (PDF only, 10MB max)
- Progress tracking
- Multiple file support
- File list management

## Usage

```tsx
import { ChatContainer } from "@/components/chat/chat-container";

export default function Page() {
  return <ChatContainer />;
}
```










