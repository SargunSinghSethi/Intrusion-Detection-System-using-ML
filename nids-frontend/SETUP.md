# Quick Setup Guide

## Prerequisites
- Node.js 18+ installed on your system
- A Clerk account (free at clerk.com)

## Installation Steps

### 1. Install Dependencies
```bash
# Run the installation script (Windows)
install.bat

# Or manually install
npm install
```

### 2. Set up Clerk Authentication

1. Go to [clerk.com](https://clerk.com) and create a free account
2. Create a new application
3. Copy your publishable key and secret key from the dashboard
4. Create a `.env.local` file in the project root with:

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_key_here
CLERK_SECRET_KEY=sk_test_your_secret_key_here
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
```

### 3. Run the Development Server
```bash
npm run dev
```

### 4. Open Your Browser
Navigate to [http://localhost:3000](http://localhost:3000)

## Features Overview

### Landing Page
- Modern hero banner with IDS information
- Feature highlights with animations
- Statistics display
- Contact information in footer

### Authentication
- Secure login/signup with Clerk
- Protected dashboard routes
- User profile management

### Dashboard
- File upload interface (supports .pcap, .log, .txt, .csv)
- Real-time analysis results
- Threat detection with severity levels
- Analysis summary and recommendations

### History Page
- Complete analysis history
- Detailed threat information
- Export and view options
- Statistics overview

## File Structure
```
nids-frontend/
├── src/
│   ├── app/
│   │   ├── dashboard/
│   │   │   ├── history/page.tsx
│   │   │   └── page.tsx
│   │   ├── api/analyze/route.ts
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   └── middleware.ts
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── README.md
```

## Customization

### Styling
- Modify `tailwind.config.js` for theme changes
- Update `src/app/globals.css` for global styles

### Backend Integration
- Update the API endpoint in `src/app/api/analyze/route.ts`
- Modify the fetch URL in `src/app/dashboard/page.tsx`

## Troubleshooting

### Common Issues

1. **Node.js not found**
   - Install Node.js from [nodejs.org](https://nodejs.org/)

2. **Clerk authentication not working**
   - Check your environment variables in `.env.local`
   - Ensure keys are correct and not expired

3. **File upload not working**
   - Check browser console for errors
   - Ensure file format is supported (.pcap, .log, .txt, .csv)

4. **Build errors**
   - Run `npm install` to ensure all dependencies are installed
   - Check TypeScript errors with `npm run lint`

## Support
- Email: nis@nids.com
- Documentation: See README.md
- Issues: Check the project repository

---

**Ready to go!** Your NIDS frontend is now set up and ready for development.

