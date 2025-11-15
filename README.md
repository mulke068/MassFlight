# MassFlight
An Object Trajectory Sim


The Idea of our project is to develop a tool that calculates and simulates the trajectory of an object with a variable mass in a certain location. The program will ask the user for the object's mass and how powerful the launcher is. The user also has to choose a position on a map, where the object should launch from. With the position, the program will determine the wind speed and other factors and calculate their effect on the object at the current time. 


# Dependencies
Python 3.9.13
pyglet 1.5.27

https://www.windy.com
https://www.ursinaengine.org



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
virtualenv myenv
```
Activate your isolated environment
```
.\myenv\Scripts\activate
```
Install the required libraries
```
pip install -r requirements.txt
```
Execute the Program
```
python .\main.py
```
