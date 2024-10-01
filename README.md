# safsecfi
Purpose of this project:

This software is a research prototype, solely developed for and published as part of the publications FIISS, I-FASST, X-IFASST, and methods evaluation (reference links below). It will neither be maintained nor monitored in any way.

Project description:

The project provides a Python implementation of the methods FIISS (reference link below), I-FASST (reference link below), X-I-FASST (in submission), 'feature dependency extraction algorithm' referred as Vogelsang method (reference link below), and their evaluation (in submission). These methods identify feature interactions between safety and security features of a safety-critical system.

Link to our FIISS publication https://ieeexplore.ieee.org/document/10092690

Link to our I-FASST publication https://ieeexplore.ieee.org/document/10092690

Link to publication of feature dependency extraction algorithm  https://www.sciencedirect.com/science/article/abs/pii/S0164121219302328#fig0001

Info on test/usage:

The main() function in the implementation of each method can be found in its respective python module in the code directory.

To run the implementation of each method:
- Input: Export the UML software architecture model of a system under consideration in XMI format. Place the xmi file(s) in the 'data' directory.
- Configure the inputs in the Python module ('code' directory) and in the user defined library ('lib' directory).
- Run the python module

License:
The safsecfi project is open-sourced under the MIT license. See the LICENSE file for details.
