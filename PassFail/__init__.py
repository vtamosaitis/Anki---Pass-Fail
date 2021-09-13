# Changed version of original add-on found here: https://github.com/lambdadog/passfail2/
#
# Another version can also be found in the PassFail.py section here: https://web.archive.org/web/20201112025532if_/https://massimmersionapproach.com/table-of-contents/anki/low-key-anki/low-key-anki-summary-and-installation/
#

from collections import defaultdict

from typing import Optional, Sequence
from anki.consts import CARD_TYPE_NEW, CARD_TYPE_REV, CARD_TYPE_LRN
from aqt.reviewer import Reviewer

BUTTON_LABEL =  { 
                    'NEW' : [
                        '<div font-family:Arial;">Again</div>',
                        '<div font-family:Arial;">Good</div>',
                        '<div font-family:Arial;">Easy</div>',
                    ],
                    'REV' : [
                        '<div font-family:Arial;">Fail</div>',
                        '<div font-family:Arial;">Pass</div>'
                    ]
                }

# Change Answer options to Again, Good, Easy for new cards and Pass/Fail for the rest.
# Changes the buttons on the GUI
def myAnswerButtonList(self):
    button_count = self.mw.col.sched.answerButtons(self.card)
    card_type = self.card.type  # set behavior by card type: CARD_TYPE_NEW, CARD_TYPE_LRN, CARD_TYPE_REV

    # New cards have easy button enabled to skip anki intervals
    # This is useful for me because it lets me set a big interval for cards of words I am already familiar with
    if self.card.type == CARD_TYPE_NEW:
        buttons_tuple: Tuple[Tuple[int, str], ...] = (
            (1, BUTTON_LABEL['NEW'][0]),
            (2, BUTTON_LABEL['NEW'][1]),
            (3, BUTTON_LABEL['NEW'][2]),
        )
        return buttons_tuple

    # Cards in the process of being learned and in review will follow the Pass/Fail behavior    
    buttons_tuple: Tuple[Tuple[int, str], ...] = (
        (1, BUTTON_LABEL['REV'][0]), 
        (2, BUTTON_LABEL['REV'][1]),
    )
    
    return buttons_tuple

# Remap keybindings guideline:
#   Ease levels are remapped such that the behavior is as you'd expect based on the options
#   'Again' maps to the 'Again' ease level, 'Good' to 'Good', and so on for New Cards
#   For cards that are not new, 'Fail' maps to 'Again' ease level, and 'Pass' maps to 'Good' ease level.
REMAP = defaultdict( lambda: 
    {
        2:  [1, 2],     # 1: Fail; 2: Pass
        3:  [1, 2],
        4:  [1, 3]
    }
)
REMAP[CARD_TYPE_NEW] = {
    4:  [1, 3, 4],   # 1: Again; 3: Good; 4: Easy
    3:  [1, 2, 3]
}

# Ease will correspond to the key pressed by happenstance, so we can remap the key to a new ease level.
# Nothing will happen if you press a key shortcut above the number of buttons available.
def myAnswerCard(self, ease):
    button_count = self.mw.col.sched.answerButtons(self.card)
    card_type = self.card.type
    
    # Simplify remappings by removing behavior from redundant keybindings:
    if card_type == CARD_TYPE_NEW and ease > 3:
        return
    elif card_type != CARD_TYPE_NEW and ease > 2:
        return
    
    # Look-up new ease level in REMAP:
    try:
        ease = REMAP[card_type][button_count][ease-1]
    except (KeyError, IndexError):
        pass
        
    _oldAnswerCard(self, ease)

# Fix time interval displayed above buttons:
def myButtonTime(self, i: int, v3_labels: Optional[Sequence[str]] = None) -> str:
    button_count = self.mw.col.sched.answerButtons(self.card)
    card_type = self.card.type
    ease = i
    
    # Look-up new ease level in REMAP:
    try:
        ease = REMAP[card_type][button_count][ease-1]
    except (KeyError, IndexError):
        pass
    
    return _oldButtonTime(self, ease, v3_labels=v3_labels)

_oldButtonTime = Reviewer._buttonTime   
Reviewer._buttonTime = myButtonTime
_oldAnswerCard = Reviewer._answerCard
Reviewer._answerCard = myAnswerCard
_oldButtonList = Reviewer._answerButtonList
Reviewer._answerButtonList = myAnswerButtonList
