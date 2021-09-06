# ThaiRomanizationSharp
- The .NET project that wraps Thai Romanization in [Thai Language Toolkit Project](https://github.com/attapol/tltk) to simplify usage in other .NET projects.

# Credit
- Credit to [Assoc.Prof. Wirote Aroonmanakun (Ph.D.)](http://pioneer.chula.ac.th/~awirote/)
- Director of the Siridhorn Thai Language Institute, Chulalongkorn University
- Original code is from https://github.com/attapol/tltk/blob/master/tltk/nlp.py.
- Thai Romanization main project page http://pioneer.chula.ac.th/~awirote/resources/thai-romanization.html.

# How to run the project locally


## Prerequisite
- A computer with Ubuntu OS, I use Ubuntu 18.04 (Bionic) but this instruction can be applied to Ubuntu 20.04 as well.
- You can also use WSL2 + Ubuntu.
- Visual Studio Code

## Install required software
- Open a new terminal and start in your home directory.
- Install .NET by follow [this instruction](https://www.dotnetthailand.com/programming-cookbook/wsl-powershell-useful-scripts/install-dotnet)
- Install Mono by executing the following commands:
  ```sh
  $ sudo apt install gnupg ca-certificates
  $ sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF
  $ echo "deb https://download.mono-project.com/repo/ubuntu stable-bionic main" | sudo tee /etc/apt/sources.list.d/mono-official-stable.list
  $ sudo apt update
  $ sudo apt install mono-devel
  ```
- Verfify if Mono has been installed successfully
  ```
  $ mono --version
  ```
- You should get Mono version `6.12.0.122` or newer.
- Install Python by executing the following command;
  ```sh
  $ sudo apt update && sudo apt -y upgrade
  $ sudo apt install python3
  ```
- Verify if Python has been installed successfully by checking a vesion.
  ```sh
  $ python3 --version
  ```
- We should get Python version `3.6.9` or newer.
- Install pip by excuting the following command:
  ```sh
  $ sudo apt install python3-pip
  ```
- Check installed pip3 version.
  ```
  $ pip3 --version
  ```
- We should get pip version `9.0.1` or newer.
- Set default python and pip command to version 3
  ```sh
  $ vi .bashrc
  ```
- Add alias for python and pip to the end of .bashrc file.
  ```
  $ alias python=python3
  $ alias pip=pip3
  ```
- Save and exit Vi by typing `:wq`.
- Load new configuration by sourcing .bashrc.
  ```sh
  $ source .bashrc
  ```
- Check if we have set alias correctly.
  ```sh
  $ python --version && pip --version
  ```
- We should get Python version 3 and pip of Python version 3.
- Install `pythonnet` and its requirement by execting the following commands:
  ```sh
  $ sudo apt install -y clang
  $ pip install -U setuptools
  $ pip install -U wheel
  $ pip install pythonnet
  ```
- Find a path of installed libpython
  ```sh
  $ wget https://gist.githubusercontent.com/tkf/d980eee120611604c0b9b5fef5b8dae6/raw/9f074cd233f83180676b4421212ed33c257968af/find_libpython.py
  $ /usr/bin/python3 find_libpython.py --list-all
  ```
- Copy a path and keep only .so e.g. `/usr/lib/x86_64-linux-gnu/libpython3.6m.so`.
- Add `PYTHONNET_PYDLL` environment variable which has value equal to libpython path
  by editing .bashrc file.
  ```sh
  $ vi .bashrc
  ```
- Define PYTHONNET_PYDLL variable and paste a value from copied pythonlib path
  to the bottom of .bashrc
  ```
  export PYTHONNET_PYDLL=/usr/lib/x86_64-linux-gnu/libpython3.6m.so
  ```
- Save .bashrc and exit Vi by typing `:wq`.
- Load new configuration by sourcing .bashrc.
  ```sh
  $ source .bashrc
  ```

## Prepare the project
- Clone the project.
  ```
  $ git clone git@github.com:dotnetthailand/ThaiRomanizationSharp.git
  ```
- CD to the project folder.
- Open the project with VS Code
  ```sh
  code .
  ```
- The structure of the project is:
  ```sh
  $ tree -I 'bin|obj' ThaiRomanizationSharp
  ThaiRomanizationSharp/
  ├── LICENSE
  ├── PhSTrigram.sts
  ├── Program.cs
  ├── README.md
  ├── ThaiRomanizationSharp.csproj
  ├── find_libpython.py
  ├── nlp.py
  ├── sylrule.lts
  ├── sylseg.3g
  ├── thaisyl.dict
  └── thdict
  ```

## Run the project
- In VS Code open integrated terminal by pressing **ctrl+`**.
- The terminal should start from the root of the project.
- Run the project with the following command:
  ```sh
  $ dotnet run
  ```
- Wait for a while and you should find an output message in the integrated terminal.


# Reference & useful links
- https://github.com/PyThaiNLP/pythainlp/issues/11
- https://github.com/comdevx/thai2karaoke

# Todo
- [ ] More details what code changes in nlp.py
- [ ] Convert project to a class library
- [ ] Unit test with xUnit
- [ ] GitHub Actions to run a unit test
- [ ] GitHub Actions to deploy a library to Nuget and release page
- [ ] Custom Docker image
- [ ] Deploy example project to Azure App Service container
