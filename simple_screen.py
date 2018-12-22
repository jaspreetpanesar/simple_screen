#!/usr/bin/python

"""
**Simple Screen**

Shortcut script for quickly opening and reopening screen sessions 
"""

import os, sys, argparse, subprocess


__author__ = "Jaspreet Panesar"
__version__ = 1


DEFAULT_SESSION_NAME = "main"


class TooManyScreensException(Exception):
    """exception to identify when there are more than
    one screens open"""
    pass

class UnrecognisedSelectionException(Exception):
    """exception to identify that selection made from
    user was unrecognised/incorrect"""
    pass


class Screen(object):
    """used to interface with screen sessions

    Params:
        name (string, optional): session name, defaults 
            to DEFAULT_SESSION_NAME
        id (string, optional): screen session id
    """

    def __init__(self, name=DEFAULT_SESSION_NAME, id=None):
        self.name = name
        self.id = id


    def run(self):
        """attach to screen with name, detach if necessary,
        create new if necessary"""
        os.system("screen -D -R %s" %self.name)


    def kill(self):
        """kill the screen session"""
        os.system("screen -X -S %s quit" %self.id)


    def __repr__(self):
        return "<Screen(name=%s, id=%s)>" %(self.name, self.id)


    @staticmethod
    def getExistingScreens():
        """returns which screens are currently running

        Returns:
            array (Screen obj): an array of currently running screens 
                objects
        """
        try:
            out = subprocess.check_output(["screen", "-ls"])
        except subprocess.CalledProcessError:
            return {}

        # remove invisibles from output, and split lines  
        out = out.replace("\t", "~")
        out = out.replace("\r", "")
        out = out.split("\n")

        # keep only session names from output  
        out = out[1:-2]

        screen_list = []
        for i in out:
            # split session line into seperate components 
            # (identifier~date~status)
            i = i.split("~")
            for j in i:
                # sessions identifiers are written as id.name
                if "." in j:
                    s = j.split(".")
                    screen_list.append( Screen(name=s[1], id=s[0]) )

        return screen_list



def connectSession(name):
    """run screen command based on cli parameters

    Args:
        name (string or None): used defined session name, 
            can be None
        *args
        *kwargs

    Raises:
        TooManyScreensException: raised if name is None and there is
            more than 1 screen session opened
    """

    # create new screen if none exist
    # if no name and one screen, attach to it
    # if no name and multiple screens, raise error

    screens = Screen.getExistingScreens()
    if not name:
        if len(screens) == 0:
            s = Screen()
        elif len(screens) == 1:
            s = screens[0]
        else:
            raise TooManyScreensException(screens)
    else:
        s = Screen(name=name)

    s.run()


def printScreenList(screens):
    """
    print screen list on screen with list number
    for easy distinction (list numbers start
    from 1)

    Args:
        screens (array, Screen Obj): list of screen objects
            to list to to the user.
    """
    if len(screens) > 0:
        count = 1
        for s in screens:
            print("\t#%s %s (%s)" %(count, s.name, s.id))
            count += 1
    else:
        print("no open sessions")


def readUserInput(prompt):
    """read input from the user

    Args:
        prompt (string): the prompt to show user

    Raises:
        UnrecognisedSelectionException: if input is suspended
            by user
    """
    try:
        return raw_input(prompt)
    except (EOFError, KeyboardInterrupt):
        raise UnrecognisedSelectionException("Selection interrupted")


def readConfirmInput():
    """asks user for confirmation
    
    Returns:
        bool: True if user confirms, False if doesn't
    """
    try:
        result = readUserInput("(y/n): ")   # UnrecognisedSelectionException
        return 'y' in result[0].lower()     # IndexError
    except (UnrecognisedSelectionException, IndexError) as e:
        return False


def readSelectionInput(msg, screens):
    """read screen selection from user and
    return the selected screen

    Args:
        msg (string): message to show to user
        screens (array, Screen obj): array of screens for
            user to select from

    Returns:
        Screen (obj): returns the selected screen

    Raises:
        UnrecognisedSelectionException: if user 
            makes incorrect selection.
    """
    # don't run selection dialogue if less than 2 sessions running
    if len(screens) == 1:
        return screens[0]
    if len(screens) == 0:
        return None

    # print screen list for user
    print(msg)
    printScreenList(screens)

    # handle user input and determine selection
    sln = readUserInput("#: ")
    try:
        return screens[int(sln)-1]
    except IndexError as e:
        raise UnrecognisedSelectionException("Selection out of range")
    except (TypeError, ValueError):
        raise UnrecognisedSelectionException("Selection not recognised")


def listSessions():
    """list running screen session for user"""
    screens = Screen.getExistingScreens()
    printScreenList(screens)


def killSession(name=None):
    """allows user to kill running session
    
    Args:
        name (string, optional): name of session to kill, can be None to 
            show kill list prompt to user
    """
    screens = Screen.getExistingScreens()
    try:
        # if name is specified find proceed with that screen, 
        # else show prompt to user
        screen = None
        if name:
            for s in screens:
                if name == s.name:
                    screen = s
                    break
        if not screen:
            screen = readSelectionInput("Please enter session number to kill:", screens)

        if screen:
            print("Are you sure you want to kill session %s ?" %screen.name)
            if readConfirmInput():
                screen.kill()
                print("%s session killed" %screen.name)
            else:
                print("session kill aborted")
        else:
            print("No sessions found")

    except UnrecognisedSelectionException as e:
        print("Error: %s" %e)


def killAllSessions():
    """allows user to kill all running sessions"""
    screens = Screen.getExistingScreens()
    if len(screens) > 0:
        print("Are you sure you want to kill all sessions?")
        if readConfirmInput():
            for s in screens:
                s.kill()
            print("all sessions killed")
        else:
            print("session kill aborted")
    else:
        print("No sessions found")


def runConnect(name):
    """run screen connection function
    
    Args:
        name (string): session name of new or running session
    """
    try:
        connectSession(name=name)
    except TooManyScreensException as e:
        # when multiple screens running, have user select one
        try:
            screen = readSelectionInput("Please enter session number to reattach:", e.args[0])
            screen.run()
        except UnrecognisedSelectionException as e:
            print("Error: %s" %e)


def main(args):
    """runs functions based on argument and main
    function of connection to screen session

    Args:
        args (parser arguments): arguments provided by user when
            running the program
    """
    # list sessions - print list, quit early
    if args.list:
        listSessions()
        return

    # kill session - show list, then quit
    if args.kill:
        killSession(args.name)
        return

    # kill all sessions - ask for confirmation, then quit
    if args.killall:
        killAllSessions()
        return

    # connect to screen
    runConnect(args.name)



if __name__ == "__main__":

    # setup command line argument parser
    parser = argparse.ArgumentParser(description="Connect to GNU Screen")
    parser.add_argument("name", metavar="n", nargs="?", type=str, help="the name of screen session")
    parser.add_argument("-l", "--list", action="store_true", help="list all open sessions")
    parser.add_argument("-k", "--kill", action="store_true", help="kill a session")
    parser.add_argument("-K", "--killall", action="store_true", help="kill all sessions")
    args = parser.parse_args()

    main(args)


