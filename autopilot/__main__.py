from autopilot import core

if __name__ == '__main__':
    core = core.Core()
    core.load_plugin('backgroundupdater')
    core.load_plugin('dropbox')
    core.load_plugin('anycheck')
    core.execute_from_command_line()
