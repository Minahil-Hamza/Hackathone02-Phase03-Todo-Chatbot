# AI Todo Chatbot Frontend - Setup Guide

## Prerequisites

- Node.js 18+ installed
- npm or yarn package manager
- Backend server running on http://localhost:8000

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The application will be available at http://localhost:3000

### 3. Build for Production

```bash
npm run build
npm start
```

## Environment Configuration

Create a `.env.local` file in the frontend directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build production bundle
- `npm start` - Start production server
- `npm run lint` - Run ESLint to check code quality

## Project Structure

```
frontend/
├── src/
│   ├── app/                  # Next.js 14 App Router
│   │   ├── globals.css       # Global styles
│   │   ├── layout.tsx        # Root layout
│   │   └── page.tsx          # Home page
│   ├── components/           # React components
│   │   ├── ui/               # Reusable UI primitives
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Skeleton.tsx
│   │   │   └── EmptyState.tsx
│   │   ├── Chat.tsx          # Main chat container
│   │   ├── ChatMessage.tsx   # Message component
│   │   ├── ChatInput.tsx     # Input component
│   │   └── Sidebar.tsx       # Sidebar component
│   └── lib/
│       └── api.ts            # API client
├── public/                   # Static assets
├── tailwind.config.ts        # Tailwind configuration
├── tsconfig.json             # TypeScript configuration
└── package.json              # Dependencies

```

## Features

### Responsive Design
- Mobile-first approach (320px+)
- Tablet optimized (768px+)
- Desktop enhanced (1024px+)
- Large display support (1920px+)

### Accessibility (WCAG 2.1 AA)
- Full keyboard navigation
- Screen reader support
- ARIA labels and live regions
- Color contrast compliance
- Focus indicators
- Reduced motion support

### Dark Mode
- System preference detection
- Smooth transitions
- Enhanced color palette

### UI Components
- Reusable button variants
- Card containers
- Loading skeletons
- Empty states
- Animated transitions

### Performance
- Server components by default
- Optimized bundle size
- Lazy loading
- GPU-accelerated animations

## Keyboard Shortcuts

- `Enter` - Send message
- `Shift + Enter` - New line in message
- `Tab` - Navigate between elements
- `Escape` - Close sidebar (mobile)

## Troubleshooting

### Dependencies Not Installing

```bash
# Clear cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Port Already in Use

```bash
# Change port
PORT=3001 npm run dev
```

### Backend Connection Issues

1. Ensure backend is running on http://localhost:8000
2. Check CORS settings in backend
3. Verify API endpoint in `.env.local`

### Build Errors

```bash
# Type check
npx tsc --noEmit

# Lint check
npm run lint
```

## Browser Support

- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Mobile browsers (iOS Safari, Chrome Android)

## Development Tips

### Hot Reload
All changes to components, styles, and pages trigger automatic reload.

### TypeScript
All components are strictly typed. Check types with:
```bash
npx tsc --noEmit
```

### Tailwind IntelliSense
Install the "Tailwind CSS IntelliSense" VS Code extension for autocomplete.

### Component Testing
Test components at different screen sizes using browser DevTools device emulation.

## Next Steps

1. Install dependencies: `npm install`
2. Start dev server: `npm run dev`
3. Open http://localhost:3000
4. Try chatting with the AI assistant
5. Test responsive behavior by resizing browser
6. Toggle dark mode in system preferences
7. Test keyboard navigation with Tab key

## Getting Help

- Check UI_ENHANCEMENTS.md for detailed component documentation
- Review component source code for usage examples
- Test all features in browser DevTools

---

**Need help?** Review the comprehensive UI_ENHANCEMENTS.md documentation.
