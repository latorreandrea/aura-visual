# AuraVisual

**AuraVisual** is a lightweight, scalable Flask web application designed for deployment on **Google Cloud Run**. It serves as a foundation for creative startups looking to showcase their web presence with modern, modular architecture.

The app uses **Google Firestore** as its database, enabling serverless, real-time data storage without managing database infrastructure. Built with **Flask Blueprints**, AuraVisual supports easy expansion and maintenance.

---

## ✨ Features

- ✅ Modular Flask app structure with support for multiple Blueprints  
- ✅ Integration with Google Firestore for fast, scalable backend data storage  
- ✅ Ready for deployment on Google Cloud Run with Docker and Cloud Build automation  
- ✅ Clean, minimal starter code for small projects  
- ✅ Production-ready with Gunicorn server configuration

---

## 🛠️ Technologies

- **Python 3.11**
- **Flask 3.0.x**
- **Google Cloud Run**
- **Google Firestore (NoSQL)**
- **Docker**
- **Gunicorn**

---

## 📝 Contact Form System

The application includes a fully-featured contact form system that securely collects user inquiries and stores them in Firestore.

### How it Works

1. **User Interaction**
   - User fills out the form fields and clicks "Submit"
   - Front-end validation provides immediate feedback for basic errors

2. **Form Submission Process**
   - JavaScript intercepts the form submission
   - Data is sent asynchronously via AJAX to prevent page reloads
   - Loading indicator provides visual feedback during submission

3. **Server-Side Processing**
   - Flask backend receives the request
   - WTForms validates all data according to defined rules
   - CSRF protection prevents cross-site request forgery attacks

4. **Data Handling**
   - If validation fails, specific error messages are returned
   - If successful, data is securely stored in Firestore
   - Sanitization prevents injection attacks

5. **Response Handling**
   - Server returns JSON response with success/error status
   - JavaScript processes the response
   - User receives appropriate feedback (success message or error details)

6. **Security Features**
   - CSRF protection with Flask-WTF
   - Input validation and sanitization
   - IP address logging for audit purposes
   - Rate limiting capability to prevent abuse

This implementation follows modern web standards and best practices, providing a smooth user experience while maintaining robust security.