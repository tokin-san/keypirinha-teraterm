# Keypirinha launcher (keypirinha.com)

import keypirinha as kp
import keypirinha_util as kpu
import os

class Teraterm(kp.Plugin):

    SECTION_GENERAL = 'general'
    PREFIX_SECTION = 'session_'

    TARGET_ENTRY = 'entry'
    TARGET_CONNECT = 'connect'

    _exe_path = ''
    _sessions = []

    def on_start(self):
        self._read_config()
    
    def on_catalog(self):
        self._read_config()

        catalog = []
        cmd_entry = self.create_item(
            category = kp.ItemCategory.KEYWORD,
            label = "Teraterm: connect",
            short_desc = "connect with Teraterm",
            target = self.TARGET_ENTRY,
            args_hint = kp.ItemArgsHint.REQUIRED,
            hit_hint = kp.ItemHitHint.IGNORE
        )
        catalog.append(cmd_entry)

        self.set_catalog(catalog)

    def on_suggest(self, user_input, items_chain):
        if not items_chain:
            return

        suggestions = []
        if not os.path.isfile(self._exe_path):
            self.warn("WARN: Teraterm: exe_path {}".format(self._exe_path))
            cmd_err = self.create_error_item(
                label = "Teraterm: Configuration Error",
                short_desc = "exe files is not found."
            )
            suggestions.append(cmd_err)
        elif len(self._sessions) == 0:
            cmd_err = self.create_error_item(
                label = "Teraterm: Configuration Error",
                short_desc = "session is empty."
            )
            suggestions.append(cmd_err)
        else:
            self.dbg("TRACE: Teraterm: on_suggest {}".format(items_chain))
            if items_chain[0].target() == self.TARGET_ENTRY:
                for session in self._sessions:
                    dest = "{}@{}:{}".format(session['username'], session['hostname'], session['port'])
                    suggestions.append(self.create_item(
                        category = kp.ItemCategory.KEYWORD,
                        label = session['title'],
                        short_desc = dest,
                        target = kpu.kwargs_encode(
                            dest = dest, auth = session['auth']),
                        args_hint = kp.ItemArgsHint.FORBIDDEN,
                        hit_hint = kp.ItemHitHint.IGNORE
                    ))

        self.set_suggestions(suggestions)    

    def on_execute(self, item, action):
        self.dbg("TRACE: Teraterm: on_execute")
        if action:
            kpu.execute_default_action(self, item, action)
        else:
            item_target = kpu.kwargs_decode(item.target())

            command_args = []
            command_args.append(item_target['dest'])
            command_args.append('/ssh2')
            command_args.append('/ask4passwd')
            if item_target['auth']:
                command_args.append("/auth={}".format(item_target['auth']))

            kpu.shell_execute(
                self._exe_path,
                args = ' '.join(command_args)
            )
    
    def _read_config(self):
        self.dbg("TRACE: Teraterm: _read_config")

        self._sessions.clear()

        settings = self.load_settings()

        # general section
        self._exe_path = settings.get_stripped('exe_path', self.SECTION_GENERAL) or ""

        # session sections
        for section_name in settings.sections():
            if not section_name.lower().startswith(self.PREFIX_SECTION):
                continue
            
            session = {
                'title': section_name.replace(self.PREFIX_SECTION, ''),
                'hostname': settings.get_stripped('hostname', section_name),
                'port': settings.get_stripped('port', section_name),
                'auth': 'password',
                'username': settings.get_stripped('username', section_name),
                'password': None
            }
            self._sessions.append(session)
