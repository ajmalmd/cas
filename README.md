# Customer Approval System

A web-based customer management and approval application built with Django and MongoDB. The system implements a Maker–Checker workflow in which Makers submit customer information for review, and assigned Checkers approve or decline those submissions.

## Project Overview

The Customer Approval System provides a centralized workflow for submitting, reviewing, and managing customer records.

The system has three user categories:

- **Admin:** Manages users, assigns roles, configures Maker–Checker relationships, and manages customer records.
- **Maker:** Creates customer records, uploads supporting documents, and tracks the status of submissions.
- **Checker:** Reviews customer records submitted by assigned Makers and approves or declines pending submissions.

## Technologies Used

- **Backend:** Python, Django
- **Database:** MongoDB Atlas
- **Frontend:** HTML, Tailwind CSS, jQuery
- **Authentication:** Django authentication system
- **File uploads:** Cloudflare R2
- **Deployment:** Render
- **Database tools:** MongoDB Database Tools

## Key Features

### Authentication and Role Management
- Secure login and logout.
- Role-based access for Admins, Makers, and Checkers.
- Admin management of user roles and assignments.

### Maker Dashboard
- Create customer records.
- Upload customer photos and resumes.
- View submitted customer details.
- Track pending, approved, and declined submissions.
- Search and filter customer records.

### Checker Dashboard
- View customer records submitted by assigned Makers.
- Search and filter submissions by customer, Maker, or status.
- Review customer details and uploaded documents.
- Approve or decline pending submissions.

### Admin Management
- Manage application users and their roles.
- Assign Makers to Checkers.
- View and manage customer records.
- Monitor the Maker–Checker hierarchy.

### Customer Approval Workflow

`Pending → Approved`

`Pending → Declined`

Only pending submissions are eligible for review.

## Maker–Checker Hierarchy

The current configured assignments are:

```text
Customer Approval System
│
├── CheckerA
│   ├── MakerA
│   └── MakerB
│
└── CheckerB
    └── MakerC
```

| Checker | Assigned Makers |
|---|---|
| CheckerA | MakerA, MakerB |
| CheckerB | MakerC |

Each Checker can review submissions belonging to their assigned Makers. Access restrictions are enforced by the backend.

## Prerequisites

Install the following before running the application:

- Python version compatible with the project's dependencies.
- MongoDB Atlas account or a compatible MongoDB deployment.
- Git, if cloning the repository.
- Python package installer (`pip`).

## Security and Access Control

- Authentication is required for protected application features.
- Users have role-specific permissions.
- Makers can access their own customer submissions.
- Checkers can access submissions belonging to their assigned Makers.
- Approval and decline operations are restricted to pending submissions.
- Uploaded documents should be accessed through the application's authorized file-serving mechanism.
- Secret keys and database credentials must remain outside the source repository.

**Project:** Customer Approval System  
**Purpose:** Customer record submission, review, and approval using a Maker–Checker workflow.
