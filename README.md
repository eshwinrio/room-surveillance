# Room Surveillance

This project is a room surveillance system that monitors and records activities within a specified area using a camera.

## Features

- Real-time video monitoring
- Motion detection
- Recording and storing video footage
- Backing up footages to a SSH enabled server

## Installation

To install and run this project, follow these steps:

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/room-surveillance.git
    cd room-surveillance
    ```

2. **Create a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Run the application:**

    ```bash
    python main.py
    ```

## Usage

1. Ensure your camera is connected and recognized by your system.
2. Run the application using the command above.
3. The system will start monitoring and recording based on motion detection.
4. Access the recorded footage in the directories specified in your .env or the defaults `~/recordings`.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.