# Gas Utility Service Management System

## Overview
The Gas Utility Service Management System is a Django-based application designed to handle customer service requests efficiently. The system allows customers to raise service requests, which are automatically assigned to support staff for resolution. It provides authentication, request tracking, and role-based access.

## Features
- **User Registration & Authentication:**
  - Customers and support staff can register and log in.
  - JWT-based authentication for secure access.
- **Service Request Management:**
  - Customers can create service requests.
  - Requests are assigned to a random support staff (can be improved to consider staff workload or specialization).
  - Customers can delete requests if they are still in the pending state.
  - Support staff can update request status.
- **Profile Management:**
  - Customers and support staff can view their profiles.
- **File Uploads:**
  - Attachments are stored on the server (can be improved by moving to Amazon S3).

## Project Structure
```
gasutility/
│── attachments/          # Handles file uploads and attachments
│── service_requests/     # Manages service request logic and database models
│── accounts/             # Handles user authentication and profile management
│── gas_utility/          # Contains settings, URLs, and main configurations
```

## Deployment
The project is deployed and API is fully documented with Swagger and can be accessed here: [API Documentation](https://gas-utility.onrender.com/swagger/)

## Test Flow
### 1. User Registration
- Register a customer account.
- Register a support_staff account.

### 2. User Authentication
- Generate an access token using the customer’s login credentials.
- Generate an access token using the support_staff’s login credentials.

### 3. Customer Actions
- Create a service request using the customer’s token.
- View all requests created by the customer.
- If a request is in the pending state, delete it.

### 4. Support Staff Actions
- View all requests assigned to the support staff.
- Update the status of a request.

## Future Enhancements
- Assign requests based on support staff availability, workload, or specialization instead of random assignment.
- Move file uploads to a cloud storage solution like Amazon S3 for better scalability.
- Implement real-time notifications for request status updates.


