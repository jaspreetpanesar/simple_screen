# SIMPLE SCREEN

A simple wrapper around linux screen GNU to simplify starting and resuming screen sessions.

## Getting Started
The following examples will show you how to install and setup the simple_screen script to easily use it from the commandline.

### Prerequisites
Make sure you have Python (version 2.7) installed.


### Installation
To install the script, follow the steps listed below:  

1.  Clone this repository into your preferred directory.  
    ```
    git clone https://github.com/jaspreetpanesar/simple_screen.git
    ```

2.  Create an entry in your .bashrc with an alias pointing to the simple_screen.py scipt.  
    ```
    alias ss='python /path/to/simple_screen/simple_screen.py'
    ```

3.  Reload bashrc file.
    ```
    source ~/.bashrc
    ```

4.  Run Simple Screen.
    ```
    ss 
    ```

### More Features
Additionally, you can add the following code to the end of your .bashrc to automatically connect to a new or detached screen session when starting a new shell.
```
if [ "$STY" == "" ]; then
    python /path/to/simple_screen/simple_screen.py
fi
```

## Author
Jaspreet Panesar 

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
