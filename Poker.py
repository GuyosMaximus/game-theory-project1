import random

# קבועים עבור קלפים ופעולות
CARDS = ['Q', 'K', 'A']
CARD_RANKS = {'Q': 1, 'K': 2, 'A': 3}

# --- אסטרטגיית שיווי משקל נאש (GTO) ---
# פרמטר alpha של שחקן 1 (תדירות הבלוף עם Q בהימור פתיחה, נע בין 0 ל-1/3. נבחר 1/3)
ALPHA = 1 / 3


def get_gto_action(player, card, history):
    """
    מחזיר החלטה (check, bet, call, fold) לפי שיווי משקל נאש של Kuhn Poker.
    """
    rand = random.random()

    if player == 1:
        # החלטה ראשונה של שחקן 1
        if history == "":
            if card == 'Q':
                return 'b' if rand < ALPHA else 'p'  # בלוף בסיכוי alpha, אחרת Check (Pass)
            elif card == 'K':
                return 'p'  # תמיד Check
            elif card == 'A':
                return 'b' if rand < (3 * ALPHA) else 'p'  # הימור ערך (ב-alpha=1/3 מהמר ב-100%)

        # תגובת שחקן 1 לאחר ששחקן 2 הימר (היסטוריה: "p,b")
        elif history == "pb":
            if card == 'Q':
                return 'f'  # תמיד Fold
            elif card == 'K':
                return 'c' if rand < (ALPHA + 1 / 3) else 'f'  # קורא בתדירות מסוימת
            elif card == 'A':
                return 'c'  # תמיד Call

    elif player == 2:
        # תגובת שחקן 2 לשחקן 1 שעשה Check (היסטוריה: "p")
        if history == "p":
            if card == 'Q':
                return 'b' if rand < (1 / 3) else 'p'  # בלוף בעמדה בסיכוי 1/3
            elif card == 'K':
                return 'p'  # תמיד Check מאחור
            elif card == 'A':
                return 'b'  # תמיד Value Bet

        # תגובת שחקן 2 לשחקן 1 שהימר (היסטוריה: "b")
        elif history == "b":
            if card == 'Q':
                return 'f'  # תמיד Fold
            elif card == 'K':
                return 'c' if rand < (1 / 3) else 'f'  # Bluff Catch בסיכוי 1/3
            elif card == 'A':
                return 'c'  # תמיד Call

    return 'p'


def play_hand(human_player=None, verbose=True):
    """
    מריץ יד אחת של Kuhn Poker.
    אם human_player הוא 1 או 2, השחקן האנושי יתבקש להזין מהלך.
    אחרת שני השחקנים משחקים לפי GTO.
    מחזיר את הרווח/הפסד הנקי של שחקן 1 (Payoff לשחקן 1).
    """
    # שלב 1: ערבוב וחלוקת קלפים + Ante (1 לכל שחקן)
    deck = CARDS.copy()
    random.shuffle(deck)
    p1_card, p2_card = deck[0], deck[1]
    pot = 2
    history = ""

    if verbose:
        print("\n" + "=" * 35)
        print("--- יד חדשה ב-Kuhn Poker ---")
        if human_player == 1:
            print(f"הקלף שלך (שחקן 1): [{p1_card}]")
        elif human_player == 2:
            print(f"הקלף שלך (שחקן 2): [{p2_card}]")

    # שלב 2: תור שחקן 1
    if human_player == 1:
        p1_act = input("התור שלך (p = Check, b = Bet): ").strip().lower()
        while p1_act not in ['p', 'b']:
            p1_act = input("בחירה לא תקינה. הקלד p או b: ").strip().lower()
    else:
        p1_act = get_gto_action(player=1, card=p1_card, history=history)

    history += p1_act
    if verbose:
        print(f"שחקן 1 בחר: {'הימור (Bet)' if p1_act == 'b' else 'צ\'ק (Check)'}")

    # שלב 3: תור שחקן 2
    if p1_act == 'p':
        # שחקן 1 עשה Check
        if human_player == 2:
            p2_act = input("שחקן 1 עשה Check. התור שלך (p = Check, b = Bet): ").strip().lower()
            while p2_act not in ['p', 'b']:
                p2_act = input("בחירה לא תקינה. הקלד p או b: ").strip().lower()
        else:
            p2_act = get_gto_action(player=2, card=p2_card, history=history)

        history += p2_act
        if verbose:
            print(f"שחקן 2 בחר: {'הימור (Bet)' if p2_act == 'b' else 'צ\'ק (Check)'}")

        if p2_act == 'p':
            # שני השחקנים עשו Check -> Showdown
            pot = 2
            winner = 1 if CARD_RANKS[p1_card] > CARD_RANKS[p2_card] else 2
            payoff_p1 = 1 if winner == 1 else -1
            if verbose:
                print(f"-> Showdown! קלף שחקן 1: [{p1_card}], קלף שחקן 2: [{p2_card}]. מנצח: שחקן {winner}")
            return payoff_p1

        elif p2_act == 'b':
            # שחקן 2 הימר (שם 1 בקופה)
            pot = 3
            # תור שחקן 1 להגיב (Call או Fold)
            if human_player == 1:
                p1_resp = input("שחקן 2 הימר! התור שלך (c = Call, f = Fold): ").strip().lower()
                while p1_resp not in ['c', 'f']:
                    p1_resp = input("בחירה לא תקינה. הקלד c או f: ").strip().lower()
            else:
                p1_resp = get_gto_action(player=1, card=p1_card, history=history)

            history += p1_resp
            if verbose:
                print(f"שחקן 1 בחר: {'השוואה (Call)' if p1_resp == 'c' else 'קיפול (Fold)'}")

            if p1_resp == 'f':
                # שחקן 1 קיפל
                if verbose:
                    print("-> שחקן 1 קיפל. שחקן 2 גורף את הקופה!")
                return -1
            else:
                # שחקן 1 השווה (שם 1 בקופה) -> Showdown על קופה של 4
                winner = 1 if CARD_RANKS[p1_card] > CARD_RANKS[p2_card] else 2
                payoff_p1 = 2 if winner == 1 else -2
                if verbose:
                    print(f"-> Showdown! קלף שחקן 1: [{p1_card}], קלף שחקן 2: [{p2_card}]. מנצח: שחקן {winner}")
                return payoff_p1

    elif p1_act == 'b':
        # שחקן 1 הימר (שם 1 בקופה)
        pot = 3
        if human_player == 2:
            p2_resp = input("שחקן 1 הימר! התור שלך (c = Call, f = Fold): ").strip().lower()
            while p2_resp not in ['c', 'f']:
                p2_resp = input("בחירה לא תקינה. הקלד c או f: ").strip().lower()
        else:
            p2_resp = get_gto_action(player=2, card=p2_card, history=history)

        history += p2_resp
        if verbose:
            print(f"שחקן 2 בחר: {'השוואה (Call)' if p2_resp == 'c' else 'קיפול (Fold)'}")

        if p2_resp == 'f':
            if verbose:
                print("-> שחקן 2 קיפל. שחקן 1 גורף את הקופה!")
            return 1
        else:
            # שחקן 2 השווה (שם 1 בקופה) -> Showdown על קופה של 4
            winner = 1 if CARD_RANKS[p1_card] > CARD_RANKS[p2_card] else 2
            payoff_p1 = 2 if winner == 1 else -2
            if verbose:
                print(f"-> Showdown! קלף שחקן 1: [{p1_card}], קלף שחקן 2: [{p2_card}]. מנצח: שחקן {winner}")
            return payoff_p1


def run_simulation(num_hands=10000):
    """מריץ סימולציה של משחקי GTO זה מול זה לבדיקת תוחלת מתמטית"""
    print(f"\nמריץ סימולציה של {num_hands:,} ידיים (GTO מול GTO)...")
    total_p1_payoff = 0
    for _ in range(num_hands):
        total_p1_payoff += play_hand(human_player=None, verbose=False)

    avg_ev = total_p1_payoff / num_hands
    theoretical_ev = -1 / 18
    print(f"תוחלת שחקן 1 אמפירית: {avg_ev:.4f} יחידות ליד")
    print(f"תוחלת שחקן 1 תאורטית (-1/18): {theoretical_ev:.4f} יחידות ליד")


if __name__ == "__main__":
    print("ברוכים הבאים ל-Kuhn Poker!")
    mode = input(
        "בחר מצב:\n1 = שחק נגד הבוט (בתור שחקן 1)\n2 = שחק נגד הבוט (בתור שחקן 2)\n3 = הרץ סימולציית 10,000 ידיים לבדיקת תוחלת\nבחירה: ").strip()

    if mode == '1':
        play_hand(human_player=1)
    elif mode == '2':
        play_hand(human_player=2)
    elif mode == '3':
        run_simulation()