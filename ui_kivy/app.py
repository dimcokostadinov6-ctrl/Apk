
import os, time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.graphics import Color, Rectangle, Line
from kivy.metrics import dp
from core.services import SavePageService

class DrawArea(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw); self.orientation='vertical'; self.padding=dp(8); self.spacing=dp(8)
        self.canvas_box=BoxLayout(size_hint=(1,1)); self.add_widget(self.canvas_box)
        with self.canvas_box.canvas: Color(1,1,1,1); self.bg=Rectangle(size=self.canvas_box.size,pos=self.canvas_box.pos)
        self.canvas_box.bind(size=self._u,pos=self._u); self.lines=[]
        self.canvas_box.bind(on_touch_down=self._d, on_touch_move=self._m)
    def _u(self,*_): self.bg.size=self.canvas_box.size; self.bg.pos=self.canvas_box.pos
    def _d(self,w,t):
        if not self.canvas_box.collide_point(*t.pos): return
        with self.canvas_box.canvas: Color(0,0,0,1); self.lines.append(Line(points=[*t.pos], width=2))
    def _m(self,w,t):
        if not self.canvas_box.collide_point(*t.pos): return
        if self.lines: self.lines[-1].points += [*t.pos]
    def export_to_png(self, path): self.canvas_box.export_as_image().save(path)

class SearchView(Screen):
    def __init__(self, repo, **kw):
        super().__init__(**kw); self.repo=repo
        root=BoxLayout(orientation='vertical')
        top=GridLayout(cols=3, size_hint=(1,None), height=dp(64), padding=[dp(12),0,dp(12),0], spacing=dp(8))
        with top.canvas.before: Color(0,0,0,1); self._r=Rectangle(size=top.size,pos=top.pos)
        top.bind(size=lambda *_:self._u(top), pos=lambda *_:self._u(top))
        btn_back=Button(text='← Платно', size_hint=(None,1), width=dp(140)); btn_back.bind(on_press=lambda *_: setattr(self.manager,'current','draw'))
        top.add_widget(btn_back); top.add_widget(Label(text='Търсене', color=(1,1,1,1), font_size=dp(22))); top.add_widget(Label()); root.add_widget(top)
        bar=BoxLayout(orientation='horizontal', size_hint=(1,None), height=dp(56), padding=[dp(12),dp(8)], spacing=dp(8))
        self.search=TextInput(hint_text='🔍 Име…', multiline=False, font_size=dp(18))
        btn=Button(text='Търси'); btn.bind(on_press=self.on_search)
        bar.add_widget(self.search); bar.add_widget(btn); root.add_widget(bar)
        self.results=Label(text='', halign='left', valign='top', markup=True); self.results.bind(size=lambda *_: setattr(self.results,'text_size', self.results.size))
        sv=ScrollView(); sv.add_widget(self.results); root.add_widget(sv); self.add_widget(root)
    def _u(self,w): self._r.size=w.size; self._r.pos=w.pos
    def on_search(self,*_):
        rows=self.repo.search_by_name(self.search.text or '')
        self.results.text='Нищо не е намерено.' if not rows else '\n'.join([f'• [b]{n}[/b] — {t/100:.2f} лв' for n,t in rows])

class DrawView(Screen):
    def __init__(self, service: SavePageService, **kw):
        super().__init__(**kw); self.service=service
        root=BoxLayout(orientation='vertical')
        top=GridLayout(cols=3, size_hint=(1,None), height=dp(64), padding=[dp(12),0,dp(12),0], spacing=dp(8))
        with top.canvas.before: Color(0,0.4,1,1); self._r=Rectangle(size=top.size,pos=top.pos)
        top.bind(size=lambda *_:self._u(top), pos=lambda *_:self._u(top))
        btn_save=Button(text='Запази'); btn_save.bind(on_press=self.on_save); top.add_widget(btn_save)
        top.add_widget(Label(text='Платно', color=(1,1,1,1), font_size=dp(22)))
        btn_search=Button(text='Търсене'); btn_search.bind(on_press=lambda *_: setattr(self.manager,'current','search')); top.add_widget(btn_search)
        root.add_widget(top)
        self.draw=DrawArea(); root.add_widget(self.draw)
        self.status=Label(text='Готово', size_hint=(1,None), height=dp(28))
        root.add_widget(self.status); self.add_widget(root)
    def _u(self,w): self._r.size=w.size; self._r.pos=w.pos
    def on_save(self,*_):
        os.makedirs('pages', exist_ok=True)
        ts=time.strftime('%Y%m%d_%H%M%S'); path=f'pages/page_{ts}.png'
        try: self.draw.export_to_png(path)
        except Exception as e: self.status.text=f'Грешка: {e}'; return
        from datetime import datetime
        pid,n=self.service.save_drawn_page(path, datetime.now().isoformat(timespec='seconds'))
        self.draw.canvas_box.canvas.clear()
        with self.draw.canvas_box.canvas: Color(1,1,1,1); self.draw.bg=Rectangle(size=self.draw.canvas_box.size,pos=self.draw.canvas_box.pos)
        self.status.text=f'Запазено. Редове: {n}. PNG: {path}'

class VeresiyaApp(App):
    def __init__(self, repo, service, **kw):
        super().__init__(**kw); self.repo=repo; self.service=service
    def build(self):
        from kivy.uix.screenmanager import ScreenManager, FadeTransition
        sm=ScreenManager(transition=FadeTransition()); self.repo.init()
        sm.add_widget(DrawView(self.service, name='draw')); sm.add_widget(SearchView(self.repo, name='search')); sm.current='draw'; return sm
