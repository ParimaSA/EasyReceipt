# EasyReceipt

# Easy Receipt

Easy Receipt is a web application that helps users manage **personal and shared income/expense records**.
Users can track their own receipts or create groups to share financial records with others.
The system also supports **QR code scanning** to quickly add receipt information.

---

## Features

* Personal income and expense tracking
* Create and manage shared expense groups
* Add receipts manually
* Add receipts by scanning QR codes
* View transaction history
* Simple and user-friendly interface

---

## System Architecture

The project follows a **layered architecture** to separate responsibilities between different parts of the system.

Frontend (Vue)
⬇
REST API (Node.js + Express)
⬇
Controller Layer
⬇
Service / Repository Layer
⬇
MySQL Database


## Installation

### Clone the repository

```
git clone https://github.com/ParimaSA/EasyReceipt
```

---

### Frontend Setup

```
cd frontend
npm install
npm run dev
```

The frontend will run at:

```
http://localhost:5173
```

---

### Backend Setup

```
cd backend
npm install
npm run dev
```

The backend server will run at:

```
http://localhost:3000
```
