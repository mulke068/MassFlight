# MassFlight
An Object Trajectory Sim


The Idea of our project is to develop a tool that calculates and simulates the trajectory of an object with a variable mass in a certain location. The program will ask the user for the object's mass and how powerful the launcher is. The user also has to choose a position on a map, where the object should launch from. With the position, the program will determine the wind speed and other factors and calculate their effect on the object at the current time. 


# Dependencies
Python 3.9.13
pyglet 1.5.27
pyqt5


Live Data Source: NOAA/NWS tg-ftp

WGS84 ellipsoidal gravity formula

$$ \gamma (\phi )=\gamma _{a}\frac{1+p\cdot \sin ^{2}\phi }{\sqrt{1-e^{2}\cdot \sin ^{2}\phi }}\ $$

# setup guide

```install-pyenv-win.ps1``` -> open in PowerShell

Install Python version 3.9.13
```
pyenv install 3.9.13
```
Set Local Python inside a folder
```
pyenv local 3.9.13
```
Install virutalenv for a separate environment
```
python -m pip install --user virtualenv
```
Create your separated environment
```
virtualenv myenv || python -m virtualenv myenv
```
Activate your isolated environment
```
.\myenv\Scripts\activate
```
Install the required libraries
```
pip install -r requirements.txt || pip install PyQt6 PyOpenGL numpy pilkit matplotlib requests pytest
```
Execute the Program
```
python .\main.py
```
