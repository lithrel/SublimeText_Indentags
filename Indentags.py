import sublime
import sublime_plugin
import re

class IndentagsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sublime.status_message('[Indentags] indenting...')
        view    = self.view
        regions = view.sel()
        # if there are more than 1 region or region one and it's not empty
        if len(regions) > 1 or not regions[0].empty():
            for region in view.sel():
                if not region.empty():
                    s = view.substr(region)
                    s = self.indent(s)
                    view.replace(edit, region, s)
        # format all text
        else:
            alltextreg = sublime.Region(0, view.size())
            s = view.substr(alltextreg)
            s = self.indent(s)
            view.replace(edit, alltextreg, s)
        sublime.status_message('[Indentags] ended successfully.')

    # TODO: keep first whitespaces instead of trim, start pad at this position
    # TODO: new thread ?
    def indent(self, s):
        indentsize = self.view.settings().get('tab_size', 4)
        pad  = 0
        text = ''
        # convert to plain string without indents and spaces
        s = re.compile('>\s+([^\s])', re.DOTALL).sub('>\g<1>', s)
        # trim string
        s = s.strip(' \t\n\r')
        # add newline to iterate
        s = re.sub(r'(>)(<)(\/*)', r'\1\n\2\3', s)
        # iterate through lines
        for line in s.splitlines():
            # open and closing tags on same line - no change
            if re.match(r'.+<\/\w[^>]*>', line):
                action = 'open+close'
                indent = 0
            # closing tag - outdent now
            elif re.match(r'^<\/\w[^>]*>', line):
                action = 'close'
                pad = pad - indentsize
            # opening tag - don't pad this one, only subsequent tags
            elif re.match(r'^<\w[^>]*[^\/]>.*$', line):
                action = 'open'
                indent = indentsize
            # no indentation needed
            else:
                action = 'none'
                indent = 0

            # pad the line with the required number of leading spaces
            line = line.rjust(len(line) + pad)
            text = text + line + '\n'
            # update the pad size for subsequent lines
            if action != 'close':
                pad = pad + indent

            # if indent is too deep, markup is probably broken, back to 0
            if pad > indentsize * 50:
                sublime.status_message('[Indentags] This markup is out of control !')
                pad = 0

        return text