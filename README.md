# 🚗 Vehicle Parking App - V1

A multi-user parking management web application for 4-wheeler vehicles, built using Flask, SQLite, and Bootstrap. The system supports both admin (superuser) and user roles to manage parking lots and parking spots dynamically.

---

## 📌 Features

### 🔐 Authentication
- **Admin Login** (no registration required)
- **User Registration & Login**

### 👨‍💼 Admin Functionalities
- Create/edit/delete parking lots
- Automatically generate parking spots based on lot capacity
- View real-time status of all parking spots
- View parked vehicle details
- View and manage all registered users
- Visual summary charts of lot/spot usage

### 👤 User Functionalities
- Register and log in
- View available parking lots
- Book first available parking spot automatically
- Release parking spot
- View personal booking history
- Parking timestamps & cost calculation
- View usage summaries

---

## 🧱 Tech Stack

| Layer        | Technology Used                      |
|--------------|--------------------------------------|
| Backend      | Flask, SQLAlchemy (ORM)              |
| Frontend     | HTML, CSS, Jinja2, Bootstrap         |
| Database     | SQLite (programmatically created)    |
| Tools        | Visual Studio Code, Git              |

---

## 🗃️ Database Models

### `User`
- `id`, `username`, `email`, `password`, `role`, `location`, `vehicle_number`, `pin`
- Relationship: `posts` → `Release`

### `Lot`
- `id`, `prime_location`, `price`, `address`, `pin_code`, `maximum_spots`
- Relationship: `spots` → `Spot`

### `Spot`
- `id`, `lot_id`, `user_id`, `spot_number`, `status`
- Relationship: `user`, `releases` → `Release`

### `Release`
- `id`, `spot_id`, `user_id`, `parked_at`, `released_at`, `cost`

---

## 🚦 Booking & Release Logic

- On **booking**, a user is auto-assigned the first available spot in the selected lot.
- On **release**, the spot is marked available again, and the session's start/end time and cost are recorded.

---

## 📊 Admin/User Dashboard

- Displays booking history and current status
- Charts or summaries for:
  - Number of active users
  - Total lots/spots
  - Usage trends (optional enhancements)

---

## 🛠️ How to Run

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/vehicle-parking-app.git
cd vehicle-parking-app

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the Flask server
python app.py

