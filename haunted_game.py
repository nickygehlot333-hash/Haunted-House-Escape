"""HAUNTED HOUSE ESCAPE - open in IDLE and press F5 (Run Module).
Keep story.html in the same folder: the in-game Diary button opens it."""
import tkinter as tk, random, math, pathlib, webbrowser

W, H, NEED = 800, 600, 5
BG, INK, BLOOD = "#050508", "#d9d0b8", "#b01818"
EXIT = ("Secret Room", "Final Door")
ROOMS = {
    "library": "You found an old book.",
    "kitchen": "You found a rusty knife.",
    "bedroom": "You found a mysterious painting.",
    "basement": "It is cold and damp. Something drips in the dark.",
    "attic": "Dusty boxes and cobwebs fill the room.",
    "dining room": "A long table is set for guests who never came.",
    "garden": "Dead flowers and a broken fountain surround you.",
}
ITEMS = {"library": "Old Book", "kitchen": "Rusty Knife", "bedroom": "Mysterious Painting",
         "basement": "Cracked Lantern", "attic": "Silver Locket",
         "dining room": "Tarnished Spoon", "garden": "Fountain Coin"}
RIDDLES = [
    ("I have keys but no locks. I have space but no room. What am I?", "keyboard"),
    ("I have hands but I cannot clap. What am I?", "clock"),
    ("The more you take, the more you leave behind. What am I?", "footsteps"),
    ("I speak without a mouth and hear without ears. What am I?", "echo"),
    ("What has to be broken before you can use it?", "egg"),
    ("I am tall when I am young and short when I am old. What am I?", "candle"),
    ("The more it gets wetter the more it makes you dry. who am I?", "towel"),
    ("What can you catch but never throw?", "cold"),
]
THEME = {"library": "#2a1c12", "kitchen": "#1e2a26", "bedroom": "#2a1a2e", "basement": "#141c26",
         "attic": "#2a2618", "dining room": "#2e1414", "garden": "#0e1e12"}
PROPS = {"kitchen": [(450, 290, 780, 340, "#4a4a4a"), (480, 340, 500, 420, "#333"), (730, 340, 750, 420, "#333")],
         "bedroom": [(450, 260, 780, 330, "#4a2030"), (450, 230, 480, 400, "#2a1018")],
         "basement": [(480, 250, 560, 380, "#3a2a1a"), (600, 270, 670, 380, "#33251a")],
         "attic": [(470, 240, 560, 330, "#4a3a20"), (580, 270, 680, 330, "#3d3018"), (700, 200, 760, 330, "#33280f")],
         "dining room": [(420, 300, 780, 340, "#4a1c1c"), (440, 340, 460, 430, "#2a1010"), (740, 340, 760, 430, "#2a1010")],
         "garden": [(500, 250, 640, 330, "#3a4a44"), (540, 180, 600, 250, "#2f3a36")]}
BOOKS = ["#5a1e1e", "#1e3a5a", "#3a5a1e", "#5a4a1e", "#4a1e5a"]


class Game:
    def __init__(s, root):
        s.root, s.t, s.wid, s.gpos, s.on_enter = root, 0.0, [], None, None
        s.name = "Stranger"
        root.title("HAUNTED HOUSE ESCAPE")
        root.resizable(False, False)
        s.c = tk.Canvas(root, width=W, height=H, bg=BG, highlightthickness=0)
        s.c.pack()
        root.bind("<Return>", lambda e: s.on_enter and s.on_enter())
        s.title()
        s.tick()

    # ---------- state ----------
    def reset(s):
        s.lives, s.score, s.inv, s.done = 3, 0, [], []
        s.pool = random.sample(RIDDLES, len(RIDDLES))

    # ---------- helpers ----------
    def clear(s):
        for w in s.wid: w.destroy()
        s.wid, s.gpos, s.on_enter = [], None, None
        s.c.delete("all")

    def txt(s, x, y, t, size=14, col=INK, **k):
        return s.c.create_text(x, y, text=t, fill=col, font=("Georgia", size), **k)

    def btn(s, x, y, w, h, label, cmd):
        t = "b%d" % random.randrange(10 ** 9)
        r = s.c.create_rectangle(x, y, x + w, y + h, fill="#1a1216", outline="#8a1c1c", width=2, tags=t)
        s.c.create_text(x + w / 2, y + h / 2, text=label, fill="#e6d9b8", font=("Georgia", 13), tags=t)
        s.c.tag_bind(t, "<Button-1>", lambda e: cmd())
        s.c.tag_bind(t, "<Enter>", lambda e: s.c.itemconfig(r, fill="#3a1414"))
        s.c.tag_bind(t, "<Leave>", lambda e: s.c.itemconfig(r, fill="#1a1216"))

    def field(s, y, text=""):
        e = tk.Entry(s.root, font=("Georgia", 14), justify="center", bg="#120d0d", fg=INK,
                     insertbackground=INK, relief="flat")
        e.insert(0, text)
        s.wid.append(e)
        s.c.create_window(400, y, window=e, width=280, height=34)
        return e

    def hud(s):
        s.txt(20, 16, "LIVES  " + "\u2665 " * s.lives + "\u2661 " * (3 - s.lives), 12, "#d33", anchor="w")
        s.txt(400, 16, "%s   \u00b7   Score %d" % (s.name, s.score), 12)
        s.txt(780, 16, "Key fragments %d/%d" % (len(s.done), NEED), 12, anchor="e")

    # ---------- unique haunted art ----------
    def vig(s):  # dark vignette, like a lantern beam closing in
        s.c.create_oval(-120, -90, W + 120, H + 90, outline=BG, width=220)

    def fog(s):
        for _ in range(8):
            x, y = random.randint(-200, W), random.randint(420, 560)
            s.c.create_oval(x, y, x + random.randint(200, 340), y + random.randint(40, 70),
                            fill="#161a24", width=0, tags="fog")

    def sky(s, dawn=False):
        c = s.c
        for i in range(30):
            col = (30 + i * 7, 20 + i * 4, 50 + i) if dawn else (4 + i // 2, 4 + i // 2, 14 + i)
            c.create_rectangle(0, i * 20, W, i * 20 + 20, fill="#%02x%02x%02x" % col, width=0)
        if not dawn:
            for _ in range(70):
                x, y = random.randint(0, W), random.randint(0, 300)
                c.create_oval(x, y, x + 2, y + 2, fill="#9a9aa8", width=0)
            c.create_oval(575, 35, 685, 145, fill="#1a1c2a", width=0)
        c.create_oval(590, 50, 670, 130, fill="#ffd9a0" if dawn else "#e8e2c4", width=0)

    def house(s, col="#08070a", lit=True):
        c = s.c
        c.create_polygon(230, 260, 400, 140, 570, 260, fill=col, width=0)
        c.create_rectangle(250, 260, 550, 520, fill=col, width=0)
        c.create_rectangle(250, 170, 300, 260, fill=col, width=0)
        c.create_polygon(240, 175, 275, 110, 310, 175, fill=col, width=0)
        c.create_rectangle(500, 150, 520, 215, fill=col, width=0)
        c.create_rectangle(0, 520, W, H, fill=col, width=0)
        for x1, y1, x2, y2 in ((120, 540, 120, 380), (120, 430, 70, 380), (120, 410, 165, 350),
                               (120, 470, 80, 440), (125, 390, 100, 330)):
            c.create_line(x1, y1, x2, y2, fill=col, width=7)
        if lit:
            for x, y in ((280, 290), (350, 290), (430, 290), (500, 290), (280, 390), (500, 390)):
                c.create_rectangle(x, y, x + 34, y + 50, fill="#f2c14e", width=0, tags="win")
        c.create_rectangle(378, 420, 422, 520, fill="#000", width=0)

    def ghost(s, x, y, k=1.0):
        c, f = s.c, "#d8dde6"
        c.create_oval(x - 40 * k, y - 60 * k, x + 40 * k, y + 20 * k, fill=f, width=0, tags="ghost")
        pts = [x - 40, y - 20, x + 40, y - 20, x + 40, y + 70, x + 27, y + 52, x + 13, y + 70, x, y + 52,
               x - 13, y + 70, x - 27, y + 52, x - 40, y + 70]
        pts = [x + (p - x) * k if i % 2 == 0 else y + (p - y) * k for i, p in enumerate(pts)]
        c.create_polygon(pts, fill=f, width=0, tags="ghost")
        for dx in (-15, 15):
            c.create_oval(x + (dx - 7) * k, y - 30 * k, x + (dx + 7) * k, y - 8 * k, fill="#000", tags="ghost")
        c.create_oval(x - 8 * k, y, x + 8 * k, y + 22 * k, fill="#000", tags="ghost")

    def room_bg(s, name):
        c = s.c
        c.create_rectangle(0, 0, W, 380, fill=THEME[name], width=0)
        c.create_rectangle(0, 380, W, H, fill="#0d0b0a", width=0)
        for i in range(-6, 15):
            c.create_line(400, 380, i * 70, H, fill="#1c1714")
        c.create_rectangle(80, 80, 240, 260, fill="#0a0f1c", outline="#3a2a1a", width=8)
        c.create_oval(170, 100, 215, 145, fill="#d8d2b0", width=0)
        c.create_line(160, 80, 160, 260, fill="#3a2a1a", width=4)
        c.create_line(80, 170, 240, 170, fill="#3a2a1a", width=4)
        for r in (30, 60, 90, 120):
            c.create_line(r, 0, 0, r, fill="#4a4a4a")
            c.create_line(W - r, 0, W, r, fill="#4a4a4a")
        if name == "library":
            c.create_rectangle(470, 100, 770, 330, fill="#3a2312", width=0)
            for y in (165, 230, 295):
                for x in range(480, 760, 22):
                    c.create_rectangle(x, y - random.randint(30, 55), x + 16, y, fill=random.choice(BOOKS), width=0)
        for x1, y1, x2, y2, col in PROPS.get(name, []):
            c.create_rectangle(x1, y1, x2, y2, fill=col, width=0)
        s.gpos = (150, 310)
        c.create_oval(30, 190, 270, 430, fill="#c98a1a", stipple="gray25", width=0, tags="glow")
        c.create_rectangle(100, 350, 200, 365, fill="#2a1a10", width=0)
        c.create_rectangle(144, 322, 156, 350, fill="#d8ccaa", width=0)
        c.create_oval(146, 302, 154, 320, fill="#ffd25a", width=0, tags="win")

    # ---------- animation ----------
    def tick(s):
        c = s.c
        s.t += 0.15
        for i in c.find_withtag("win"):
            if random.random() < 0.15:
                c.itemconfig(i, fill=random.choice(("#f2c14e", "#f2c14e", "#5a3d0a", "#120c02")))
        for g in c.find_withtag("glow"):
            r, (gx, gy) = random.randint(110, 130), s.gpos
            c.coords(g, gx - r, gy - r, gx + r, gy + r)
        c.move("ghost", 0, math.sin(s.t) * 3)
        for i in c.find_withtag("fog"):
            c.move(i, 1, 0)
            if c.coords(i)[0] > W: c.move(i, -W - 500, 0)
        s.root.after(80, s.tick)

    # ---------- screens ----------
    def title(s):
        s.clear(); s.reset()
        s.sky(); s.house(); s.fog(); s.vig()
        s.txt(403, 113, "HAUNTED HOUSE", 54, "#400a0a")
        s.txt(400, 110, "HAUNTED HOUSE", 54, BLOOD)
        s.txt(400, 165, "E  S  C  A  P  E", 22)
        s.e = s.field(400, "Your name")
        s.e.bind("<FocusIn>", lambda ev: s.e.get() == "Your name" and s.e.delete(0, "end"))
        s.btn(300, 440, 200, 44, "ENTER THE HOUSE", s.begin)
        s.btn(300, 495, 200, 44, "READ THE DIARY", s.diary)
        s.on_enter = s.begin

    def diary(s):
        p = pathlib.Path(__file__).resolve().parent / "story.html"
        webbrowser.open(p.as_uri())

    def begin(s):
        n = s.e.get().strip()
        s.name = n if n and n != "Your name" else "Stranger"
        s.hall()

    def hall(s):
        s.clear(); c = s.c
        c.create_rectangle(0, 0, W, H, fill="#100c0e", width=0)
        for x in range(0, W, 50):
            c.create_rectangle(x, 0, x + 25, 400, fill="#160f13", width=0)
        for r in range(6):
            for k in range(20):
                if (r + k) % 2:
                    c.create_rectangle(k * 40, 400 + r * 33, k * 40 + 40, 433 + r * 33, fill="#16110f", width=0)
        c.create_line(400, 0, 400, 60, fill="#6a5a2a", width=2)
        c.create_oval(340, 60, 460, 84, outline="#6a5a2a", width=3)
        for x in (350, 375, 400, 425, 450):
            c.create_oval(x - 4, 44, x + 4, 60, fill="#ffd25a", width=0, tags="win")
        s.ghost(670, 300, 1); s.fog(); s.vig(); s.hud()
        s.txt(400, 70, "The Entrance Hall", 28, BLOOD)
        left = NEED - len(s.done)
        if left > 0:
            s.txt(400, 125, "Search the rooms. %d more key fragment%s to forge." % (left, "s" if left > 1 else ""), 13)
        else:
            s.txt(400, 125, "The key is forged! The %s hides the %s." % (EXIT[0], EXIT[1]), 13, "#f2c14e")
            s.btn(275, 500, 250, 46, "OPEN THE " + EXIT[1].upper(), s.secret)
        for i, r in enumerate([r for r in ROOMS if r not in s.done]):
            s.btn(50 + (i // 4) * 230, 190 + (i % 4) * 58, 210, 42, r.title(), lambda r=r: s.room(r))

    def room(s, name):
        s.clear(); s.room_bg(name); s.vig(); s.hud()
        s.txt(400, 70, name.title(), 30, BLOOD)
        s.txt(40, 415, ROOMS[name] + "  A pale shape hovers over it...", 13, width=400, anchor="nw")
        s.btn(40, 480, 260, 42, "Search (a ghost will ask a riddle)", lambda: s.riddle(name))
        s.btn(40, 530, 260, 42, "Back to the hall", s.hall)

    def riddle(s, name):
        s.clear(); s.cur = name
        s.q, s.a = s.pool.pop() if s.pool else random.choice(RIDDLES)
        s.c.create_rectangle(0, 0, W, H, fill="#07060a", width=0)
        s.fog(); s.ghost(400, 230, 2); s.vig(); s.hud()
        s.txt(400, 405, s.q, 15, width=640, justify="center")
        s.e = s.field(465); s.e.focus_set()
        s.btn(300, 500, 200, 42, "ANSWER", s.answer)
        s.on_enter = s.answer

    def answer(s):
        g = s.e.get().lower().strip()
        for p in ("a ", "an ", "the "):
            if g.startswith(p): g = g[len(p):]
        if g == s.a:
            item = ITEMS[s.cur]
            s.inv.append(item); s.done.append(s.cur); s.score += 10
            s.msg("The spirit fades...", "You take the %s. Key fragment %d/%d is yours!" % (item, len(s.done), NEED), s.hall)
        else:
            s.lives -= 1; s.score = max(0, s.score - 5)
            s.c.create_rectangle(0, 0, W, H, fill="#8a0000", width=0)
            s.ghost(400, 300, 3.5)
            s.root.after(450, (lambda: s.end(False)) if s.lives <= 0 else
                         (lambda: s.msg("WRONG!", "The ghost shrieks and hurls you into the hall.", s.hall, col=BLOOD)))

    def msg(s, title, text, cmd, label="Continue", col=INK):
        s.clear()
        s.c.create_rectangle(0, 0, W, H, fill="#07060a", width=0)
        s.fog(); s.vig(); s.hud()
        s.txt(400, 210, title, 30, col)
        s.txt(400, 300, text, 15, width=560, justify="center")
        s.btn(300, 400, 200, 44, label, cmd)
        s.on_enter = cmd

    def secret(s):
        s.score += 50 + 10 * s.lives
        s.end(True)

    def end(s, win):
        s.clear()
        s.sky(win); s.house("#0a0808", lit=False); s.fog(); s.vig()
        if win:
            s.txt(400, 90, "YOU ESCAPED!", 44, "#ffd9a0")
            s.txt(400, 150, "Dawn breaks as the %s swings open, %s." % (EXIT[1], s.name), 14, "#ffd9a0")
        else:
            s.ghost(400, 330, 1.4)
            s.txt(400, 90, "THE HOUSE KEEPS YOU", 40, BLOOD)
            s.txt(400, 150, "Your name joins the others on the wall.", 14)
        s.txt(400, 200, "Final score: %d   \u00b7   Items: %s" % (s.score, ", ".join(s.inv) or "none"), 13,
              width=700, justify="center")
        s.btn(250, 470, 140, 44, "PLAY AGAIN", s.title)
        s.btn(410, 470, 140, 44, "LEAVE", s.root.destroy)


if __name__ == "__main__":
    root = tk.Tk()
    Game(root)
    root.mainloop()
