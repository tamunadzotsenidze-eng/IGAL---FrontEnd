# IGAL - Financial Advisor Frontend

Modern, responsive web interface for the IGAL (Intelligent Georgian Advisor for Law) system.

## 🎯 Overview

This is the frontend application for IGAL, a specialized Georgian financial and tax law assistant that provides accurate answers based on indexed Georgian payment procedure and tax documents.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- IGAL Backend running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Access the application at: `http://localhost:3000`

## 📁 Project Structure

```
frontend/
├── app/                    # Next.js 14 App Router
│   ├── page.tsx           # Home page
│   ├── layout.tsx         # Root layout
│   └── globals.css        # Global styles
├── components/            # React components
│   ├── Chat/             # Chat interface
│   ├── Layout/           # Layout components
│   └── UI/               # Reusable UI components
├── lib/                   # Utility functions
│   ├── api.ts            # API client
│   └── utils.ts          # Helper functions
├── public/               # Static assets
├── styles/               # Additional styles
├── package.json
├── tsconfig.json
└── next.config.js
```

## 🎨 Features

- 💬 Real-time chat interface with streaming responses
- 🌐 Bilingual support (Georgian & English)
- 📱 Responsive design for mobile and desktop
- 🔍 Document source citations
- 📝 Markdown rendering for formatted responses
- 🎯 Topic-specific guidance
- 💾 Chat history and session management
- ⚡ Fast and optimized with Next.js 14

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_BASE=/api

# App Configuration
NEXT_PUBLIC_APP_NAME=IGAL
NEXT_PUBLIC_APP_DESCRIPTION=Georgian Financial & Tax Law Assistant
```

## 🎨 Design System

### Colors

- **Primary**: Blue (#3B82F6)
- **Secondary**: Indigo (#4F46E5)
- **Success**: Green (#10B981)
- **Warning**: Yellow (#F59E0B)
- **Error**: Red (#EF4444)

### Typography

- **Headings**: Georgian: "BPG Nino Mtavruli", Fallback: system-ui
- **Body**: Georgian: "BPG Arial", Fallback: -apple-system

## 📱 Pages

### 1. Chat Interface (`/`)

Main chat interface where users can:
- Ask questions about Georgian tax and payment law
- View AI responses with source citations
- See conversation history
- Switch between Georgian and English

### 2. About (`/about`)

Information about IGAL system and its capabilities

### 3. Documents (`/documents`)

Browse indexed documents by category:
- საგადასახადო კოდექსი (Tax Code)
- გადახდის პროცედურები (Payment Procedures)
- And other categories

## 🔌 API Integration

The frontend communicates with the Django backend:

```typescript
// Example API call
import { sendMessage } from '@/lib/api';

const response = await sendMessage({
  message: 'როგორია მოგების გადასახადის განაკვეთი?',
  session_id: sessionId
});
```

### API Endpoints Used

- `POST /api/chat/` - Send chat message
- `GET /api/chat/sessions/` - Get chat sessions
- `GET /api/chat/sessions/{id}/` - Get session messages
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout

## 🛠️ Development

### Available Scripts

```bash
# Development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint

# Type check
npm run type-check
```

### Code Style

- TypeScript for type safety
- ESLint for code quality
- Prettier for code formatting
- Component-based architecture
- Custom hooks for shared logic

## 🚀 Deployment

### Build for Production

```bash
npm run build
npm start
```

### Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Environment Variables for Production

Set these in your deployment platform:

```
NEXT_PUBLIC_API_URL=https://api.igal.ge
```

## 🌐 Localization

The app supports:
- **Georgian** (ka) - Primary language
- **English** (en) - Secondary language

Language detection is automatic based on user input.

## 🎯 User Experience

### Chat Flow

1. User enters question in Georgian or English
2. System detects language and processes query
3. Backend retrieves relevant documents (3-layer RAG)
4. AI generates response with citations
5. Response is displayed with source references
6. User can ask follow-up questions

### Features for Better UX

- Loading indicators during response generation
- Error handling with clear messages
- Responsive design for all screen sizes
- Keyboard shortcuts (Enter to send, Shift+Enter for new line)
- Auto-scroll to latest message
- Message timestamps
- Session persistence

## 📊 Analytics (Optional)

Track user interactions:
- Question topics
- Response satisfaction
- Most queried regulations
- Session duration

## 🔒 Security

- CORS configured for backend domain only
- CSRF protection for form submissions
- Secure session management
- Input sanitization
- XSS protection

## 🐛 Troubleshooting

### Common Issues

**API Connection Error:**
```
Error: Failed to fetch
```
Solution: Check that backend is running on `http://localhost:8000`

**Build Errors:**
```
Type error: ...
```
Solution: Run `npm run type-check` to identify TypeScript issues

## 📞 Support

For issues or questions:
- Backend: Check `../backend/README.md`
- GitHub: `tamunadzotsenidze-eng/IGAL---FrontEnd`

## 📄 License

Private project for IGAL Financial Advisor system.
