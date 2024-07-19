
# Squad Quick Team-Building Tool

## Introduction

This tool is designed to help "Squad" players quickly create teams after a game ends, saving time and enhancing the overall gaming experience. It's especially useful for players with less powerful computers, giving them a fair chance to compete for vehicle use.

## Features

### Python Code Features

1. **GUI Creation and Management**:
   - Uses the Tkinter library to create a user-friendly interface.
   - Includes features like window centering, debug information display and saving, and window icon settings.

2. **QR Code Generation**:
   - Generates a QR code containing the local IP address and available port, making it easy for users to scan and automatically open the corresponding webpage.

3. **Flask Web Server**:
   - Creates a Flask web application to handle web requests and dynamically generate content.
   - Provides a main route to display a webpage with vehicle data and background images.

4. **Remote File Retrieval**:
   - Fetches URL configuration files, HTML template files, and JSON data files from GitHub, ensuring real-time data updates and synchronization.

5. **Image Processing**:
   - Retrieves background images from Bing daily images or a backup URL and calculates the dominant color for use on the webpage.

6. **Sound Playback**:
   - Uses the PyAudio library to play specific notification sounds, enhancing the user experience.

7. **Screen Blackout Detection**:
   - Detects if the screen brightness is below a threshold to determine if the game has ended, triggering automatic team creation.

8. **Vehicle Data Processing**:
   - Parses JSON files to extract map names, game modes, and version information, generating corresponding HTML option lists.

### HTML Code Features

1. **Dynamic Webpage Generation**:
   - Uses Jinja2 templates to dynamically render HTML content based on vehicle data, background images, and colors.

2. **User Interaction**:
   - Provides input fields, buttons, sliders, and other interactive elements for users to input team names, select repetition times, set key press order, and delay times.

3. **Map and Vehicle Query**:
   - Allows users to select maps, modes, and versions, and query vehicle information on specific maps, displaying the distribution of vehicles for two teams.

4. **Image Display**:
   - Offers a vehicle weakness query feature, displaying corresponding vehicle weakness images when buttons are clicked.

5. **Page Styling and Layout**:
   - Uses CSS to define page styles, making the page aesthetically pleasing and easy to use, including background colors, fonts, and button styles.

## Usage Instructions

1. **Install Dependencies**:
   Make sure you have the following Python libraries installed:
   - tkinter
   - pillow
   - socket
   - qrcode
   - flask
   - pyautogui
   - numpy
   - pyaudio
   - requests
   - concurrent.futures

   You can install the required dependencies using the command:
   ```sh
   pip install -r requirements.txt
   ```

2. **Run the Program**:
   Run the main program:
   ```sh
   python run.py
   ```

3. **Using the Tool**:
   - Start the program and scan the QR code to open the webpage.
   - Enter the team name, select the repetition times, key press order, and delay time on the webpage.
   - Click the "Prepare Team" button, and the program will automatically input the team creation code.

## PyInstaller Packaging Tutorial

1. **Install PyInstaller**:
   Install PyInstaller using the command:
   ```sh
   pip install pyinstaller
   ```

2. **Package the Program**:
   Before packaging, it is recommended to recompile the PyInstaller bootloader to avoid detection by Windows Defender.
   Use PyInstaller to package the Python script into an executable file:
   ```sh
   Pyinstaller -F -w run.py
   ```

   This will generate a standalone executable file that can run on computers without a Python environment.

## Disclaimer

This tool does not modify game files or memory and does not affect the normal operation of the game. It is merely an external auxiliary tool that simulates keyboard input and displays vehicle information to help players improve efficiency and experience. The intention behind developing this tool is to assist players without any intention of cheating or disrupting game fairness. If the official view is that this tool involves cheating or does not comply with game rules, we will immediately stop its distri...
