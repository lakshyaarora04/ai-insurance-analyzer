# LLM Document Query System - Frontend

A modern React-based frontend for the LLM Document Query System that incorporates all the advanced features we've built.

## Features

### 🎯 Core Features
- **Natural Language Query Processing**: Submit insurance claims in plain English
- **Real-time Analysis**: Get instant decisions with detailed justifications
- **Multi-Document Support**: Process claims across multiple policy documents

### 🌟 Advanced Features
- **Reasoning Tree Visualization**: See step-by-step decision breakdowns
- **Multi-Document Reasoning**: Analyze claims considering base policies, riders, and amendments
- **Explainable Decisions**: Get human-readable explanations of AI decisions
- **Override & Feedback System**: Correct decisions and provide feedback for improvement
- **Audit Trail**: Export detailed decision reports for compliance
- **Analytics Dashboard**: Track decision patterns and system performance

## Tech Stack

- **React 18**: Modern React with hooks
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Smooth animations and transitions
- **Lucide React**: Beautiful icons
- **Recharts**: Data visualization charts
- **React Hot Toast**: Toast notifications
- **Axios**: HTTP client for API calls

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn
- Backend server running on port 8000

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

### Building for Production

```bash
npm run build
```

## Project Structure

```
frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/
│   │   ├── ClaimAnalyzer.js      # Main claim analysis interface
│   │   ├── Analytics.js          # Analytics dashboard
│   │   ├── AuditReports.js       # Audit reports management
│   │   ├── FeedbackDashboard.js  # Feedback system
│   │   ├── DocumentManager.js    # Multi-document management
│   │   └── Navbar.js            # Navigation component
│   ├── App.js                   # Main app component
│   ├── index.js                 # React entry point
│   └── index.css               # Global styles with Tailwind
├── package.json
├── tailwind.config.js
└── postcss.config.js
```

## API Integration

The frontend communicates with the backend through the following endpoints:

### Claim Analysis
- `POST /api/analyze` - Submit claim for analysis
- `GET /api/analytics` - Get system analytics
- `GET /api/feedback/analytics` - Get feedback analytics

### Document Management
- `GET /api/documents` - List all documents
- `POST /api/documents/upload` - Upload new documents
- `DELETE /api/documents/{id}` - Delete document

### Feedback System
- `GET /api/feedback` - Get feedback list
- `POST /api/feedback` - Submit feedback
- `POST /api/feedback/override` - Override decision

### Audit System
- `GET /api/audit/reports` - Get audit reports
- `POST /api/audit/export` - Export audit report
- `GET /api/audit/export/{id}` - Download specific report

## Key Features Explained

### 1. Claim Analyzer
The main interface matches the provided image design with:
- Natural language input for claims
- Real-time analysis with decision cards
- Justification and reasoning breakdown
- Action buttons for override and export

### 2. Analytics Dashboard
- Decision distribution charts
- Monthly trends visualization
- Success rate metrics
- Recent activity tracking

### 3. Multi-Document Support
- Upload and manage different document types
- Search and filter documents
- View document details and chunks

### 4. Feedback System
- Submit corrections and improvements
- Track feedback analytics
- View feedback history

### 5. Audit Reports
- Browse all decision reports
- Filter by date, decision type, and search
- Export reports as PDF
- View detailed decision breakdowns

## Styling

The frontend uses Tailwind CSS with a custom color scheme:
- Primary: Blue gradient (`primary-50` to `primary-900`)
- Secondary: Purple gradient (`secondary-50` to `secondary-900`)
- Status colors: Green (approved), Red (rejected), Yellow (pending)

## Responsive Design

The interface is fully responsive and works on:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (320px - 767px)

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Development

### Adding New Features

1. Create new component in `src/components/`
2. Add route in `App.js`
3. Add navigation item in `Navbar.js`
4. Update API calls as needed

### Styling Guidelines

- Use Tailwind utility classes
- Follow the established color scheme
- Use Framer Motion for animations
- Maintain consistent spacing and typography

### State Management

- Use React hooks for local state
- Keep API calls in components
- Use toast notifications for user feedback
- Handle loading and error states

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure backend is running on port 8000
2. **API Connection**: Check proxy settings in package.json
3. **Build Errors**: Clear node_modules and reinstall
4. **Styling Issues**: Ensure Tailwind CSS is properly configured

### Performance

- Lazy load components for better performance
- Optimize images and assets
- Use React.memo for expensive components
- Implement proper error boundaries

## Contributing

1. Follow the existing code style
2. Add proper error handling
3. Include loading states
4. Test on multiple screen sizes
5. Update documentation as needed

## License

This project is part of the LLM Document Query System.
