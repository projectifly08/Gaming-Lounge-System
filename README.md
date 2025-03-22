# Gaming Lounge Management System

A comprehensive management system for gaming lounges, internet cafes, and gaming centers. This application provides both an admin panel for staff and a game launcher for customers.


## Features

### Admin Panel

- **Dashboard**: Real-time statistics and overview of the gaming lounge
- **Registration**: Register new users and assign PCs
- **Sessions**: Manage active gaming sessions, extend time, pause/resume sessions
- **Orders**: Process food and drink orders, track order status
- **Menu Management**: Add, edit, and remove menu items
- **Reports**: Generate revenue reports, usage statistics, and analytics
- **Settings**: Configure system settings, pricing, and backup options

### Game Launcher (Client)

- **Login**: Secure user authentication
- **Dashboard**: View session information and time remaining
- **Games**: Browse and launch available games
- **Food & Drinks**: Order food and drinks directly from the PC
- **Orders**: View order history with cancel options

## Technical Details

- **Language**: Python 3.8+
- **GUI Framework**: PyQt5
- **Database**: MySQL
- **Architecture**: Modular design with clear separation of concerns

## Prerequisites

Before installing, make sure you have:

1. **Python 3.8+** installed
2. **MySQL 5.7+** server installed and running
3. Basic knowledge of database administration if you need to troubleshoot setup

## Quick Start

### Windows Installation

1. Double-click on `install.bat`
2. Follow the on-screen instructions to complete the installation
3. When prompted, edit the `.env` file with your MySQL credentials
4. To start the admin panel, run `run_admin.bat`
5. To start the game launcher, run `run_launcher.bat`

## Manual Installation

1. Clone the repository:
   ```
   git clone https://github.com/projectifly08/Gaming-Lounge-System.git
   cd gaming-lounge-system
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Update `.env` file
   - Update the database connection details and other settings

4. Initialize the database:
   ```
   python -m src.database.init_db
   ```

5. Running the Admin Panel
   ```
   python -m src.main --admin
   ```

6. Running the Game Launcher
   ```
   python -m src.main --user
   ```


## System Requirements

- **OS**: Windows 10/11
- **Processor**: Intel Core i3 or equivalent
- **Memory**: 4GB RAM
- **Storage**: 500MB free disk space
- **Database**: MySQL 5.7+
- **Python**: 3.8+



## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Ensure MySQL server is running
   - Check database credentials in `.env` file

2. **Application Won't Start**
   - Ensure all dependencies are installed
   - Check Python version (3.8+ required)

3. **GUI Issues**
   - Ensure PyQt5 is properly installed
   - Try updating your graphics drivers
