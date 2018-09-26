import urwid

from estop.cli.node import RootNode

MODE_PAUSE = 0
MODE_PLAY = 1

PALETTE = [
    ('body', 'light gray', 'black'),
    ('head', 'light gray', 'dark blue'),
    ('footer', 'light gray', 'dark blue'),
    ('key', 'light cyan', 'dark blue'),
    ('title', 'yellow', 'dark blue'),
    ('cluster_name', 'white', 'dark blue'),
    ('cluster_unknown', 'white', 'black'),
    ('cluster_green', 'white', 'dark green'),
    ('cluster_yellow', 'white', 'brown'),
    ('cluster_red', 'white', 'dark red'),
    ('column_header', 'white', 'black'),
    ('mode_none', 'white', 'black'),
    ('mode_play', 'white', 'dark green'),
    ('mode_pause', 'white', 'dark red'),
    ('refresh', 'yellow', 'dark blue'),
    ('focus', 'yellow', 'dark blue'),
    ('field_title', 'yellow', 'black'),
    ('field_value', 'light gray', 'black'),
    ('message_info', 'white', 'dark green'),
    ('message_warning', 'white', 'brown'),
    ('message_error', 'white', 'dark red'),
]


class View:
    def __init__(self, controller):
        self.controller = controller

        self.__init_widgets()

        self.set_mode(MODE_PAUSE)

    def __init_widgets(self):
        # header content
        self.txt_title = urwid.Text(('title', 'ESTop'))

        self.txt_mode = urwid.Text('', align='center')
        self.map_mode = urwid.AttrMap(self.txt_mode, 'mode_none')

        self.txt_cluster_name = urwid.Text('', align='center')
        self.txt_cluster_version = urwid.Text('')
        self.txt_cluster_nodes = urwid.Text('')

        self.txt_cluster_status = urwid.Text('', align='center')
        self.map_cluster_status = urwid.AttrMap(self.txt_cluster_status, 'cluster_unknown')

        self.col_header = urwid.Columns(
            [
                (6, self.txt_title),
                (10, self.map_mode),
                self.txt_cluster_name,
                (10, self.txt_cluster_version),
                (10, self.txt_cluster_nodes),
                (10, self.map_cluster_status),
            ]
        )

        # main content
        self.txt_body = urwid.Text('')
        self.fil_body = urwid.Filler(self.txt_body)

        # footer content
        self.txt_footer = urwid.Text(
            [
                ('key', "P to Play/Pause"),
                ' | ',
                ('key', "R to refresh"),
                ' | ',
                ('key', "Enter to Fold/Unfold"),
                ' | ',
                ('key', "D to detail"),
                ' | ',
                ('key', "C to cancel"),
                ' | ',
                ('key', "Q to quit")
            ]
        )

        self.txt_refresh = urwid.Text('', align='right')

        self.col_footer = urwid.Columns(
            [
                self.txt_footer,
                (12, urwid.AttrWrap(self.txt_refresh, 'refresh'))
            ]
        )

        # frame content
        self.frm_main = urwid.Frame(
            urwid.AttrWrap(self.fil_body, 'body'),
            header=urwid.AttrWrap(self.col_header, 'head'),
            footer=urwid.AttrWrap(self.col_footer, 'footer')
        )
        self.view = self.frm_main

    def unhandled_input(self, k):
        if k in ('p', 'P', 'f4'):
            self.controller.play_pause()
        elif k in ('q', 'Q', 'f10'):
            self.controller.quit()
        elif k == 'f2':
            self.controller.dec_refresh_time()
            self.refresh()
        elif k == 'f3':
            self.controller.inc_refresh_time()
            self.refresh()
        elif k in ['r', 'f5']:
            self.controller.refresh()

    def set_mode(self, mode):
        if mode == MODE_PLAY:
            self.txt_mode.set_text('PLAY')
            self.map_mode.set_attr_map({None: 'mode_play'})
        elif mode == MODE_PAUSE:
            self.txt_mode.set_text('PAUSE')
            self.map_mode.set_attr_map({None: 'mode_pause'})

    def refresh(self):
        conn = self.controller.connector

        self.txt_refresh.set_text('Refresh {0}s'.format(self.controller.refresh_time))

        self.txt_cluster_name.set_text(conn.cluster_name)

        self.txt_cluster_status.set_text(conn.cluster_status)
        self.map_cluster_status.set_attr_map({None: 'cluster_' + conn.cluster_status})

        self.txt_cluster_nodes.set_text("{0} nodes".format(conn.number_of_nodes))

        content = urwid.TreeWalker(RootNode(self.controller))
        body = urwid.TreeListBox(content)
        self.frm_main.contents['body'] = (urwid.AttrWrap(body, 'body'), None)
