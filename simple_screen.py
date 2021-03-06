"""
**Simple Screen**

A wrapper around screen GNU to simplify starting and resuming
screen sessions.
"""

import os
import sys
import argparse
import subprocess
import difflib


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

class ScreenSessionUnreachableException(Exception):
    """exception to identify if screen session is 
    unreachable when trying to connect to it"""
    pass

class ScreenConnectionFailedException(Exception):
    """exception to identify if screen session could
    not be created or connected to"""
    pass

class IncorrectSessionName(Exception):
    """exception to identify if session name provided
    by user does not match required criteria"""
    pass

class NoConnectedSessions(Exception):
    """exception to identify no attached screen 
    session""" 
    pass


class Screen(object):
    """used to interface with screen sessions

    Params:
        name (string, optional): session name, defaults 
            to DEFAULT_SESSION_NAME
        id (string, optional): screen session id
        status (string, optional): status of screen (used to determine status value, stored
            as constant int)
    """

    UNKNOWN = 0
    ATTACHED = 1
    DETACHED = 2
    MULTI = 3
    UNREACHABLE = 4
    DEAD = 5

    STATUSES = ["unknown", "attached", "detached", "multi", "unreachable", "dead"]

    def __init__(self, name=DEFAULT_SESSION_NAME, id=None, status=None):
        self.name = name
        self.id = id

        if status:
            self.status = Screen.STATUSES.index(difflib.get_close_matches(status, 
                    Screen.STATUSES)[0])
        else:
            self.status = Screen.UNKNOWN


    def create(self):
        """creates new screen session and detaches from it"""
        os.system("screen -d -m %s" %self.name)


    def connect(self):
        """connect to screen with name, detach if necessary,
        create new if necessary

        Raises:
            ScreenSessionUnreachableException: if connection to screen
                cannot be made.
        """

        # if status unknown use only name to connect, else use
        # both id.name 

        if self.status == Screen.UNKNOWN:
            os.system("screen -D -R %s" %self.name)
        elif self.status not in [Screen.UNREACHABLE, Screen.DEAD]:
            os.system("screen -D -R %s.%s" %(self.id, self.name))
        else:
            raise ScreenSessionUnreachableException


    def kill(self):
        """kill the screen session"""
        # wipe if dead, quit if running
        if self.status in [Screen.DEAD, Screen.UNREACHABLE]:
            os.system("screen -wipe %s.%s" %(self.id, self.name)) 
        else:
            os.system("screen -X -S %s quit" %self.id)


    def run(self):
        """use correct connection command depending on status of
        screen session
        
        Raises:
            ScreenConnectionFailedException: if screen session had
                to be wiped due to dead or unreachable session.
        """
        if self.status == Screen.UNKNOWN:
            self.create()
        elif self.status in [Screen.DEAD, Screen.UNREACHABLE]:
            self.kill()
            raise ScreenConnectionFailedException(
                    "Unreachable session has been wiped. "
                    "Please try connecting again"
                    )
        self.connect()


    def getStatus(self):
        """returns the string representation of screen 
        status value
        
        Returns:
            String: human readable session status.
        """
        return Screen.STATUSES[self.status]

    
    def getStatusIcon(self):
        """returns the icon represetation of screen
        status value

        Returns:
            String: icon representation of status
        """
        try:
            return ["?", ">", "#", ">", "?", "X"][self.status]
        except IndexError:
            return "?"


    def __repr__(self):
        return "<Screen(name=%s, id=%s, status=%s)>" %(self.name, self.id, 
                                            self.getStatus())


    @staticmethod
    def getExistingScreens():
        """returns which screens are currently running

        Returns:
            array (Screen obj): an array of currently running screens 
                objects.
        """
        try:
            out = subprocess.check_output(["screen", "-ls"])
        except subprocess.CalledProcessError:
            return []

        # remove invisibles from output, and split lines  
        out = out.replace("\t", "~")
        out = out.replace("\r", "")
        out = out.split("\n")

        # remove header and footer - keep only session list
        out = out[1:-2]

        screen_list = []
        for i in out:
            # split session line into components (''~identifier~date~status)
            i = i.split("~")

            try:
                # split id and name by period
                vals = i[1].split(".")
                id = vals[0]
                # join remaining name using periods which existed before split
                name = ".".join(vals[1:])
            except Exception as e:
                print("Error: %s" %e)
                continue

            status = i[3].replace("(","").replace(")","").lower()
            screen_list.append( Screen(name=name, id=id, status=status) )

        return screen_list


    @staticmethod
    def changeDirectory(newdir):
        """changes the screens default directory to 
        specified directory
        
        Args:
            dirc (string): string directory path
        
        Raises:
            NoConnectedSessions: currently not connected to
                any screen sessions.
        """
        if Screen.inSession():
            os.system("screen -X chdir '%s'" %newdir)
        else:
            raise NoConnectedSessions("Not in screen session")


    @staticmethod
    def inSession():
        """returns weather currently attached to a screen
        session
        
        Returns:
            bool: True if in session, False if not
        """
        # $STY stores current screen session
        try:
            return os.environ["STY"] != ""
        except KeyError as e:
            return False


    @staticmethod
    def getCurrentSession():
        """returns current sessions screen object
        
        Returns:
            Screen (obj): the currently connected session
        
        Raises:
            NoConnectedSessions: if no attached session
        """
        if Screen.inSession():
            session = os.environ["STY"]
            id, name = session.split(".")
            return Screen(name=name, id=id, status="attached")
        else:
            raise NoConnectedSessions("Not in screen session")



def connectSession(name):
    """run screen command based on cli parameters

    Args:
        name (string or None): used defined session name, 
            can be None

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

    try:
        s.run()
    except ScreenConnectionFailedException as e:
        print("Error: %s" %e)



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
            print("    %s%s %s (%s)" %(s.getStatusIcon(), count, s.name, s.id))
            count += 1
    else:
        print("no open sessions")


def readUserInput(prompt):
    """read input from the user

    Args:
        prompt (string): the prompt to show user

    Returns:
        string: user input

    Raises:
        UnrecognisedSelectionException: if input is suspended
            by user
    """
    try:
        return raw_input(prompt)
    except (EOFError, KeyboardInterrupt):
        raise UnrecognisedSelectionException("Input interrupted")


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

    Raises:
        IncorrectSessionName: if session name begins with numeric character
    """
    if name and len(name) > 0 and name[0].isdigit():
        raise IncorrectSessionName("session name must not begin with numeric character")

    try:
        connectSession(name=name)
    except TooManyScreensException as e:
        # when multiple screens running, have user select one
        try:
            screen = readSelectionInput("Please enter session number to reattach:", e.args[0])
            screen.run()
        except (UnrecognisedSelectionException, ScreenConnectionFailedException) as e:
            print("Error: %s" %e)


def updateDirectory(newdir=None):
    """update the default directory of the current
    screen session
    
    Args:
        newdir (string, optional): specifies the new directory
            if no directory provided, uses current directory
    """
    try:
        if not newdir:
            newdir = os.environ["PWD"]
        else:
            newdir = os.path.abspath(os.path.realpath(newdir))
        if not os.path.isdir(newdir):
            raise ValueError("Directory does not exist")
        Screen.changeDirectory(newdir)
        print("Success: directory changed to '%s'" %newdir) 
    except KeyError:
        print("Error: could not get current directory")
    except (ValueError, NoConnectedSessions) as e:
        print("Error: %s" %e)


def detachSession(session=None):
    """detaches from a screen session
    
    Args:
        name (string, optional): the name of the session
            to detach from. If none provided, uses currently
            attached session
    """
    if not session:
        try:
            session = Screen.getCurrentSession()
        except NoConnectedSessions as e:
            print("Error: %s" %e)
            return
    os.system("screen -D %s.%s" %(session.id, session.name))


def main(args):
    """runs functions based on argument and main
    function of connection to screen session

    Args:
        args (parser arguments): arguments provided by user when
            running the program
    """
    # detach from current session
    if args.detach:
        detachSession()
        return

    # set default directory to specified
    if args.changeDirectory:
        updateDirectory(args.changeDirectory)
        return

    # set default directory to current
    if args.directory:
        updateDirectory()
        return

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
    try:
        runConnect(args.name)
    except IncorrectSessionName as e:
        print("Error: %s" %e)



if __name__ == "__main__":

    # setup command line argument parser
    parser = argparse.ArgumentParser(description="Connect to GNU Screen")
    parser.add_argument("name", metavar="n", nargs="?", type=str, help="the name of screen session")
    parser.add_argument("-l", "--list", action="store_true", help="list all open sessions")
    parser.add_argument("-k", "--kill", action="store_true", help="kill a session")
    parser.add_argument("-K", "--killall", action="store_true", help="kill all sessions")
    parser.add_argument("-d", "--directory", action="store_true", help="set current directory as main directory")
    parser.add_argument("-cd", "--changeDirectory", type=str, help="set directory to provided value")
    parser.add_argument("-x", "--detach", action="store_true", help="detaches from current session")
    args = parser.parse_args()

    main(args)


