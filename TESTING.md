# Valence Testing Documentation

## Overview

This document provides comprehensive information about the test suite for the Valence application. The test suite covers backend functionality including CRUD operations, API endpoints, permissions, email functionality, and import/export features.

## Test Suite Statistics

### Total Test Count: **126+ Tests**

| Test Category | Test File | Tests | Description |
|--------------|-----------|-------|-------------|
| **User Operations** | `users/tests.py` | 34 | User creation, authentication, projects, CAM operations |
| **Block Operations** | `block/tests.py` | 11 | Block CRUD, drag/drop, resize, validation |
| **Link Operations** | `link/tests.py` | 13 | Link CRUD, direction swap, cascade deletion |
| **Import/Export** | `users/test_import_export.py` | 10 | ZIP file handling, CSV export/import |
| **Email** | `users/test_email.py` | 13 | Contact forms, CAM sharing, password reset |
| **API Endpoints** | `users/test_api.py` | 20 | JSON responses, endpoint validation, error handling |
| **Permissions** | `users/test_permissions.py` | 25 | Access control, authentication, authorization |

---

## Test Categories

### 1. User Operations (`users/tests.py`)

**UserTestCase** - 24 tests
- ✅ User creation (participant, affiliated/non-affiliated)
- ✅ Login/logout functionality
- ✅ Invalid credentials handling
- ✅ Researcher account creation
- ✅ Language preference changes
- ✅ Project creation, deletion, settings
- ✅ Random user creation
- ✅ Model update methods
- ✅ String representations
- ✅ Database constraints (unique names)
- ✅ Project link joining (new, reuse, duplicate CAM)

**CAMOperationsTestCase** - 10 tests
- ✅ Individual CAM creation
- ✅ CAM loading
- ✅ CAM deletion
- ✅ CAM name updates
- ✅ CAM download (JSON)
- ✅ CAM cloning with all content
- ✅ CAM clearing
- ✅ Project-CAM associations
- ✅ Model string representations

---

### 2. Block Operations (`block/tests.py`)

**BlockTestCase** - 11 tests
- ✅ Block creation
- ✅ Block updates
- ✅ Block deletion
- ✅ Drag and drop positioning
- ✅ Block resizing
- ✅ Text size updates
- ✅ Model update methods
- ✅ All 8 shape types validation
- ✅ String representation
- ✅ Default values
- ✅ Cascade deletion with CAM

**Supported Block Shapes:**
1. Neutral (rectangle)
2. Positive (rounded circle)
3. Negative (hexagon)
4. Positive strong
5. Negative strong
6. Ambivalent
7. Negative weak
8. Positive weak

---

### 3. Link Operations (`link/tests.py`)

**LinkTestCase** - 13 tests
- ✅ Link creation
- ✅ Link updates
- ✅ Link deletion
- ✅ Direction swapping
- ✅ Position updates
- ✅ Model update methods
- ✅ All 6 line style types
- ✅ All 3 arrow types
- ✅ String representation
- ✅ Default values
- ✅ Cascade deletion with blocks
- ✅ Cascade deletion with CAM
- ✅ Bidirectional links

**Supported Link Styles:**
- Solid, Solid-Strong, Solid-Weak
- Dashed, Dashed-Strong, Dashed-Weak

**Supported Arrow Types:**
- None, Uni-directional, Bi-directional

---

### 4. Import/Export (`users/test_import_export.py`)

**CAMImportExportTestCase** - 10 tests
- ✅ ZIP file creation on export
- ✅ CSV content validation
- ✅ Import from valid ZIP files
- ✅ Clearing existing blocks on import
- ✅ Empty CAM export
- ✅ Malformed file handling
- ✅ Block property preservation
- ✅ Link property preservation
- ✅ Filename includes username
- ✅ File structure validation

**Export Format:**
```
username_CAM.zip
├── blocks.csv  (all block properties)
└── links.csv   (all link properties)
```

---

### 5. Email Functionality (`users/test_email.py`)

**EmailFunctionalityTestCase** - 13 tests
- ✅ Contact form submission
- ✅ Invalid email handling
- ✅ Missing field validation
- ✅ CAM sharing via email
- ✅ Password reset emails
- ✅ HTML escaping (XSS prevention)
- ✅ Invalid recipient handling
- ✅ Unauthorized CAM sharing prevention
- ✅ Email backend configuration
- ✅ Complete field inclusion
- ✅ Multiple sequential emails
- ✅ GET request form display

**Email Features Tested:**
- Contact form → Support team
- CAM sharing → Recipients
- Password reset → Users
- XSS prevention
- Email validation

---

### 6. API Endpoints (`users/test_api.py`)

**APIEndpointTestCase** - 20 tests
- ✅ JSON response validation
- ✅ CAM download endpoint
- ✅ CAM load endpoint
- ✅ Block CRUD via API
- ✅ Link CRUD via API
- ✅ Link direction swap
- ✅ Invalid request handling
- ✅ Unauthorized access prevention
- ✅ Cross-user data access prevention
- ✅ Drag function positioning
- ✅ Block resizing
- ✅ Text size updates
- ✅ Project creation
- ✅ Concurrent request handling

**API Endpoints Tested:**

*Authentication:*
- POST `/users/loginpage`
- GET `/users/logout`
- POST `/users/password_reset/`

*CAM Management:*
- GET `/users/download_cam`
- POST `/users/load_cam`
- POST `/users/create_individual_cam`
- POST `/users/delete_cam`
- POST `/users/update_cam_name`

*Block Operations:*
- POST `/block/add_block`
- POST `/block/update_block`
- POST `/block/delete_block`
- POST `/block/drag_function`
- POST `/block/resize_block`
- POST `/block/update_text_size`

*Link Operations:*
- POST `/link/add_link`
- POST `/link/update_link`
- POST `/link/delete_link`
- POST `/link/swap_link_direction`
- POST `/link/update_link_pos`

*Project Management:*
- POST `/users/create_project`
- POST `/users/join_project`
- GET `/users/download_project`

---

### 7. Permissions & Access Control (`users/test_permissions.py`)

**PermissionsAndAccessControlTestCase** - 25 tests

**Authentication Tests:**
- ✅ Unauthenticated redirect to login
- ✅ Login required decorator
- ✅ Session management after logout
- ✅ Anonymous user capabilities

**Authorization Tests:**
- ✅ Participant cannot create projects
- ✅ Researcher can only edit own projects
- ✅ Researcher can only delete own projects
- ✅ User can only access own CAMs
- ✅ User cannot delete others' CAMs
- ✅ User cannot modify others' blocks
- ✅ Cross-user data access prevention

**Project Access Tests:**
- ✅ Join with correct password
- ✅ Deny access with wrong password
- ✅ Participant can access project CAMs
- ✅ Researcher can download project data
- ✅ Non-owner cannot download project
- ✅ Project link authentication

**Role-Based Tests:**
- ✅ Researcher status required for projects
- ✅ Researcher can view own project page
- ✅ User can only clear own CAM

**Permission Matrix:**

| Action | Researcher (Owner) | Researcher (Other) | Participant | Anonymous |
|--------|-------------------|-------------------|-------------|-----------|
| Create Project | ✅ | ✅ | ❌ | ❌ |
| Edit Own Project | ✅ | - | ❌ | ❌ |
| Edit Other Project | ❌ | ❌ | ❌ | ❌ |
| Delete Own Project | ✅ | - | ❌ | ❌ |
| Delete Other Project | ❌ | ❌ | ❌ | ❌ |
| Create CAM | ✅ | ✅ | ✅ | ❌ |
| Edit Own CAM | ✅ | ✅ | ✅ | ❌ |
| Edit Other CAM | ❌ | ❌ | ❌ | ❌ |
| Join Project | ✅ | ✅ | ✅ | ❌ |
| Download Project | ✅ (own) | ❌ | ❌ | ❌ |
| Create Random User | ❌ | ❌ | ❌ | ✅ |

---

## Running Tests

### Setup

1. **Set environment variable:**
```bash
export DJANGO_LOCAL=True  # Use SQLite for testing
```

2. **Activate virtual environment:**
```bash
# Using venv
source venv/bin/activate

# Using conda
conda activate valence
```

### Run All Tests

```bash
# Run entire test suite
python manage.py test

# Run with verbose output
python manage.py test --verbosity=2

# Run tests and keep database
python manage.py test --keepdb
```

---

## Test Coverage Analysis

### Install Coverage.py

```bash
pip install coverage
```

### Generate Coverage Report

```bash
# Run tests with coverage
coverage run --source='.' manage.py test

# Generate terminal report
coverage report

# Generate detailed HTML report
coverage html

# Open report in browser
# Open htmlcov/index.html
```
