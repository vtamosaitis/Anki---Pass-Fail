# Changed version of original add-on found here: https://github.com/lambdadog/passfail2/
#
# Another version can also be found in the PassFail.py section here: https://web.archive.org/web/20201112025532if_/https://massimmersionapproach.com/table-of-contents/anki/low-key-anki/low-key-anki-summary-and-installation/
#

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
    card_type = self.card.type  # set behavior by card type: CARD_TYPE_NEW, CARD_TYPE_LRN, CARD_TYPE_REV

    # New cards have easy button enabled to skip anki intervals
    # This is useful for me because it lets me set a big interval for cards of words I am already familiar with
    if self.card.type == CARD_TYPE_NEW:
        buttons_tuple: Tuple[Tuple[int, str], ...] = (
            (1, BUTTON_LABEL['NEW'][0]),
            (3, BUTTON_LABEL['NEW'][1]),
            (4, BUTTON_LABEL['NEW'][2]),
        )
        return buttons_tuple

    # Cards in the process of being learned and in review will follow the Pass/Fail behavior
    button_count = self.mw.col.sched.answerButtons(self.card)
    
    buttons_tuple: Tuple[Tuple[int, str], ...] = ((1, BUTTON_LABEL['REV'][0]),)
    if button_count == 4:
        buttons_tuple += ((3, BUTTON_LABEL['REV'][1]),)
    else:
        buttons_tuple += ((2, BUTTON_LABEL['REV'][1]),)
    
    return buttons_tuple

# Remap keybindings:
# 	Ease levels are remapped such that the behavior is as you'd expect based on the options
#	'Again' maps to the 'Again' ease level, 'Good' to 'Good', and so on for New Cards
#	For cards that are not new, 'Fail' maps to 'Again' ease level, and 'Pass' maps to 'Good' ease level.
REMAP = {
            CARD_TYPE_NEW : {
                4:  [1, 3, 4]	# 1: Again; 3: Good; 4: Easy
            },
            CARD_TYPE_REV : {
                2:  [1, 2],		# 1: Fail; 2: Pass
                3:  [1, 2],
                4:  [1, 3]
            },
            CARD_TYPE_LRN : {
                2:  [1, 2],		# 1: Fail; 2: Pass
                3:  [1, 2],
                4:  [1, 3]
            }
}

# Ease will correspond to the key pressed by happenstance, so we can remap the key to a new ease level.
# Remappings are done in REMAP. 
# Nothing will happen if you press a key above the number of buttons available.
def myAnswerCard(self, ease):
    card_type = self.card.type
	
	# Simplify remappings by removing behavior from redundant keybindings:
    if card_type == CARD_TYPE_NEW and ease > 3:
        return
    elif card_type != CARD_TYPE_NEW and ease > 2:
        return
	
    # Look-up new ease level in REMAP:
    button_count = self.mw.col.sched.answerButtons(self.card)
    try:
        ease = REMAP[card_type][button_count][ease-1]
    except (KeyError, IndexError):
        pass
        
    _originalAnswerCard(self, ease)
    
    

_originalAnswerCard = Reviewer._answerCard
Reviewer._answerCard = myAnswerCard
_newCardButtonList = Reviewer._answerButtonList
Reviewer._answerButtonList = myAnswerButtonList