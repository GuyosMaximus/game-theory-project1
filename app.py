import streamlit as st
import streamlit.components.v1 as components
import random

st.set_page_config(
    page_title="Kuhn Poker GTO Table",
    page_icon="♠️",
    layout="wide"
)

# --- עיצוב ממשק, כפתורי קזינו וסרגל צד ב-CSS ---
st.markdown("""
<style>
    .stApp {
        direction: rtl;
    }

    /* מירכוז וריווח תיבת הפעולות הראשית */
    div[data-testid="stHorizontalBlock"] {
        max-width: 520px !important;
        margin: 5px auto 20px auto !important;
        gap: 20px !important;
    }

    /* כפתורי הפוקר בשולחן */
    .stButton > button {
        height: 58px !important;
        border-radius: 30px !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        font-size: 19px !important;
        font-weight: 800 !important;
        letter-spacing: 0.5px !important;
        border: none !important;
        color: white !important;
        cursor: pointer !important;
        transition: all 0.15s ease-in-out !important;
    }

    /* כפתור ימני (Check / Call / Next Hand) - ירוק זוהר */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) .stButton > button {
        background: linear-gradient(180deg, #2ecc71 0%, #27ae60 100%) !important;
        box-shadow: 0 6px 0 #1e8449, 0 10px 15px rgba(0,0,0,0.3) !important;
        border-top: 1px solid #a9dfbf !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) .stButton > button:hover {
        background: linear-gradient(180deg, #34d677 0%, #2ecc71 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 0 #1e8449, 0 12px 18px rgba(0,0,0,0.35) !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) .stButton > button:active {
        transform: translateY(4px) !important;
        box-shadow: 0 2px 0 #1e8449, 0 4px 6px rgba(0,0,0,0.2) !important;
    }

    /* כפתור שמאלי (Bet / Fold) - כתום-זהב / אדום */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton > button {
        background: linear-gradient(180deg, #f39c12 0%, #d68910 100%) !important;
        box-shadow: 0 6px 0 #b7790b, 0 10px 15px rgba(0,0,0,0.3) !important;
        border-top: 1px solid #f9e79f !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton > button:hover {
        background: linear-gradient(180deg, #f5b041 0%, #f39c12 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 0 #b7790b, 0 12px 18px rgba(0,0,0,0.35) !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton > button:active {
        transform: translateY(4px) !important;
        box-shadow: 0 2px 0 #b7790b, 0 4px 6px rgba(0,0,0,0.2) !important;
    }

    /* עיצוב כפתור איפוס משחק בסרגל הצד */
    section[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(180deg, #c0392b 0%, #962d22 100%) !important;
        box-shadow: 0 4px 0 #78241b, 0 6px 12px rgba(0,0,0,0.2) !important;
        color: #ffffff !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        height: 44px !important;
        border-radius: 12px !important;
        border: none !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(180deg, #d9534f 0%, #c0392b 100%) !important;
        box-shadow: 0 5px 0 #78241b, 0 8px 14px rgba(0,0,0,0.3) !important;
        transform: translateY(-1px) !important;
    }
    section[data-testid="stSidebar"] .stButton > button:active {
        transform: translateY(2px) !important;
        box-shadow: 0 1px 0 #78241b !important;
    }

    /* יישור סרגל צד לימין */
    section[data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# קבועים
CARDS = ['Q', 'K', 'A']
CARD_INFO = {
    'Q': {'rank': 'Q', 'suit': '♦', 'color': '#d32f2f', 'icon': '👸', 'name': 'מלכה'},
    'K': {'rank': 'K', 'suit': '♣', 'color': '#111111', 'icon': '🤴', 'name': 'מלך'},
    'A': {'rank': 'A', 'suit': '♠', 'color': '#111111', 'icon': '🅰️', 'name': 'אס'},
}
CARD_RANKS = {'Q': 1, 'K': 2, 'A': 3}
ALPHA = 1 / 3


def get_card_html(card_code, face_up=True, is_peeked=False):
    """מייצר קוד HTML לקלף גלוי, הפוך או במצב הצצה (Peek)"""
    if not face_up:
        return """
        <div style="display:inline-block; width:120px; height:175px; background:repeating-linear-gradient(45deg,#8b0000,#8b0000 12px,#5c0000 12px,#5c0000 24px); border:4px solid #ffffff; border-radius:12px; box-shadow:0 8px 20px rgba(0,0,0,0.45); text-align:center; line-height:175px; font-size:38px; color:#ffcccc;">
            ♠️
        </div>
        """
    info = CARD_INFO[card_code]
    border_style = "3px dashed #ffd54f" if is_peeked else "1px solid #ddd"
    opacity_style = "opacity: 0.9;" if is_peeked else ""
    badge_html = "<div style='position:absolute; top:-10px; left:50%; transform:translateX(-50%); background:#f39c12; color:black; font-size:11px; font-weight:bold; padding:2px 8px; border-radius:10px;'>👁️ מצב לימוד</div>" if is_peeked else ""

    return f"""
    <div style="display:inline-block; width:120px; height:175px; background:#ffffff; border-radius:12px; box-shadow:0 8px 20px rgba(0,0,0,0.45); position:relative; font-family:sans-serif; color:{info['color']}; border:{border_style}; {opacity_style}">
        {badge_html}
        <div style="position:absolute; top:8px; right:10px; font-size:22px; font-weight:bold; line-height:1;">
            {info['rank']}<br><span style="font-size:16px;">{info['suit']}</span>
        </div>
        <div style="position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); font-size:46px;">
            {info['icon']}
        </div>
        <div style="position:absolute; bottom:8px; left:10px; font-size:22px; font-weight:bold; line-height:1; transform:rotate(180deg);">
            {info['rank']}<br><span style="font-size:16px;">{info['suit']}</span>
        </div>
    </div>
    """


def get_gto_action(player, card, history):
    rand = random.random()
    if player == 1:
        if history == "":
            if card == 'Q':
                return 'b' if rand < ALPHA else 'p'
            elif card == 'K':
                return 'p'
            elif card == 'A':
                return 'b' if rand < (3 * ALPHA) else 'p'
        elif history == "pb":
            if card == 'Q':
                return 'f'
            elif card == 'K':
                return 'c' if rand < (ALPHA + 1 / 3) else 'f'
            elif card == 'A':
                return 'c'
    elif player == 2:
        if history == "p":
            if card == 'Q':
                return 'b' if rand < (1 / 3) else 'p'
            elif card == 'K':
                return 'p'
            elif card == 'A':
                return 'b'
        elif history == "b":
            if card == 'Q':
                return 'f'
            elif card == 'K':
                return 'c' if rand < (1 / 3) else 'f'
            elif card == 'A':
                return 'c'
    return 'p'


def reset_hand():
    deck = CARDS.copy()
    random.shuffle(deck)
    st.session_state.deck = deck
    st.session_state.p1_card = deck[0]
    st.session_state.p2_card = deck[1]
    st.session_state.history = ""
    st.session_state.game_over = False
    st.session_state.result_message = ""
    st.session_state.p1_payoff = 0
    st.session_state.bot_action_log = "יד חדשה החלה. כל שחקן שם 1 ₪ Ante."


# אתחול State
if 'score_human' not in st.session_state:
    st.session_state.score_human = 0
    st.session_state.score_bot = 0
    st.session_state.hands_played = 0
    st.session_state.current_human_position = 1
    reset_hand()

# סרגל צד מעוצב
with st.sidebar:
    st.markdown("<h2 style='text-align: right; margin-bottom: 10px;'>⚙️ הגדרות שולחן</h2>", unsafe_allow_html=True)

    # מצב לימוד
    peek_mode = st.toggle("👁️ מצב לימוד (חשוף קלף בוט)", value=False)

    # כרטיסיית עמדה נוכחית
    st.markdown("---")
    pos_num = st.session_state.current_human_position
    pos_title = "שחקן 1 (מדבר ראשון)" if pos_num == 1 else "שחקן 2 (כפתור / Button)"
    pos_badge_color = "#3498db" if pos_num == 1 else "#e67e22"

    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.15); border-radius: 10px; padding: 12px; margin-bottom: 12px;">
        <div style="font-size: 13px; color: #888;">עמדה ביד זו:</div>
        <div style="font-size: 16px; font-weight: bold; color: {pos_badge_color}; margin: 4px 0;">{pos_title}</div>
        <div style="font-size: 12px; color: #777;">מתחלף אוטומטית בכל סיבוב 🔄</div>
    </div>
    """, unsafe_allow_html=True)

    # מאזן תוצאות צבעוני
    st.markdown("---")
    st.markdown("<h4 style='margin-bottom: 8px;'>📊 לוח תוצאות חי</h4>", unsafe_allow_html=True)

    user_score = st.session_state.score_human
    bot_score = st.session_state.score_bot

    user_delta = f"{user_score:+} ₪" if user_score != 0 else "0 ₪"
    bot_delta = f"{bot_score:+} ₪" if bot_score != 0 else "0 ₪"

    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        st.metric(
            label="הרווח שלך",
            value=f"{user_score:+} ₪",
            delta=user_delta,
            delta_color="normal"
        )
    with col_sb2:
        st.metric(
            label="מאזן בוט (GTO)",
            value=f"{bot_score:+} ₪",
            delta=bot_delta,
            delta_color="inverse"
        )

    st.caption(f"🏁 סך ידיים ששוחקו: **{st.session_state.hands_played}**")
    st.markdown("<br>", unsafe_allow_html=True)

    # כפתור איפוס בולט ואדום
    if st.button("🗑️ איפוס משחק מלא", use_container_width=True):
        st.session_state.score_human = 0
        st.session_state.score_bot = 0
        st.session_state.hands_played = 0
        st.session_state.current_human_position = 1
        reset_hand()
        st.rerun()

# חישוב קופה נוכחית
pot = 2
if 'b' in st.session_state.history:
    pot += 1
if st.session_state.history in ['bc', 'pbc']:
    pot += 1

# כותרת ממורכזת
st.markdown(
    "<h2 style='text-align: center; direction: rtl; margin-bottom: 5px;'>♠️ שולחן פוקר קון — Kuhn Poker GTO ♣️</h2>",
    unsafe_allow_html=True)

# קביעת קלפים לפי העמדה
human_pos = st.session_state.current_human_position
if human_pos == 1:
    user_card = st.session_state.p1_card
    bot_card = st.session_state.p2_card
    bot_label = "יריב (בוט GTO - שחקן 2)"
    user_label = "אתה (שחקן 1 - פועל ראשון)"
else:
    user_card = st.session_state.p2_card
    bot_card = st.session_state.p1_card
    bot_label = "יריב (בוט GTO - שחקן 1 - פועל ראשון)"
    user_label = "אתה (שחקן 2 - בעמדה)"

bot_face_up = st.session_state.game_over or peek_mode
is_bot_peeked = peek_mode and not st.session_state.game_over

bot_card_rendered = get_card_html(bot_card, face_up=bot_face_up, is_peeked=is_bot_peeked)
user_card_rendered = get_card_html(user_card, face_up=True)

table_code = f"""
<!DOCTYPE html>
<html dir="rtl">
<head>
<meta charset="utf-8">
</head>
<body style="margin:0; background:transparent; font-family:system-ui, -apple-system, sans-serif;">
    <div style="background: radial-gradient(ellipse at center, #1e6b3b 0%, #0d4222 75%, #082814 100%); border: 15px solid #382012; border-radius: 90px; box-shadow: inset 0 0 50px rgba(0,0,0,0.85), 0 12px 30px rgba(0,0,0,0.45); padding: 30px 20px; max-width: 880px; margin: 0 auto; text-align: center; color: white;">

        <!-- בוט -->
        <div style="font-size: 17px; font-weight: 500; margin-bottom: 12px; color: #cfd8dc;">🤖 {bot_label}</div>
        <div>{bot_card_rendered}</div>

        <!-- קופה והודעות -->
        <div style="margin: 22px 0;">
            <div style="background: rgba(0,0,0,0.55); border: 2px dashed #ffd54f; border-radius: 25px; display: inline-block; padding: 8px 28px; font-size: 24px; font-weight: bold; color: #ffe082; box-shadow: 0 4px 10px rgba(0,0,0,0.3);">
                💰 קופה (Pot): {pot} ₪
            </div>
            <div style="font-size: 15px; margin-top: 8px; color: #eceff1;">
                {st.session_state.bot_action_log}
            </div>
        </div>

        <!-- שחקן -->
        <div>{user_card_rendered}</div>
        <div style="font-size: 18px; margin-top: 12px; font-weight: bold; color: #a5d6a7;">👤 {user_label}</div>
    </div>
</body>
</html>
"""

components.html(table_code, height=620)

history = st.session_state.history

# אם אתה שחקן 2 והיד רק התחילה -> הבוט פועל מיד
if human_pos == 2 and history == "" and not st.session_state.game_over:
    bot_act = get_gto_action(1, st.session_state.p1_card, "")
    st.session_state.history = bot_act
    if bot_act == 'p':
        st.session_state.bot_action_log = "הבוט בחר: **צ'ק (Check)** ✋. התור שלך לפעול!"
    else:
        st.session_state.bot_action_log = "הבוט בחר: **הימור (Bet 1 ₪)** 💰. מה תעשה?"
    st.rerun()

# --- כפתורי פעולה ---
if human_pos == 1 and history == "" and not st.session_state.game_over:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("CHECK  ✋", use_container_width=True):
            bot_act = get_gto_action(2, st.session_state.p2_card, "p")
            if bot_act == 'p':
                p1_wins = CARD_RANKS[st.session_state.p1_card] > CARD_RANKS[st.session_state.p2_card]
                st.session_state.p1_payoff = 1 if p1_wins else -1
                st.session_state.game_over = True
                st.session_state.bot_action_log = "שני השחקנים ביצעו Check -> Showdown!"
                st.session_state.result_message = "ניצחת ב-Showdown (+1 ₪)!" if p1_wins else "הבוט ניצח ב-Showdown (-1 ₪)."
            else:
                st.session_state.history = "pb"
                st.session_state.bot_action_log = "הבוט הימר (Bet 1 ₪) בתגובה ל-Check שלך!"
            st.rerun()
    with col2:
        if st.button("BET 1₪  🪙", use_container_width=True):
            bot_resp = get_gto_action(2, st.session_state.p2_card, "b")
            if bot_resp == 'f':
                st.session_state.p1_payoff = 1
                st.session_state.game_over = True
                st.session_state.bot_action_log = "הבוט קיפל (Fold)!"
                st.session_state.result_message = "הבוט קיפל! לקחת את הקופה (+1 ₪)."
            else:
                p1_wins = CARD_RANKS[st.session_state.p1_card] > CARD_RANKS[st.session_state.p2_card]
                st.session_state.p1_payoff = 2 if p1_wins else -2
                st.session_state.game_over = True
                st.session_state.bot_action_log = "הבוט השווה (Call) -> Showdown!"
                st.session_state.result_message = "Showdown: ניצחת (+2 ₪)!" if p1_wins else "Showdown: הבוט ניצח (-2 ₪)."
            st.rerun()

elif human_pos == 1 and history == "pb" and not st.session_state.game_over:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("CALL 1₪  ⚔️", use_container_width=True):
            p1_wins = CARD_RANKS[st.session_state.p1_card] > CARD_RANKS[st.session_state.p2_card]
            st.session_state.p1_payoff = 2 if p1_wins else -2
            st.session_state.game_over = True
            st.session_state.bot_action_log = "השווית (Call) -> Showdown!"
            st.session_state.result_message = "קריאה מוצלחת! ניצחת (+2 ₪)!" if p1_wins else "הבוט היה עם יד חזקה יותר (-2 ₪)."
            st.rerun()
    with col2:
        if st.button("FOLD  🏳️", use_container_width=True):
            st.session_state.p1_payoff = -1
            st.session_state.game_over = True
            st.session_state.bot_action_log = "קיפלת (Fold)."
            st.session_state.result_message = "קיפלת. הפסד האנטה (-1 ₪)."
            st.rerun()

elif human_pos == 2 and history == "p" and not st.session_state.game_over:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("CHECK  ✋", use_container_width=True):
            p1_wins = CARD_RANKS[st.session_state.p1_card] > CARD_RANKS[st.session_state.p2_card]
            st.session_state.p1_payoff = 1 if p1_wins else -1
            st.session_state.game_over = True
            st.session_state.bot_action_log = "Check-Check -> Showdown!"
            st.session_state.result_message = "ניצחת ב-Showdown (+1 ₪)!" if not p1_wins else "הבוט ניצח ב-Showdown (-1 ₪)."
            st.rerun()
    with col2:
        if st.button("BET 1₪  🪙", use_container_width=True):
            bot_resp = get_gto_action(1, st.session_state.p1_card, "pb")
            if bot_resp == 'f':
                st.session_state.p1_payoff = -1
                st.session_state.game_over = True
                st.session_state.bot_action_log = "הבוט קיפל (Fold)!"
                st.session_state.result_message = "הימור מוצלח בעמדה! הבוט קיפל (+1 ₪)."
            else:
                p1_wins = CARD_RANKS[st.session_state.p1_card] > CARD_RANKS[st.session_state.p2_card]
                st.session_state.p1_payoff = 2 if p1_wins else -2
                st.session_state.game_over = True
                st.session_state.bot_action_log = "הבוט השווה (Call) -> Showdown!"
                st.session_state.result_message = "ניצחת ב-Showdown (+2 ₪)!" if not p1_wins else "הבוט תפס אותך (-2 ₪)."
            st.rerun()

elif human_pos == 2 and history == "b" and not st.session_state.game_over:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("CALL 1₪  ⚔️", use_container_width=True):
            p1_wins = CARD_RANKS[st.session_state.p1_card] > CARD_RANKS[st.session_state.p2_card]
            st.session_state.p1_payoff = 2 if p1_wins else -2
            st.session_state.game_over = True
            st.session_state.bot_action_log = "השווית (Call) -> Showdown!"
            st.session_state.result_message = "קריאה מוצלחת! ניצחת (+2 ₪)!" if not p1_wins else "לבוט היה קלף חזק יותר (-2 ₪)."
            st.rerun()
    with col2:
        if st.button("FOLD  🏳️", use_container_width=True):
            st.session_state.p1_payoff = 1
            st.session_state.game_over = True
            st.session_state.bot_action_log = "קיפלת (Fold)."
            st.session_state.result_message = "קיפלת (-1 ₪)."
            st.rerun()

# סיום יד והחלפת עמדות
if st.session_state.game_over:
    payoff_user = st.session_state.p1_payoff if human_pos == 1 else -st.session_state.p1_payoff

    st.markdown("<div style='max-width: 520px; margin: 15px auto;'>", unsafe_allow_html=True)
    if payoff_user > 0:
        st.success(f"### 🎉 {st.session_state.result_message}")
    elif payoff_user < 0:
        st.error(f"### 💀 {st.session_state.result_message}")
    st.markdown("</div>", unsafe_allow_html=True)

    col_single = st.columns([1, 2, 1])
    with col_single[1]:
        if st.button("NEXT HAND ➡️", use_container_width=True):
            st.session_state.score_human += payoff_user
            st.session_state.score_bot -= payoff_user
            st.session_state.hands_played += 1
            st.session_state.current_human_position = 2 if human_pos == 1 else 1
            reset_hand()
            st.rerun()