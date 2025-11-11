# MassFlight
An Object Trajectory Sim


The Idea of our project is to developpe a tool that calculate and make a simulation of the trajectory of an object with a variable mass in a certain place. The program will ask the user for the objects mass and how powerful the launcher is. The user also has to choose a position on a map, were the object should launch from. With the position, the program will determine the wind speed and others and calculate the effect on the object for the current time. 


# Dependencies
Python 3.9.13
pyglet 1.5.27

https://www.windy.com
https://www.ursinaengine.org



# setup guide
install-pyenv-win.ps1 -> open in PowerShell

pyenv install 3.9.13
pyenv local 3.9.13

python -m pip install --user virtualenv

virtualenv myenv

.\myenv\Scripts\activate

pip install -r requirements.txt

python .\main.py