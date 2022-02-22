#!/usr/bin/python
"""confirmation.py - this script contains functions for getting confirmation of
potentially dangerous actions.
"""

#------------------------------------------------------------------------------
# Configuration options
#------------------------------------------------------------------------------
# Synonyms for the word 'yes' in user input
YES_SYNONYMS = ['y', 'yes']

#------------------------------------------------------------------------------
# Key functions
#------------------------------------------------------------------------------
def simple_confirm(warning_str):
    """This function prints the warning string, following by "Continue? [y/N]".
    It returns True or False depending on whether the user typed 'y' or not.
    """
    message_str = warning_str + " Continue? [y/N]\n"
    result = raw_input(message_str)
    return (result.lower() in YES_SYNONYMS)

def keyword_confirm(warning_str, keyword):
    """This function prints the warning string, followed by a request to enter
    a keyword. This is modelled on the GitHub feature, where the user is asked
    to enter the full name of the repository before deleting it. It returns
    True or False depending on whether the user typed the correct keyword.
    """
    message_str = ''.join([
        warning_str.strip() + " ",
        "Type the string '%s' to continue, " % keyword.lower(),
        "followed by <ENTER>. Any other input will cancel the action.\n"
    ])
    result = raw_input(message_str)
    return (result == keyword)

def twostep_confirm(warning_str, keyword):
    """This function uses a simple y/n prompt, followed by a keyword prompt.
    It returns True or False depending on whether the user passed both prompts.
    """
    result1 = simple_confirm(warning_str)
    if not result1:
        return False

    result2 = keyword_confirm("Please confirm this action.", keyword)
    return result2
