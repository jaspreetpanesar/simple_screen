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


class Screen(object):
    """used to interface with screen sessions

    Params:
        name (string): session name
    """

    def __init__(self, name):
        self.name = name


    def reattach(self):
        """reattach screen to running session"""
        print("reattaching to session '%s'" %self.name)
        self.runCmd("-r")


    def create(self):
        """create new session and attach"""
        print("creating new session '%s'" %self.name)
        self.runCmd("-S")


    def runCmd(self, args):
        """run screen command with required parameters and
        session name"""
        cmd = "screen " + args + " " +self.name
        os.system(cmd)


    def run(self):
        """used to run appropriate session connecting
        command based on name"""
        if Screen.doesExists(self.name):
            self.reattach()
        else:
            self.create()


    def __repr__(self):
        return "<Screen(name=%s)>" %(self.name)


    @staticmethod
    def doesExists(name):
        """returns if screen with name is 
        currently running.

        Args:
            name (str): the name of the screen session

        Returns:
            bool: if screen with session name is currently
                running
        """
        for i in Screen.getExistingScreens():
            if i["name"] == name:
                return True
        return False


    @staticmethod
    def getExistingScreens():
        """returns which screens are currently running

        Returns:
            dict (name, process_id): a dictionary of currently
                running screens identified with their name, and
                their process id
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
            # split session line into seperate components (identifier~date~status)
            i = i.split("~")
            for j in i:
                # sessions identifiers are written as id.name
                if "." in j:
                    s = j.split(".")
                    screen_list.append( {"id": s[0], "name": s[1]} )

        return screen_list



def main(name, *args, **kwargs):
    """run screen command based on cli parameters

    Args:
        name (string or None): used defined session name, can be None
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
            name = DEFAULT_SESSION_NAME
        elif len(screens) == 1:
            name = screens[0]["name"]
        else:
            raise TooManyScreensException(screens)

    s = Screen(name)
    s.run()


def printScreenList(screens):
    """
    print screen list on screen with list number
    for easy distinction (list numbers start
    from 1)
    """
    if len(screens) > 0:
        count = 1
        for i in screens:
            print("\t#%s %s" %(count,i["name"]))
            count += 1
    else:
        print("no open sessions")



if __name__ == "__main__":

    # setup arg parser
    parser = argparse.ArgumentParser(description="Connect to GNU Screen")
    parser.add_argument("name", metavar="n", nargs="?", type=str, help="the name of screen session")
    parser.add_argument("-l", action="store_true", help="list all open sessions")
    args = parser.parse_args()

    # show list, quit early
    if args.l:
        screens = Screen.getExistingScreens()
        printScreenList(screens)
        sys.exit()

    try:
        main(name=args.name)
    except TooManyScreensException as e:
        screens = e.args[0]
        # print screen list for user
        print("Please select session name when reattaching:")
        printScreenList(screens)

        # read selection from user
        sln = raw_input("#: ")
        try:
            main(name=screens[int(sln)-1]["name"])
        except IndexError:
            print("Error: Selection out of range")
        except (TypeError, ValueError):
            print("Error: Selection not recognised")

