# NIDS Frontend - Network Intrusion Detection System

A modern Next.js frontend application for Network Intrusion Detection System with Clerk authentication.

## Features

- 🔐 **Authentication**: Secure login/signup using Clerk
- 📊 **Dashboard**: File upload and analysis results display
- 📈 **History**: View analysis history with detailed reports
- 🎨 **Modern UI**: Beautiful, responsive design with animations
- ⚡ **Real-time**: Live analysis status and updates

## Tech Stack

- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **Clerk** for authentication
- **Lucide React** for icons

## Getting Started

### Prerequisites

- Node.js 18+ installed
- npm or yarn package manager

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set up Clerk Authentication:**
   - Go to [clerk.com](https://clerk.com) and create an account
   - Create a new application
   - Copy your publishable key and secret key
   - Create a `.env.local` file in the root directory:
   ```env
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key_here
   CLERK_SECRET_KEY=your_clerk_secret_key_here
   NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
   NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
   NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
   NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

## Project Structure

```
src/
├── app/
│   ├── dashboard/
│   │   ├── history/
│   │   │   └── page.tsx      # History page
│   │   └── page.tsx          # Dashboard page
│   ├── globals.css           # Global styles
│   ├── layout.tsx            # Root layout
│   └── page.tsx              # Landing page
├── components/               # Reusable components
└── lib/                      # Utility functions
```

## Pages

### Landing Page (`/`)
- Hero banner with IDS information
- Feature highlights
- Statistics display
- Footer with contact information

### Dashboard (`/dashboard`)
- File upload interface
- Real-time analysis results
- Quick stats overview
- Navigation to history

### History (`/dashboard/history`)
- Analysis history list
- Detailed view of past analyses
- Download and view options
- Statistics summary

## Features in Detail

### Authentication
- Secure login/signup with Clerk
- Protected routes
- User profile management

### File Upload
- Support for multiple file formats (.pcap, .log, .txt, .csv)
- Drag and drop interface
- File size display
- Processing status indicators

### Analysis Results
- Real-time threat detection display
- Severity levels (High, Medium, Low)
- Detailed threat descriptions
- Analysis timestamps

### History Management
- Complete analysis history
- Search and filter capabilities
- Export options
- Detailed analysis views

## Backend Integration

The frontend is designed to work with a backend API. Update the `NEXT_PUBLIC_API_URL` in your environment variables to point to your backend server.

### API Endpoints Expected:
- `POST /api/analyze` - Upload and analyze files
- `GET /api/history` - Get user analysis history
- `GET /api/history/:id` - Get specific analysis details

## Customization

### Styling
- Modify `tailwind.config.js` for theme customization
- Update `src/app/globals.css` for global styles
- Component-specific styles are in individual files

### Features
- Add new analysis types in the dashboard
- Extend history functionality
- Add more file format support
- Implement real-time notifications

## Deployment

### Vercel (Recommended)
1. Push your code to GitHub
2. Connect your repository to Vercel
3. Add environment variables in Vercel dashboard
4. Deploy automatically

### Other Platforms
- Build the project: `npm run build`
- Start production server: `npm start`
- Configure your hosting platform accordingly

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- Email: nis@nids.com
- Documentation: [Link to docs]
- Issues: [GitHub Issues]

---

Built with ❤️ for Network Security

