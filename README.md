# pdf_chatbot
# PDF Q&A Assistant Frontend

A React-based frontend application for uploading PDF documents and asking questions about their content using AI.

## Features 

- **PDF Upload**: Upload PDF documents with drag-and-drop or file selection.
- **Document Management**: View all uploaded documents with metadata.
- **Interactive Q&A**: Ask questions about uploaded documents and get AI-powered answers.
- **Real-time Progress**: Visual feedback for uploads and processing.
- **Responsive Design**: Works seamlessly on desktop and mobile devices.
- **Modern UI**: Clean, intuitive interface with smooth animations.

## Tech Stack

- **React 18** - Modern React with hooks
- **Axios** - HTTP client for API communication
- **Lucide React** - Beautiful, customizable icons
- **CSS3** - Custom styling with flexbox and grid
- **Create React App** - Project setup and build tools

## Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- Backend API server running (typically on port 8000)

## Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd pdf-qa-frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set `REACT_APP_API_URL` to your backend URL.

4. **Start the development server**
   ```bash
   npm start
   ```

   The app will open at [http://localhost:3000](http://localhost:3000)

## Project Structure

```
src/
├── App.js          # Main application component
├── App.css         # Application-specific styles
├── index.js        # React entry point
├── index.css       # Global styles
└── reportWebVitals.js  # Performance monitoring

public/
├── index.html      # HTML template
├── favicon.ico     # App icon
└── manifest.json   # PWA manifest
```

## API Integration

The app communicates with a backend API that should provide these endpoints:

- `GET /documents` - Fetch all documents
- `POST /upload` - Upload new PDF document
- `GET /documents/{id}/questions` - Fetch questions for a document
- `POST /ask` - Ask a question about a document

## Environment Variables

- `REACT_APP_API_URL` - Backend API base URL (default: http://localhost:8000)

## Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App (irreversible)

## Features Overview

### Document Upload
- Supports PDF files only
- Shows upload progress
- Automatic file validation
- Visual feedback for upload status

### Document Management
- List all uploaded documents
- Show upload date and file size
- Click to select and interact with documents
- Visual indication of selected document

### Q&A Interface
- Ask questions in natural language
- View conversation history
- Real-time processing indicators
- Keyboard shortcuts (Enter to submit)

### Responsive Design
- Mobile-first approach
- Flexible layouts for all screen sizes
- Touch-friendly interfaces
- Optimized for both desktop and mobile

## Customization

### Styling
- Modify `App.css` for component-specific styles
- Update `index.css` for global styles
- CSS custom properties for easy theming

### API Configuration
- Update API endpoints in `App.js`
- Modify request/response handling as needed
- Add authentication headers if required

## Deployment

### Build for Production
```bash
npm run build
```

### Deploy to Static Hosting
The build folder can be deployed to any static hosting service:
- Netlify
- Vercel
- GitHub Pages
- AWS S3
- Firebase Hosting

### Environment Variables for Production
Make sure to set the correct `REACT_APP_API_URL` for your production backend.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support or questions, please open an issue in the repository.
